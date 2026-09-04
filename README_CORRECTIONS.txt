CORRECTED SELECTION ATTACK RUNTIME
==================================

Replace the files in the active poisoning runtime with the files in this folder.
Keep all files together under the exact clean filenames shown here.

Modified files
--------------
selection_attacks.py
  Min Sum now uses sums of squared Euclidean distances, matching Krum geometry.
  Min Sum and Krum Optimal now apply the configured boundary strength.
  Candidate diagnostics now include boundary gamma, applied gamma, peer mean norm,
  gamma to peer mean ratio, direction crossing, and cosine to peer mean.

peer_fingerprint.py
  Peer matrices and peer envelopes now use observations from one FL round only.
  The current round is used when all eligible peers are available. Otherwise the
  latest previous complete round is used. Different rounds are never mixed.

stealth_engine.py
  The current round is passed to peer retrieval.
  Krum Optimal uses the configured active Krum or Multi Krum defense and refuses
  incompatible FedAvg execution.
  Min Sum and Krum Optimal receive the configured boundary strength.

poison_live.py
  Preflight rejects Krum Optimal unless the active server defense is Krum or
  Multi Krum.
  The interactive wizard defaults boundary strength to 1.0 for Min Sum and Krum
  Optimal.
  Selection and round synchronization diagnostics are retained in the attack CSV.

Unchanged runtime behavior
--------------------------
Transport forwarding, HTTP/2 flow control, phase gating, client targeting,
global model matching, tensor extraction, serialization, reconstruction,
Sign Flip, Scale, Noise, Min Max, ALIE, IPM, envelope projection, and server code
were not changed.

Important experiment configuration
----------------------------------
For Min Sum against FedAvg:
  live_attack=envelope
  live_raw_attack=min_sum
  live_active_defense=fedavg
  live_aggressiveness=1.0 for the full Min Sum boundary

For Krum Optimal:
  Run a Krum or Multi Krum server.
  Set live_active_defense to krum or multi_krum.
  Do not label a FedAvg run as Krum Optimal because FedAvg has no Krum selection
  boundary.

Validation
----------
python3 validate_selection_attack_corrections.py
python3 validate_transport_isolation.py
python3 validate_update_space.py

All three validations passed in the supplied package.
