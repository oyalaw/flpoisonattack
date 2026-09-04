MODEL-AGNOSTIC FL POISON PROXY V27.1 — NON-TARGET TRANSPORT ISOLATION
=====================================================================

Purpose
-------
V27.1 fixes the repeated CNN truncation pattern observed on non-target client
10.42.0.47. In the previous V27 transport path, every plaintext Flower/gRPC
HTTP/2 client entered the gRPC rewriter and FlowControlBridge when live poisoning
was enabled, even when the client was not selected for attack. This meant a
non-target connection could still receive synthetic WINDOW_UPDATE credit and
have later real server credit suppressed.

V27.1 policy
------------
Target client (for example 10.42.0.210):
  - gRPC update reconstruction enabled
  - phase gate enabled
  - true update-space poisoning enabled
  - synthetic HTTP/2 flow credit allowed only when DATA is intentionally withheld
  - server WINDOW_UPDATE suppression allowed only to compensate that target credit

Non-target client (for example 10.42.0.47):
  - exact HTTP/2 frames forwarded immediately and unchanged
  - no GrpcStreamRewriter on forwarding path
  - no pending DATA queue on forwarding path
  - no synthetic WINDOW_UPDATE credit
  - no real server WINDOW_UPDATE suppression
  - peer/model observation runs asynchronously after forwarding
  - queue saturation disables observation rather than delaying transport

New diagnostics
---------------
Relay termination now records:
  - termination reason (peer EOF or exception type)
  - exception representation when present
  - bytes and frame/chunk counts
  - target FlowControlBridge outstanding credit
  - total synthetic credit granted and server credit suppressed
  - non-target async observer queue/drop/error counters

Validation performed
--------------------
1. Python compile/import checks: PASS
2. validate_update_space.py: PASS
3. Exact non-target client->server HTTP/2 byte preservation: PASS
4. No synthetic credit delivered to non-target client: PASS
5. Exact non-target server->client HTTP/2 byte preservation: PASS
6. Zero server-credit suppression for non-target client: PASS
7. Target authorization for 10.42.0.210 preserved: PASS
8. 62-tensor ResNet-18 scale test (~42.65 MiB raw parameters): PASS

Deployment
----------
Back up the current active directory first, then replace the corresponding
runtime files with the files in this release. At minimum replace poison_live.py.
For a reproducible authoritative runtime, replace the complete set.

Run before any live experiment:

  python3 -m py_compile *.py
  python3 validate_update_space.py
  python3 validate_transport_isolation_v27_1.py

Both validators must report status PASS.

Expected startup behavior for non-target 10.42.0.47:

  NON-TARGET HTTP/2 connection: transparent bidirectional relay;
  no rewriter, no synthetic WINDOW_UPDATE, no server-credit suppression;
  peer/model observation runs asynchronously

Expected startup behavior for target 10.42.0.210:

  TARGET HTTP/2 connection: update-space rewriter enabled;
  synthetic flow credit=True

Recommended next experiment
---------------------------
Use a short 10-round CNN smoke test before another 200-round run. Confirm that:
  - all five clients complete every round;
  - .47 does not truncate;
  - .47 logs synthetic_credit=0 and server_credit_suppressed=0;
  - .210 reaches update_space_poison_applied after warm-up and phase gating;
  - no relay terminates with an uninvestigated exception.
