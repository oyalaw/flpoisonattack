#!/usr/bin/env python3
"""Generate publication ready evaluation reports for phase aware FL poisoning experiments.

The program discovers timestamped analyzer, proxy, server, and client logs, removes
exact duplicates, forms run bundles, computes run level metrics for RQ1 to RQ5,
and aggregates repeated experiments using the mean and sample standard deviation.

Every plot is written as PNG, PDF, and EPS. Every numerical result is written as CSV.
The program never silently joins unrelated runs. Cross component metrics are produced
only when run identifiers agree or the observed time intervals overlap within the
configured tolerance.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import math
import re
import shutil
import sys
import traceback
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Optional

import matplotlib
matplotlib.use("Agg")
logging.getLogger("matplotlib.backends.backend_ps").setLevel(logging.ERROR)
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

try:
    from sklearn.metrics import (
        accuracy_score,
        confusion_matrix,
        f1_score,
        precision_score,
        recall_score,
    )
except ImportError as exc:
    raise SystemExit(
        "scikit-learn is required. Install dependencies with: "
        "python -m pip install pandas numpy matplotlib scikit-learn"
    ) from exc


TIMESTAMP_RE = re.compile(r"(?P<date>20\d{6})_(?P<time>\d{6})")
COPY_SUFFIX_RE = re.compile(r"\(\d+\)(?=\.[^.]+$)")
NON_ALNUM_RE = re.compile(r"[^A-Za-z0-9_.]+")

ROLE_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("analyzer_decision", re.compile(r"^analyzer_decision_log", re.I)),
    ("analyzer_phase", re.compile(r"^analyzer_phase_log", re.I)),
    ("analyzer_round", re.compile(r"^analyzer_round_log", re.I)),
    ("analyzer_wire_upload", re.compile(r"^analyzer_wire_upload_log", re.I)),
    ("analyzer_events", re.compile(r"^analyzer_events", re.I)),
    ("proxy_attack", re.compile(r"^proxy_attack_events", re.I)),
    ("proxy_resource", re.compile(r"^proxy_resource_log", re.I)),
    ("proxy_manifest", re.compile(r"^proxy_run_manifest", re.I)),
    ("server_metrics", re.compile(r"^server_metrics_log", re.I)),
    ("server_client_defense", re.compile(r"^server_client_defense_log", re.I)),
    ("server_round_defense", re.compile(r"^server_round_defense_log", re.I)),
    ("server_failure", re.compile(r"^server_failure_log", re.I)),
    ("server_manifest", re.compile(r"^server_run_manifest", re.I)),
    ("client_metrics", re.compile(r"^client_metrics_log", re.I)),
    ("inference_clients", re.compile(r".*_inference_clients", re.I)),
    ("inference_rounds", re.compile(r".*_inference_rounds", re.I)),
    ("inference_summary", re.compile(r".*_inference_summary", re.I)),
]

ROLE_COMPONENT = {
    "analyzer_decision": "analyzer",
    "analyzer_phase": "analyzer",
    "analyzer_round": "analyzer",
    "analyzer_wire_upload": "analyzer",
    "analyzer_events": "analyzer",
    "proxy_attack": "proxy",
    "proxy_resource": "proxy",
    "proxy_manifest": "proxy",
    "server_metrics": "server",
    "server_client_defense": "server",
    "server_round_defense": "server",
    "server_failure": "server",
    "server_manifest": "server",
    "inference_clients": "server",
    "inference_rounds": "server",
    "inference_summary": "server",
    "client_metrics": "client",
}

LOG_TIMEZONE = "America/New_York"


KEY_PLOT_METRICS = {
    "phase_accuracy",
    "phase_macro_f1",
    "fingerprint_accuracy",
    "fingerprint_macro_f1",
    "round_identification_accuracy",
    "trigger_precision",
    "trigger_recall",
    "trigger_f1",
    "mean_trigger_latency_s",
    "selective_modification_rate",
    "non_target_spillover_rate",
    "reconstruction_success_rate",
    "wire_compatibility_rate",
    "model_contract_hash_match_rate",
    "mean_projected_to_genuine_norm_ratio",
    "mean_genuine_projected_cosine",
    "mean_coordinate_containment_fraction",
    "mean_norm_containment_fraction",
    "mean_absolute_sparsity_drift",
    "malicious_admission_rate",
    "benign_rejection_rate",
    "defense_detection_accuracy",
    "defense_detection_macro_f1",
    "mean_flame_rejected_count",
    "final_global_accuracy",
    "final_global_macro_f1",
    "final_global_loss",
    "aulc_global_accuracy",
    "aulc_global_macro_f1",
    "mean_server_aggregation_duration_s",
    "mean_server_evaluation_duration_s",
    "mean_analyzer_decision_lag_ms",
    "mean_proxy_process_cpu_percent",
    "mean_proxy_rss_mb",
    "server_failure_count",
}

PHASE_MAP = {
    "download": "DOWNLOAD",
    "modeldown": "DOWNLOAD",
    "server_upload": "DOWNLOAD",
    "train": "TRAINING",
    "training": "TRAINING",
    "modeltrain": "TRAINING",
    "evaluate": "EVALUATION",
    "evaluation": "EVALUATION",
    "modelevaluate": "EVALUATION",
    "upload": "UPLOAD",
    "modelup": "UPLOAD",
    "server_download": "UPLOAD",
    "idle": "IDLE",
    "unknown": "UNKNOWN",
}


@dataclass
class FileRecord:
    path: Path
    role: str
    component: str
    file_timestamp: Optional[pd.Timestamp]
    sha256: str
    size_bytes: int
    rows: Optional[int] = None
    columns: Optional[int] = None
    experiment_id: str = ""
    run_id: str = ""
    condition: str = ""
    defense: str = ""
    attack: str = ""
    raw_attack: str = ""
    start_s: float = math.nan
    end_s: float = math.nan
    client_ips: set[str] = field(default_factory=set)
    metadata_error: str = ""


@dataclass
class ComponentRun:
    component_run_id: str
    component: str
    records: list[FileRecord]
    experiment_id: str = ""
    run_id: str = ""
    condition: str = ""
    defense: str = ""
    attack: str = ""
    raw_attack: str = ""
    start_s: float = math.nan
    end_s: float = math.nan
    client_ips: set[str] = field(default_factory=set)


@dataclass
class Bundle:
    bundle_id: str
    component_runs: list[ComponentRun]
    match_method: str
    match_score: float
    condition: str
    defense: str
    attack: str
    raw_attack: str

    def components(self) -> set[str]:
        return {run.component for run in self.component_runs}

    def files_for_role(self, role: str) -> list[Path]:
        paths: list[Path] = []
        for run in self.component_runs:
            for record in run.records:
                if record.role == role:
                    paths.append(record.path)
        return paths

    def first_file(self, role: str) -> Optional[Path]:
        files = self.files_for_role(role)
        return files[0] if files else None


class ReportContext:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.tables_dir = output_dir / "tables"
        self.figures_dir = output_dir / "figures"
        self.logs_dir = output_dir / "logs"
        self.tables_dir.mkdir(parents=True, exist_ok=True)
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.run_metrics: list[dict[str, Any]] = []
        self.issues: list[dict[str, Any]] = []
        self.generated_files: list[dict[str, Any]] = []

    def issue(self, severity: str, scope: str, message: str, bundle_id: str = "") -> None:
        self.issues.append(
            {
                "severity": severity,
                "scope": scope,
                "bundle_id": bundle_id,
                "message": message,
            }
        )

    def metric(
        self,
        bundle: Bundle,
        rq: str,
        metric: str,
        value: Any,
        unit: str = "",
        source_files: str = "",
        notes: str = "",
    ) -> None:
        numeric = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
        if pd.isna(numeric):
            return
        self.run_metrics.append(
            {
                "bundle_id": bundle.bundle_id,
                "condition": bundle.condition,
                "defense": bundle.defense,
                "attack": bundle.attack,
                "raw_attack": bundle.raw_attack,
                "rq": rq,
                "metric": metric,
                "value": float(numeric),
                "unit": unit,
                "source_files": source_files,
                "notes": notes,
            }
        )

    def save_table(self, df: pd.DataFrame, relative_name: str) -> Path:
        path = self.tables_dir / relative_name
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)
        self.generated_files.append(
            {"artifact_type": "csv", "path": str(path.relative_to(self.output_dir))}
        )
        return path

    def save_figure(self, fig: plt.Figure, stem: str) -> None:
        safe_stem = sanitize(stem)
        for ext in ("png", "pdf", "eps"):
            path = self.figures_dir / f"{safe_stem}.{ext}"
            kwargs: dict[str, Any] = {"bbox_inches": "tight"}
            if ext == "png":
                kwargs["dpi"] = 300
            if ext == "eps":
                kwargs["format"] = "eps"
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                fig.savefig(path, **kwargs)
            self.generated_files.append(
                {"artifact_type": ext, "path": str(path.relative_to(self.output_dir))}
            )
        plt.close(fig)


def sanitize(value: Any) -> str:
    text = str(value) if value is not None else "unknown"
    text = NON_ALNUM_RE.sub("_", text).strip("_.")
    return text or "unknown"


def nonempty(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    text = str(value).strip()
    return "" if text.lower() in {"", "nan", "none", "null"} else text


def first_nonempty(values: Iterable[Any]) -> str:
    for value in values:
        text = nonempty(value)
        if text:
            return text
    return ""


def sha256_file(path: Path, block_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            block = handle.read(block_size)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def detect_role(path: Path) -> Optional[str]:
    name = COPY_SUFFIX_RE.sub("", path.name)
    stem = path.stem
    for role, pattern in ROLE_PATTERNS:
        if pattern.match(stem) or pattern.match(name):
            return role
    return None


def parse_file_timestamp(path: Path) -> Optional[pd.Timestamp]:
    match = TIMESTAMP_RE.search(path.name)
    if not match:
        return None
    try:
        return pd.to_datetime(
            match.group("date") + match.group("time"), format="%Y%m%d%H%M%S"
        )
    except ValueError:
        return None


def to_epoch_seconds(values: pd.Series) -> pd.Series:
    if values.empty:
        return pd.Series(dtype=float)
    numeric = pd.to_numeric(values, errors="coerce")
    numeric_count = int(numeric.notna().sum())
    if pd.api.types.is_numeric_dtype(values) or numeric_count >= max(1, int(0.7 * len(values))):
        med = numeric.dropna().abs().median() if numeric.notna().any() else math.nan
        if pd.isna(med):
            return numeric.astype(float)
        if med > 1e17:
            return numeric / 1e9
        if med > 1e14:
            return numeric / 1e9
        if med > 1e11:
            return numeric / 1e3
        return numeric.astype(float)
    parsed = pd.to_datetime(values, errors="coerce")
    result = pd.Series(np.nan, index=values.index, dtype=float)
    valid = parsed.notna()
    if valid.any():
        try:
            if getattr(parsed.dt, "tz", None) is None:
                parsed = parsed.dt.tz_localize(LOG_TIMEZONE, ambiguous="NaT", nonexistent="shift_forward")
            parsed = parsed.dt.tz_convert("UTC")
            valid = parsed.notna()
            result.loc[valid] = parsed.loc[valid].astype("int64") / 1e9
        except (AttributeError, TypeError, ValueError):
            parsed_utc = pd.to_datetime(values, errors="coerce", utc=True)
            valid = parsed_utc.notna()
            result.loc[valid] = parsed_utc.loc[valid].astype("int64") / 1e9
    return result


def choose_time_series(df: pd.DataFrame) -> pd.Series:
    for column in (
        "ts_wall",
        "timestamp",
        "timestamp_utc",
        "packet_wall_time_ns",
        "first_wall_time_ns",
        "last_wall_time_ns",
        "phase_start",
    ):
        if column in df.columns:
            result = to_epoch_seconds(df[column])
            if result.notna().any():
                return result
    return pd.Series(np.nan, index=df.index, dtype=float)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        return json.load(handle)


def load_jsonl(path: Path, limit: Optional[int] = None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for index, line in enumerate(handle):
            if limit is not None and index >= limit:
                break
            line = line.strip()
            if not line:
                continue
            try:
                value = json.loads(line)
                if isinstance(value, dict):
                    rows.append(value)
            except json.JSONDecodeError:
                continue
    return rows


def get_nested(mapping: dict[str, Any], path: str, default: Any = "") -> Any:
    current: Any = mapping
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return default
        current = current[part]
    return current


def inspect_file(path: Path, role: str, digest: str) -> FileRecord:
    record = FileRecord(
        path=path,
        role=role,
        component=ROLE_COMPONENT[role],
        file_timestamp=parse_file_timestamp(path),
        sha256=digest,
        size_bytes=path.stat().st_size,
    )
    try:
        if path.suffix.lower() == ".csv":
            df = pd.read_csv(path, low_memory=False)
            record.rows = len(df)
            record.columns = len(df.columns)
            for column in ("experiment_id", "run_id", "condition"):
                if column in df.columns:
                    values = df[column].dropna().astype(str).unique().tolist()
                    setattr(record, column, first_nonempty(values))
            defense_values: list[Any] = []
            for column in ("effective_defense", "requested_defense"):
                if column in df.columns:
                    defense_values.extend(df[column].dropna().unique().tolist())
            record.defense = first_nonempty(defense_values)
            if "client_ip" in df.columns:
                record.client_ips.update(df["client_ip"].dropna().astype(str).unique())
            if "src_ip" in df.columns:
                record.client_ips.update(df["src_ip"].dropna().astype(str).unique())
            if "client_id" in df.columns:
                values = df["client_id"].dropna().astype(str)
                record.client_ips.update(value for value in values.unique() if re.match(r"^\d+\.\d+\.\d+\.\d+$", value))
            times = choose_time_series(df)
            if times.notna().any():
                record.start_s = float(times.min())
                record.end_s = float(times.max())
            if role == "inference_summary":
                pass
            if role.startswith("inference_"):
                prefix = TIMESTAMP_RE.split(path.stem)[0].rstrip("_")
                if prefix:
                    record.condition = record.condition or prefix
        elif path.suffix.lower() == ".json":
            obj = load_json(path)
            if not isinstance(obj, dict):
                return record
            record.experiment_id = nonempty(obj.get("experiment_id"))
            record.run_id = nonempty(obj.get("run_id"))
            record.condition = nonempty(obj.get("condition"))
            record.defense = first_nonempty(
                [
                    obj.get("requested_defense"),
                    get_nested(obj, "experiment_configuration.requested_defense"),
                    get_nested(obj, "configuration.live_active_defense"),
                ]
            )
            record.attack = first_nonempty(
                [get_nested(obj, "configuration.live_attack"), obj.get("attack")]
            )
            record.raw_attack = first_nonempty(
                [get_nested(obj, "configuration.live_raw_attack"), obj.get("raw_attack")]
            )
            start = obj.get("started_at_epoch_s")
            end = obj.get("ended_at_epoch_s")
            if start is not None:
                record.start_s = float(start)
            if end is not None:
                record.end_s = float(end)
            if math.isnan(record.start_s) and obj.get("timestamp") and role not in {"server_manifest", "inference_summary"}:
                parsed = to_epoch_seconds(pd.Series([obj.get("timestamp")])).iloc[0]
                if pd.notna(parsed):
                    record.start_s = record.end_s = float(parsed)
            if role == "inference_summary":
                record.condition = record.condition or nonempty(obj.get("condition"))
                record.defense = record.defense or nonempty(obj.get("requested_defense"))
        elif path.suffix.lower() == ".jsonl":
            rows = load_jsonl(path)
            record.rows = len(rows)
            if rows:
                record.columns = len(set().union(*(row.keys() for row in rows)))
                record.experiment_id = first_nonempty(row.get("experiment_id") for row in rows)
                record.run_id = first_nonempty(row.get("run_id") for row in rows)
                record.condition = first_nonempty(row.get("condition") for row in rows)
                raw_times = pd.Series(
                    [row.get("wall_time_ns", row.get("timestamp")) for row in rows]
                )
                times = to_epoch_seconds(raw_times)
                if times.notna().any():
                    record.start_s = float(times.min())
                    record.end_s = float(times.max())
    except Exception as exc:
        record.metadata_error = f"{type(exc).__name__}: {exc}"
    return record


def discover_files(input_dir: Path) -> tuple[list[FileRecord], pd.DataFrame]:
    candidates: list[Path] = []
    for path in input_dir.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".csv", ".json", ".jsonl"}:
            continue
        if any(part in {"evaluation_reports", "fl_evaluation_reports"} for part in path.parts):
            continue
        if detect_role(path):
            candidates.append(path)

    by_hash: dict[str, list[Path]] = {}
    for path in candidates:
        digest = sha256_file(path)
        by_hash.setdefault(digest, []).append(path)

    records: list[FileRecord] = []
    duplicate_rows: list[dict[str, Any]] = []
    for digest, paths in by_hash.items():
        preferred = sorted(
            paths,
            key=lambda p: (
                1 if COPY_SUFFIX_RE.search(p.name) else 0,
                0 if TIMESTAMP_RE.search(p.name) else 1,
                len(p.name),
                str(p),
            ),
        )[0]
        role = detect_role(preferred)
        if role is None:
            continue
        records.append(inspect_file(preferred, role, digest))
        for duplicate in paths:
            duplicate_rows.append(
                {
                    "sha256": digest,
                    "selected": str(preferred),
                    "file": str(duplicate),
                    "is_duplicate": duplicate != preferred,
                }
            )
    return records, pd.DataFrame(duplicate_rows)


def median_timestamp(records: list[FileRecord]) -> Optional[pd.Timestamp]:
    values = [record.file_timestamp for record in records if record.file_timestamp is not None]
    if not values:
        return None
    series = pd.Series(values).sort_values()
    return pd.Timestamp(series.iloc[len(series) // 2])


def merge_time_bounds(records: Iterable[FileRecord]) -> tuple[float, float]:
    starts = [record.start_s for record in records if not math.isnan(record.start_s)]
    ends = [record.end_s for record in records if not math.isnan(record.end_s)]
    return (min(starts) if starts else math.nan, max(ends) if ends else math.nan)


def group_component_runs(records: list[FileRecord]) -> list[ComponentRun]:
    grouped: dict[tuple[str, str], list[FileRecord]] = {}
    for record in records:
        # Files emitted by one process normally share the timestamp suffix even when
        # some auxiliary summaries omit run_id or experiment_id. Prefer that suffix
        # so the manifest, metrics, defense, failure, and inference files remain one
        # component run. Fall back to content identifiers only when no suffix exists.
        if record.file_timestamp is not None:
            stamp = record.file_timestamp.strftime("%Y%m%d_%H%M%S")
            key = (record.component, f"time:{stamp}")
        elif record.run_id:
            key = (record.component, f"run:{record.run_id}")
        elif record.experiment_id:
            key = (record.component, f"exp:{record.experiment_id}")
        else:
            key = (record.component, f"file:{record.path.name}")
        grouped.setdefault(key, []).append(record)

    component_runs: list[ComponentRun] = []
    for (component, key), group in grouped.items():
        start_s, end_s = merge_time_bounds(group)
        conditions = [record.condition for record in group]
        if not first_nonempty(conditions):
            parent_candidates = [record.path.parent.name for record in group]
            parent = first_nonempty(
                value for value in parent_candidates if value not in {"", ".", "mnt", "data"}
            )
        else:
            parent = ""
        condition = first_nonempty(conditions) or parent
        defense = first_nonempty(record.defense for record in group)
        attack = first_nonempty(record.attack for record in group)
        raw_attack = first_nonempty(record.raw_attack for record in group)
        if not condition:
            inference_names = [
                record.path.stem for record in group if record.role.startswith("inference_")
            ]
            for name in inference_names:
                match = TIMESTAMP_RE.search(name)
                if match:
                    condition = name[: match.start()].rstrip("_")
                    break
        component_runs.append(
            ComponentRun(
                component_run_id=f"{component}:{sanitize(key)}",
                component=component,
                records=sorted(group, key=lambda r: (r.role, str(r.path))),
                experiment_id=first_nonempty(record.experiment_id for record in group),
                run_id=first_nonempty(record.run_id for record in group),
                condition=condition,
                defense=defense,
                attack=attack,
                raw_attack=raw_attack,
                start_s=start_s,
                end_s=end_s,
                client_ips=set().union(*(record.client_ips for record in group)),
            )
        )
    return component_runs


def interval_gap(a: ComponentRun, b: ComponentRun) -> float:
    if math.isnan(a.start_s) or math.isnan(a.end_s) or math.isnan(b.start_s) or math.isnan(b.end_s):
        return math.inf
    if a.end_s < b.start_s:
        return b.start_s - a.end_s
    if b.end_s < a.start_s:
        return a.start_s - b.end_s
    return 0.0


def overlap_seconds(a: ComponentRun, b: ComponentRun) -> float:
    if math.isnan(a.start_s) or math.isnan(a.end_s) or math.isnan(b.start_s) or math.isnan(b.end_s):
        return 0.0
    return max(0.0, min(a.end_s, b.end_s) - max(a.start_s, b.start_s))


def pair_match(a: ComponentRun, b: ComponentRun, tolerance_s: float) -> tuple[bool, str, float]:
    if a.component == b.component:
        return False, "same_component", 0.0
    if a.run_id and b.run_id and a.run_id == b.run_id:
        return True, "exact_run_id", 100.0
    if a.experiment_id and b.experiment_id and a.experiment_id == b.experiment_id:
        return True, "exact_experiment_id", 90.0
    gap = interval_gap(a, b)
    overlap = overlap_seconds(a, b)
    if overlap > 0:
        common_ips = len(a.client_ips.intersection(b.client_ips))
        return True, "time_overlap", 70.0 + min(20.0, overlap / 10.0) + min(5.0, common_ips)
    if gap <= tolerance_s:
        common_ips = len(a.client_ips.intersection(b.client_ips))
        if common_ips > 0:
            return True, "near_time_with_common_client", 50.0 + min(10.0, common_ips) - gap / max(tolerance_s, 1)
    return False, "unmatched", 0.0


class UnionFind:
    def __init__(self, items: Iterable[str]):
        self.parent = {item: item for item in items}

    def find(self, item: str) -> str:
        while self.parent[item] != item:
            self.parent[item] = self.parent[self.parent[item]]
            item = self.parent[item]
        return item

    def union(self, a: str, b: str) -> None:
        root_a, root_b = self.find(a), self.find(b)
        if root_a != root_b:
            self.parent[root_b] = root_a


def load_overrides(path: Optional[Path]) -> pd.DataFrame:
    if path is None or not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, dtype=str).fillna("")


def apply_overrides(component_runs: list[ComponentRun], overrides: pd.DataFrame) -> None:
    if overrides.empty:
        return
    key_columns = [
        column
        for column in ("component_run_id", "experiment_id", "run_id", "file_timestamp")
        if column in overrides.columns
    ]
    for run in component_runs:
        matches = pd.Series(False, index=overrides.index)
        if "component_run_id" in key_columns:
            matches |= overrides["component_run_id"].eq(run.component_run_id)
        if "experiment_id" in key_columns and run.experiment_id:
            matches |= overrides["experiment_id"].eq(run.experiment_id)
        if "run_id" in key_columns and run.run_id:
            matches |= overrides["run_id"].eq(run.run_id)
        if "file_timestamp" in key_columns:
            stamp = median_timestamp(run.records)
            if stamp is not None:
                matches |= overrides["file_timestamp"].eq(stamp.strftime("%Y%m%d_%H%M%S"))
        selected = overrides[matches]
        if selected.empty:
            continue
        row = selected.iloc[0]
        run.condition = nonempty(row.get("condition")) or run.condition
        run.defense = nonempty(row.get("defense")) or run.defense
        run.attack = nonempty(row.get("attack")) or run.attack
        run.raw_attack = nonempty(row.get("raw_attack")) or run.raw_attack


def make_bundles(component_runs: list[ComponentRun], tolerance_s: float) -> tuple[list[Bundle], pd.DataFrame]:
    uf = UnionFind(run.component_run_id for run in component_runs)
    match_rows: list[dict[str, Any]] = []
    accepted_edges: list[tuple[str, str, str, float]] = []
    for i, left in enumerate(component_runs):
        for right in component_runs[i + 1 :]:
            matched, method, score = pair_match(left, right, tolerance_s)
            match_rows.append(
                {
                    "left_component_run": left.component_run_id,
                    "right_component_run": right.component_run_id,
                    "left_component": left.component,
                    "right_component": right.component,
                    "matched": matched,
                    "method": method,
                    "score": score,
                    "interval_gap_s": interval_gap(left, right),
                    "overlap_s": overlap_seconds(left, right),
                    "common_client_ips": len(left.client_ips.intersection(right.client_ips)),
                }
            )
            if matched:
                uf.union(left.component_run_id, right.component_run_id)
                accepted_edges.append((left.component_run_id, right.component_run_id, method, score))

    groups: dict[str, list[ComponentRun]] = {}
    for run in component_runs:
        groups.setdefault(uf.find(run.component_run_id), []).append(run)

    bundles: list[Bundle] = []
    for index, group in enumerate(sorted(groups.values(), key=lambda g: min(r.component_run_id for r in g)), start=1):
        components = [run.component for run in group]
        if len(components) != len(set(components)):
            # A transitive match must not combine two independent runs of the same component.
            # Split conservatively by component run instead of risking false end to end joins.
            for run in group:
                bundles.append(
                    Bundle(
                        bundle_id=f"bundle_{len(bundles)+1:04d}",
                        component_runs=[run],
                        match_method="conservative_split",
                        match_score=0.0,
                        condition=derive_condition([run]),
                        defense=run.defense,
                        attack=run.attack,
                        raw_attack=run.raw_attack,
                    )
                )
            continue
        methods = [edge[2] for edge in accepted_edges if edge[0] in {r.component_run_id for r in group} and edge[1] in {r.component_run_id for r in group}]
        scores = [edge[3] for edge in accepted_edges if edge[0] in {r.component_run_id for r in group} and edge[1] in {r.component_run_id for r in group}]
        bundles.append(
            Bundle(
                bundle_id=f"bundle_{len(bundles)+1:04d}",
                component_runs=group,
                match_method="+".join(sorted(set(methods))) if methods else "single_component",
                match_score=min(scores) if scores else 0.0,
                condition=derive_condition(group),
                defense=first_nonempty(run.defense for run in group),
                attack=first_nonempty(run.attack for run in group),
                raw_attack=first_nonempty(run.raw_attack for run in group),
            )
        )
    return bundles, pd.DataFrame(match_rows)


def derive_condition(group: list[ComponentRun]) -> str:
    explicit = first_nonempty(run.condition for run in group)
    if explicit:
        return sanitize(explicit)
    attack = first_nonempty(run.attack for run in group)
    raw_attack = first_nonempty(run.raw_attack for run in group)
    defense = first_nonempty(run.defense for run in group)
    parts = [part for part in (attack, raw_attack, defense) if part]
    return sanitize("_".join(parts)) if parts else "unlabeled"


def build_inventory(records: list[FileRecord]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for record in records:
        rows.append(
            {
                "file": str(record.path),
                "role": record.role,
                "component": record.component,
                "file_timestamp": record.file_timestamp.isoformat() if record.file_timestamp is not None else "",
                "sha256": record.sha256,
                "size_bytes": record.size_bytes,
                "rows": record.rows,
                "columns": record.columns,
                "experiment_id": record.experiment_id,
                "run_id": record.run_id,
                "condition": record.condition,
                "defense": record.defense,
                "attack": record.attack,
                "raw_attack": record.raw_attack,
                "start_epoch_s": record.start_s,
                "end_epoch_s": record.end_s,
                "client_ips": ";".join(sorted(record.client_ips)),
                "metadata_error": record.metadata_error,
            }
        )
    return pd.DataFrame(rows)


def build_component_registry(component_runs: list[ComponentRun]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for run in component_runs:
        rows.append(
            {
                "component_run_id": run.component_run_id,
                "component": run.component,
                "experiment_id": run.experiment_id,
                "run_id": run.run_id,
                "condition": run.condition,
                "defense": run.defense,
                "attack": run.attack,
                "raw_attack": run.raw_attack,
                "start_epoch_s": run.start_s,
                "end_epoch_s": run.end_s,
                "duration_s": run.end_s - run.start_s if not math.isnan(run.start_s) and not math.isnan(run.end_s) else math.nan,
                "client_ips": ";".join(sorted(run.client_ips)),
                "roles": ";".join(sorted(record.role for record in run.records)),
                "files": ";".join(str(record.path) for record in run.records),
            }
        )
    return pd.DataFrame(rows)


def build_bundle_registry(bundles: list[Bundle]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for bundle in bundles:
        rows.append(
            {
                "bundle_id": bundle.bundle_id,
                "condition": bundle.condition,
                "defense": bundle.defense,
                "attack": bundle.attack,
                "raw_attack": bundle.raw_attack,
                "components": ";".join(sorted(bundle.components())),
                "match_method": bundle.match_method,
                "match_score": bundle.match_score,
                "component_run_ids": ";".join(run.component_run_id for run in bundle.component_runs),
                "experiment_ids": ";".join(sorted(set(run.experiment_id for run in bundle.component_runs if run.experiment_id))),
                "run_ids": ";".join(sorted(set(run.run_id for run in bundle.component_runs if run.run_id))),
                "files": ";".join(str(record.path) for run in bundle.component_runs for record in run.records),
            }
        )
    return pd.DataFrame(rows)


def read_csv(path: Optional[Path]) -> pd.DataFrame:
    if path is None or not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, low_memory=False)


def as_bool(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series.fillna(False)
    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.notna().any():
        return numeric.fillna(0).ne(0)
    return series.astype(str).str.strip().str.lower().isin({"true", "yes", "y", "1", "selected", "included"})


def normalize_phase(value: Any) -> str:
    text = nonempty(value).lower()
    return PHASE_MAP.get(text, text.upper() if text else "UNKNOWN")


def find_true_phase_intervals(client_df: pd.DataFrame) -> pd.DataFrame:
    required = {"phase", "phase_start", "phase_end"}
    if not required.issubset(client_df.columns):
        return pd.DataFrame()
    result = client_df.copy()
    result["true_phase"] = result["phase"].map(normalize_phase)
    result["start_s"] = to_epoch_seconds(result["phase_start"])
    result["end_s"] = to_epoch_seconds(result["phase_end"])
    if "src_ip" in result.columns:
        result["true_client"] = result["src_ip"].astype(str)
    else:
        result["true_client"] = result.get("client_id", pd.Series("", index=result.index)).astype(str)
    result["true_round"] = pd.to_numeric(result.get("round"), errors="coerce")
    return result.dropna(subset=["start_s", "end_s"])


def align_predictions_to_intervals(
    prediction_df: pd.DataFrame,
    intervals: pd.DataFrame,
    prediction_client_col: str,
    prediction_time_col: str,
    prediction_phase_col: str,
) -> pd.DataFrame:
    if intervals.empty or prediction_df.empty:
        return pd.DataFrame()
    pred = prediction_df.copy()
    pred["prediction_s"] = to_epoch_seconds(pred[prediction_time_col])
    pred["predicted_phase"] = pred[prediction_phase_col].map(normalize_phase)
    pred["predicted_client"] = pred[prediction_client_col].astype(str)
    aligned_rows: list[pd.DataFrame] = []
    for client, group in pred.groupby("predicted_client"):
        true_group = intervals[intervals["true_client"].eq(client)].sort_values("start_s")
        if true_group.empty:
            continue
        starts = true_group["start_s"].to_numpy()
        ends = true_group["end_s"].to_numpy()
        times = group["prediction_s"].to_numpy()
        indices = np.searchsorted(starts, times, side="right") - 1
        valid = (indices >= 0) & (indices < len(starts))
        valid_indices = np.where(valid)[0]
        if len(valid_indices) == 0:
            continue
        actual_idx = indices[valid_indices]
        inside = times[valid_indices] <= ends[actual_idx]
        valid_indices = valid_indices[inside]
        actual_idx = actual_idx[inside]
        if len(valid_indices) == 0:
            continue
        selected = group.iloc[valid_indices].copy()
        matched = true_group.iloc[actual_idx].reset_index(drop=True)
        selected = selected.reset_index(drop=True)
        selected["true_phase"] = matched["true_phase"]
        selected["true_round"] = matched["true_round"]
        selected["true_interval_start_s"] = matched["start_s"]
        selected["true_interval_end_s"] = matched["end_s"]
        aligned_rows.append(selected)
    return pd.concat(aligned_rows, ignore_index=True) if aligned_rows else pd.DataFrame()


def classification_metrics(y_true: pd.Series, y_pred: pd.Series) -> dict[str, float]:
    labels = sorted(set(y_true.astype(str)).union(set(y_pred.astype(str))))
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "macro_precision": precision_score(y_true, y_pred, labels=labels, average="macro", zero_division=0),
        "macro_recall": recall_score(y_true, y_pred, labels=labels, average="macro", zero_division=0),
        "macro_f1": f1_score(y_true, y_pred, labels=labels, average="macro", zero_division=0),
    }


def plot_confusion(ctx: ReportContext, matrix: np.ndarray, labels: list[str], title: str, stem: str) -> None:
    fig, ax = plt.subplots(figsize=(max(6, len(labels) * 1.1), max(5, len(labels) * 0.9)))
    image = ax.imshow(matrix)
    fig.colorbar(image, ax=ax)
    ax.set(
        xticks=np.arange(len(labels)),
        yticks=np.arange(len(labels)),
        xticklabels=labels,
        yticklabels=labels,
        xlabel="Predicted label",
        ylabel="True label",
        title=title,
    )
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    threshold = matrix.max() / 2 if matrix.size and matrix.max() else 0
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ax.text(j, i, f"{matrix[i, j]:g}", ha="center", va="center")
    fig.tight_layout()
    ctx.save_figure(fig, stem)


def evaluate_rq1(bundle: Bundle, ctx: ReportContext) -> None:
    analyzer_path = bundle.first_file("analyzer_decision")
    client_path = bundle.first_file("client_metrics")
    if analyzer_path is None or client_path is None:
        ctx.issue(
            "info",
            "RQ1",
            "Phase confusion requires matched analyzer decision and client metric files.",
            bundle.bundle_id,
        )
        return
    analyzer = read_csv(analyzer_path)
    client = read_csv(client_path)
    intervals = find_true_phase_intervals(client)
    if intervals.empty:
        ctx.issue("warning", "RQ1", "Client phase intervals are unavailable.", bundle.bundle_id)
        return
    phase_column = "decision_phase" if "decision_phase" in analyzer.columns else "stable_phase"
    time_column = "packet_wall_time_ns" if "packet_wall_time_ns" in analyzer.columns else "timestamp"
    if not {"client_id", phase_column, time_column}.issubset(analyzer.columns):
        ctx.issue("warning", "RQ1", "Analyzer phase prediction fields are incomplete.", bundle.bundle_id)
        return
    aligned = align_predictions_to_intervals(
        analyzer,
        intervals,
        prediction_client_col="client_id",
        prediction_time_col=time_column,
        prediction_phase_col=phase_column,
    )
    if aligned.empty:
        ctx.issue(
            "warning",
            "RQ1",
            "No analyzer predictions fell inside matched client phase intervals. Verify clocks and run matching.",
            bundle.bundle_id,
        )
        return
    metrics = classification_metrics(aligned["true_phase"], aligned["predicted_phase"])
    source = f"{analyzer_path.name};{client_path.name}"
    for metric, value in metrics.items():
        ctx.metric(bundle, "RQ1", f"phase_{metric}", value, "ratio", source)
    if "round" in aligned.columns:
        valid_round = pd.to_numeric(aligned["round"], errors="coerce").notna() & aligned["true_round"].notna()
        if valid_round.any():
            round_acc = (
                pd.to_numeric(aligned.loc[valid_round, "round"], errors="coerce")
                .eq(aligned.loc[valid_round, "true_round"])
                .mean()
            )
            ctx.metric(bundle, "RQ1", "round_identification_accuracy", round_acc, "ratio", source)
    ctx.metric(bundle, "RQ1", "phase_prediction_alignment_coverage", len(aligned) / max(len(analyzer), 1), "ratio", source)
    aligned["bundle_id"] = bundle.bundle_id
    ctx.save_table(aligned, f"rq1/{bundle.bundle_id}_aligned_phase_predictions.csv")

    labels = sorted(set(aligned["true_phase"]).union(set(aligned["predicted_phase"])))
    matrix = confusion_matrix(aligned["true_phase"], aligned["predicted_phase"], labels=labels)
    matrix_df = pd.DataFrame(matrix, index=labels, columns=labels).reset_index(names="true_phase")
    ctx.save_table(matrix_df, f"rq1/{bundle.bundle_id}_phase_confusion_counts.csv")
    plot_confusion(
        ctx,
        matrix,
        labels,
        f"RQ1 phase confusion: {bundle.condition}",
        f"rq1_{bundle.bundle_id}_phase_confusion",
    )

    predicted_client_columns = [
        column for column in ("predicted_client_id", "fingerprint_client_id", "fingerprinted_client") if column in analyzer.columns
    ]
    if predicted_client_columns:
        pred_column = predicted_client_columns[0]
        fingerprint = aligned.dropna(subset=[pred_column, "true_client"]).copy()
        if not fingerprint.empty:
            fp_metrics = classification_metrics(fingerprint["true_client"].astype(str), fingerprint[pred_column].astype(str))
            for metric, value in fp_metrics.items():
                ctx.metric(bundle, "RQ1", f"fingerprint_{metric}", value, "ratio", source)
            labels = sorted(set(fingerprint["true_client"].astype(str)).union(set(fingerprint[pred_column].astype(str))))
            matrix = confusion_matrix(fingerprint["true_client"].astype(str), fingerprint[pred_column].astype(str), labels=labels)
            ctx.save_table(
                pd.DataFrame(matrix, index=labels, columns=labels).reset_index(names="true_client"),
                f"rq1/{bundle.bundle_id}_fingerprint_confusion_counts.csv",
            )
            plot_confusion(
                ctx,
                matrix,
                labels,
                f"RQ1 client fingerprint confusion: {bundle.condition}",
                f"rq1_{bundle.bundle_id}_fingerprint_confusion",
            )
    else:
        ctx.issue(
            "warning",
            "RQ1",
            "No explicit predicted client fingerprint field was found. Flow IP identity is not treated as classifier output.",
            bundle.bundle_id,
        )


def true_upload_intervals(client: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    if client.empty:
        return pd.DataFrame(), "unavailable"
    start_candidates = ["wire_upload_start_ns", "wire_upload_start_s", "upload_start_time_s"]
    end_candidates = ["wire_upload_end_ns", "wire_upload_end_s", "upload_end_time_s"]
    start_col = next((column for column in start_candidates if column in client.columns), None)
    end_col = next((column for column in end_candidates if column in client.columns), None)
    quality = "independent_wire_ground_truth"
    if start_col is None or end_col is None:
        if {"phase", "phase_start", "phase_end"}.issubset(client.columns):
            selected = client[client["phase"].astype(str).str.lower().eq("upload")].copy()
            selected["upload_start_s"] = to_epoch_seconds(selected["phase_start"])
            selected["upload_end_s"] = to_epoch_seconds(selected["phase_end"])
            quality = "client_serialization_interval_only"
        else:
            return pd.DataFrame(), "unavailable"
    else:
        selected = client.copy()
        selected["upload_start_s"] = to_epoch_seconds(selected[start_col])
        selected["upload_end_s"] = to_epoch_seconds(selected[end_col])
    selected["client_ip_key"] = (
        selected["src_ip"].astype(str)
        if "src_ip" in selected.columns
        else selected.get("client_ip", selected.get("client_id", pd.Series("", index=selected.index))).astype(str)
    )
    selected["round_key"] = pd.to_numeric(selected.get("round"), errors="coerce")
    return selected.dropna(subset=["upload_start_s", "upload_end_s", "round_key"]), quality


def evaluate_rq2(bundle: Bundle, ctx: ReportContext) -> None:
    proxy_path = bundle.first_file("proxy_attack")
    analyzer_path = bundle.first_file("analyzer_decision")
    client_path = bundle.first_file("client_metrics")
    source_files = ";".join(path.name for path in (proxy_path, analyzer_path, client_path) if path is not None)

    if proxy_path is not None:
        proxy = read_csv(proxy_path)
        if not proxy.empty:
            selected = as_bool(proxy["selected_for_attack"]) if "selected_for_attack" in proxy.columns else pd.Series(False, index=proxy.index)
            targeted = as_bool(proxy["targeted"]) if "targeted" in proxy.columns else pd.Series(False, index=proxy.index)
            modified = as_bool(proxy["modified"]) if "modified" in proxy.columns else pd.Series(False, index=proxy.index)
            eligible_target = targeted & selected
            ctx.metric(bundle, "RQ2", "proxy_targeted_events", targeted.sum(), "count", source_files)
            ctx.metric(bundle, "RQ2", "proxy_selected_attack_events", selected.sum(), "count", source_files)
            ctx.metric(bundle, "RQ2", "proxy_modified_events", modified.sum(), "count", source_files)
            if eligible_target.any():
                ctx.metric(bundle, "RQ2", "selective_modification_rate", modified[eligible_target].mean(), "ratio", source_files)
            non_target = ~targeted
            if non_target.any():
                ctx.metric(bundle, "RQ2", "non_target_spillover_rate", modified[non_target].mean(), "ratio", source_files)
            if "phase_gate_open" in proxy.columns:
                ctx.metric(bundle, "RQ2", "phase_gate_open_rate", as_bool(proxy["phase_gate_open"]).mean(), "ratio", source_files)
            if "phase_client_match" in proxy.columns:
                valid = proxy["phase_client_match"].notna()
                if valid.any():
                    ctx.metric(bundle, "RQ2", "phase_client_match_rate", as_bool(proxy.loc[valid, "phase_client_match"]).mean(), "ratio", source_files)
            if {"phase_prediction_round", "fl_round"}.issubset(proxy.columns):
                left = pd.to_numeric(proxy["phase_prediction_round"], errors="coerce")
                right = pd.to_numeric(proxy["fl_round"], errors="coerce")
                valid = left.notna() & right.notna()
                if valid.any():
                    ctx.metric(bundle, "RQ2", "phase_round_match_rate", left[valid].eq(right[valid]).mean(), "ratio", source_files)

    if analyzer_path is None or client_path is None:
        ctx.issue(
            "info",
            "RQ2",
            "Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.",
            bundle.bundle_id,
        )
        return
    analyzer = read_csv(analyzer_path)
    client = read_csv(client_path)
    uploads, quality = true_upload_intervals(client)
    if uploads.empty:
        ctx.issue("warning", "RQ2", "No client upload intervals are available.", bundle.bundle_id)
        return
    if quality != "independent_wire_ground_truth":
        ctx.issue(
            "warning",
            "RQ2",
            "Upload timing uses client serialization intervals rather than independent wire transfer intervals.",
            bundle.bundle_id,
        )
    trigger_mask = pd.Series(False, index=analyzer.index)
    if "action" in analyzer.columns:
        trigger_mask = ~analyzer["action"].astype(str).str.lower().isin({"", "skip", "none", "nan"})
    if "trigger_publish_wall_time_ns" in analyzer.columns:
        trigger_mask |= pd.to_numeric(analyzer["trigger_publish_wall_time_ns"], errors="coerce").fillna(0).gt(0)
    triggers = analyzer[trigger_mask].copy()
    if triggers.empty:
        ctx.metric(bundle, "RQ2", "trigger_count", 0, "count", source_files, quality)
        return
    time_col = "trigger_publish_wall_time_ns" if "trigger_publish_wall_time_ns" in triggers.columns else "packet_wall_time_ns"
    triggers["trigger_s"] = to_epoch_seconds(triggers[time_col])
    if time_col == "trigger_publish_wall_time_ns":
        fallback = triggers["trigger_s"].isna() | triggers["trigger_s"].eq(0)
        if fallback.any() and "packet_wall_time_ns" in triggers.columns:
            triggers.loc[fallback, "trigger_s"] = to_epoch_seconds(triggers.loc[fallback, "packet_wall_time_ns"])
    triggers["client_ip_key"] = triggers["client_id"].astype(str)
    triggers["round_key"] = pd.to_numeric(triggers.get("round"), errors="coerce")

    rows: list[dict[str, Any]] = []
    for _, upload in uploads.iterrows():
        candidates = triggers[
            triggers["client_ip_key"].eq(upload["client_ip_key"])
            & triggers["round_key"].eq(upload["round_key"])
        ]
        inside = candidates[
            candidates["trigger_s"].between(upload["upload_start_s"], upload["upload_end_s"], inclusive="both")
        ]
        first_trigger = inside["trigger_s"].min() if not inside.empty else math.nan
        rows.append(
            {
                "bundle_id": bundle.bundle_id,
                "client_ip": upload["client_ip_key"],
                "round": upload["round_key"],
                "upload_start_s": upload["upload_start_s"],
                "upload_end_s": upload["upload_end_s"],
                "upload_duration_s": upload["upload_end_s"] - upload["upload_start_s"],
                "triggered_inside": not inside.empty,
                "trigger_count_inside": len(inside),
                "first_trigger_s": first_trigger,
                "trigger_latency_s": first_trigger - upload["upload_start_s"] if pd.notna(first_trigger) else math.nan,
                "ground_truth_quality": quality,
            }
        )
    upload_eval = pd.DataFrame(rows)
    trigger_inside_count = int(upload_eval["triggered_inside"].sum())
    trigger_recall = trigger_inside_count / max(len(upload_eval), 1)
    total_trigger_count = len(triggers)
    correct_trigger_count = int(upload_eval["trigger_count_inside"].sum())
    trigger_precision = correct_trigger_count / max(total_trigger_count, 1)
    ctx.metric(bundle, "RQ2", "trigger_precision", trigger_precision, "ratio", source_files, quality)
    ctx.metric(bundle, "RQ2", "trigger_recall", trigger_recall, "ratio", source_files, quality)
    if trigger_precision + trigger_recall > 0:
        ctx.metric(bundle, "RQ2", "trigger_f1", 2 * trigger_precision * trigger_recall / (trigger_precision + trigger_recall), "ratio", source_files, quality)
    if upload_eval["trigger_latency_s"].notna().any():
        ctx.metric(bundle, "RQ2", "mean_trigger_latency_s", upload_eval["trigger_latency_s"].mean(), "s", source_files, quality)
        ctx.metric(bundle, "RQ2", "p95_trigger_latency_s", upload_eval["trigger_latency_s"].quantile(0.95), "s", source_files, quality)
    ctx.save_table(upload_eval, f"rq2/{bundle.bundle_id}_upload_trigger_alignment.csv")


def evaluate_rq3(bundle: Bundle, ctx: ReportContext) -> None:
    proxy_path = bundle.first_file("proxy_attack")
    if proxy_path is None:
        return
    proxy = read_csv(proxy_path)
    if proxy.empty:
        return
    source = proxy_path.name
    modified = as_bool(proxy["modified"]) if "modified" in proxy.columns else pd.Series(False, index=proxy.index)
    rows = proxy[modified].copy()
    ctx.metric(bundle, "RQ3", "modified_update_count", modified.sum(), "count", source)
    if rows.empty:
        ctx.issue("info", "RQ3", "No modified proxy updates were logged.", bundle.bundle_id)
        return
    rate_fields = {
        "reconstruction_success_rate": "reconstruction_valid",
        "finite_value_validity_rate": "finite_values_valid",
        "wire_compatibility_rate": "wire_compatible",
        "update_space_usage_rate": "update_space_used",
        "global_model_cached_rate": "global_model_cached",
        "global_model_match_rate": "global_model_matched",
        "global_model_match_valid_rate": "global_model_match_valid",
        "global_norm_containment_rate": "envelope_global_norm_contained",
    }
    for metric, column in rate_fields.items():
        if column in rows.columns:
            valid = rows[column].notna()
            if valid.any():
                ctx.metric(bundle, "RQ3", metric, as_bool(rows.loc[valid, column]).mean(), "ratio", source)
    numeric_fields = {
        "mean_projected_to_genuine_norm_ratio": "projected_to_genuine_norm_ratio",
        "mean_genuine_projected_cosine": "cosine_genuine_to_projected_update",
        "mean_genuine_projected_distance": "distance_genuine_to_projected_update",
        "mean_coordinate_containment_fraction": "envelope_coordinate_containment_fraction",
        "mean_norm_containment_fraction": "envelope_norm_containment_fraction",
        "mean_direction_containment_cosine": "envelope_mean_direction_cosine",
        "mean_global_direction_cosine": "envelope_global_direction_cosine",
        "mean_rewrite_processing_duration_s": "rewrite_processing_duration_s",
    }
    for metric, column in numeric_fields.items():
        if column in rows.columns:
            values = pd.to_numeric(rows[column], errors="coerce")
            if values.notna().any():
                ctx.metric(bundle, "RQ3", metric, values.mean(), "ratio" if "fraction" in metric or "cosine" in metric or "ratio" in metric else "", source)
                ctx.metric(bundle, "RQ3", metric.replace("mean_", "std_", 1), values.std(ddof=1), "", source)
    if {"genuine_update_near_zero_fraction", "projected_update_near_zero_fraction"}.issubset(rows.columns):
        genuine = pd.to_numeric(rows["genuine_update_near_zero_fraction"], errors="coerce")
        projected = pd.to_numeric(rows["projected_update_near_zero_fraction"], errors="coerce")
        drift = (projected - genuine).abs()
        if drift.notna().any():
            ctx.metric(bundle, "RQ3", "mean_absolute_sparsity_drift", drift.mean(), "ratio", source)
    if {"global_model_contract_sha256", "model_contract_sha256"}.issubset(rows.columns):
        valid = rows["global_model_contract_sha256"].notna() & rows["model_contract_sha256"].notna()
        if valid.any():
            ctx.metric(
                bundle,
                "RQ3",
                "model_contract_hash_match_rate",
                rows.loc[valid, "global_model_contract_sha256"].astype(str).eq(rows.loc[valid, "model_contract_sha256"].astype(str)).mean(),
                "ratio",
                source,
            )
    selected_columns = [
        column
        for column in (
            "timestamp",
            "experiment_id",
            "run_id",
            "client_ip",
            "fl_round",
            "targeted",
            "selected_for_attack",
            "modified",
            "reconstruction_valid",
            "finite_values_valid",
            "wire_compatible",
            "update_space_used",
            "projected_to_genuine_norm_ratio",
            "cosine_genuine_to_projected_update",
            "distance_genuine_to_projected_update",
            "genuine_update_near_zero_fraction",
            "projected_update_near_zero_fraction",
            "envelope_coordinate_containment_fraction",
            "envelope_norm_containment_fraction",
            "envelope_mean_direction_cosine",
            "envelope_global_norm_contained",
            "envelope_global_direction_cosine",
            "rewrite_processing_duration_s",
        )
        if column in rows.columns
    ]
    ctx.save_table(rows[selected_columns], f"rq3/{bundle.bundle_id}_modified_update_geometry.csv")


def proxy_ground_truth(proxy: pd.DataFrame) -> pd.DataFrame:
    if proxy.empty or not {"client_ip", "fl_round"}.issubset(proxy.columns):
        return pd.DataFrame()
    result = proxy.copy()
    result["round_key"] = pd.to_numeric(result["fl_round"], errors="coerce")
    result["client_ip_key"] = result["client_ip"].astype(str)
    result["attack_ground_truth"] = as_bool(result["modified"]) if "modified" in result.columns else False
    grouped = (
        result.groupby(["round_key", "client_ip_key"], dropna=False)
        .agg(
            attack_ground_truth=("attack_ground_truth", "max"),
            proxy_event_count=("attack_ground_truth", "size"),
        )
        .reset_index()
    )
    return grouped.dropna(subset=["round_key"])


def evaluate_rq4(bundle: Bundle, ctx: ReportContext) -> None:
    server_client_path = bundle.first_file("server_client_defense")
    server_round_path = bundle.first_file("server_round_defense")
    proxy_path = bundle.first_file("proxy_attack")
    source = ";".join(path.name for path in (server_client_path, server_round_path, proxy_path) if path is not None)

    if server_round_path is not None:
        rounds = read_csv(server_round_path)
        if not rounds.empty:
            for metric, column in {
                "mean_inferred_suspicious_count": "inferred_suspicious_count",
                "mean_selected_suspicious_count": "selected_inferred_suspicious_count",
                "mean_flame_rejected_count": "flame_rejected_count",
                "mean_flame_main_cluster_size": "flame_main_cluster_size",
                "mean_aggregation_duration_s": "aggregation_duration_s",
            }.items():
                if column in rounds.columns:
                    values = pd.to_numeric(rounds[column], errors="coerce")
                    if values.notna().any():
                        ctx.metric(bundle, "RQ4", metric, values.mean(), "count" if "count" in metric or "size" in metric else "s", source)

    if server_client_path is None or proxy_path is None:
        if server_client_path is not None:
            ctx.issue(
                "info",
                "RQ4",
                "Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.",
                bundle.bundle_id,
            )
        return
    server = read_csv(server_client_path)
    proxy = read_csv(proxy_path)
    truth = proxy_ground_truth(proxy)
    if truth.empty or server.empty:
        return
    server = server.copy()
    server["round_key"] = pd.to_numeric(server["round"], errors="coerce")
    server["client_ip_key"] = server["client_ip"].astype(str)
    joined = server.merge(truth, on=["round_key", "client_ip_key"], how="inner", validate="many_to_one")
    if joined.empty:
        ctx.issue(
            "warning",
            "RQ4",
            "Proxy and server files were bundled but no round and client identities joined.",
            bundle.bundle_id,
        )
        return
    if "flame_in_main_cluster" in joined.columns and joined["flame_in_main_cluster"].notna().any():
        admitted = as_bool(joined["flame_in_main_cluster"])
        admission_field = "flame_in_main_cluster"
    elif "selected_or_included" in joined.columns:
        admitted = as_bool(joined["selected_or_included"])
        admission_field = "selected_or_included"
    else:
        admitted = pd.Series(False, index=joined.index)
        admission_field = "unavailable"
    malicious = as_bool(joined["attack_ground_truth"])
    if malicious.any():
        ctx.metric(bundle, "RQ4", "malicious_admission_rate", admitted[malicious].mean(), "ratio", source, admission_field)
        ctx.metric(bundle, "RQ4", "malicious_rejection_rate", (~admitted[malicious]).mean(), "ratio", source, admission_field)
    if (~malicious).any():
        ctx.metric(bundle, "RQ4", "benign_admission_rate", admitted[~malicious].mean(), "ratio", source, admission_field)
        ctx.metric(bundle, "RQ4", "benign_rejection_rate", (~admitted[~malicious]).mean(), "ratio", source, admission_field)
    if "inferred_suspicious" in joined.columns:
        suspicious = as_bool(joined["inferred_suspicious"])
        y_true = malicious.astype(int)
        y_pred = suspicious.astype(int)
        metrics = classification_metrics(y_true.astype(str), y_pred.astype(str))
        for metric, value in metrics.items():
            ctx.metric(bundle, "RQ4", f"defense_detection_{metric}", value, "ratio", source)
        labels = ["benign", "malicious"]
        matrix = confusion_matrix(y_true, y_pred, labels=[0, 1])
        ctx.save_table(
            pd.DataFrame(matrix, index=labels, columns=labels).reset_index(names="true_label"),
            f"rq4/{bundle.bundle_id}_defense_confusion_counts.csv",
        )
        plot_confusion(
            ctx,
            matrix,
            labels,
            f"RQ4 defense confusion: {bundle.condition}",
            f"rq4_{bundle.bundle_id}_defense_confusion",
        )
    joined["admitted"] = admitted
    joined["malicious"] = malicious
    ctx.save_table(joined, f"rq4/{bundle.bundle_id}_proxy_server_join.csv")

    byzantine = (
        joined.groupby("round_key")
        .agg(
            byzantine_count=("malicious", "sum"),
            malicious_admitted=("admitted", lambda s: int(s[joined.loc[s.index, "malicious"]].sum())),
            malicious_total=("malicious", "sum"),
            benign_rejected=("admitted", lambda s: int((~s[joined.loc[s.index, "malicious"] == False]).sum())),
        )
        .reset_index()
    )
    byzantine["malicious_admission_rate"] = byzantine["malicious_admitted"] / byzantine["malicious_total"].replace(0, np.nan)
    ctx.save_table(byzantine, f"rq4/{bundle.bundle_id}_dynamic_byzantine_rounds.csv")


def evaluate_learning(bundle: Bundle, ctx: ReportContext) -> list[pd.DataFrame]:
    curves: list[pd.DataFrame] = []
    server_path = bundle.first_file("server_metrics")
    if server_path is not None:
        df = read_csv(server_path)
        if not df.empty:
            if "measurement_scope" in df.columns:
                selected = df[df["measurement_scope"].astype(str).eq("aggregation_and_global_evaluation")].copy()
            elif "phase" in df.columns:
                selected = df[df["phase"].astype(str).str.lower().eq("server_download")].copy()
            else:
                selected = df.copy()
            selected["round"] = pd.to_numeric(selected["round"], errors="coerce")
            selected["bundle_id"] = bundle.bundle_id
            selected["condition"] = bundle.condition
            selected["source"] = "server"
            metric_columns = [column for column in ("global_accuracy", "global_macro_f1", "global_loss", "aggregation_duration_s", "evaluation_duration_s", "phase_duration_s") if column in selected.columns]
            curves.append(selected[["bundle_id", "condition", "round", "source"] + metric_columns])
            source = server_path.name
            ordered = selected.sort_values("round")
            if not ordered.empty:
                for column, unit in (
                    ("global_accuracy", "ratio"),
                    ("global_macro_f1", "ratio"),
                    ("global_loss", "loss"),
                ):
                    values = pd.to_numeric(ordered.get(column), errors="coerce") if column in ordered.columns else pd.Series(dtype=float)
                    if values.notna().any():
                        ctx.metric(bundle, "RQ5", f"final_{column}", values.dropna().iloc[-1], unit, source)
                        ctx.metric(bundle, "RQ5", f"best_{column}" if column != "global_loss" else "minimum_global_loss", values.max() if column != "global_loss" else values.min(), unit, source)
                        if column in {"global_accuracy", "global_macro_f1"}:
                            ctx.metric(bundle, "RQ5", f"aulc_{column}", values.mean(), unit, source)
                for column in ("aggregation_duration_s", "evaluation_duration_s", "phase_duration_s"):
                    if column in ordered.columns:
                        values = pd.to_numeric(ordered[column], errors="coerce")
                        if values.notna().any():
                            ctx.metric(bundle, "RQ5", f"mean_server_{column}", values.mean(), "s", source)
    client_path = bundle.first_file("client_metrics")
    if client_path is not None:
        df = read_csv(client_path)
        if not df.empty:
            train = df[df["phase"].astype(str).str.lower().eq("train")].copy() if "phase" in df.columns else df.copy()
            train["round"] = pd.to_numeric(train["round"], errors="coerce")
            train["bundle_id"] = bundle.bundle_id
            train["condition"] = bundle.condition
            train["source"] = "client"
            metric_columns = [column for column in ("accuracy", "f1_score", "loss", "fit_duration_s", "train_duration_s", "evaluation_duration_s") if column in train.columns]
            curves.append(train[["bundle_id", "condition", "round", "source"] + metric_columns])
            source = client_path.name
            ordered = train.sort_values("round")
            for column, unit in (
                ("accuracy", "ratio"),
                ("f1_score", "ratio"),
                ("loss", "loss"),
                ("fit_duration_s", "s"),
                ("train_duration_s", "s"),
                ("evaluation_duration_s", "s"),
            ):
                if column in ordered.columns:
                    values = pd.to_numeric(ordered[column], errors="coerce")
                    if values.notna().any():
                        prefix = "final" if column in {"accuracy", "f1_score", "loss"} else "mean"
                        ctx.metric(bundle, "RQ5", f"{prefix}_client_{column}", values.dropna().iloc[-1] if prefix == "final" else values.mean(), unit, source)
            for column in ("grpc_error_count", "retry_count", "disconnect_count"):
                if column in df.columns:
                    values = pd.to_numeric(df[column], errors="coerce")
                    if values.notna().any():
                        ctx.metric(bundle, "RQ5", f"client_{column}", values.max(), "count", source)
    return curves


def evaluate_system(bundle: Bundle, ctx: ReportContext) -> None:
    analyzer_path = bundle.first_file("analyzer_decision")
    if analyzer_path is not None:
        df = read_csv(analyzer_path)
        for metric, column, aggregation, unit in (
            ("mean_analyzer_decision_lag_ms", "decision_lag_ms", "mean", "ms"),
            ("p95_analyzer_decision_lag_ms", "decision_lag_ms", "p95", "ms"),
            ("mean_analyzer_cpu_percent", "analyzer_cpu_percent", "mean", "percent"),
            ("p95_analyzer_rss_mb", "analyzer_rss_mb", "p95", "MB"),
        ):
            if column in df.columns:
                values = pd.to_numeric(df[column], errors="coerce")
                if column == "decision_lag_ms":
                    values = values[values.ge(0)]
                if values.notna().any():
                    value = values.mean() if aggregation == "mean" else values.quantile(0.95)
                    ctx.metric(bundle, "RQ5", metric, value, unit, analyzer_path.name)
    resource_path = bundle.first_file("proxy_resource")
    if resource_path is not None:
        df = read_csv(resource_path)
        for metric, column, aggregation, unit in (
            ("mean_proxy_process_cpu_percent", "process_cpu_percent", "mean", "percent"),
            ("p95_proxy_process_cpu_percent", "process_cpu_percent", "p95", "percent"),
            ("mean_proxy_rss_mb", "process_rss_mb", "mean", "MB"),
            ("p95_proxy_rss_mb", "process_rss_mb", "p95", "MB"),
            ("mean_proxy_power_watts", "power_watts", "mean", "W"),
        ):
            if column in df.columns:
                values = pd.to_numeric(df[column], errors="coerce")
                if values.notna().any():
                    value = values.mean() if aggregation == "mean" else values.quantile(0.95)
                    ctx.metric(bundle, "RQ5", metric, value, unit, resource_path.name)
    failure_path = bundle.first_file("server_failure")
    if failure_path is not None:
        df = read_csv(failure_path)
        ctx.metric(bundle, "RQ5", "server_failure_count", len(df), "count", failure_path.name)
        if not df.empty and "recovered" in df.columns:
            ctx.metric(bundle, "RQ5", "server_failure_recovery_rate", as_bool(df["recovered"]).mean(), "ratio", failure_path.name)


def aggregate_run_metrics(ctx: ReportContext) -> tuple[pd.DataFrame, pd.DataFrame]:
    run_df = pd.DataFrame(ctx.run_metrics)
    if run_df.empty:
        return run_df, pd.DataFrame()
    group_columns = ["condition", "defense", "attack", "raw_attack", "rq", "metric", "unit"]
    aggregate = (
        run_df.groupby(group_columns, dropna=False)["value"]
        .agg(n_runs="count", mean="mean", std=lambda s: s.std(ddof=1), minimum="min", maximum="max")
        .reset_index()
    )
    aggregate["sem"] = aggregate["std"] / np.sqrt(aggregate["n_runs"])
    aggregate["ci95_half_width"] = 1.96 * aggregate["sem"]
    aggregate["ci95_low"] = aggregate["mean"] - aggregate["ci95_half_width"]
    aggregate["ci95_high"] = aggregate["mean"] + aggregate["ci95_half_width"]
    aggregate.loc[aggregate["n_runs"].lt(2), ["std", "sem", "ci95_half_width", "ci95_low", "ci95_high"]] = np.nan
    return run_df.sort_values(["rq", "condition", "metric", "bundle_id"]), aggregate.sort_values(["rq", "metric", "condition"])


def plot_aggregate_metric_groups(ctx: ReportContext, aggregate: pd.DataFrame, plot_all: bool = False) -> None:
    if aggregate.empty:
        return
    for rq, rq_df in aggregate.groupby("rq"):
        selected_metrics = rq_df["metric"].unique().tolist()
        if not plot_all:
            selected_metrics = [metric for metric in selected_metrics if metric in KEY_PLOT_METRICS]
        for metric in selected_metrics:
            data = rq_df[rq_df["metric"].eq(metric)].copy()
            if data.empty or data["mean"].isna().all():
                continue
            data = data.sort_values("condition")
            fig, ax = plt.subplots(figsize=(max(7, len(data) * 1.3), 5))
            x = np.arange(len(data))
            yerr = data["std"].fillna(0).to_numpy()
            ax.bar(x, data["mean"].to_numpy(), yerr=yerr, capsize=4)
            ax.set_xticks(x)
            ax.set_xticklabels(data["condition"], rotation=35, ha="right")
            ax.set_ylabel(first_nonempty(data["unit"].tolist()) or "Value")
            ax.set_title(f"{rq}: {metric.replace('_', ' ')}")
            ax.grid(axis="y", linewidth=0.5)
            fig.tight_layout()
            ctx.save_figure(fig, f"{rq.lower()}_{metric}_mean_std")


def aggregate_curves(curves: list[pd.DataFrame], ctx: ReportContext) -> None:
    if not curves:
        return
    all_curves = pd.concat(curves, ignore_index=True, sort=False)
    ctx.save_table(all_curves, "rq5/learning_curves_run_values.csv")
    identifiers = {"bundle_id", "condition", "round", "source"}
    metric_columns = [column for column in all_curves.columns if column not in identifiers]
    aggregate_rows: list[pd.DataFrame] = []
    for source, source_df in all_curves.groupby("source"):
        for metric in metric_columns:
            if metric not in source_df.columns:
                continue
            work = source_df[["condition", "round", metric]].copy()
            work[metric] = pd.to_numeric(work[metric], errors="coerce")
            work = work.dropna(subset=["round", metric])
            if work.empty:
                continue
            summary = (
                work.groupby(["condition", "round"])[metric]
                .agg(n_runs="count", mean="mean", std=lambda s: s.std(ddof=1))
                .reset_index()
            )
            summary["source"] = source
            summary["metric"] = metric
            aggregate_rows.append(summary)
            fig, ax = plt.subplots(figsize=(8, 5))
            for condition, condition_df in summary.groupby("condition"):
                condition_df = condition_df.sort_values("round")
                yerr = condition_df["std"].fillna(0).to_numpy()
                error_every = max(1, len(condition_df) // 20)
                ax.errorbar(
                    condition_df["round"],
                    condition_df["mean"],
                    yerr=yerr,
                    label=condition,
                    capsize=2,
                    errorevery=error_every,
                )
            ax.set_xlabel("Communication round")
            ax.set_ylabel(metric.replace("_", " "))
            ax.set_title(f"RQ5 {source} {metric.replace('_', ' ')}: mean and standard deviation")
            ax.grid(linewidth=0.5)
            ax.legend()
            fig.tight_layout()
            ctx.save_figure(fig, f"rq5_{source}_{metric}_learning_curve")
    if aggregate_rows:
        ctx.save_table(pd.concat(aggregate_rows, ignore_index=True), "rq5/learning_curves_mean_std.csv")


def make_metric_catalog() -> pd.DataFrame:
    rows = [
        ("RQ1", "Phase accuracy, macro precision, recall, F1, confusion matrix", "client_metrics_log; analyzer_decision_log", "client: phase, phase_start, phase_end, src_ip, round; analyzer: decision_phase, decision_confidence, client_id, packet_wall_time_ns, round"),
        ("RQ1", "Client fingerprint accuracy and confusion matrix", "client_metrics_log; analyzer_decision_log", "client: src_ip or client_id; analyzer: predicted_client_id or fingerprint_client_id"),
        ("RQ2", "Trigger precision, recall, F1, latency", "client_metrics_log; analyzer_decision_log", "wire_upload_start_ns, wire_upload_end_ns, client_id or src_ip, round; action, trigger_publish_wall_time_ns, packet_wall_time_ns"),
        ("RQ2", "Selective modification and spillover", "proxy_attack_events", "targeted, selected_for_attack, modified, phase_gate_open, phase_client_match, phase_prediction_round, fl_round"),
        ("RQ3", "Update reconstruction and protocol compatibility", "proxy_attack_events", "modified, reconstruction_valid, finite_values_valid, wire_compatible, update_space_used, global_model_matched, contract hashes"),
        ("RQ3", "Benign geometry preservation", "proxy_attack_events", "projected_to_genuine_norm_ratio, cosine_genuine_to_projected_update, distance_genuine_to_projected_update, sparsity fields, envelope containment fields"),
        ("RQ4", "Malicious admission and benign rejection", "proxy_attack_events; server_client_defense_log", "proxy: modified, client_ip, fl_round; server: round, client_ip, selected_or_included, flame_in_main_cluster"),
        ("RQ4", "Defense detection confusion matrix", "proxy_attack_events; server_client_defense_log", "proxy modified ground truth; server inferred_suspicious"),
        ("RQ5", "Global learning impact", "server_metrics_log", "round, global_accuracy, global_macro_f1, global_loss"),
        ("RQ5", "Client learning and timing", "client_metrics_log", "round, accuracy, f1_score, loss, fit_duration_s, train_duration_s, evaluation_duration_s"),
        ("RQ5", "Systems overhead and reliability", "analyzer_decision_log; proxy_resource_log; proxy_attack_events; server_metrics_log; server_failure_log", "decision_lag_ms, CPU, RSS, rewrite_processing_duration_s, aggregation_duration_s, evaluation_duration_s, failures"),
    ]
    return pd.DataFrame(rows, columns=["research_question", "report_metric", "source_files", "fields"])


def create_metadata_template(component_registry: pd.DataFrame, output_path: Path) -> None:
    columns = ["component_run_id", "experiment_id", "run_id"]
    template = component_registry[columns].copy()
    timestamp_values = []
    for value in component_registry.get("files", pd.Series("", index=component_registry.index)):
        match = TIMESTAMP_RE.search(str(value))
        timestamp_values.append(match.group(0) if match else "")
    template["file_timestamp"] = timestamp_values
    template["condition"] = component_registry.get("condition", "")
    template["defense"] = component_registry.get("defense", "")
    template["attack"] = component_registry.get("attack", "")
    template["raw_attack"] = component_registry.get("raw_attack", "")
    template["model"] = ""
    template["dataset"] = ""
    template["repetition"] = ""
    template.to_csv(output_path, index=False)


def write_summary(ctx: ReportContext, bundles: list[Bundle], aggregate: pd.DataFrame) -> None:
    lines = [
        "# Federated learning evaluation report",
        "",
        f"Discovered run bundles: {len(bundles)}",
        f"Run level metrics: {len(ctx.run_metrics)}",
        f"Data quality issues: {len(ctx.issues)}",
        "",
        "## Interpretation rule",
        "",
        "Metrics are first computed once per run. Repeated experiments are then aggregated by condition using the arithmetic mean and sample standard deviation. Cross component metrics are omitted when the logs cannot be matched safely.",
        "",
        "## Aggregate metrics",
        "",
    ]
    if aggregate.empty:
        lines.append("No aggregate metrics were produced.")
    else:
        display = aggregate[["rq", "condition", "metric", "n_runs", "mean", "std", "ci95_low", "ci95_high", "unit"]].copy()
        lines.append(display.to_markdown(index=False))
    lines.extend(["", "## Data quality notes", ""])
    if ctx.issues:
        for issue in ctx.issues:
            lines.append(f"{issue['severity'].upper()}: {issue['scope']} {issue['bundle_id']} {issue['message']}")
    else:
        lines.append("No issues were recorded.")
    path = ctx.output_dir / "evaluation_summary.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    ctx.generated_files.append({"artifact_type": "markdown", "path": str(path.relative_to(ctx.output_dir))})


def package_output(output_dir: Path) -> Path:
    archive_base = output_dir.parent / output_dir.name
    archive_path = Path(shutil.make_archive(str(archive_base), "zip", root_dir=output_dir))
    return archive_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("."), help="Directory containing all experiment logs")
    parser.add_argument("--output", type=Path, default=Path("fl_evaluation_reports"), help="Report output directory")
    parser.add_argument("--metadata", type=Path, default=None, help="Optional experiment metadata CSV for condition labels")
    parser.add_argument("--match-tolerance-seconds", type=float, default=120.0, help="Maximum nonoverlap gap for a temporal match when client identities also agree")
    parser.add_argument("--timezone", default="America/New_York", help="IANA timezone used by naive log timestamps")
    parser.add_argument("--plot-all-metrics", action="store_true", help="Create a bar chart for every aggregate metric instead of the publication focused subset")
    parser.add_argument("--no-zip", action="store_true", help="Do not create a ZIP archive")
    return parser.parse_args()


def main() -> int:
    global LOG_TIMEZONE
    args = parse_args()
    LOG_TIMEZONE = args.timezone
    input_dir = args.input.resolve()
    output_dir = args.output.resolve()
    if not input_dir.exists():
        raise SystemExit(f"Input directory does not exist: {input_dir}")
    if output_dir.exists():
        shutil.rmtree(output_dir)
    ctx = ReportContext(output_dir)

    records, duplicates = discover_files(input_dir)
    if not records:
        raise SystemExit("No recognized FL log files were found.")
    ctx.save_table(build_inventory(records), "data_quality/file_inventory.csv")
    ctx.save_table(duplicates, "data_quality/duplicate_files.csv")

    component_runs = group_component_runs(records)
    overrides = load_overrides(args.metadata)
    apply_overrides(component_runs, overrides)
    component_registry = build_component_registry(component_runs)
    ctx.save_table(component_registry, "data_quality/component_run_registry.csv")
    create_metadata_template(component_registry, output_dir / "experiment_metadata_template.csv")
    ctx.generated_files.append({"artifact_type": "csv", "path": "experiment_metadata_template.csv"})

    bundles, match_table = make_bundles(component_runs, args.match_tolerance_seconds)
    ctx.save_table(match_table, "data_quality/run_match_candidates.csv")
    ctx.save_table(build_bundle_registry(bundles), "data_quality/run_bundle_registry.csv")
    ctx.save_table(make_metric_catalog(), "metric_file_field_catalog.csv")

    curves: list[pd.DataFrame] = []
    for bundle in bundles:
        try:
            evaluate_rq1(bundle, ctx)
            evaluate_rq2(bundle, ctx)
            evaluate_rq3(bundle, ctx)
            evaluate_rq4(bundle, ctx)
            curves.extend(evaluate_learning(bundle, ctx))
            evaluate_system(bundle, ctx)
        except Exception as exc:
            ctx.issue(
                "error",
                "evaluation",
                f"{type(exc).__name__}: {exc}",
                bundle.bundle_id,
            )
            error_path = ctx.logs_dir / f"{bundle.bundle_id}_error.txt"
            error_path.write_text(traceback.format_exc(), encoding="utf-8")

    run_metrics, aggregate = aggregate_run_metrics(ctx)
    ctx.save_table(run_metrics, "run_level_metrics.csv")
    ctx.save_table(aggregate, "aggregate_mean_std_metrics.csv")
    plot_aggregate_metric_groups(ctx, aggregate, plot_all=args.plot_all_metrics)
    aggregate_curves(curves, ctx)

    issues_df = pd.DataFrame(ctx.issues, columns=["severity", "scope", "bundle_id", "message"])
    ctx.save_table(issues_df, "data_quality/data_quality_issues.csv")
    write_summary(ctx, bundles, aggregate)

    index = pd.DataFrame(ctx.generated_files).drop_duplicates()
    ctx.save_table(index, "report_index.csv")

    archive = None
    if not args.no_zip:
        archive = package_output(output_dir)
    print(f"Report directory: {output_dir}")
    if archive:
        print(f"ZIP archive: {archive}")
    print(f"Run bundles: {len(bundles)}")
    print(f"Run level metrics: {len(run_metrics)}")
    print(f"Aggregate metrics: {len(aggregate)}")
    print(f"Quality issues: {len(ctx.issues)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
