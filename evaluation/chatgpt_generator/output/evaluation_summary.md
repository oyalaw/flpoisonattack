# Federated learning evaluation report

Discovered run bundles: 711
Run level metrics: 7390
Data quality issues: 1579

## Interpretation rule

Metrics are first computed once per run. Repeated experiments are then aggregated by condition using the arithmetic mean and sample standard deviation. Cross component metrics are omitted when the logs cannot be matched safely.

## Aggregate metrics

| rq   | condition           | metric                               |   n_runs |           mean |           std |       ci95_low |     ci95_high | unit    |
|:-----|:--------------------|:-------------------------------------|---------:|---------------:|--------------:|---------------:|--------------:|:--------|
| RQ1  | exp1                | phase_accuracy                       |        1 |    0.0162602   | nan           |  nan           | nan           | ratio   |
| RQ1  | exp1                | phase_accuracy                       |        1 |    0.025695    | nan           |  nan           | nan           | ratio   |
| RQ1  | exp1                | phase_accuracy                       |        1 |    0.111111    | nan           |  nan           | nan           | ratio   |
| RQ1  | exp1                | phase_accuracy                       |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ1  | exp1                | phase_accuracy                       |        1 |    0.028436    | nan           |  nan           | nan           | ratio   |
| RQ1  | exp1                | phase_macro_f1                       |        1 |    0.0106667   | nan           |  nan           | nan           | ratio   |
| RQ1  | exp1                | phase_macro_f1                       |        1 |    0.0250513   | nan           |  nan           | nan           | ratio   |
| RQ1  | exp1                | phase_macro_f1                       |        1 |    0.0514706   | nan           |  nan           | nan           | ratio   |
| RQ1  | exp1                | phase_macro_f1                       |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ1  | exp1                | phase_macro_f1                       |        1 |    0.0184332   | nan           |  nan           | nan           | ratio   |
| RQ1  | exp1                | phase_macro_precision                |        1 |    0.00542005  | nan           |  nan           | nan           | ratio   |
| RQ1  | exp1                | phase_macro_precision                |        1 |    0.0128475   | nan           |  nan           | nan           | ratio   |
| RQ1  | exp1                | phase_macro_precision                |        1 |    0.0286885   | nan           |  nan           | nan           | ratio   |
| RQ1  | exp1                | phase_macro_precision                |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ1  | exp1                | phase_macro_precision                |        1 |    0.00947867  | nan           |  nan           | nan           | ratio   |
| RQ1  | exp1                | phase_macro_recall                   |        1 |    0.333333    | nan           |  nan           | nan           | ratio   |
| RQ1  | exp1                | phase_macro_recall                   |        1 |    0.5         | nan           |  nan           | nan           | ratio   |
| RQ1  | exp1                | phase_macro_recall                   |        1 |    0.25        | nan           |  nan           | nan           | ratio   |
| RQ1  | exp1                | phase_macro_recall                   |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ1  | exp1                | phase_macro_recall                   |        1 |    0.333333    | nan           |  nan           | nan           | ratio   |
| RQ1  | exp1                | phase_prediction_alignment_coverage  |        1 |    0.00212626  | nan           |  nan           | nan           | ratio   |
| RQ1  | exp1                | phase_prediction_alignment_coverage  |        1 |    0.0221803   | nan           |  nan           | nan           | ratio   |
| RQ1  | exp1                | phase_prediction_alignment_coverage  |        1 |    0.00299415  | nan           |  nan           | nan           | ratio   |
| RQ1  | exp1                | phase_prediction_alignment_coverage  |        1 |    8.33813e-06 | nan           |  nan           | nan           | ratio   |
| RQ1  | exp1                | phase_prediction_alignment_coverage  |        1 |    0.00185924  | nan           |  nan           | nan           | ratio   |
| RQ1  | exp1                | round_identification_accuracy        |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ1  | exp1                | round_identification_accuracy        |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ1  | exp1                | round_identification_accuracy        |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ1  | exp1                | round_identification_accuracy        |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ1  | exp1                | round_identification_accuracy        |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ2  | exp1                | non_target_spillover_rate            |        1 |    0           | nan           |  nan           | nan           | ratio   |
| RQ2  | exp1                | non_target_spillover_rate            |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ2  | exp1                | non_target_spillover_rate            |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ2  | exp1                | non_target_spillover_rate            |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ2  | exp1                | non_target_spillover_rate            |        4 |    0           |   0           |    0           |   0           | ratio   |
| RQ2  | exp1                | non_target_spillover_rate            |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ2  | exp1                | non_target_spillover_rate            |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ2  | exp1                | non_target_spillover_rate            |        2 |    0           |   0           |    0           |   0           | ratio   |
| RQ2  | exp1                | non_target_spillover_rate            |        5 |    0           |   0           |    0           |   0           | ratio   |
| RQ2  | exp1                | non_target_spillover_rate            |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ2  | exp1                | non_target_spillover_rate            |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ2  | exp1                | non_target_spillover_rate            |        1 |    0           | nan           |  nan           | nan           | ratio   |
| RQ2  | exp1                | non_target_spillover_rate            |        1 |    0           | nan           |  nan           | nan           | ratio   |
| RQ2  | exp1                | non_target_spillover_rate            |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ2  | exp1                | non_target_spillover_rate            |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ2  | exp1                | non_target_spillover_rate            |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ2  | exp1                | non_target_spillover_rate            |        2 |    0           |   0           |    0           |   0           | ratio   |
| RQ2  | exp1                | non_target_spillover_rate            |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ2  | exp1                | non_target_spillover_rate            |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ2  | exp1                | non_target_spillover_rate            |        2 |    0           |   0           |    0           |   0           | ratio   |
| RQ2  | exp1                | non_target_spillover_rate            |        2 |    0           |   0           |    0           |   0           | ratio   |
| RQ2  | exp1                | non_target_spillover_rate            |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ2  | exp1                | non_target_spillover_rate            |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ2  | exp1                | non_target_spillover_rate            |        1 |    0           | nan           |  nan           | nan           | ratio   |
| RQ2  | exp1                | non_target_spillover_rate            |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ2  | exp1                | non_target_spillover_rate            |        4 |    0           |   0           |    0           |   0           | ratio   |
| RQ2  | exp1                | non_target_spillover_rate            |        2 |    0           |   0           |    0           |   0           | ratio   |
| RQ2  | exp1                | non_target_spillover_rate            |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ2  | exp1                | non_target_spillover_rate            |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ2  | exp1                | non_target_spillover_rate            |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ2  | exp1                | non_target_spillover_rate            |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ2  | exp1                | non_target_spillover_rate            |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ2  | exp1                | non_target_spillover_rate            |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ2  | exp1                | non_target_spillover_rate            |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ2  | exp2                | non_target_spillover_rate            |        1 |    0           | nan           |  nan           | nan           | ratio   |
| RQ2  | exp2                | non_target_spillover_rate            |        1 |    0           | nan           |  nan           | nan           | ratio   |
| RQ2  | exp2                | non_target_spillover_rate            |        1 |    0           | nan           |  nan           | nan           | ratio   |
| RQ2  | exp2                | non_target_spillover_rate            |        1 |    0           | nan           |  nan           | nan           | ratio   |
| RQ2  | flame_blind         | non_target_spillover_rate            |        1 |    0           | nan           |  nan           | nan           | ratio   |
| RQ2  | exp1                | phase_client_match_rate              |        1 |    0.998       | nan           |  nan           | nan           | ratio   |
| RQ2  | exp1                | phase_client_match_rate              |        3 |    0.999333    |   0.0011547   |    0.998027    |   1.00064     | ratio   |
| RQ2  | exp1                | phase_client_match_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ2  | exp1                | phase_client_match_rate              |        3 |    0.7785      |   0.381919    |    0.346319    |   1.21068     | ratio   |
| RQ2  | exp1                | phase_client_match_rate              |        4 |    0.845625    |   0.30875     |    0.54305     |   1.1482      | ratio   |
| RQ2  | exp1                | phase_client_match_rate              |        3 |    0.842667    |   0.270779    |    0.536251    |   1.14908     | ratio   |
| RQ2  | exp1                | phase_client_match_rate              |        3 |    0.999333    |   0.0011547   |    0.998027    |   1.00064     | ratio   |
| RQ2  | exp1                | phase_client_match_rate              |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ2  | exp1                | phase_client_match_rate              |        5 |    0.9996      |   0.000894427 |    0.998816    |   1.00038     | ratio   |
| RQ2  | exp1                | phase_client_match_rate              |        3 |    0.999333    |   0.0011547   |    0.998027    |   1.00064     | ratio   |
| RQ2  | exp1                | phase_client_match_rate              |        3 |    0.999333    |   0.0011547   |    0.998027    |   1.00064     | ratio   |
| RQ2  | exp1                | phase_client_match_rate              |        1 |    0.97        | nan           |  nan           | nan           | ratio   |
| RQ2  | exp1                | phase_client_match_rate              |        1 |    0.996       | nan           |  nan           | nan           | ratio   |
| RQ2  | exp1                | phase_client_match_rate              |        3 |    0.999333    |   0.0011547   |    0.998027    |   1.00064     | ratio   |
| RQ2  | exp1                | phase_client_match_rate              |        3 |    0.999333    |   0.0011547   |    0.998027    |   1.00064     | ratio   |
| RQ2  | exp1                | phase_client_match_rate              |        3 |    0.878333    |   0.210733    |    0.639867    |   1.1168      | ratio   |
| RQ2  | exp1                | phase_client_match_rate              |        2 |    0.72125     |   0.394212    |    0.1749      |   1.2676      | ratio   |
| RQ2  | exp1                | phase_client_match_rate              |        3 |    0.998667    |   0.0011547   |    0.99736     |   0.999973    | ratio   |
| RQ2  | exp1                | phase_client_match_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ2  | exp1                | phase_client_match_rate              |        2 |    0.999       |   0.00141421  |    0.99704     |   1.00096     | ratio   |
| RQ2  | exp1                | phase_client_match_rate              |        2 |    0.999       |   0.00141421  |    0.99704     |   1.00096     | ratio   |
| RQ2  | exp1                | phase_client_match_rate              |        3 |    0.999333    |   0.0011547   |    0.998027    |   1.00064     | ratio   |
| RQ2  | exp1                | phase_client_match_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ2  | exp1                | phase_client_match_rate              |        1 |    0.996       | nan           |  nan           | nan           | ratio   |
| RQ2  | exp1                | phase_client_match_rate              |        3 |    0.999333    |   0.0011547   |    0.998027    |   1.00064     | ratio   |
| RQ2  | exp1                | phase_client_match_rate              |        4 |    1           |   0           |    1           |   1           | ratio   |
| RQ2  | exp1                | phase_client_match_rate              |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ2  | exp1                | phase_client_match_rate              |        3 |    0.875       |   0.216506    |    0.63        |   1.12        | ratio   |
| RQ2  | exp1                | phase_client_match_rate              |        3 |    0.926667    |   0.127017    |    0.782933    |   1.0704      | ratio   |
| RQ2  | exp1                | phase_client_match_rate              |        3 |    0.999333    |   0.0011547   |    0.998027    |   1.00064     | ratio   |
| RQ2  | exp1                | phase_client_match_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ2  | exp1                | phase_client_match_rate              |        3 |    0.999333    |   0.0011547   |    0.998027    |   1.00064     | ratio   |
| RQ2  | exp1                | phase_client_match_rate              |        3 |    0.999333    |   0.0011547   |    0.998027    |   1.00064     | ratio   |
| RQ2  | exp1                | phase_client_match_rate              |        3 |    0.998667    |   0.0023094   |    0.996053    |   1.00128     | ratio   |
| RQ2  | exp2                | phase_client_match_rate              |        1 |    0.998       | nan           |  nan           | nan           | ratio   |
| RQ2  | exp2                | phase_client_match_rate              |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ2  | exp2                | phase_client_match_rate              |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ2  | exp2                | phase_client_match_rate              |        1 |    0.8425      | nan           |  nan           | nan           | ratio   |
| RQ2  | flame_blind         | phase_client_match_rate              |        1 |    0.9975      | nan           |  nan           | nan           | ratio   |
| RQ2  | exp1                | phase_gate_open_rate                 |        1 |    0.998       | nan           |  nan           | nan           | ratio   |
| RQ2  | exp1                | phase_gate_open_rate                 |        3 |    0.999333    |   0.0011547   |    0.998027    |   1.00064     | ratio   |
| RQ2  | exp1                | phase_gate_open_rate                 |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ2  | exp1                | phase_gate_open_rate                 |        3 |    0.750167    |   0.430993    |    0.262452    |   1.23788     | ratio   |
| RQ2  | exp1                | phase_gate_open_rate                 |        4 |    0.81625     |   0.3675      |    0.4561      |   1.1764      | ratio   |
| RQ2  | exp1                | phase_gate_open_rate                 |        3 |    0.742667    |   0.443983    |    0.240252    |   1.24508     | ratio   |
| RQ2  | exp1                | phase_gate_open_rate                 |        3 |    0.999333    |   0.0011547   |    0.998027    |   1.00064     | ratio   |
| RQ2  | exp1                | phase_gate_open_rate                 |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ2  | exp1                | phase_gate_open_rate                 |        5 |    0.9996      |   0.000894427 |    0.998816    |   1.00038     | ratio   |
| RQ2  | exp1                | phase_gate_open_rate                 |        3 |    0.999333    |   0.0011547   |    0.998027    |   1.00064     | ratio   |
| RQ2  | exp1                | phase_gate_open_rate                 |        3 |    0.999333    |   0.0011547   |    0.998027    |   1.00064     | ratio   |
| RQ2  | exp1                | phase_gate_open_rate                 |        1 |    0.194       | nan           |  nan           | nan           | ratio   |
| RQ2  | exp1                | phase_gate_open_rate                 |        1 |    0.996       | nan           |  nan           | nan           | ratio   |
| RQ2  | exp1                | phase_gate_open_rate                 |        3 |    0.999333    |   0.0011547   |    0.998027    |   1.00064     | ratio   |
| RQ2  | exp1                | phase_gate_open_rate                 |        3 |    0.999333    |   0.0011547   |    0.998027    |   1.00064     | ratio   |
| RQ2  | exp1                | phase_gate_open_rate                 |        3 |    0.798333    |   0.349297    |    0.403067    |   1.1936      | ratio   |
| RQ2  | exp1                | phase_gate_open_rate                 |        2 |    0.64375     |   0.503814    |   -0.0545      |   1.342       | ratio   |
| RQ2  | exp1                | phase_gate_open_rate                 |        3 |    0.998667    |   0.0011547   |    0.99736     |   0.999973    | ratio   |
| RQ2  | exp1                | phase_gate_open_rate                 |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ2  | exp1                | phase_gate_open_rate                 |        2 |    0.999       |   0.00141421  |    0.99704     |   1.00096     | ratio   |
| RQ2  | exp1                | phase_gate_open_rate                 |        2 |    0.999       |   0.00141421  |    0.99704     |   1.00096     | ratio   |
| RQ2  | exp1                | phase_gate_open_rate                 |        3 |    0.999333    |   0.0011547   |    0.998027    |   1.00064     | ratio   |
| RQ2  | exp1                | phase_gate_open_rate                 |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ2  | exp1                | phase_gate_open_rate                 |        1 |    0.994       | nan           |  nan           | nan           | ratio   |
| RQ2  | exp1                | phase_gate_open_rate                 |        3 |    0.999333    |   0.0011547   |    0.998027    |   1.00064     | ratio   |
| RQ2  | exp1                | phase_gate_open_rate                 |        4 |    1           |   0           |    1           |   1           | ratio   |
| RQ2  | exp1                | phase_gate_open_rate                 |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ2  | exp1                | phase_gate_open_rate                 |        3 |    0.773333    |   0.392598    |    0.329067    |   1.2176      | ratio   |
| RQ2  | exp1                | phase_gate_open_rate                 |        3 |    0.770833    |   0.396928    |    0.321667    |   1.22        | ratio   |
| RQ2  | exp1                | phase_gate_open_rate                 |        3 |    0.999333    |   0.0011547   |    0.998027    |   1.00064     | ratio   |
| RQ2  | exp1                | phase_gate_open_rate                 |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ2  | exp1                | phase_gate_open_rate                 |        3 |    0.999333    |   0.0011547   |    0.998027    |   1.00064     | ratio   |
| RQ2  | exp1                | phase_gate_open_rate                 |        3 |    0.999333    |   0.0011547   |    0.998027    |   1.00064     | ratio   |
| RQ2  | exp1                | phase_gate_open_rate                 |        3 |    0.998667    |   0.0023094   |    0.996053    |   1.00128     | ratio   |
| RQ2  | exp2                | phase_gate_open_rate                 |        1 |    0.998       | nan           |  nan           | nan           | ratio   |
| RQ2  | exp2                | phase_gate_open_rate                 |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ2  | exp2                | phase_gate_open_rate                 |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ2  | exp2                | phase_gate_open_rate                 |        1 |    0.1425      | nan           |  nan           | nan           | ratio   |
| RQ2  | flame_blind         | phase_gate_open_rate                 |        1 |    0.9975      | nan           |  nan           | nan           | ratio   |
| RQ2  | exp1                | phase_round_match_rate               |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ2  | exp1                | phase_round_match_rate               |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ2  | exp1                | phase_round_match_rate               |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ2  | exp1                | phase_round_match_rate               |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ2  | exp1                | phase_round_match_rate               |        4 |    1           |   0           |    1           |   1           | ratio   |
| RQ2  | exp1                | phase_round_match_rate               |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ2  | exp1                | phase_round_match_rate               |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ2  | exp1                | phase_round_match_rate               |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ2  | exp1                | phase_round_match_rate               |        5 |    1           |   0           |    1           |   1           | ratio   |
| RQ2  | exp1                | phase_round_match_rate               |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ2  | exp1                | phase_round_match_rate               |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ2  | exp1                | phase_round_match_rate               |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ2  | exp1                | phase_round_match_rate               |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ2  | exp1                | phase_round_match_rate               |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ2  | exp1                | phase_round_match_rate               |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ2  | exp1                | phase_round_match_rate               |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ2  | exp1                | phase_round_match_rate               |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ2  | exp1                | phase_round_match_rate               |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ2  | exp1                | phase_round_match_rate               |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ2  | exp1                | phase_round_match_rate               |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ2  | exp1                | phase_round_match_rate               |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ2  | exp1                | phase_round_match_rate               |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ2  | exp1                | phase_round_match_rate               |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ2  | exp1                | phase_round_match_rate               |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ2  | exp1                | phase_round_match_rate               |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ2  | exp1                | phase_round_match_rate               |        4 |    1           |   0           |    1           |   1           | ratio   |
| RQ2  | exp1                | phase_round_match_rate               |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ2  | exp1                | phase_round_match_rate               |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ2  | exp1                | phase_round_match_rate               |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ2  | exp1                | phase_round_match_rate               |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ2  | exp1                | phase_round_match_rate               |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ2  | exp1                | phase_round_match_rate               |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ2  | exp1                | phase_round_match_rate               |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ2  | exp1                | phase_round_match_rate               |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ2  | exp2                | phase_round_match_rate               |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ2  | exp2                | phase_round_match_rate               |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ2  | exp2                | phase_round_match_rate               |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ2  | exp2                | phase_round_match_rate               |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ2  | flame_blind         | phase_round_match_rate               |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ2  | exp1                | proxy_modified_events                |        1 |   80           | nan           |  nan           | nan           | count   |
| RQ2  | exp1                | proxy_modified_events                |        3 |   79.6667      |   0.57735     |   79.0133      |  80.32        | count   |
| RQ2  | exp1                | proxy_modified_events                |        3 |   80           |   0           |   80           |  80           | count   |
| RQ2  | exp1                | proxy_modified_events                |        3 |   79           |   1.73205     |   77.04        |  80.96        | count   |
| RQ2  | exp1                | proxy_modified_events                |        4 |   79           |   2           |   77.04        |  80.96        | count   |
| RQ2  | exp1                | proxy_modified_events                |        3 |   79           |   1.73205     |   77.04        |  80.96        | count   |
| RQ2  | exp1                | proxy_modified_events                |        3 |   80           |   0           |   80           |  80           | count   |
| RQ2  | exp1                | proxy_modified_events                |        2 |   80           |   0           |   80           |  80           | count   |
| RQ2  | exp1                | proxy_modified_events                |        5 |   80           |   0           |   80           |  80           | count   |
| RQ2  | exp1                | proxy_modified_events                |        3 |   80           |   0           |   80           |  80           | count   |
| RQ2  | exp1                | proxy_modified_events                |        3 |   80           |   0           |   80           |  80           | count   |
| RQ2  | exp1                | proxy_modified_events                |        1 |   97           | nan           |  nan           | nan           | count   |
| RQ2  | exp1                | proxy_modified_events                |        1 |   45           | nan           |  nan           | nan           | count   |
| RQ2  | exp1                | proxy_modified_events                |        3 |   80           |   0           |   80           |  80           | count   |
| RQ2  | exp1                | proxy_modified_events                |        3 |   80           |   0           |   80           |  80           | count   |
| RQ2  | exp1                | proxy_modified_events                |        3 |   79           |   1.73205     |   77.04        |  80.96        | count   |
| RQ2  | exp1                | proxy_modified_events                |        2 |   78.5         |   2.12132     |   75.56        |  81.44        | count   |
| RQ2  | exp1                | proxy_modified_events                |        3 |   80           |   0           |   80           |  80           | count   |
| RQ2  | exp1                | proxy_modified_events                |        3 |   80           |   0           |   80           |  80           | count   |
| RQ2  | exp1                | proxy_modified_events                |        2 |   80           |   0           |   80           |  80           | count   |
| RQ2  | exp1                | proxy_modified_events                |        2 |   80           |   0           |   80           |  80           | count   |
| RQ2  | exp1                | proxy_modified_events                |        3 |   80           |   0           |   80           |  80           | count   |
| RQ2  | exp1                | proxy_modified_events                |        3 |   80           |   0           |   80           |  80           | count   |
| RQ2  | exp1                | proxy_modified_events                |        1 |    0           | nan           |  nan           | nan           | count   |
| RQ2  | exp1                | proxy_modified_events                |        3 |   80           |   0           |   80           |  80           | count   |
| RQ2  | exp1                | proxy_modified_events                |        4 |   80           |   0           |   80           |  80           | count   |
| RQ2  | exp1                | proxy_modified_events                |        2 |   80           |   0           |   80           |  80           | count   |
| RQ2  | exp1                | proxy_modified_events                |        3 |   79           |   1.73205     |   77.04        |  80.96        | count   |
| RQ2  | exp1                | proxy_modified_events                |        3 |   79           |   1.73205     |   77.04        |  80.96        | count   |
| RQ2  | exp1                | proxy_modified_events                |        3 |   80           |   0           |   80           |  80           | count   |
| RQ2  | exp1                | proxy_modified_events                |        3 |   80           |   0           |   80           |  80           | count   |
| RQ2  | exp1                | proxy_modified_events                |        3 |   80           |   0           |   80           |  80           | count   |
| RQ2  | exp1                | proxy_modified_events                |        3 |   80           |   0           |   80           |  80           | count   |
| RQ2  | exp1                | proxy_modified_events                |        3 |   79.6667      |   0.57735     |   79.0133      |  80.32        | count   |
| RQ2  | exp2                | proxy_modified_events                |        1 |   79           | nan           |  nan           | nan           | count   |
| RQ2  | exp2                | proxy_modified_events                |        1 |   80           | nan           |  nan           | nan           | count   |
| RQ2  | exp2                | proxy_modified_events                |        1 |   80           | nan           |  nan           | nan           | count   |
| RQ2  | exp2                | proxy_modified_events                |        1 |    0           | nan           |  nan           | nan           | count   |
| RQ2  | flame_blind         | proxy_modified_events                |        1 |   80           | nan           |  nan           | nan           | count   |
| RQ2  | exp1                | proxy_selected_attack_events         |        1 |  500           | nan           |  nan           | nan           | count   |
| RQ2  | exp1                | proxy_selected_attack_events         |        3 |  500           |   0           |  500           | 500           | count   |
| RQ2  | exp1                | proxy_selected_attack_events         |        3 |  500           |   0           |  500           | 500           | count   |
| RQ2  | exp1                | proxy_selected_attack_events         |        3 |  466.667       |  57.735       |  401.333       | 532           | count   |
| RQ2  | exp1                | proxy_selected_attack_events         |        4 |  474.5         |  49.6756      |  425.818       | 523.182       | count   |
| RQ2  | exp1                | proxy_selected_attack_events         |        3 |  500           |   0           |  500           | 500           | count   |
| RQ2  | exp1                | proxy_selected_attack_events         |        3 |  500           |   0           |  500           | 500           | count   |
| RQ2  | exp1                | proxy_selected_attack_events         |        2 |  500.5         |   0.707107    |  499.52        | 501.48        | count   |
| RQ2  | exp1                | proxy_selected_attack_events         |        5 |  500           |   0           |  500           | 500           | count   |
| RQ2  | exp1                | proxy_selected_attack_events         |        3 |  500.333       |   0.57735     |  499.68        | 500.987       | count   |
| RQ2  | exp1                | proxy_selected_attack_events         |        3 |  500.333       |   0.57735     |  499.68        | 500.987       | count   |
| RQ2  | exp1                | proxy_selected_attack_events         |        1 |  500           | nan           |  nan           | nan           | count   |
| RQ2  | exp1                | proxy_selected_attack_events         |        1 |  500           | nan           |  nan           | nan           | count   |
| RQ2  | exp1                | proxy_selected_attack_events         |        3 |  500           |   0           |  500           | 500           | count   |
| RQ2  | exp1                | proxy_selected_attack_events         |        3 |  500           |   0           |  500           | 500           | count   |
| RQ2  | exp1                | proxy_selected_attack_events         |        3 |  466.667       |  57.735       |  401.333       | 532           | count   |
| RQ2  | exp1                | proxy_selected_attack_events         |        2 |  450           |  70.7107      |  352           | 548           | count   |
| RQ2  | exp1                | proxy_selected_attack_events         |        3 |  500           |   0           |  500           | 500           | count   |
| RQ2  | exp1                | proxy_selected_attack_events         |        3 |  500           |   0           |  500           | 500           | count   |
| RQ2  | exp1                | proxy_selected_attack_events         |        2 |  500           |   0           |  500           | 500           | count   |
| RQ2  | exp1                | proxy_selected_attack_events         |        2 |  500           |   0           |  500           | 500           | count   |
| RQ2  | exp1                | proxy_selected_attack_events         |        3 |  500           |   0           |  500           | 500           | count   |
| RQ2  | exp1                | proxy_selected_attack_events         |        3 |  500           |   0           |  500           | 500           | count   |
| RQ2  | exp1                | proxy_selected_attack_events         |        1 |  500           | nan           |  nan           | nan           | count   |
| RQ2  | exp1                | proxy_selected_attack_events         |        3 |  500           |   0           |  500           | 500           | count   |
| RQ2  | exp1                | proxy_selected_attack_events         |        4 |  500           |   0           |  500           | 500           | count   |
| RQ2  | exp1                | proxy_selected_attack_events         |        2 |  500           |   0           |  500           | 500           | count   |
| RQ2  | exp1                | proxy_selected_attack_events         |        3 |  466.667       |  57.735       |  401.333       | 532           | count   |
| RQ2  | exp1                | proxy_selected_attack_events         |        3 |  466.667       |  57.735       |  401.333       | 532           | count   |
| RQ2  | exp1                | proxy_selected_attack_events         |        3 |  500.333       |   0.57735     |  499.68        | 500.987       | count   |
| RQ2  | exp1                | proxy_selected_attack_events         |        3 |  500.333       |   0.57735     |  499.68        | 500.987       | count   |
| RQ2  | exp1                | proxy_selected_attack_events         |        3 |  500.333       |   0.57735     |  499.68        | 500.987       | count   |
| RQ2  | exp1                | proxy_selected_attack_events         |        3 |  500           |   0           |  500           | 500           | count   |
| RQ2  | exp1                | proxy_selected_attack_events         |        3 |  500           |   0           |  500           | 500           | count   |
| RQ2  | exp2                | proxy_selected_attack_events         |        1 |  500           | nan           |  nan           | nan           | count   |
| RQ2  | exp2                | proxy_selected_attack_events         |        1 |  500           | nan           |  nan           | nan           | count   |
| RQ2  | exp2                | proxy_selected_attack_events         |        1 |  500           | nan           |  nan           | nan           | count   |
| RQ2  | exp2                | proxy_selected_attack_events         |        1 |  400           | nan           |  nan           | nan           | count   |
| RQ2  | flame_blind         | proxy_selected_attack_events         |        1 |  400           | nan           |  nan           | nan           | count   |
| RQ2  | exp1                | proxy_targeted_events                |        1 |  100           | nan           |  nan           | nan           | count   |
| RQ2  | exp1                | proxy_targeted_events                |        3 |  100           |   0           |  100           | 100           | count   |
| RQ2  | exp1                | proxy_targeted_events                |        3 |  100           |   0           |  100           | 100           | count   |
| RQ2  | exp1                | proxy_targeted_events                |        3 |  100           |   0           |  100           | 100           | count   |
| RQ2  | exp1                | proxy_targeted_events                |        4 |  100           |   0           |  100           | 100           | count   |
| RQ2  | exp1                | proxy_targeted_events                |        3 |  100           |   0           |  100           | 100           | count   |
| RQ2  | exp1                | proxy_targeted_events                |        3 |  100           |   0           |  100           | 100           | count   |
| RQ2  | exp1                | proxy_targeted_events                |        2 |  100.5         |   0.707107    |   99.52        | 101.48        | count   |
| RQ2  | exp1                | proxy_targeted_events                |        5 |  100           |   0           |  100           | 100           | count   |
| RQ2  | exp1                | proxy_targeted_events                |        3 |  100.333       |   0.57735     |   99.68        | 100.987       | count   |
| RQ2  | exp1                | proxy_targeted_events                |        3 |  100.333       |   0.57735     |   99.68        | 100.987       | count   |
| RQ2  | exp1                | proxy_targeted_events                |        1 |  100           | nan           |  nan           | nan           | count   |
| RQ2  | exp1                | proxy_targeted_events                |        1 |  100           | nan           |  nan           | nan           | count   |
| RQ2  | exp1                | proxy_targeted_events                |        3 |  100           |   0           |  100           | 100           | count   |
| RQ2  | exp1                | proxy_targeted_events                |        3 |  100           |   0           |  100           | 100           | count   |
| RQ2  | exp1                | proxy_targeted_events                |        3 |  100           |   0           |  100           | 100           | count   |
| RQ2  | exp1                | proxy_targeted_events                |        2 |  100           |   0           |  100           | 100           | count   |
| RQ2  | exp1                | proxy_targeted_events                |        3 |  100           |   0           |  100           | 100           | count   |
| RQ2  | exp1                | proxy_targeted_events                |        3 |  100           |   0           |  100           | 100           | count   |
| RQ2  | exp1                | proxy_targeted_events                |        2 |  100           |   0           |  100           | 100           | count   |
| RQ2  | exp1                | proxy_targeted_events                |        2 |  100           |   0           |  100           | 100           | count   |
| RQ2  | exp1                | proxy_targeted_events                |        3 |  100           |   0           |  100           | 100           | count   |
| RQ2  | exp1                | proxy_targeted_events                |        3 |  100           |   0           |  100           | 100           | count   |
| RQ2  | exp1                | proxy_targeted_events                |        1 |  100           | nan           |  nan           | nan           | count   |
| RQ2  | exp1                | proxy_targeted_events                |        3 |  100           |   0           |  100           | 100           | count   |
| RQ2  | exp1                | proxy_targeted_events                |        4 |  100           |   0           |  100           | 100           | count   |
| RQ2  | exp1                | proxy_targeted_events                |        2 |  100           |   0           |  100           | 100           | count   |
| RQ2  | exp1                | proxy_targeted_events                |        3 |  100           |   0           |  100           | 100           | count   |
| RQ2  | exp1                | proxy_targeted_events                |        3 |  100           |   0           |  100           | 100           | count   |
| RQ2  | exp1                | proxy_targeted_events                |        3 |  100.333       |   0.57735     |   99.68        | 100.987       | count   |
| RQ2  | exp1                | proxy_targeted_events                |        3 |  100.333       |   0.57735     |   99.68        | 100.987       | count   |
| RQ2  | exp1                | proxy_targeted_events                |        3 |  100.333       |   0.57735     |   99.68        | 100.987       | count   |
| RQ2  | exp1                | proxy_targeted_events                |        3 |  100           |   0           |  100           | 100           | count   |
| RQ2  | exp1                | proxy_targeted_events                |        3 |  100           |   0           |  100           | 100           | count   |
| RQ2  | exp2                | proxy_targeted_events                |        1 |  100           | nan           |  nan           | nan           | count   |
| RQ2  | exp2                | proxy_targeted_events                |        1 |  100           | nan           |  nan           | nan           | count   |
| RQ2  | exp2                | proxy_targeted_events                |        1 |  100           | nan           |  nan           | nan           | count   |
| RQ2  | exp2                | proxy_targeted_events                |        1 |  100           | nan           |  nan           | nan           | count   |
| RQ2  | flame_blind         | proxy_targeted_events                |        1 |  100           | nan           |  nan           | nan           | count   |
| RQ2  | exp1                | selective_modification_rate          |        1 |    0.8         | nan           |  nan           | nan           | ratio   |
| RQ2  | exp1                | selective_modification_rate          |        3 |    0.796667    |   0.0057735   |    0.790133    |   0.8032      | ratio   |
| RQ2  | exp1                | selective_modification_rate          |        3 |    0.8         |   1.35974e-16 |    0.8         |   0.8         | ratio   |
| RQ2  | exp1                | selective_modification_rate          |        3 |    0.79        |   0.0173205   |    0.7704      |   0.8096      | ratio   |
| RQ2  | exp1                | selective_modification_rate          |        4 |    0.79        |   0.02        |    0.7704      |   0.8096      | ratio   |
| RQ2  | exp1                | selective_modification_rate          |        3 |    0.79        |   0.0173205   |    0.7704      |   0.8096      | ratio   |
| RQ2  | exp1                | selective_modification_rate          |        3 |    0.8         |   1.35974e-16 |    0.8         |   0.8         | ratio   |
| RQ2  | exp1                | selective_modification_rate          |        2 |    0.79604     |   0.00560085  |    0.788277    |   0.803802    | ratio   |
| RQ2  | exp1                | selective_modification_rate          |        5 |    0.8         |   0           |    0.8         |   0.8         | ratio   |
| RQ2  | exp1                | selective_modification_rate          |        3 |    0.79736     |   0.00457307  |    0.792185    |   0.802535    | ratio   |
| RQ2  | exp1                | selective_modification_rate          |        3 |    0.79736     |   0.00457307  |    0.792185    |   0.802535    | ratio   |
| RQ2  | exp1                | selective_modification_rate          |        1 |    0.97        | nan           |  nan           | nan           | ratio   |
| RQ2  | exp1                | selective_modification_rate          |        1 |    0.45        | nan           |  nan           | nan           | ratio   |
| RQ2  | exp1                | selective_modification_rate          |        3 |    0.8         |   1.35974e-16 |    0.8         |   0.8         | ratio   |
| RQ2  | exp1                | selective_modification_rate          |        3 |    0.8         |   1.35974e-16 |    0.8         |   0.8         | ratio   |
| RQ2  | exp1                | selective_modification_rate          |        3 |    0.79        |   0.0173205   |    0.7704      |   0.8096      | ratio   |
| RQ2  | exp1                | selective_modification_rate          |        2 |    0.785       |   0.0212132   |    0.7556      |   0.8144      | ratio   |
| RQ2  | exp1                | selective_modification_rate          |        3 |    0.8         |   1.35974e-16 |    0.8         |   0.8         | ratio   |
| RQ2  | exp1                | selective_modification_rate          |        3 |    0.8         |   1.35974e-16 |    0.8         |   0.8         | ratio   |
| RQ2  | exp1                | selective_modification_rate          |        2 |    0.8         |   0           |    0.8         |   0.8         | ratio   |
| RQ2  | exp1                | selective_modification_rate          |        2 |    0.8         |   0           |    0.8         |   0.8         | ratio   |
| RQ2  | exp1                | selective_modification_rate          |        3 |    0.8         |   1.35974e-16 |    0.8         |   0.8         | ratio   |
| RQ2  | exp1                | selective_modification_rate          |        3 |    0.8         |   1.35974e-16 |    0.8         |   0.8         | ratio   |
| RQ2  | exp1                | selective_modification_rate          |        1 |    0           | nan           |  nan           | nan           | ratio   |
| RQ2  | exp1                | selective_modification_rate          |        3 |    0.8         |   1.35974e-16 |    0.8         |   0.8         | ratio   |
| RQ2  | exp1                | selective_modification_rate          |        4 |    0.8         |   0           |    0.8         |   0.8         | ratio   |
| RQ2  | exp1                | selective_modification_rate          |        2 |    0.8         |   0           |    0.8         |   0.8         | ratio   |
| RQ2  | exp1                | selective_modification_rate          |        3 |    0.79        |   0.0173205   |    0.7704      |   0.8096      | ratio   |
| RQ2  | exp1                | selective_modification_rate          |        3 |    0.79        |   0.0173205   |    0.7704      |   0.8096      | ratio   |
| RQ2  | exp1                | selective_modification_rate          |        3 |    0.79736     |   0.00457307  |    0.792185    |   0.802535    | ratio   |
| RQ2  | exp1                | selective_modification_rate          |        3 |    0.79736     |   0.00457307  |    0.792185    |   0.802535    | ratio   |
| RQ2  | exp1                | selective_modification_rate          |        3 |    0.79736     |   0.00457307  |    0.792185    |   0.802535    | ratio   |
| RQ2  | exp1                | selective_modification_rate          |        3 |    0.8         |   1.35974e-16 |    0.8         |   0.8         | ratio   |
| RQ2  | exp1                | selective_modification_rate          |        3 |    0.796667    |   0.0057735   |    0.790133    |   0.8032      | ratio   |
| RQ2  | exp2                | selective_modification_rate          |        1 |    0.79        | nan           |  nan           | nan           | ratio   |
| RQ2  | exp2                | selective_modification_rate          |        1 |    0.8         | nan           |  nan           | nan           | ratio   |
| RQ2  | exp2                | selective_modification_rate          |        1 |    0.8         | nan           |  nan           | nan           | ratio   |
| RQ2  | exp2                | selective_modification_rate          |        1 |    0           | nan           |  nan           | nan           | ratio   |
| RQ2  | flame_blind         | selective_modification_rate          |        1 |    0.8         | nan           |  nan           | nan           | ratio   |
| RQ2  | exp1                | trigger_precision                    |        1 |    0           | nan           |  nan           | nan           | ratio   |
| RQ2  | exp1                | trigger_precision                    |        1 |    0           | nan           |  nan           | nan           | ratio   |
| RQ2  | exp1                | trigger_precision                    |        1 |    0           | nan           |  nan           | nan           | ratio   |
| RQ2  | exp1                | trigger_precision                    |        1 |    0           | nan           |  nan           | nan           | ratio   |
| RQ2  | exp1                | trigger_precision                    |        1 |    0           | nan           |  nan           | nan           | ratio   |
| RQ2  | exp1                | trigger_recall                       |        1 |    0           | nan           |  nan           | nan           | ratio   |
| RQ2  | exp1                | trigger_recall                       |        1 |    0           | nan           |  nan           | nan           | ratio   |
| RQ2  | exp1                | trigger_recall                       |        1 |    0           | nan           |  nan           | nan           | ratio   |
| RQ2  | exp1                | trigger_recall                       |        1 |    0           | nan           |  nan           | nan           | ratio   |
| RQ2  | exp1                | trigger_recall                       |        1 |    0           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | finite_value_validity_rate           |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | finite_value_validity_rate           |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | finite_value_validity_rate           |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | finite_value_validity_rate           |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | finite_value_validity_rate           |        4 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | finite_value_validity_rate           |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | finite_value_validity_rate           |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | finite_value_validity_rate           |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | finite_value_validity_rate           |        5 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | finite_value_validity_rate           |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | finite_value_validity_rate           |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | finite_value_validity_rate           |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | finite_value_validity_rate           |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | finite_value_validity_rate           |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | finite_value_validity_rate           |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | finite_value_validity_rate           |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | finite_value_validity_rate           |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | finite_value_validity_rate           |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | finite_value_validity_rate           |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | finite_value_validity_rate           |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | finite_value_validity_rate           |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | finite_value_validity_rate           |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | finite_value_validity_rate           |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | finite_value_validity_rate           |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | finite_value_validity_rate           |        4 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | finite_value_validity_rate           |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | finite_value_validity_rate           |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | finite_value_validity_rate           |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | finite_value_validity_rate           |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | finite_value_validity_rate           |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | finite_value_validity_rate           |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | finite_value_validity_rate           |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | finite_value_validity_rate           |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp2                | finite_value_validity_rate           |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp2                | finite_value_validity_rate           |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp2                | finite_value_validity_rate           |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | flame_blind         | finite_value_validity_rate           |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | global_model_cached_rate             |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | global_model_cached_rate             |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_cached_rate             |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_cached_rate             |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_cached_rate             |        4 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_cached_rate             |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_cached_rate             |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_cached_rate             |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_cached_rate             |        5 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_cached_rate             |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_cached_rate             |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_cached_rate             |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | global_model_cached_rate             |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | global_model_cached_rate             |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_cached_rate             |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_cached_rate             |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_cached_rate             |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_cached_rate             |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_cached_rate             |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_cached_rate             |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_cached_rate             |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_cached_rate             |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_cached_rate             |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_cached_rate             |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_cached_rate             |        4 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_cached_rate             |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_cached_rate             |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_cached_rate             |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_cached_rate             |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_cached_rate             |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_cached_rate             |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_cached_rate             |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_cached_rate             |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp2                | global_model_cached_rate             |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp2                | global_model_cached_rate             |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp2                | global_model_cached_rate             |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | flame_blind         | global_model_cached_rate             |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | global_model_match_rate              |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | global_model_match_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_rate              |        4 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_rate              |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_rate              |        5 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_rate              |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | global_model_match_rate              |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | global_model_match_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_rate              |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_rate              |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_rate              |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_rate              |        4 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_rate              |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp2                | global_model_match_rate              |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp2                | global_model_match_rate              |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp2                | global_model_match_rate              |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | flame_blind         | global_model_match_rate              |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | global_model_match_valid_rate        |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | global_model_match_valid_rate        |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_valid_rate        |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_valid_rate        |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_valid_rate        |        4 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_valid_rate        |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_valid_rate        |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_valid_rate        |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_valid_rate        |        5 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_valid_rate        |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_valid_rate        |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_valid_rate        |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | global_model_match_valid_rate        |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | global_model_match_valid_rate        |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_valid_rate        |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_valid_rate        |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_valid_rate        |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_valid_rate        |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_valid_rate        |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_valid_rate        |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_valid_rate        |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_valid_rate        |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_valid_rate        |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_valid_rate        |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_valid_rate        |        4 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_valid_rate        |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_valid_rate        |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_valid_rate        |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_valid_rate        |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_valid_rate        |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_valid_rate        |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_valid_rate        |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | global_model_match_valid_rate        |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp2                | global_model_match_valid_rate        |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp2                | global_model_match_valid_rate        |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp2                | global_model_match_valid_rate        |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | flame_blind         | global_model_match_valid_rate        |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | global_norm_containment_rate         |        1 |    0           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | global_norm_containment_rate         |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ3  | exp1                | global_norm_containment_rate         |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ3  | exp1                | global_norm_containment_rate         |        3 |    0.00416667  |   0.00721688  |   -0.004       |   0.0123333   | ratio   |
| RQ3  | exp1                | global_norm_containment_rate         |        4 |    0.209539    |   0.23991     |   -0.0255727   |   0.444652    | ratio   |
| RQ3  | exp1                | global_norm_containment_rate         |        3 |    0.0166667   |   0.0288675   |   -0.016       |   0.0493333   | ratio   |
| RQ3  | exp1                | global_norm_containment_rate         |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ3  | exp1                | global_norm_containment_rate         |        2 |    0           |   0           |    0           |   0           | ratio   |
| RQ3  | exp1                | global_norm_containment_rate         |        5 |    0.1575      |   0.105549    |    0.0649821   |   0.250018    | ratio   |
| RQ3  | exp1                | global_norm_containment_rate         |        3 |    0.508333    |   0.227188    |    0.251245    |   0.765421    | ratio   |
| RQ3  | exp1                | global_norm_containment_rate         |        3 |    0.358333    |   0.220204    |    0.10915     |   0.607517    | ratio   |
| RQ3  | exp1                | global_norm_containment_rate         |        1 |    0           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | global_norm_containment_rate         |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ3  | exp1                | global_norm_containment_rate         |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ3  | exp1                | global_norm_containment_rate         |        3 |    0.117154    |   0.170293    |   -0.0755507   |   0.309858    | ratio   |
| RQ3  | exp1                | global_norm_containment_rate         |        2 |    0.0714286   |   0.101015    |   -0.0685714   |   0.211429    | ratio   |
| RQ3  | exp1                | global_norm_containment_rate         |        3 |    0.254167    |   0.244417    |   -0.022417    |   0.53075     | ratio   |
| RQ3  | exp1                | global_norm_containment_rate         |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ3  | exp1                | global_norm_containment_rate         |        2 |    0           |   0           |    0           |   0           | ratio   |
| RQ3  | exp1                | global_norm_containment_rate         |        2 |    0.00625     |   0.00883883  |   -0.006       |   0.0185      | ratio   |
| RQ3  | exp1                | global_norm_containment_rate         |        3 |    0.116667    |   0.118805    |   -0.0177736   |   0.251107    | ratio   |
| RQ3  | exp1                | global_norm_containment_rate         |        3 |    0.0458333   |   0.0590727   |   -0.0210137   |   0.11268     | ratio   |
| RQ3  | exp1                | global_norm_containment_rate         |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ3  | exp1                | global_norm_containment_rate         |        4 |    0           |   0           |    0           |   0           | ratio   |
| RQ3  | exp1                | global_norm_containment_rate         |        2 |    0.0375      |   0.053033    |   -0.036       |   0.111       | ratio   |
| RQ3  | exp1                | global_norm_containment_rate         |        3 |    0.121158    |   0.187807    |   -0.0913659   |   0.333682    | ratio   |
| RQ3  | exp1                | global_norm_containment_rate         |        3 |    0.00416667  |   0.00721688  |   -0.004       |   0.0123333   | ratio   |
| RQ3  | exp1                | global_norm_containment_rate         |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ3  | exp1                | global_norm_containment_rate         |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ3  | exp1                | global_norm_containment_rate         |        3 |    0.00833333  |   0.0144338   |   -0.008       |   0.0246667   | ratio   |
| RQ3  | exp1                | global_norm_containment_rate         |        3 |    0.0625      |   0.0976281   |   -0.0479766   |   0.172977    | ratio   |
| RQ3  | exp1                | global_norm_containment_rate         |        3 |    0.0757911   |   0.100562    |   -0.038005    |   0.189587    | ratio   |
| RQ3  | exp2                | global_norm_containment_rate         |        1 |    0           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp2                | global_norm_containment_rate         |        1 |    0.2375      | nan           |  nan           | nan           | ratio   |
| RQ3  | exp2                | global_norm_containment_rate         |        1 |    0.0125      | nan           |  nan           | nan           | ratio   |
| RQ3  | flame_blind         | global_norm_containment_rate         |        1 |    0.975       | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | mean_absolute_sparsity_drift         |        1 |    7.59316e-05 | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | mean_absolute_sparsity_drift         |        3 |    0.0178422   |   0.0308725   |   -0.0170933   |   0.0527777   | ratio   |
| RQ3  | exp1                | mean_absolute_sparsity_drift         |        3 |    0.0189428   |   0.0324935   |   -0.0178271   |   0.0557128   | ratio   |
| RQ3  | exp1                | mean_absolute_sparsity_drift         |        3 |    0.0737247   |   0.127476    |   -0.070528    |   0.217977    | ratio   |
| RQ3  | exp1                | mean_absolute_sparsity_drift         |        4 |    0.0191747   |   0.0277154   |   -0.00798646  |   0.0463358   | ratio   |
| RQ3  | exp1                | mean_absolute_sparsity_drift         |        3 |    0.0136033   |   0.0234988   |   -0.0129881   |   0.0401947   | ratio   |
| RQ3  | exp1                | mean_absolute_sparsity_drift         |        3 |    0.0278422   |   0.0481816   |   -0.0266804   |   0.0823649   | ratio   |
| RQ3  | exp1                | mean_absolute_sparsity_drift         |        2 |    0.0411604   |   0.0574633   |   -0.0384796   |   0.1208      | ratio   |
| RQ3  | exp1                | mean_absolute_sparsity_drift         |        5 |    0.0328499   |   0.0733391   |   -0.0314346   |   0.0971345   | ratio   |
| RQ3  | exp1                | mean_absolute_sparsity_drift         |        3 |    0.0254818   |   0.0440721   |   -0.0243905   |   0.0753541   | ratio   |
| RQ3  | exp1                | mean_absolute_sparsity_drift         |        3 |    0.0267322   |   0.0462202   |   -0.0255708   |   0.0790353   | ratio   |
| RQ3  | exp1                | mean_absolute_sparsity_drift         |        1 |    2.63126e-06 | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | mean_absolute_sparsity_drift         |        1 |    2.26873e-05 | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | mean_absolute_sparsity_drift         |        3 |    0.0216613   |   0.0348708   |   -0.0177987   |   0.0611213   | ratio   |
| RQ3  | exp1                | mean_absolute_sparsity_drift         |        3 |    0.0226616   |   0.0228834   |   -0.00323344  |   0.0485566   | ratio   |
| RQ3  | exp1                | mean_absolute_sparsity_drift         |        3 |    0.113612    |   0.196518    |   -0.108769    |   0.335993    | ratio   |
| RQ3  | exp1                | mean_absolute_sparsity_drift         |        2 |    7.40042e-05 |   9.99701e-05 |   -6.45472e-05 |   0.000212556 | ratio   |
| RQ3  | exp1                | mean_absolute_sparsity_drift         |        3 |    0.0174635   |   0.0301693   |   -0.0166763   |   0.0516033   | ratio   |
| RQ3  | exp1                | mean_absolute_sparsity_drift         |        3 |    0.0271014   |   0.0469      |   -0.0259709   |   0.0801738   | ratio   |
| RQ3  | exp1                | mean_absolute_sparsity_drift         |        2 |    0.0386419   |   0.0546037   |   -0.037035    |   0.114319    | ratio   |
| RQ3  | exp1                | mean_absolute_sparsity_drift         |        2 |    0.165476    |   0.233679    |   -0.158387    |   0.489338    | ratio   |
| RQ3  | exp1                | mean_absolute_sparsity_drift         |        3 |    0.0156062   |   0.0269182   |   -0.0148547   |   0.046067    | ratio   |
| RQ3  | exp1                | mean_absolute_sparsity_drift         |        3 |    0.0277272   |   0.047944    |   -0.0265265   |   0.081981    | ratio   |
| RQ3  | exp1                | mean_absolute_sparsity_drift         |        3 |    0.0311532   |   0.0538738   |   -0.0298108   |   0.0921171   | ratio   |
| RQ3  | exp1                | mean_absolute_sparsity_drift         |        4 |    0.0205997   |   0.0394345   |   -0.0180461   |   0.0592455   | ratio   |
| RQ3  | exp1                | mean_absolute_sparsity_drift         |        2 |    0.135976    |   0.191911    |   -0.13        |   0.401951    | ratio   |
| RQ3  | exp1                | mean_absolute_sparsity_drift         |        3 |    0.0256722   |   0.0443593   |   -0.0245251   |   0.0758695   | ratio   |
| RQ3  | exp1                | mean_absolute_sparsity_drift         |        3 |    0.0305724   |   0.0528809   |   -0.029268    |   0.0904128   | ratio   |
| RQ3  | exp1                | mean_absolute_sparsity_drift         |        3 |    0.0246883   |   0.0426615   |   -0.0235877   |   0.0729643   | ratio   |
| RQ3  | exp1                | mean_absolute_sparsity_drift         |        3 |    0.03501     |   0.0473836   |   -0.0186096   |   0.0886296   | ratio   |
| RQ3  | exp1                | mean_absolute_sparsity_drift         |        3 |    0.116183    |   0.20098     |   -0.111248    |   0.343614    | ratio   |
| RQ3  | exp1                | mean_absolute_sparsity_drift         |        3 |    0.0124992   |   0.0215414   |   -0.0118772   |   0.0368756   | ratio   |
| RQ3  | exp1                | mean_absolute_sparsity_drift         |        3 |    0.0277084   |   0.0478964   |   -0.0264915   |   0.0819082   | ratio   |
| RQ3  | exp2                | mean_absolute_sparsity_drift         |        1 |    4.10948e-05 | nan           |  nan           | nan           | ratio   |
| RQ3  | exp2                | mean_absolute_sparsity_drift         |        1 |    0.0663939   | nan           |  nan           | nan           | ratio   |
| RQ3  | exp2                | mean_absolute_sparsity_drift         |        1 |    0.000200951 | nan           |  nan           | nan           | ratio   |
| RQ3  | flame_blind         | mean_absolute_sparsity_drift         |        1 |    1.27616e-06 | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | mean_coordinate_containment_fraction |        1 |    0           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | mean_coordinate_containment_fraction |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ3  | exp1                | mean_coordinate_containment_fraction |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ3  | exp1                | mean_coordinate_containment_fraction |        3 |    0.645391    |   0.226806    |    0.388735    |   0.902047    | ratio   |
| RQ3  | exp1                | mean_coordinate_containment_fraction |        4 |    0.815938    |   0.202426    |    0.61756     |   1.01432     | ratio   |
| RQ3  | exp1                | mean_coordinate_containment_fraction |        3 |    0.781663    |   0.190246    |    0.56638     |   0.996947    | ratio   |
| RQ3  | exp1                | mean_coordinate_containment_fraction |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ3  | exp1                | mean_coordinate_containment_fraction |        2 |    0           |   0           |    0           |   0           | ratio   |
| RQ3  | exp1                | mean_coordinate_containment_fraction |        5 |    0.784718    |   0.158157    |    0.646087    |   0.923349    | ratio   |
| RQ3  | exp1                | mean_coordinate_containment_fraction |        3 |    0.83327     |   0.174113    |    0.636242    |   1.0303      | ratio   |
| RQ3  | exp1                | mean_coordinate_containment_fraction |        3 |    0.848735    |   0.183468    |    0.641122    |   1.05635     | ratio   |
| RQ3  | exp1                | mean_coordinate_containment_fraction |        1 |    0           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | mean_coordinate_containment_fraction |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ3  | exp1                | mean_coordinate_containment_fraction |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ3  | exp1                | mean_coordinate_containment_fraction |        3 |    0.586915    |   0.257043    |    0.296044    |   0.877786    | ratio   |
| RQ3  | exp1                | mean_coordinate_containment_fraction |        2 |    0.711589    |   0.403267    |    0.15269     |   1.27049     | ratio   |
| RQ3  | exp1                | mean_coordinate_containment_fraction |        3 |    0.724987    |   0.247605    |    0.444796    |   1.00518     | ratio   |
| RQ3  | exp1                | mean_coordinate_containment_fraction |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ3  | exp1                | mean_coordinate_containment_fraction |        2 |    0           |   0           |    0           |   0           | ratio   |
| RQ3  | exp1                | mean_coordinate_containment_fraction |        2 |    0.532516    |   0.000816868 |    0.531384    |   0.533648    | ratio   |
| RQ3  | exp1                | mean_coordinate_containment_fraction |        3 |    0.792299    |   0.268534    |    0.488424    |   1.09617     | ratio   |
| RQ3  | exp1                | mean_coordinate_containment_fraction |        3 |    0.765831    |   0.277317    |    0.452017    |   1.07965     | ratio   |
| RQ3  | exp1                | mean_coordinate_containment_fraction |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ3  | exp1                | mean_coordinate_containment_fraction |        4 |    0           |   0           |    0           |   0           | ratio   |
| RQ3  | exp1                | mean_coordinate_containment_fraction |        2 |    0.479431    |   0.0682484   |    0.384843    |   0.574018    | ratio   |
| RQ3  | exp1                | mean_coordinate_containment_fraction |        3 |    0.824198    |   0.218076    |    0.577422    |   1.07097     | ratio   |
| RQ3  | exp1                | mean_coordinate_containment_fraction |        3 |    0.794655    |   0.185396    |    0.584859    |   1.00445     | ratio   |
| RQ3  | exp1                | mean_coordinate_containment_fraction |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ3  | exp1                | mean_coordinate_containment_fraction |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ3  | exp1                | mean_coordinate_containment_fraction |        3 |    0.586981    |   0.260703    |    0.291968    |   0.881994    | ratio   |
| RQ3  | exp1                | mean_coordinate_containment_fraction |        3 |    0.805186    |   0.258616    |    0.512535    |   1.09784     | ratio   |
| RQ3  | exp1                | mean_coordinate_containment_fraction |        3 |    0.763258    |   0.242589    |    0.488743    |   1.03777     | ratio   |
| RQ3  | exp2                | mean_coordinate_containment_fraction |        1 |    0           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp2                | mean_coordinate_containment_fraction |        1 |    0.913332    | nan           |  nan           | nan           | ratio   |
| RQ3  | exp2                | mean_coordinate_containment_fraction |        1 |    0.54564     | nan           |  nan           | nan           | ratio   |
| RQ3  | flame_blind         | mean_coordinate_containment_fraction |        1 |    0.991861    | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | mean_direction_containment_cosine    |        1 |   -0.05        | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | mean_direction_containment_cosine    |        3 |   -1           |   3.91522e-12 |   -1           |  -1           | ratio   |
| RQ3  | exp1                | mean_direction_containment_cosine    |        3 |   -0.9         |   0.0661438   |   -0.974849    |  -0.825151    | ratio   |
| RQ3  | exp1                | mean_direction_containment_cosine    |        3 |    0.781747    |   0.0790165   |    0.692332    |   0.871163    | ratio   |
| RQ3  | exp1                | mean_direction_containment_cosine    |        4 |    0.799366    |   0.0701317   |    0.730637    |   0.868095    | ratio   |
| RQ3  | exp1                | mean_direction_containment_cosine    |        3 |    0.618063    |   0.0748447   |    0.533368    |   0.702757    | ratio   |
| RQ3  | exp1                | mean_direction_containment_cosine    |        3 |   -0.991667    |   0.0144338   |   -1.008       |  -0.975333    | ratio   |
| RQ3  | exp1                | mean_direction_containment_cosine    |        2 |   -0.95        |   4.42695e-12 |   -0.95        |  -0.95        | ratio   |
| RQ3  | exp1                | mean_direction_containment_cosine    |        5 |    0.926174    |   0.0220968   |    0.906805    |   0.945543    | ratio   |
| RQ3  | exp1                | mean_direction_containment_cosine    |        3 |    0.881475    |   0.0426167   |    0.83325     |   0.929701    | ratio   |
| RQ3  | exp1                | mean_direction_containment_cosine    |        3 |    0.905644    |   0.0330482   |    0.868247    |   0.943042    | ratio   |
| RQ3  | exp1                | mean_direction_containment_cosine    |        1 |   -0.733333    | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | mean_direction_containment_cosine    |        3 |   -0.616667    |   0.203613    |   -0.847077    |  -0.386257    | ratio   |
| RQ3  | exp1                | mean_direction_containment_cosine    |        3 |   -0.0333333   |   0.212623    |   -0.273938    |   0.207272    | ratio   |
| RQ3  | exp1                | mean_direction_containment_cosine    |        3 |    0.838101    |   0.0497382   |    0.781817    |   0.894385    | ratio   |
| RQ3  | exp1                | mean_direction_containment_cosine    |        2 |    0.808553    |   0.0770308   |    0.701794    |   0.915312    | ratio   |
| RQ3  | exp1                | mean_direction_containment_cosine    |        3 |    0.625029    |   0.0787772   |    0.535884    |   0.714173    | ratio   |
| RQ3  | exp1                | mean_direction_containment_cosine    |        3 |   -1           |   9.82347e-12 |   -1           |  -1           | ratio   |
| RQ3  | exp1                | mean_direction_containment_cosine    |        2 |   -0.9         |   0.0353553   |   -0.949       |  -0.851       | ratio   |
| RQ3  | exp1                | mean_direction_containment_cosine    |        2 |    0.901268    |   0.0031044   |    0.896966    |   0.90557     | ratio   |
| RQ3  | exp1                | mean_direction_containment_cosine    |        3 |    0.772329    |   0.0720494   |    0.690798    |   0.853861    | ratio   |
| RQ3  | exp1                | mean_direction_containment_cosine    |        3 |    0.631444    |   0.0856981   |    0.534467    |   0.72842     | ratio   |
| RQ3  | exp1                | mean_direction_containment_cosine    |        3 |   -0.991667    |   0.0144338   |   -1.008       |  -0.975333    | ratio   |
| RQ3  | exp1                | mean_direction_containment_cosine    |        4 |   -0.90625     |   0.0515388   |   -0.956758    |  -0.855742    | ratio   |
| RQ3  | exp1                | mean_direction_containment_cosine    |        2 |    0.824005    |   0.109048    |    0.672872    |   0.975138    | ratio   |
| RQ3  | exp1                | mean_direction_containment_cosine    |        3 |    0.829237    |   0.050188    |    0.772444    |   0.88603     | ratio   |
| RQ3  | exp1                | mean_direction_containment_cosine    |        3 |    0.651192    |   0.0813482   |    0.559137    |   0.743246    | ratio   |
| RQ3  | exp1                | mean_direction_containment_cosine    |        3 |   -1           |   5.59299e-12 |   -1           |  -1           | ratio   |
| RQ3  | exp1                | mean_direction_containment_cosine    |        3 |   -0.808333    |   0.0144338   |   -0.824667    |  -0.792       | ratio   |
| RQ3  | exp1                | mean_direction_containment_cosine    |        3 |    0.794643    |   0.0758227   |    0.708842    |   0.880445    | ratio   |
| RQ3  | exp1                | mean_direction_containment_cosine    |        3 |    0.805238    |   0.0714399   |    0.724396    |   0.88608     | ratio   |
| RQ3  | exp1                | mean_direction_containment_cosine    |        3 |    0.660475    |   0.0802656   |    0.569645    |   0.751304    | ratio   |
| RQ3  | exp2                | mean_direction_containment_cosine    |        1 |   -1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp2                | mean_direction_containment_cosine    |        1 |    0.807995    | nan           |  nan           | nan           | ratio   |
| RQ3  | exp2                | mean_direction_containment_cosine    |        1 |    0.908413    | nan           |  nan           | nan           | ratio   |
| RQ3  | flame_blind         | mean_direction_containment_cosine    |        1 |    0.906325    | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | mean_genuine_projected_cosine        |        1 |   -0.00180741  | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | mean_genuine_projected_cosine        |        3 |   -0.0378096   |   0.0707857   |   -0.117911    |   0.0422919   | ratio   |
| RQ3  | exp1                | mean_genuine_projected_cosine        |        3 |   -0.0348788   |   0.0550907   |   -0.0972198   |   0.0274622   | ratio   |
| RQ3  | exp1                | mean_genuine_projected_cosine        |        3 |    0.52205     |   0.201134    |    0.294446    |   0.749655    | ratio   |
| RQ3  | exp1                | mean_genuine_projected_cosine        |        4 |    0.826766    |   0.10042     |    0.728354    |   0.925177    | ratio   |
| RQ3  | exp1                | mean_genuine_projected_cosine        |        3 |   -0.308778    |   0.264117    |   -0.607655    |  -0.00990156  | ratio   |
| RQ3  | exp1                | mean_genuine_projected_cosine        |        3 |   -0.0915364   |   0.0777599   |   -0.17953     |  -0.00354277  | ratio   |
| RQ3  | exp1                | mean_genuine_projected_cosine        |        2 |   -0.0322381   |   0.0132187   |   -0.0505583   |  -0.0139178   | ratio   |
| RQ3  | exp1                | mean_genuine_projected_cosine        |        5 |    0.297411    |   0.116594    |    0.195212    |   0.39961     | ratio   |
| RQ3  | exp1                | mean_genuine_projected_cosine        |        3 |    0.532751    |   0.0647101   |    0.459524    |   0.605977    | ratio   |
| RQ3  | exp1                | mean_genuine_projected_cosine        |        3 |   -0.0614005   |   0.113402    |   -0.189727    |   0.066926    | ratio   |
| RQ3  | exp1                | mean_genuine_projected_cosine        |        1 |    0.46755     | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | mean_genuine_projected_cosine        |        1 |   -0.178702    | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | mean_genuine_projected_cosine        |        3 |   -0.254682    |   0.0755474   |   -0.340172    |  -0.169192    | ratio   |
| RQ3  | exp1                | mean_genuine_projected_cosine        |        3 |   -0.0204757   |   0.112855    |   -0.148183    |   0.107231    | ratio   |
| RQ3  | exp1                | mean_genuine_projected_cosine        |        3 |    0.629014    |   0.247192    |    0.349289    |   0.908738    | ratio   |
| RQ3  | exp1                | mean_genuine_projected_cosine        |        2 |    0.822285    |   0.174007    |    0.581123    |   1.06345     | ratio   |
| RQ3  | exp1                | mean_genuine_projected_cosine        |        3 |   -0.28897     |   0.269694    |   -0.594158    |   0.0162175   | ratio   |
| RQ3  | exp1                | mean_genuine_projected_cosine        |        3 |   -0.0675177   |   0.0741354   |   -0.15141     |   0.0163744   | ratio   |
| RQ3  | exp1                | mean_genuine_projected_cosine        |        2 |   -0.0535499   |   0.0304583   |   -0.0957629   |  -0.0113368   | ratio   |
| RQ3  | exp1                | mean_genuine_projected_cosine        |        2 |    0.329391    |   0.265179    |   -0.0381288   |   0.69691     | ratio   |
| RQ3  | exp1                | mean_genuine_projected_cosine        |        3 |    0.768476    |   0.0360367   |    0.727696    |   0.809255    | ratio   |
| RQ3  | exp1                | mean_genuine_projected_cosine        |        3 |   -0.319395    |   0.260576    |   -0.614265    |  -0.0245257   | ratio   |
| RQ3  | exp1                | mean_genuine_projected_cosine        |        3 |   -0.17365     |   0.142627    |   -0.335048    |  -0.0122515   | ratio   |
| RQ3  | exp1                | mean_genuine_projected_cosine        |        4 |   -0.0903521   |   0.0849156   |   -0.173569    |  -0.00713489  | ratio   |
| RQ3  | exp1                | mean_genuine_projected_cosine        |        2 |    0.412833    |   0.363006    |   -0.0902681   |   0.915934    | ratio   |
| RQ3  | exp1                | mean_genuine_projected_cosine        |        3 |    0.796577    |   0.140829    |    0.637214    |   0.95594     | ratio   |
| RQ3  | exp1                | mean_genuine_projected_cosine        |        3 |   -0.30661     |   0.280091    |   -0.623563    |   0.0103426   | ratio   |
| RQ3  | exp1                | mean_genuine_projected_cosine        |        3 |   -0.075923    |   0.0824548   |   -0.169229    |   0.0173835   | ratio   |
| RQ3  | exp1                | mean_genuine_projected_cosine        |        3 |   -0.0588766   |   0.0885041   |   -0.159028    |   0.0412753   | ratio   |
| RQ3  | exp1                | mean_genuine_projected_cosine        |        3 |    0.481709    |   0.29214     |    0.151122    |   0.812296    | ratio   |
| RQ3  | exp1                | mean_genuine_projected_cosine        |        3 |    0.76761     |   0.0594301   |    0.700358    |   0.834861    | ratio   |
| RQ3  | exp1                | mean_genuine_projected_cosine        |        3 |   -0.441594    |   0.116601    |   -0.57354     |  -0.309647    | ratio   |
| RQ3  | exp2                | mean_genuine_projected_cosine        |        1 |   -0.033733    | nan           |  nan           | nan           | ratio   |
| RQ3  | exp2                | mean_genuine_projected_cosine        |        1 |    0.725443    | nan           |  nan           | nan           | ratio   |
| RQ3  | exp2                | mean_genuine_projected_cosine        |        1 |    0.138056    | nan           |  nan           | nan           | ratio   |
| RQ3  | flame_blind         | mean_genuine_projected_cosine        |        1 |    0.836265    | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | mean_genuine_projected_distance      |        1 |    0.736099    | nan           |  nan           | nan           |         |
| RQ3  | exp1                | mean_genuine_projected_distance      |        3 |    3.23831     |   3.57512     |   -0.807315    |   7.28394     |         |
| RQ3  | exp1                | mean_genuine_projected_distance      |        3 |    3.05249     |   3.3614      |   -0.751289    |   6.85627     |         |
| RQ3  | exp1                | mean_genuine_projected_distance      |        3 |    2.37473     |   1.78977     |    0.349406    |   4.40005     |         |
| RQ3  | exp1                | mean_genuine_projected_distance      |        4 |    2.9906      |   3.32396     |   -0.266879    |   6.24807     |         |
| RQ3  | exp1                | mean_genuine_projected_distance      |        3 |    3.59849     |   3.59053     |   -0.464575    |   7.66156     |         |
| RQ3  | exp1                | mean_genuine_projected_distance      |        3 |    3.98609     |   4.89425     |   -1.55228     |   9.52445     |         |
| RQ3  | exp1                | mean_genuine_projected_distance      |        2 |    5.23636     |   5.32377     |   -2.14201     |  12.6147      |         |
| RQ3  | exp1                | mean_genuine_projected_distance      |        5 |    2.2937      |   2.46404     |    0.133871    |   4.45352     |         |
| RQ3  | exp1                | mean_genuine_projected_distance      |        3 |    2.51121     |   2.90583     |   -0.777046    |   5.79946     |         |
| RQ3  | exp1                | mean_genuine_projected_distance      |        3 |    3.64982     |   3.79117     |   -0.640288    |   7.93993     |         |
| RQ3  | exp1                | mean_genuine_projected_distance      |        1 |    1.39856     | nan           |  nan           | nan           |         |
| RQ3  | exp1                | mean_genuine_projected_distance      |        1 |    0.770645    | nan           |  nan           | nan           |         |
| RQ3  | exp1                | mean_genuine_projected_distance      |        3 |    5.26992     |   7.17853     |   -2.85334     |  13.3932      |         |
| RQ3  | exp1                | mean_genuine_projected_distance      |        3 |    5.64321     |   7.91038     |   -3.30822     |  14.5946      |         |
| RQ3  | exp1                | mean_genuine_projected_distance      |        3 |    3.43859     |   3.63998     |   -0.68044     |   7.55762     |         |
| RQ3  | exp1                | mean_genuine_projected_distance      |        2 |    0.560853    |   0.370462    |    0.0474184   |   1.07429     |         |
| RQ3  | exp1                | mean_genuine_projected_distance      |        3 |    5.97321     |   7.36313     |   -2.35896     |  14.3054      |         |
| RQ3  | exp1                | mean_genuine_projected_distance      |        3 |    3.40354     |   3.98657     |   -1.10769     |   7.91476     |         |
| RQ3  | exp1                | mean_genuine_projected_distance      |        2 |    4.24825     |   4.93947     |   -2.5975      |  11.094       |         |
| RQ3  | exp1                | mean_genuine_projected_distance      |        2 |    3.53861     |   2.2934      |    0.360117    |   6.7171      |         |
| RQ3  | exp1                | mean_genuine_projected_distance      |        3 |    1.5058      |   1.53836     |   -0.235016    |   3.24662     |         |
| RQ3  | exp1                | mean_genuine_projected_distance      |        3 |    3.81835     |   4.17955     |   -0.911254    |   8.54795     |         |
| RQ3  | exp1                | mean_genuine_projected_distance      |        3 |    4.34263     |   5.49156     |   -1.87166     |  10.5569      |         |
| RQ3  | exp1                | mean_genuine_projected_distance      |        4 |    3.67747     |   5.07009     |   -1.29123     |   8.64616     |         |
| RQ3  | exp1                | mean_genuine_projected_distance      |        2 |    3.65125     |   2.15093     |    0.670222    |   6.63229     |         |
| RQ3  | exp1                | mean_genuine_projected_distance      |        3 |    2.03897     |   2.4752      |   -0.761974    |   4.83992     |         |
| RQ3  | exp1                | mean_genuine_projected_distance      |        3 |    4.58658     |   5.24154     |   -1.34479     |  10.5179      |         |
| RQ3  | exp1                | mean_genuine_projected_distance      |        3 |    3.4112      |   4.11402     |   -1.24425     |   8.06664     |         |
| RQ3  | exp1                | mean_genuine_projected_distance      |        3 |    3.20332     |   3.82538     |   -1.12551     |   7.53214     |         |
| RQ3  | exp1                | mean_genuine_projected_distance      |        3 |    2.52418     |   2.04303     |    0.212272    |   4.83609     |         |
| RQ3  | exp1                | mean_genuine_projected_distance      |        3 |    1.45241     |   1.39856     |   -0.130206    |   3.03502     |         |
| RQ3  | exp1                | mean_genuine_projected_distance      |        3 |    4.05449     |   4.36266     |   -0.882322    |   8.9913      |         |
| RQ3  | exp2                | mean_genuine_projected_distance      |        1 |    1.57038     | nan           |  nan           | nan           |         |
| RQ3  | exp2                | mean_genuine_projected_distance      |        1 |    3.60276     | nan           |  nan           | nan           |         |
| RQ3  | exp2                | mean_genuine_projected_distance      |        1 |    1.91333     | nan           |  nan           | nan           |         |
| RQ3  | flame_blind         | mean_genuine_projected_distance      |        1 |    0.295365    | nan           |  nan           | nan           |         |
| RQ3  | exp1                | mean_global_direction_cosine         |        1 |   -0.05        | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | mean_global_direction_cosine         |        3 |   -1           |   3.91522e-12 |   -1           |  -1           | ratio   |
| RQ3  | exp1                | mean_global_direction_cosine         |        3 |   -0.9         |   0.0661438   |   -0.974849    |  -0.825151    | ratio   |
| RQ3  | exp1                | mean_global_direction_cosine         |        3 |    0.775945    |   0.0355765   |    0.735686    |   0.816204    | ratio   |
| RQ3  | exp1                | mean_global_direction_cosine         |        4 |    0.771134    |   0.0554054   |    0.716837    |   0.825432    | ratio   |
| RQ3  | exp1                | mean_global_direction_cosine         |        3 |    0.613373    |   0.0979314   |    0.502553    |   0.724193    | ratio   |
| RQ3  | exp1                | mean_global_direction_cosine         |        3 |   -0.991667    |   0.0144338   |   -1.008       |  -0.975333    | ratio   |
| RQ3  | exp1                | mean_global_direction_cosine         |        2 |   -0.95        |   4.42695e-12 |   -0.95        |  -0.95        | ratio   |
| RQ3  | exp1                | mean_global_direction_cosine         |        5 |    0.939327    |   0.0105629   |    0.930069    |   0.948586    | ratio   |
| RQ3  | exp1                | mean_global_direction_cosine         |        3 |    0.881327    |   0.047812    |    0.827223    |   0.935431    | ratio   |
| RQ3  | exp1                | mean_global_direction_cosine         |        3 |    0.94242     |   0.00718214  |    0.934292    |   0.950547    | ratio   |
| RQ3  | exp1                | mean_global_direction_cosine         |        1 |   -0.733333    | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | mean_global_direction_cosine         |        3 |   -0.616667    |   0.203613    |   -0.847077    |  -0.386257    | ratio   |
| RQ3  | exp1                | mean_global_direction_cosine         |        3 |   -0.0333333   |   0.212623    |   -0.273938    |   0.207272    | ratio   |
| RQ3  | exp1                | mean_global_direction_cosine         |        3 |    0.835386    |   0.0456039   |    0.783781    |   0.886992    | ratio   |
| RQ3  | exp1                | mean_global_direction_cosine         |        2 |    0.780566    |   0.0725254   |    0.680051    |   0.881081    | ratio   |
| RQ3  | exp1                | mean_global_direction_cosine         |        3 |    0.648879    |   0.0509168   |    0.591261    |   0.706496    | ratio   |
| RQ3  | exp1                | mean_global_direction_cosine         |        3 |   -1           |   9.82347e-12 |   -1           |  -1           | ratio   |
| RQ3  | exp1                | mean_global_direction_cosine         |        2 |   -0.9         |   0.0353553   |   -0.949       |  -0.851       | ratio   |
| RQ3  | exp1                | mean_global_direction_cosine         |        2 |    0.902644    |   0.0448983   |    0.840418    |   0.96487     | ratio   |
| RQ3  | exp1                | mean_global_direction_cosine         |        3 |    0.743901    |   0.0519465   |    0.685118    |   0.802684    | ratio   |
| RQ3  | exp1                | mean_global_direction_cosine         |        3 |    0.626018    |   0.100508    |    0.512283    |   0.739753    | ratio   |
| RQ3  | exp1                | mean_global_direction_cosine         |        3 |   -0.991667    |   0.0144338   |   -1.008       |  -0.975333    | ratio   |
| RQ3  | exp1                | mean_global_direction_cosine         |        4 |   -0.90625     |   0.0515388   |   -0.956758    |  -0.855742    | ratio   |
| RQ3  | exp1                | mean_global_direction_cosine         |        2 |    0.832157    |   0.0603549   |    0.748509    |   0.915805    | ratio   |
| RQ3  | exp1                | mean_global_direction_cosine         |        3 |    0.790068    |   0.0524818   |    0.730679    |   0.849457    | ratio   |
| RQ3  | exp1                | mean_global_direction_cosine         |        3 |    0.625493    |   0.0911644   |    0.522331    |   0.728656    | ratio   |
| RQ3  | exp1                | mean_global_direction_cosine         |        3 |   -1           |   5.59299e-12 |   -1           |  -1           | ratio   |
| RQ3  | exp1                | mean_global_direction_cosine         |        3 |   -0.808333    |   0.0144338   |   -0.824667    |  -0.792       | ratio   |
| RQ3  | exp1                | mean_global_direction_cosine         |        3 |    0.779833    |   0.0462315   |    0.727518    |   0.832149    | ratio   |
| RQ3  | exp1                | mean_global_direction_cosine         |        3 |    0.784797    |   0.0503566   |    0.727813    |   0.841781    | ratio   |
| RQ3  | exp1                | mean_global_direction_cosine         |        3 |    0.662712    |   0.0447939   |    0.612023    |   0.713401    | ratio   |
| RQ3  | exp2                | mean_global_direction_cosine         |        1 |   -1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp2                | mean_global_direction_cosine         |        1 |    0.751699    | nan           |  nan           | nan           | ratio   |
| RQ3  | exp2                | mean_global_direction_cosine         |        1 |    0.926834    | nan           |  nan           | nan           | ratio   |
| RQ3  | flame_blind         | mean_global_direction_cosine         |        1 |    0.880113    | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | mean_norm_containment_fraction       |        1 |    0           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | mean_norm_containment_fraction       |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ3  | exp1                | mean_norm_containment_fraction       |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ3  | exp1                | mean_norm_containment_fraction       |        3 |    0.225703    |   0.195034    |    0.00500197  |   0.446405    | ratio   |
| RQ3  | exp1                | mean_norm_containment_fraction       |        4 |    0.362659    |   0.109424    |    0.255424    |   0.469894    | ratio   |
| RQ3  | exp1                | mean_norm_containment_fraction       |        3 |    0.278694    |   0.0967516   |    0.169209    |   0.388179    | ratio   |
| RQ3  | exp1                | mean_norm_containment_fraction       |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ3  | exp1                | mean_norm_containment_fraction       |        2 |    0           |   0           |    0           |   0           | ratio   |
| RQ3  | exp1                | mean_norm_containment_fraction       |        5 |    0.472       |   0.246317    |    0.256093    |   0.687907    | ratio   |
| RQ3  | exp1                | mean_norm_containment_fraction       |        3 |    0.635556    |   0.0784411   |    0.546791    |   0.72432     | ratio   |
| RQ3  | exp1                | mean_norm_containment_fraction       |        3 |    0.627778    |   0.12286     |    0.488749    |   0.766807    | ratio   |
| RQ3  | exp1                | mean_norm_containment_fraction       |        1 |    0           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | mean_norm_containment_fraction       |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ3  | exp1                | mean_norm_containment_fraction       |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ3  | exp1                | mean_norm_containment_fraction       |        3 |    0.264628    |   0.217984    |    0.0179568   |   0.5113      | ratio   |
| RQ3  | exp1                | mean_norm_containment_fraction       |        2 |    0.337151    |   0.156838    |    0.119785    |   0.554517    | ratio   |
| RQ3  | exp1                | mean_norm_containment_fraction       |        3 |    0.427639    |   0.206874    |    0.193539    |   0.661739    | ratio   |
| RQ3  | exp1                | mean_norm_containment_fraction       |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ3  | exp1                | mean_norm_containment_fraction       |        2 |    0           |   0           |    0           |   0           | ratio   |
| RQ3  | exp1                | mean_norm_containment_fraction       |        2 |    0.21        |   0.129047    |    0.03115     |   0.38885     | ratio   |
| RQ3  | exp1                | mean_norm_containment_fraction       |        3 |    0.340417    |   0.111316    |    0.214451    |   0.466382    | ratio   |
| RQ3  | exp1                | mean_norm_containment_fraction       |        3 |    0.265972    |   0.0468789   |    0.212924    |   0.319021    | ratio   |
| RQ3  | exp1                | mean_norm_containment_fraction       |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ3  | exp1                | mean_norm_containment_fraction       |        4 |    0           |   0           |    0           |   0           | ratio   |
| RQ3  | exp1                | mean_norm_containment_fraction       |        2 |    0.15625     |   0.171473    |   -0.0814      |   0.3939      | ratio   |
| RQ3  | exp1                | mean_norm_containment_fraction       |        3 |    0.34921     |   0.0638733   |    0.276931    |   0.421489    | ratio   |
| RQ3  | exp1                | mean_norm_containment_fraction       |        3 |    0.217549    |   0.190519    |    0.00195627  |   0.433141    | ratio   |
| RQ3  | exp1                | mean_norm_containment_fraction       |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ3  | exp1                | mean_norm_containment_fraction       |        3 |    0           |   0           |    0           |   0           | ratio   |
| RQ3  | exp1                | mean_norm_containment_fraction       |        3 |    0.172083    |   0.153166    |   -0.00124058  |   0.345407    | ratio   |
| RQ3  | exp1                | mean_norm_containment_fraction       |        3 |    0.32125     |   0.112964    |    0.193419    |   0.449081    | ratio   |
| RQ3  | exp1                | mean_norm_containment_fraction       |        3 |    0.317472    |   0.126666    |    0.174136    |   0.460808    | ratio   |
| RQ3  | exp2                | mean_norm_containment_fraction       |        1 |    0           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp2                | mean_norm_containment_fraction       |        1 |    0.24125     | nan           |  nan           | nan           | ratio   |
| RQ3  | exp2                | mean_norm_containment_fraction       |        1 |    0.06125     | nan           |  nan           | nan           | ratio   |
| RQ3  | flame_blind         | mean_norm_containment_fraction       |        1 |    0.98125     | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | mean_projected_to_genuine_norm_ratio |        1 |    0.0920522   | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | mean_projected_to_genuine_norm_ratio |        3 |    0.42885     |   0.152969    |    0.255749    |   0.601951    | ratio   |
| RQ3  | exp1                | mean_projected_to_genuine_norm_ratio |        3 |    0.227546    |   0.0966008   |    0.118232    |   0.33686     | ratio   |
| RQ3  | exp1                | mean_projected_to_genuine_norm_ratio |        3 |    1.32497     |   0.44541     |    0.820945    |   1.829       | ratio   |
| RQ3  | exp1                | mean_projected_to_genuine_norm_ratio |        4 |    0.679032    |   0.137       |    0.544772    |   0.813292    | ratio   |
| RQ3  | exp1                | mean_projected_to_genuine_norm_ratio |        3 |    0.680727    |   0.144225    |    0.517521    |   0.843933    | ratio   |
| RQ3  | exp1                | mean_projected_to_genuine_norm_ratio |        3 |    0.38039     |   0.148415    |    0.212442    |   0.548337    | ratio   |
| RQ3  | exp1                | mean_projected_to_genuine_norm_ratio |        2 |    0.233346    |   0.102277    |    0.0915968   |   0.375095    | ratio   |
| RQ3  | exp1                | mean_projected_to_genuine_norm_ratio |        5 |    1.08806     |   0.26736     |    0.853712    |   1.32241     | ratio   |
| RQ3  | exp1                | mean_projected_to_genuine_norm_ratio |        3 |    0.721598    |   0.182368    |    0.515229    |   0.927967    | ratio   |
| RQ3  | exp1                | mean_projected_to_genuine_norm_ratio |        3 |    0.666087    |   0.190982    |    0.44997     |   0.882204    | ratio   |
| RQ3  | exp1                | mean_projected_to_genuine_norm_ratio |        1 |    2.16106     | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | mean_projected_to_genuine_norm_ratio |        1 |    0.233508    | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | mean_projected_to_genuine_norm_ratio |        3 |    0.134224    |   0.0992568   |    0.0219041   |   0.246544    | ratio   |
| RQ3  | exp1                | mean_projected_to_genuine_norm_ratio |        3 |    0.052282    |   0.0369916   |    0.010422    |   0.0941419   | ratio   |
| RQ3  | exp1                | mean_projected_to_genuine_norm_ratio |        3 |    1.25588     |   0.484958    |    0.707102    |   1.80467     | ratio   |
| RQ3  | exp1                | mean_projected_to_genuine_norm_ratio |        2 |    0.776629    |   0.120263    |    0.609953    |   0.943305    | ratio   |
| RQ3  | exp1                | mean_projected_to_genuine_norm_ratio |        3 |    0.593939    |   0.11676     |    0.461813    |   0.726066    | ratio   |
| RQ3  | exp1                | mean_projected_to_genuine_norm_ratio |        3 |    0.424573    |   0.202058    |    0.195923    |   0.653223    | ratio   |
| RQ3  | exp1                | mean_projected_to_genuine_norm_ratio |        2 |    0.17117     |   0.0941679   |    0.0406598   |   0.30168     | ratio   |
| RQ3  | exp1                | mean_projected_to_genuine_norm_ratio |        2 |    0.926525    |   0.368903    |    0.415251    |   1.4378      | ratio   |
| RQ3  | exp1                | mean_projected_to_genuine_norm_ratio |        3 |    0.696393    |   0.11662     |    0.564425    |   0.828361    | ratio   |
| RQ3  | exp1                | mean_projected_to_genuine_norm_ratio |        3 |    0.657762    |   0.157375    |    0.479676    |   0.835848    | ratio   |
| RQ3  | exp1                | mean_projected_to_genuine_norm_ratio |        3 |    0.346981    |   0.235245    |    0.0807758   |   0.613186    | ratio   |
| RQ3  | exp1                | mean_projected_to_genuine_norm_ratio |        4 |    0.26528     |   0.106401    |    0.161007    |   0.369553    | ratio   |
| RQ3  | exp1                | mean_projected_to_genuine_norm_ratio |        2 |    1.12635     |   0.590585    |    0.307841    |   1.94486     | ratio   |
| RQ3  | exp1                | mean_projected_to_genuine_norm_ratio |        3 |    0.70667     |   0.137281    |    0.551322    |   0.862017    | ratio   |
| RQ3  | exp1                | mean_projected_to_genuine_norm_ratio |        3 |    0.661401    |   0.165642    |    0.473959    |   0.848842    | ratio   |
| RQ3  | exp1                | mean_projected_to_genuine_norm_ratio |        3 |    0.358923    |   0.152125    |    0.186777    |   0.53107     | ratio   |
| RQ3  | exp1                | mean_projected_to_genuine_norm_ratio |        3 |    0.188335    |   0.0450601   |    0.137345    |   0.239325    | ratio   |
| RQ3  | exp1                | mean_projected_to_genuine_norm_ratio |        3 |    1.28647     |   0.517206    |    0.701192    |   1.87174     | ratio   |
| RQ3  | exp1                | mean_projected_to_genuine_norm_ratio |        3 |    0.711484    |   0.0980029   |    0.600583    |   0.822384    | ratio   |
| RQ3  | exp1                | mean_projected_to_genuine_norm_ratio |        3 |    0.640012    |   0.167337    |    0.450652    |   0.829371    | ratio   |
| RQ3  | exp2                | mean_projected_to_genuine_norm_ratio |        1 |    0.589769    | nan           |  nan           | nan           | ratio   |
| RQ3  | exp2                | mean_projected_to_genuine_norm_ratio |        1 |    0.568828    | nan           |  nan           | nan           | ratio   |
| RQ3  | exp2                | mean_projected_to_genuine_norm_ratio |        1 |    1.16249     | nan           |  nan           | nan           | ratio   |
| RQ3  | flame_blind         | mean_projected_to_genuine_norm_ratio |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | mean_rewrite_processing_duration_s   |        1 |    0.0106364   | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | mean_rewrite_processing_duration_s   |        3 |    0.240341    |   0.205368    |    0.00794598  |   0.472737    | ratio   |
| RQ3  | exp1                | mean_rewrite_processing_duration_s   |        3 |    0.228702    |   0.199042    |    0.00346394  |   0.453939    | ratio   |
| RQ3  | exp1                | mean_rewrite_processing_duration_s   |        3 |    0.168712    |   0.146911    |    0.00246605  |   0.334958    | ratio   |
| RQ3  | exp1                | mean_rewrite_processing_duration_s   |        4 |    0.158345    |   0.106616    |    0.0538617   |   0.262829    | ratio   |
| RQ3  | exp1                | mean_rewrite_processing_duration_s   |        3 |    0.154979    |   0.127103    |    0.0111478   |   0.29881     | ratio   |
| RQ3  | exp1                | mean_rewrite_processing_duration_s   |        3 |    0.195581    |   0.16264     |    0.0115364   |   0.379626    | ratio   |
| RQ3  | exp1                | mean_rewrite_processing_duration_s   |        2 |    0.368367    |   0.0422962   |    0.309748    |   0.426987    | ratio   |
| RQ3  | exp1                | mean_rewrite_processing_duration_s   |        5 |    0.129706    |   0.146272    |    0.00149255  |   0.257919    | ratio   |
| RQ3  | exp1                | mean_rewrite_processing_duration_s   |        3 |    0.214914    |   0.185312    |    0.00521374  |   0.424614    | ratio   |
| RQ3  | exp1                | mean_rewrite_processing_duration_s   |        3 |    0.218797    |   0.180609    |    0.0144186   |   0.423176    | ratio   |
| RQ3  | exp1                | mean_rewrite_processing_duration_s   |        1 |    0.00573823  | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | mean_rewrite_processing_duration_s   |        1 |    0.0242209   | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | mean_rewrite_processing_duration_s   |        3 |    0.239489    |   0.207714    |    0.00443842  |   0.474539    | ratio   |
| RQ3  | exp1                | mean_rewrite_processing_duration_s   |        3 |    0.276603    |   0.263252    |   -0.0212941   |   0.574501    | ratio   |
| RQ3  | exp1                | mean_rewrite_processing_duration_s   |        3 |    0.179913    |   0.154104    |    0.0055278   |   0.354299    | ratio   |
| RQ3  | exp1                | mean_rewrite_processing_duration_s   |        2 |    0.145673    |   0.182675    |   -0.107501    |   0.398848    | ratio   |
| RQ3  | exp1                | mean_rewrite_processing_duration_s   |        3 |    0.150279    |   0.12294     |    0.0111592   |   0.289398    | ratio   |
| RQ3  | exp1                | mean_rewrite_processing_duration_s   |        3 |    0.229724    |   0.202787    |    0.000248822 |   0.4592      | ratio   |
| RQ3  | exp1                | mean_rewrite_processing_duration_s   |        2 |    0.140366    |   0.183325    |   -0.11371     |   0.394442    | ratio   |
| RQ3  | exp1                | mean_rewrite_processing_duration_s   |        2 |    0.281565    |   0.111101    |    0.127587    |   0.435544    | ratio   |
| RQ3  | exp1                | mean_rewrite_processing_duration_s   |        3 |    0.154131    |   0.126582    |    0.0108899   |   0.297373    | ratio   |
| RQ3  | exp1                | mean_rewrite_processing_duration_s   |        3 |    0.145676    |   0.113457    |    0.0172874   |   0.274064    | ratio   |
| RQ3  | exp1                | mean_rewrite_processing_duration_s   |        3 |    0.204294    |   0.167837    |    0.0143689   |   0.39422     | ratio   |
| RQ3  | exp1                | mean_rewrite_processing_duration_s   |        4 |    0.288546    |   0.201948    |    0.090637    |   0.486454    | ratio   |
| RQ3  | exp1                | mean_rewrite_processing_duration_s   |        2 |    0.241592    |   0.0643461   |    0.152413    |   0.330772    | ratio   |
| RQ3  | exp1                | mean_rewrite_processing_duration_s   |        3 |    0.162618    |   0.134942    |    0.00991705  |   0.31532     | ratio   |
| RQ3  | exp1                | mean_rewrite_processing_duration_s   |        3 |    0.162537    |   0.140648    |    0.00337805  |   0.321695    | ratio   |
| RQ3  | exp1                | mean_rewrite_processing_duration_s   |        3 |    0.214615    |   0.179956    |    0.0109747   |   0.418254    | ratio   |
| RQ3  | exp1                | mean_rewrite_processing_duration_s   |        3 |    0.214541    |   0.180532    |    0.0102496   |   0.418833    | ratio   |
| RQ3  | exp1                | mean_rewrite_processing_duration_s   |        3 |    0.156947    |   0.128404    |    0.0116444   |   0.30225     | ratio   |
| RQ3  | exp1                | mean_rewrite_processing_duration_s   |        3 |    0.154932    |   0.126849    |    0.0113888   |   0.298476    | ratio   |
| RQ3  | exp1                | mean_rewrite_processing_duration_s   |        3 |    0.157237    |   0.132187    |    0.00765297  |   0.30682     | ratio   |
| RQ3  | exp2                | mean_rewrite_processing_duration_s   |        1 |    0.415019    | nan           |  nan           | nan           | ratio   |
| RQ3  | exp2                | mean_rewrite_processing_duration_s   |        1 |    0.176194    | nan           |  nan           | nan           | ratio   |
| RQ3  | exp2                | mean_rewrite_processing_duration_s   |        1 |    0.343568    | nan           |  nan           | nan           | ratio   |
| RQ3  | flame_blind         | mean_rewrite_processing_duration_s   |        1 |    0.0241433   | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | model_contract_hash_match_rate       |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | model_contract_hash_match_rate       |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | model_contract_hash_match_rate       |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | model_contract_hash_match_rate       |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | model_contract_hash_match_rate       |        4 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | model_contract_hash_match_rate       |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | model_contract_hash_match_rate       |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | model_contract_hash_match_rate       |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | model_contract_hash_match_rate       |        5 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | model_contract_hash_match_rate       |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | model_contract_hash_match_rate       |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | model_contract_hash_match_rate       |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | model_contract_hash_match_rate       |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | model_contract_hash_match_rate       |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | model_contract_hash_match_rate       |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | model_contract_hash_match_rate       |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | model_contract_hash_match_rate       |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | model_contract_hash_match_rate       |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | model_contract_hash_match_rate       |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | model_contract_hash_match_rate       |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | model_contract_hash_match_rate       |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | model_contract_hash_match_rate       |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | model_contract_hash_match_rate       |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | model_contract_hash_match_rate       |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | model_contract_hash_match_rate       |        4 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | model_contract_hash_match_rate       |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | model_contract_hash_match_rate       |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | model_contract_hash_match_rate       |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | model_contract_hash_match_rate       |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | model_contract_hash_match_rate       |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | model_contract_hash_match_rate       |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | model_contract_hash_match_rate       |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | model_contract_hash_match_rate       |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp2                | model_contract_hash_match_rate       |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp2                | model_contract_hash_match_rate       |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp2                | model_contract_hash_match_rate       |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | flame_blind         | model_contract_hash_match_rate       |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | modified_update_count                |        1 |   80           | nan           |  nan           | nan           | count   |
| RQ3  | exp1                | modified_update_count                |        3 |   79.6667      |   0.57735     |   79.0133      |  80.32        | count   |
| RQ3  | exp1                | modified_update_count                |        3 |   80           |   0           |   80           |  80           | count   |
| RQ3  | exp1                | modified_update_count                |        3 |   79           |   1.73205     |   77.04        |  80.96        | count   |
| RQ3  | exp1                | modified_update_count                |        4 |   79           |   2           |   77.04        |  80.96        | count   |
| RQ3  | exp1                | modified_update_count                |        3 |   79           |   1.73205     |   77.04        |  80.96        | count   |
| RQ3  | exp1                | modified_update_count                |        3 |   80           |   0           |   80           |  80           | count   |
| RQ3  | exp1                | modified_update_count                |        2 |   80           |   0           |   80           |  80           | count   |
| RQ3  | exp1                | modified_update_count                |        5 |   80           |   0           |   80           |  80           | count   |
| RQ3  | exp1                | modified_update_count                |        3 |   80           |   0           |   80           |  80           | count   |
| RQ3  | exp1                | modified_update_count                |        3 |   80           |   0           |   80           |  80           | count   |
| RQ3  | exp1                | modified_update_count                |        1 |   97           | nan           |  nan           | nan           | count   |
| RQ3  | exp1                | modified_update_count                |        1 |   45           | nan           |  nan           | nan           | count   |
| RQ3  | exp1                | modified_update_count                |        3 |   80           |   0           |   80           |  80           | count   |
| RQ3  | exp1                | modified_update_count                |        3 |   80           |   0           |   80           |  80           | count   |
| RQ3  | exp1                | modified_update_count                |        3 |   79           |   1.73205     |   77.04        |  80.96        | count   |
| RQ3  | exp1                | modified_update_count                |        2 |   78.5         |   2.12132     |   75.56        |  81.44        | count   |
| RQ3  | exp1                | modified_update_count                |        3 |   80           |   0           |   80           |  80           | count   |
| RQ3  | exp1                | modified_update_count                |        3 |   80           |   0           |   80           |  80           | count   |
| RQ3  | exp1                | modified_update_count                |        2 |   80           |   0           |   80           |  80           | count   |
| RQ3  | exp1                | modified_update_count                |        2 |   80           |   0           |   80           |  80           | count   |
| RQ3  | exp1                | modified_update_count                |        3 |   80           |   0           |   80           |  80           | count   |
| RQ3  | exp1                | modified_update_count                |        3 |   80           |   0           |   80           |  80           | count   |
| RQ3  | exp1                | modified_update_count                |        1 |    0           | nan           |  nan           | nan           | count   |
| RQ3  | exp1                | modified_update_count                |        3 |   80           |   0           |   80           |  80           | count   |
| RQ3  | exp1                | modified_update_count                |        4 |   80           |   0           |   80           |  80           | count   |
| RQ3  | exp1                | modified_update_count                |        2 |   80           |   0           |   80           |  80           | count   |
| RQ3  | exp1                | modified_update_count                |        3 |   79           |   1.73205     |   77.04        |  80.96        | count   |
| RQ3  | exp1                | modified_update_count                |        3 |   79           |   1.73205     |   77.04        |  80.96        | count   |
| RQ3  | exp1                | modified_update_count                |        3 |   80           |   0           |   80           |  80           | count   |
| RQ3  | exp1                | modified_update_count                |        3 |   80           |   0           |   80           |  80           | count   |
| RQ3  | exp1                | modified_update_count                |        3 |   80           |   0           |   80           |  80           | count   |
| RQ3  | exp1                | modified_update_count                |        3 |   80           |   0           |   80           |  80           | count   |
| RQ3  | exp1                | modified_update_count                |        3 |   79.6667      |   0.57735     |   79.0133      |  80.32        | count   |
| RQ3  | exp2                | modified_update_count                |        1 |   79           | nan           |  nan           | nan           | count   |
| RQ3  | exp2                | modified_update_count                |        1 |   80           | nan           |  nan           | nan           | count   |
| RQ3  | exp2                | modified_update_count                |        1 |   80           | nan           |  nan           | nan           | count   |
| RQ3  | exp2                | modified_update_count                |        1 |    0           | nan           |  nan           | nan           | count   |
| RQ3  | flame_blind         | modified_update_count                |        1 |   80           | nan           |  nan           | nan           | count   |
| RQ3  | exp1                | reconstruction_success_rate          |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | reconstruction_success_rate          |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | reconstruction_success_rate          |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | reconstruction_success_rate          |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | reconstruction_success_rate          |        4 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | reconstruction_success_rate          |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | reconstruction_success_rate          |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | reconstruction_success_rate          |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | reconstruction_success_rate          |        5 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | reconstruction_success_rate          |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | reconstruction_success_rate          |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | reconstruction_success_rate          |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | reconstruction_success_rate          |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | reconstruction_success_rate          |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | reconstruction_success_rate          |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | reconstruction_success_rate          |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | reconstruction_success_rate          |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | reconstruction_success_rate          |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | reconstruction_success_rate          |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | reconstruction_success_rate          |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | reconstruction_success_rate          |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | reconstruction_success_rate          |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | reconstruction_success_rate          |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | reconstruction_success_rate          |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | reconstruction_success_rate          |        4 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | reconstruction_success_rate          |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | reconstruction_success_rate          |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | reconstruction_success_rate          |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | reconstruction_success_rate          |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | reconstruction_success_rate          |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | reconstruction_success_rate          |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | reconstruction_success_rate          |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | reconstruction_success_rate          |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp2                | reconstruction_success_rate          |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp2                | reconstruction_success_rate          |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp2                | reconstruction_success_rate          |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | flame_blind         | reconstruction_success_rate          |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | std_coordinate_containment_fraction  |        1 |    0           | nan           |  nan           | nan           |         |
| RQ3  | exp1                | std_coordinate_containment_fraction  |        3 |    0           |   0           |    0           |   0           |         |
| RQ3  | exp1                | std_coordinate_containment_fraction  |        3 |    0           |   0           |    0           |   0           |         |
| RQ3  | exp1                | std_coordinate_containment_fraction  |        3 |    0.0287639   |   0.00888312  |    0.0187117   |   0.0388161   |         |
| RQ3  | exp1                | std_coordinate_containment_fraction  |        4 |    0.0600816   |   0.0545963   |    0.00657724  |   0.113586    |         |
| RQ3  | exp1                | std_coordinate_containment_fraction  |        3 |    0.0490391   |   0.0559582   |   -0.0142836   |   0.112362    |         |
| RQ3  | exp1                | std_coordinate_containment_fraction  |        3 |    0           |   0           |    0           |   0           |         |
| RQ3  | exp1                | std_coordinate_containment_fraction  |        2 |    0           |   0           |    0           |   0           |         |
| RQ3  | exp1                | std_coordinate_containment_fraction  |        5 |    0.0480044   |   0.0114388   |    0.0379778   |   0.0580309   |         |
| RQ3  | exp1                | std_coordinate_containment_fraction  |        3 |    0.0529342   |   0.0400155   |    0.00765239  |   0.098216    |         |
| RQ3  | exp1                | std_coordinate_containment_fraction  |        3 |    0.0397298   |   0.0218754   |    0.0149754   |   0.0644841   |         |
| RQ3  | exp1                | std_coordinate_containment_fraction  |        1 |    0           | nan           |  nan           | nan           |         |
| RQ3  | exp1                | std_coordinate_containment_fraction  |        3 |    0           |   0           |    0           |   0           |         |
| RQ3  | exp1                | std_coordinate_containment_fraction  |        3 |    0           |   0           |    0           |   0           |         |
| RQ3  | exp1                | std_coordinate_containment_fraction  |        3 |    0.0544412   |   0.0379249   |    0.0115252   |   0.0973572   |         |
| RQ3  | exp1                | std_coordinate_containment_fraction  |        2 |    0.00879413  |   0.00435307  |    0.00276109  |   0.0148272   |         |
| RQ3  | exp1                | std_coordinate_containment_fraction  |        3 |    0.0491133   |   0.0506873   |   -0.00824484  |   0.106471    |         |
| RQ3  | exp1                | std_coordinate_containment_fraction  |        3 |    0           |   0           |    0           |   0           |         |
| RQ3  | exp1                | std_coordinate_containment_fraction  |        2 |    0           |   0           |    0           |   0           |         |
| RQ3  | exp1                | std_coordinate_containment_fraction  |        2 |    0.0449363   |   0.0246606   |    0.0107585   |   0.0791142   |         |
| RQ3  | exp1                | std_coordinate_containment_fraction  |        3 |    0.0379275   |   0.0210838   |    0.014069    |   0.061786    |         |
| RQ3  | exp1                | std_coordinate_containment_fraction  |        3 |    0.0248564   |   0.011662    |    0.0116596   |   0.0380532   |         |
| RQ3  | exp1                | std_coordinate_containment_fraction  |        3 |    0           |   0           |    0           |   0           |         |
| RQ3  | exp1                | std_coordinate_containment_fraction  |        4 |    0           |   0           |    0           |   0           |         |
| RQ3  | exp1                | std_coordinate_containment_fraction  |        2 |    0.0655387   |   0.0346218   |    0.0175554   |   0.113522    |         |
| RQ3  | exp1                | std_coordinate_containment_fraction  |        3 |    0.0282363   |   0.0349591   |   -0.0113237   |   0.0677962   |         |
| RQ3  | exp1                | std_coordinate_containment_fraction  |        3 |    0.0391938   |   0.0187282   |    0.0180008   |   0.0603867   |         |
| RQ3  | exp1                | std_coordinate_containment_fraction  |        3 |    0           |   0           |    0           |   0           |         |
| RQ3  | exp1                | std_coordinate_containment_fraction  |        3 |    0           |   0           |    0           |   0           |         |
| RQ3  | exp1                | std_coordinate_containment_fraction  |        3 |    0.0416863   |   0.0198856   |    0.0191836   |   0.064189    |         |
| RQ3  | exp1                | std_coordinate_containment_fraction  |        3 |    0.0381573   |   0.0249637   |    0.00990816  |   0.0664064   |         |
| RQ3  | exp1                | std_coordinate_containment_fraction  |        3 |    0.0355758   |   0.0267289   |    0.00532914  |   0.0658224   |         |
| RQ3  | exp2                | std_coordinate_containment_fraction  |        1 |    0           | nan           |  nan           | nan           |         |
| RQ3  | exp2                | std_coordinate_containment_fraction  |        1 |    0.0605223   | nan           |  nan           | nan           |         |
| RQ3  | exp2                | std_coordinate_containment_fraction  |        1 |    0.0248645   | nan           |  nan           | nan           |         |
| RQ3  | flame_blind         | std_coordinate_containment_fraction  |        1 |    0.0131601   | nan           |  nan           | nan           |         |
| RQ3  | exp1                | std_direction_containment_cosine     |        1 |    1.00505     | nan           |  nan           | nan           |         |
| RQ3  | exp1                | std_direction_containment_cosine     |        3 |    2.0305e-12  |   2.70255e-12 |   -1.02772e-12 |   5.08873e-12 |         |
| RQ3  | exp1                | std_direction_containment_cosine     |        3 |    0.421761    |   0.131734    |    0.27269     |   0.570832    |         |
| RQ3  | exp1                | std_direction_containment_cosine     |        3 |    0.095217    |   0.0298697   |    0.0614162   |   0.129018    |         |
| RQ3  | exp1                | std_direction_containment_cosine     |        4 |    0.108482    |   0.0636876   |    0.0460686   |   0.170896    |         |
| RQ3  | exp1                | std_direction_containment_cosine     |        3 |    0.13841     |   0.0308109   |    0.103544    |   0.173276    |         |
| RQ3  | exp1                | std_direction_containment_cosine     |        3 |    0.0745356   |   0.129099    |   -0.0715542   |   0.220625    |         |
| RQ3  | exp1                | std_direction_containment_cosine     |        2 |    0.31422     |   2.98514e-13 |    0.31422     |   0.31422     |         |
| RQ3  | exp1                | std_direction_containment_cosine     |        5 |    0.071996    |   0.0281202   |    0.0473476   |   0.0966444   |         |
| RQ3  | exp1                | std_direction_containment_cosine     |        3 |    0.097162    |   0.0285201   |    0.0648885   |   0.129435    |         |
| RQ3  | exp1                | std_direction_containment_cosine     |        3 |    0.100687    |   0.0386786   |    0.0569177   |   0.144456    |         |
| RQ3  | exp1                | std_direction_containment_cosine     |        1 |    0.687552    | nan           |  nan           | nan           |         |
| RQ3  | exp1                | std_direction_containment_cosine     |        3 |    0.757372    |   0.197354    |    0.534045    |   0.980699    |         |
| RQ3  | exp1                | std_direction_containment_cosine     |        3 |    0.990326    |   0.0200353   |    0.967654    |   1.013       |         |
| RQ3  | exp1                | std_direction_containment_cosine     |        3 |    0.079154    |   0.0421783   |    0.0314248   |   0.126883    |         |
| RQ3  | exp1                | std_direction_containment_cosine     |        2 |    0.0782188   |   0.034078    |    0.0309891   |   0.125449    |         |
| RQ3  | exp1                | std_direction_containment_cosine     |        3 |    0.119022    |   0.0380108   |    0.0760085   |   0.162035    |         |
| RQ3  | exp1                | std_direction_containment_cosine     |        3 |    2.75455e-11 |   4.68251e-11 |   -2.54421e-11 |   8.05331e-11 |         |
| RQ3  | exp1                | std_direction_containment_cosine     |        2 |    0.434771    |   0.074114    |    0.332054    |   0.537488    |         |
| RQ3  | exp1                | std_direction_containment_cosine     |        2 |    0.0848759   |   0.0106407   |    0.0701287   |   0.0996231   |         |
| RQ3  | exp1                | std_direction_containment_cosine     |        3 |    0.116749    |   0.0473288   |    0.0631919   |   0.170307    |         |
| RQ3  | exp1                | std_direction_containment_cosine     |        3 |    0.103174    |   0.0101568   |    0.0916803   |   0.114667    |         |
| RQ3  | exp1                | std_direction_containment_cosine     |        3 |    0.0745356   |   0.129099    |   -0.0715542   |   0.220625    |         |
| RQ3  | exp1                | std_direction_containment_cosine     |        4 |    0.411431    |   0.113609    |    0.300094    |   0.522768    |         |
| RQ3  | exp1                | std_direction_containment_cosine     |        2 |    0.0914318   |   0.0175073   |    0.0671678   |   0.115696    |         |
| RQ3  | exp1                | std_direction_containment_cosine     |        3 |    0.0898186   |   0.0348388   |    0.0503948   |   0.129242    |         |
| RQ3  | exp1                | std_direction_containment_cosine     |        3 |    0.125315    |   0.0173939   |    0.105632    |   0.144998    |         |
| RQ3  | exp1                | std_direction_containment_cosine     |        3 |    2.48734e-12 |   3.26279e-12 |   -1.20486e-12 |   6.17953e-12 |         |
| RQ3  | exp1                | std_direction_containment_cosine     |        3 |    0.59209     |   0.0202576   |    0.569166    |   0.615013    |         |
| RQ3  | exp1                | std_direction_containment_cosine     |        3 |    0.0704986   |   0.0318106   |    0.0345015   |   0.106496    |         |
| RQ3  | exp1                | std_direction_containment_cosine     |        3 |    0.0896139   |   0.0226425   |    0.0639915   |   0.115236    |         |
| RQ3  | exp1                | std_direction_containment_cosine     |        3 |    0.107634    |   0.0251577   |    0.0791651   |   0.136102    |         |
| RQ3  | exp2                | std_direction_containment_cosine     |        1 |    7.92301e-13 | nan           |  nan           | nan           |         |
| RQ3  | exp2                | std_direction_containment_cosine     |        1 |    0.124182    | nan           |  nan           | nan           |         |
| RQ3  | exp2                | std_direction_containment_cosine     |        1 |    0.0500146   | nan           |  nan           | nan           |         |
| RQ3  | flame_blind         | std_direction_containment_cosine     |        1 |    0.0693182   | nan           |  nan           | nan           |         |
| RQ3  | exp1                | std_genuine_projected_cosine         |        1 |    0.227122    | nan           |  nan           | nan           |         |
| RQ3  | exp1                | std_genuine_projected_cosine         |        3 |    0.0558388   |   0.0413231   |    0.00907732  |   0.1026      |         |
| RQ3  | exp1                | std_genuine_projected_cosine         |        3 |    0.0621549   |   0.0593826   |   -0.00504291  |   0.129353    |         |
| RQ3  | exp1                | std_genuine_projected_cosine         |        3 |    0.172932    |   0.116189    |    0.0414518   |   0.304412    |         |
| RQ3  | exp1                | std_genuine_projected_cosine         |        4 |    0.139414    |   0.0698569   |    0.0709542   |   0.207874    |         |
| RQ3  | exp1                | std_genuine_projected_cosine         |        3 |    0.300593    |   0.276119    |   -0.0118655   |   0.613051    |         |
| RQ3  | exp1                | std_genuine_projected_cosine         |        3 |    0.078404    |   0.0745744   |   -0.00598488  |   0.162793    |         |
| RQ3  | exp1                | std_genuine_projected_cosine         |        2 |    0.0358247   |   0.0100571   |    0.0218862   |   0.0497632   |         |
| RQ3  | exp1                | std_genuine_projected_cosine         |        5 |    0.204657    |   0.102442    |    0.114863    |   0.294452    |         |
| RQ3  | exp1                | std_genuine_projected_cosine         |        3 |    0.269816    |   0.0251047   |    0.241407    |   0.298224    |         |
| RQ3  | exp1                | std_genuine_projected_cosine         |        3 |    0.361212    |   0.203172    |    0.131301    |   0.591122    |         |
| RQ3  | exp1                | std_genuine_projected_cosine         |        1 |    0.0515203   | nan           |  nan           | nan           |         |
| RQ3  | exp1                | std_genuine_projected_cosine         |        1 |    0.207873    | nan           |  nan           | nan           |         |
| RQ3  | exp1                | std_genuine_projected_cosine         |        3 |    0.321246    |   0.133547    |    0.170123    |   0.472369    |         |
| RQ3  | exp1                | std_genuine_projected_cosine         |        3 |    0.347665    |   0.0964535   |    0.238518    |   0.456813    |         |
| RQ3  | exp1                | std_genuine_projected_cosine         |        3 |    0.136268    |   0.0700439   |    0.0570059   |   0.21553     |         |
| RQ3  | exp1                | std_genuine_projected_cosine         |        2 |    0.0904171   |   0.0437228   |    0.0298203   |   0.151014    |         |
| RQ3  | exp1                | std_genuine_projected_cosine         |        3 |    0.287798    |   0.267732    |   -0.0151699   |   0.590765    |         |
| RQ3  | exp1                | std_genuine_projected_cosine         |        3 |    0.0569385   |   0.0548112   |   -0.00508625  |   0.118963    |         |
| RQ3  | exp1                | std_genuine_projected_cosine         |        2 |    0.0627055   |   0.0516766   |   -0.00891469  |   0.134326    |         |
| RQ3  | exp1                | std_genuine_projected_cosine         |        2 |    0.2236      |   0.117353    |    0.0609576   |   0.386242    |         |
| RQ3  | exp1                | std_genuine_projected_cosine         |        3 |    0.161076    |   0.0194551   |    0.139061    |   0.183092    |         |
| RQ3  | exp1                | std_genuine_projected_cosine         |        3 |    0.254934    |   0.175787    |    0.0560119   |   0.453855    |         |
| RQ3  | exp1                | std_genuine_projected_cosine         |        3 |    0.0845739   |   0.0589111   |    0.0179098   |   0.151238    |         |
| RQ3  | exp1                | std_genuine_projected_cosine         |        4 |    0.0965798   |   0.0875366   |    0.010794    |   0.182366    |         |
| RQ3  | exp1                | std_genuine_projected_cosine         |        2 |    0.180218    |   0.110001    |    0.0277638   |   0.332672    |         |
| RQ3  | exp1                | std_genuine_projected_cosine         |        3 |    0.103567    |   0.0662108   |    0.0286425   |   0.178492    |         |
| RQ3  | exp1                | std_genuine_projected_cosine         |        3 |    0.277862    |   0.195596    |    0.0565244   |   0.499199    |         |
| RQ3  | exp1                | std_genuine_projected_cosine         |        3 |    0.0625038   |   0.0637678   |   -0.00965627  |   0.134664    |         |
| RQ3  | exp1                | std_genuine_projected_cosine         |        3 |    0.0732956   |   0.0752334   |   -0.011839    |   0.15843     |         |
| RQ3  | exp1                | std_genuine_projected_cosine         |        3 |    0.123623    |   0.105547    |    0.00418556  |   0.24306     |         |
| RQ3  | exp1                | std_genuine_projected_cosine         |        3 |    0.170942    |   0.0412374   |    0.124278    |   0.217607    |         |
| RQ3  | exp1                | std_genuine_projected_cosine         |        3 |    0.285992    |   0.174009    |    0.0890822   |   0.482902    |         |
| RQ3  | exp2                | std_genuine_projected_cosine         |        1 |    0.0161089   | nan           |  nan           | nan           |         |
| RQ3  | exp2                | std_genuine_projected_cosine         |        1 |    0.18499     | nan           |  nan           | nan           |         |
| RQ3  | exp2                | std_genuine_projected_cosine         |        1 |    0.0584647   | nan           |  nan           | nan           |         |
| RQ3  | flame_blind         | std_genuine_projected_cosine         |        1 |    0.200223    | nan           |  nan           | nan           |         |
| RQ3  | exp1                | std_genuine_projected_distance       |        1 |    0.0552294   | nan           |  nan           | nan           |         |
| RQ3  | exp1                | std_genuine_projected_distance       |        3 |    0.36384     |   0.309298    |    0.0138371   |   0.713844    |         |
| RQ3  | exp1                | std_genuine_projected_distance       |        3 |    0.234343    |   0.142045    |    0.0736043   |   0.395082    |         |
| RQ3  | exp1                | std_genuine_projected_distance       |        3 |    0.557502    |   0.578062    |   -0.0966365   |   1.21164     |         |
| RQ3  | exp1                | std_genuine_projected_distance       |        4 |    1.36275     |   1.4849      |   -0.0924506   |   2.81795     |         |
| RQ3  | exp1                | std_genuine_projected_distance       |        3 |    0.647407    |   0.663628    |   -0.103559    |   1.39837     |         |
| RQ3  | exp1                | std_genuine_projected_distance       |        3 |    0.259208    |   0.175407    |    0.0607172   |   0.4577      |         |
| RQ3  | exp1                | std_genuine_projected_distance       |        2 |    0.388167    |   0.177345    |    0.142379    |   0.633954    |         |
| RQ3  | exp1                | std_genuine_projected_distance       |        5 |    0.636647    |   0.944143    |   -0.19093     |   1.46422     |         |
| RQ3  | exp1                | std_genuine_projected_distance       |        3 |    1.15535     |   1.28558     |   -0.299419    |   2.61012     |         |
| RQ3  | exp1                | std_genuine_projected_distance       |        3 |    1.20128     |   1.53697     |   -0.537968    |   2.94053     |         |
| RQ3  | exp1                | std_genuine_projected_distance       |        1 |    0.00800626  | nan           |  nan           | nan           |         |
| RQ3  | exp1                | std_genuine_projected_distance       |        1 |    0.0738124   | nan           |  nan           | nan           |         |
| RQ3  | exp1                | std_genuine_projected_distance       |        3 |    0.280425    |   0.171867    |    0.085939    |   0.474911    |         |
| RQ3  | exp1                | std_genuine_projected_distance       |        3 |    0.241733    |   0.105894    |    0.121903    |   0.361563    |         |
| RQ3  | exp1                | std_genuine_projected_distance       |        3 |    1.40692     |   2.13907     |   -1.01366     |   3.82751     |         |
| RQ3  | exp1                | std_genuine_projected_distance       |        2 |    0.209155    |   0.159339    |   -0.0116777   |   0.429987    |         |
| RQ3  | exp1                | std_genuine_projected_distance       |        3 |    1.41359     |   1.96083     |   -0.805297    |   3.63247     |         |
| RQ3  | exp1                | std_genuine_projected_distance       |        3 |    0.281088    |   0.184921    |    0.0718301   |   0.490345    |         |
| RQ3  | exp1                | std_genuine_projected_distance       |        2 |    0.185734    |   0.176224    |   -0.0585006   |   0.429969    |         |
| RQ3  | exp1                | std_genuine_projected_distance       |        2 |    1.02668     |   0.969393    |   -0.316833    |   2.37019     |         |
| RQ3  | exp1                | std_genuine_projected_distance       |        3 |    0.805936    |   0.96753     |   -0.288926    |   1.9008      |         |
| RQ3  | exp1                | std_genuine_projected_distance       |        3 |    0.505542    |   0.455663    |   -0.0100889   |   1.02117     |         |
| RQ3  | exp1                | std_genuine_projected_distance       |        3 |    0.361005    |   0.306787    |    0.0138429   |   0.708167    |         |
| RQ3  | exp1                | std_genuine_projected_distance       |        4 |    0.287577    |   0.201405    |    0.0902008   |   0.484954    |         |
| RQ3  | exp1                | std_genuine_projected_distance       |        2 |    1.34836     |   1.4457      |   -0.65528     |   3.352       |         |
| RQ3  | exp1                | std_genuine_projected_distance       |        3 |    0.994097    |   1.42381     |   -0.617092    |   2.60529     |         |
| RQ3  | exp1                | std_genuine_projected_distance       |        3 |    0.631442    |   0.646357    |   -0.0999794   |   1.36286     |         |
| RQ3  | exp1                | std_genuine_projected_distance       |        3 |    0.218445    |   0.106037    |    0.0984526   |   0.338438    |         |
| RQ3  | exp1                | std_genuine_projected_distance       |        3 |    0.216305    |   0.144915    |    0.0523181   |   0.380292    |         |
| RQ3  | exp1                | std_genuine_projected_distance       |        3 |    0.598771    |   0.788207    |   -0.29317     |   1.49071     |         |
| RQ3  | exp1                | std_genuine_projected_distance       |        3 |    0.857102    |   1.0413      |   -0.321236    |   2.03544     |         |
| RQ3  | exp1                | std_genuine_projected_distance       |        3 |    0.528292    |   0.452406    |    0.0163459   |   1.04024     |         |
| RQ3  | exp2                | std_genuine_projected_distance       |        1 |    0.299544    | nan           |  nan           | nan           |         |
| RQ3  | exp2                | std_genuine_projected_distance       |        1 |    1.53876     | nan           |  nan           | nan           |         |
| RQ3  | exp2                | std_genuine_projected_distance       |        1 |    0.302892    | nan           |  nan           | nan           |         |
| RQ3  | flame_blind         | std_genuine_projected_distance       |        1 |    0.299884    | nan           |  nan           | nan           |         |
| RQ3  | exp1                | std_global_direction_cosine          |        1 |    1.00505     | nan           |  nan           | nan           |         |
| RQ3  | exp1                | std_global_direction_cosine          |        3 |    2.0305e-12  |   2.70255e-12 |   -1.02772e-12 |   5.08873e-12 |         |
| RQ3  | exp1                | std_global_direction_cosine          |        3 |    0.421761    |   0.131734    |    0.27269     |   0.570832    |         |
| RQ3  | exp1                | std_global_direction_cosine          |        3 |    0.0955327   |   0.0509352   |    0.0378941   |   0.153171    |         |
| RQ3  | exp1                | std_global_direction_cosine          |        4 |    0.133861    |   0.0624009   |    0.072708    |   0.195014    |         |
| RQ3  | exp1                | std_global_direction_cosine          |        3 |    0.119818    |   0.0424514   |    0.07178     |   0.167856    |         |
| RQ3  | exp1                | std_global_direction_cosine          |        3 |    0.0745356   |   0.129099    |   -0.0715542   |   0.220625    |         |
| RQ3  | exp1                | std_global_direction_cosine          |        2 |    0.31422     |   2.98514e-13 |    0.31422     |   0.31422     |         |
| RQ3  | exp1                | std_global_direction_cosine          |        5 |    0.0264749   |   0.00976186  |    0.0179183   |   0.0350316   |         |
| RQ3  | exp1                | std_global_direction_cosine          |        3 |    0.115371    |   0.0464812   |    0.062773    |   0.16797     |         |
| RQ3  | exp1                | std_global_direction_cosine          |        3 |    0.0455072   |   0.0309019   |    0.0105385   |   0.080476    |         |
| RQ3  | exp1                | std_global_direction_cosine          |        1 |    0.687552    | nan           |  nan           | nan           |         |
| RQ3  | exp1                | std_global_direction_cosine          |        3 |    0.757372    |   0.197354    |    0.534045    |   0.980699    |         |
| RQ3  | exp1                | std_global_direction_cosine          |        3 |    0.990326    |   0.0200353   |    0.967654    |   1.013       |         |
| RQ3  | exp1                | std_global_direction_cosine          |        3 |    0.077115    |   0.0567972   |    0.012843    |   0.141387    |         |
| RQ3  | exp1                | std_global_direction_cosine          |        2 |    0.0799628   |   0.00594659  |    0.0717212   |   0.0882043   |         |
| RQ3  | exp1                | std_global_direction_cosine          |        3 |    0.0978609   |   0.0211823   |    0.0738909   |   0.121831    |         |
| RQ3  | exp1                | std_global_direction_cosine          |        3 |    2.75455e-11 |   4.68251e-11 |   -2.54421e-11 |   8.05331e-11 |         |
| RQ3  | exp1                | std_global_direction_cosine          |        2 |    0.434771    |   0.074114    |    0.332054    |   0.537488    |         |
| RQ3  | exp1                | std_global_direction_cosine          |        2 |    0.0948979   |   0.0307448   |    0.0522878   |   0.137508    |         |
| RQ3  | exp1                | std_global_direction_cosine          |        3 |    0.138191    |   0.0557867   |    0.0750623   |   0.20132     |         |
| RQ3  | exp1                | std_global_direction_cosine          |        3 |    0.100336    |   0.011931    |    0.0868349   |   0.113837    |         |
| RQ3  | exp1                | std_global_direction_cosine          |        3 |    0.0745356   |   0.129099    |   -0.0715542   |   0.220625    |         |
| RQ3  | exp1                | std_global_direction_cosine          |        4 |    0.411431    |   0.113609    |    0.300094    |   0.522768    |         |
| RQ3  | exp1                | std_global_direction_cosine          |        2 |    0.0838532   |   0.0137433   |    0.064806    |   0.1029      |         |
| RQ3  | exp1                | std_global_direction_cosine          |        3 |    0.0918055   |   0.0433295   |    0.0427736   |   0.140837    |         |
| RQ3  | exp1                | std_global_direction_cosine          |        3 |    0.104441    |   0.0125754   |    0.0902105   |   0.118671    |         |
| RQ3  | exp1                | std_global_direction_cosine          |        3 |    2.48734e-12 |   3.26279e-12 |   -1.20486e-12 |   6.17953e-12 |         |
| RQ3  | exp1                | std_global_direction_cosine          |        3 |    0.59209     |   0.0202576   |    0.569166    |   0.615013    |         |
| RQ3  | exp1                | std_global_direction_cosine          |        3 |    0.0706251   |   0.0494661   |    0.014649    |   0.126601    |         |
| RQ3  | exp1                | std_global_direction_cosine          |        3 |    0.0901741   |   0.0340395   |    0.0516548   |   0.128693    |         |
| RQ3  | exp1                | std_global_direction_cosine          |        3 |    0.103947    |   0.0241106   |    0.0766634   |   0.131231    |         |
| RQ3  | exp2                | std_global_direction_cosine          |        1 |    7.92301e-13 | nan           |  nan           | nan           |         |
| RQ3  | exp2                | std_global_direction_cosine          |        1 |    0.146172    | nan           |  nan           | nan           |         |
| RQ3  | exp2                | std_global_direction_cosine          |        1 |    0.0126581   | nan           |  nan           | nan           |         |
| RQ3  | flame_blind         | std_global_direction_cosine          |        1 |    0.10049     | nan           |  nan           | nan           |         |
| RQ3  | exp1                | std_norm_containment_fraction        |        1 |    0           | nan           |  nan           | nan           |         |
| RQ3  | exp1                | std_norm_containment_fraction        |        3 |    0           |   0           |    0           |   0           |         |
| RQ3  | exp1                | std_norm_containment_fraction        |        3 |    0           |   0           |    0           |   0           |         |
| RQ3  | exp1                | std_norm_containment_fraction        |        3 |    0.187855    |   0.125829    |    0.0454656   |   0.330243    |         |
| RQ3  | exp1                | std_norm_containment_fraction        |        4 |    0.210352    |   0.0606857   |    0.15088     |   0.269824    |         |
| RQ3  | exp1                | std_norm_containment_fraction        |        3 |    0.205369    |   0.0291006   |    0.172439    |   0.2383      |         |
| RQ3  | exp1                | std_norm_containment_fraction        |        3 |    0           |   0           |    0           |   0           |         |
| RQ3  | exp1                | std_norm_containment_fraction        |        2 |    0           |   0           |    0           |   0           |         |
| RQ3  | exp1                | std_norm_containment_fraction        |        5 |    0.242941    |   0.0826881   |    0.170461    |   0.31542     |         |
| RQ3  | exp1                | std_norm_containment_fraction        |        3 |    0.272025    |   0.0340888   |    0.23345     |   0.3106      |         |
| RQ3  | exp1                | std_norm_containment_fraction        |        3 |    0.232951    |   0.00946487  |    0.222241    |   0.243662    |         |
| RQ3  | exp1                | std_norm_containment_fraction        |        1 |    0           | nan           |  nan           | nan           |         |
| RQ3  | exp1                | std_norm_containment_fraction        |        3 |    0           |   0           |    0           |   0           |         |
| RQ3  | exp1                | std_norm_containment_fraction        |        3 |    0           |   0           |    0           |   0           |         |
| RQ3  | exp1                | std_norm_containment_fraction        |        3 |    0.221967    |   0.151623    |    0.0503888   |   0.393545    |         |
| RQ3  | exp1                | std_norm_containment_fraction        |        2 |    0.194393    |   0.0883475   |    0.07195     |   0.316837    |         |
| RQ3  | exp1                | std_norm_containment_fraction        |        3 |    0.209304    |   0.0354769   |    0.169158    |   0.24945     |         |
| RQ3  | exp1                | std_norm_containment_fraction        |        3 |    0           |   0           |    0           |   0           |         |
| RQ3  | exp1                | std_norm_containment_fraction        |        2 |    0           |   0           |    0           |   0           |         |
| RQ3  | exp1                | std_norm_containment_fraction        |        2 |    0.198623    |   0.0614671   |    0.113434    |   0.283812    |         |
| RQ3  | exp1                | std_norm_containment_fraction        |        3 |    0.191084    |   0.0451277   |    0.140017    |   0.242151    |         |
| RQ3  | exp1                | std_norm_containment_fraction        |        3 |    0.188654    |   0.0481025   |    0.134221    |   0.243087    |         |
| RQ3  | exp1                | std_norm_containment_fraction        |        3 |    0           |   0           |    0           |   0           |         |
| RQ3  | exp1                | std_norm_containment_fraction        |        4 |    0           |   0           |    0           |   0           |         |
| RQ3  | exp1                | std_norm_containment_fraction        |        2 |    0.199994    |   0.147636    |   -0.00461904  |   0.404606    |         |
| RQ3  | exp1                | std_norm_containment_fraction        |        3 |    0.210602    |   0.0472134   |    0.157175    |   0.264028    |         |
| RQ3  | exp1                | std_norm_containment_fraction        |        3 |    0.154492    |   0.0364067   |    0.113294    |   0.19569     |         |
| RQ3  | exp1                | std_norm_containment_fraction        |        3 |    0           |   0           |    0           |   0           |         |
| RQ3  | exp1                | std_norm_containment_fraction        |        3 |    0           |   0           |    0           |   0           |         |
| RQ3  | exp1                | std_norm_containment_fraction        |        3 |    0.152287    |   0.118587    |    0.0180929   |   0.286481    |         |
| RQ3  | exp1                | std_norm_containment_fraction        |        3 |    0.192956    |   0.0557705   |    0.129846    |   0.256066    |         |
| RQ3  | exp1                | std_norm_containment_fraction        |        3 |    0.192052    |   0.084404    |    0.0965396   |   0.287564    |         |
| RQ3  | exp2                | std_norm_containment_fraction        |        1 |    0           | nan           |  nan           | nan           |         |
| RQ3  | exp2                | std_norm_containment_fraction        |        1 |    0.151527    | nan           |  nan           | nan           |         |
| RQ3  | exp2                | std_norm_containment_fraction        |        1 |    0.163424    | nan           |  nan           | nan           |         |
| RQ3  | flame_blind         | std_norm_containment_fraction        |        1 |    0.0649231   | nan           |  nan           | nan           |         |
| RQ3  | exp1                | std_projected_to_genuine_norm_ratio  |        1 |    0.0967372   | nan           |  nan           | nan           |         |
| RQ3  | exp1                | std_projected_to_genuine_norm_ratio  |        3 |    0.0867191   |   0.0807239   |   -0.00462861  |   0.178067    |         |
| RQ3  | exp1                | std_projected_to_genuine_norm_ratio  |        3 |    0.0952465   |   0.0259935   |    0.0658321   |   0.124661    |         |
| RQ3  | exp1                | std_projected_to_genuine_norm_ratio  |        3 |    0.204911    |   0.0807982   |    0.113479    |   0.296343    |         |
| RQ3  | exp1                | std_projected_to_genuine_norm_ratio  |        4 |    0.133507    |   0.0885752   |    0.0467031   |   0.220311    |         |
| RQ3  | exp1                | std_projected_to_genuine_norm_ratio  |        3 |    0.0887164   |   0.066961    |    0.0129429   |   0.16449     |         |
| RQ3  | exp1                | std_projected_to_genuine_norm_ratio  |        3 |    0.0932243   |   0.0721037   |    0.0116313   |   0.174817    |         |
| RQ3  | exp1                | std_projected_to_genuine_norm_ratio  |        2 |    0.0561204   |   0.0193365   |    0.0293214   |   0.0829194   |         |
| RQ3  | exp1                | std_projected_to_genuine_norm_ratio  |        5 |    0.176218    |   0.0866567   |    0.10026     |   0.252176    |         |
| RQ3  | exp1                | std_projected_to_genuine_norm_ratio  |        3 |    0.155878    |   0.109365    |    0.0321199   |   0.279636    |         |
| RQ3  | exp1                | std_projected_to_genuine_norm_ratio  |        3 |    0.137506    |   0.118114    |    0.00384721  |   0.271164    |         |
| RQ3  | exp1                | std_projected_to_genuine_norm_ratio  |        1 |    0.215579    | nan           |  nan           | nan           |         |
| RQ3  | exp1                | std_projected_to_genuine_norm_ratio  |        1 |    0.134122    | nan           |  nan           | nan           |         |
| RQ3  | exp1                | std_projected_to_genuine_norm_ratio  |        3 |    0.0979075   |   0.0601221   |    0.0298729   |   0.165942    |         |
| RQ3  | exp1                | std_projected_to_genuine_norm_ratio  |        3 |    0.0723356   |   0.043374    |    0.0232532   |   0.121418    |         |
| RQ3  | exp1                | std_projected_to_genuine_norm_ratio  |        3 |    0.255646    |   0.0818223   |    0.163055    |   0.348237    |         |
| RQ3  | exp1                | std_projected_to_genuine_norm_ratio  |        2 |    0.0554127   |   0.0388953   |    0.00150659  |   0.109319    |         |
| RQ3  | exp1                | std_projected_to_genuine_norm_ratio  |        3 |    0.117974    |   0.0882253   |    0.0181381   |   0.217811    |         |
| RQ3  | exp1                | std_projected_to_genuine_norm_ratio  |        3 |    0.096261    |   0.0984699   |   -0.0151681   |   0.20769     |         |
| RQ3  | exp1                | std_projected_to_genuine_norm_ratio  |        2 |    0.103327    |   0.0561415   |    0.0255189   |   0.181135    |         |
| RQ3  | exp1                | std_projected_to_genuine_norm_ratio  |        2 |    0.31789     |   0.00851335  |    0.306091    |   0.329689    |         |
| RQ3  | exp1                | std_projected_to_genuine_norm_ratio  |        3 |    0.123443    |   0.0995148   |    0.0108311   |   0.236054    |         |
| RQ3  | exp1                | std_projected_to_genuine_norm_ratio  |        3 |    0.113313    |   0.0850279   |    0.0170949   |   0.209531    |         |
| RQ3  | exp1                | std_projected_to_genuine_norm_ratio  |        3 |    0.0886951   |   0.0857326   |   -0.00832047  |   0.185711    |         |
| RQ3  | exp1                | std_projected_to_genuine_norm_ratio  |        4 |    0.0923563   |   0.0345917   |    0.0584564   |   0.126256    |         |
| RQ3  | exp1                | std_projected_to_genuine_norm_ratio  |        2 |    0.28709     |   0.0567039   |    0.208503    |   0.365678    |         |
| RQ3  | exp1                | std_projected_to_genuine_norm_ratio  |        3 |    0.112751    |   0.106318    |   -0.00755923  |   0.233061    |         |
| RQ3  | exp1                | std_projected_to_genuine_norm_ratio  |        3 |    0.113451    |   0.0976985   |    0.00289476  |   0.224007    |         |
| RQ3  | exp1                | std_projected_to_genuine_norm_ratio  |        3 |    0.100189    |   0.0808317   |    0.00871913  |   0.191659    |         |
| RQ3  | exp1                | std_projected_to_genuine_norm_ratio  |        3 |    0.112727    |   0.0434246   |    0.0635871   |   0.161866    |         |
| RQ3  | exp1                | std_projected_to_genuine_norm_ratio  |        3 |    0.192186    |   0.0747757   |    0.107569    |   0.276802    |         |
| RQ3  | exp1                | std_projected_to_genuine_norm_ratio  |        3 |    0.122972    |   0.100698    |    0.00902174  |   0.236922    |         |
| RQ3  | exp1                | std_projected_to_genuine_norm_ratio  |        3 |    0.112918    |   0.0831143   |    0.0188658   |   0.206971    |         |
| RQ3  | exp2                | std_projected_to_genuine_norm_ratio  |        1 |    0.0244716   | nan           |  nan           | nan           |         |
| RQ3  | exp2                | std_projected_to_genuine_norm_ratio  |        1 |    0.194905    | nan           |  nan           | nan           |         |
| RQ3  | exp2                | std_projected_to_genuine_norm_ratio  |        1 |    0.0469905   | nan           |  nan           | nan           |         |
| RQ3  | flame_blind         | std_projected_to_genuine_norm_ratio  |        1 |    2.38659e-07 | nan           |  nan           | nan           |         |
| RQ3  | exp1                | std_rewrite_processing_duration_s    |        1 |    0.0019607   | nan           |  nan           | nan           |         |
| RQ3  | exp1                | std_rewrite_processing_duration_s    |        3 |    0.0450326   |   0.0450923   |   -0.00599417  |   0.0960594   |         |
| RQ3  | exp1                | std_rewrite_processing_duration_s    |        3 |    0.0384438   |   0.0314211   |    0.0028874   |   0.0740001   |         |
| RQ3  | exp1                | std_rewrite_processing_duration_s    |        3 |    0.0187941   |   0.0196495   |   -0.00344146  |   0.0410296   |         |
| RQ3  | exp1                | std_rewrite_processing_duration_s    |        4 |    0.0199526   |   0.0143251   |    0.00591402  |   0.0339911   |         |
| RQ3  | exp1                | std_rewrite_processing_duration_s    |        3 |    0.0144559   |   0.0109802   |    0.00203065  |   0.0268812   |         |
| RQ3  | exp1                | std_rewrite_processing_duration_s    |        3 |    0.0364634   |   0.0298224   |    0.00271626  |   0.0702106   |         |
| RQ3  | exp1                | std_rewrite_processing_duration_s    |        2 |    0.073813    |   0.00214041  |    0.0708465   |   0.0767794   |         |
| RQ3  | exp1                | std_rewrite_processing_duration_s    |        5 |    0.0156438   |   0.0169169   |    0.000815503 |   0.0304721   |         |
| RQ3  | exp1                | std_rewrite_processing_duration_s    |        3 |    0.0426224   |   0.0427427   |   -0.00574554  |   0.0909903   |         |
| RQ3  | exp1                | std_rewrite_processing_duration_s    |        3 |    0.04565     |   0.0412671   |   -0.00104806  |   0.0923481   |         |
| RQ3  | exp1                | std_rewrite_processing_duration_s    |        1 |    0.00124058  | nan           |  nan           | nan           |         |
| RQ3  | exp1                | std_rewrite_processing_duration_s    |        1 |    0.0026844   | nan           |  nan           | nan           |         |
| RQ3  | exp1                | std_rewrite_processing_duration_s    |        3 |    0.0610166   |   0.0628363   |   -0.0100894   |   0.132123    |         |
| RQ3  | exp1                | std_rewrite_processing_duration_s    |        3 |    0.0732729   |   0.0824962   |   -0.0200804   |   0.166626    |         |
| RQ3  | exp1                | std_rewrite_processing_duration_s    |        3 |    0.0374255   |   0.0388778   |   -0.00656896  |   0.0814199   |         |
| RQ3  | exp1                | std_rewrite_processing_duration_s    |        2 |    0.0197654   |   0.0240441   |   -0.0135581   |   0.0530889   |         |
| RQ3  | exp1                | std_rewrite_processing_duration_s    |        3 |    0.0138567   |   0.0124708   |   -0.00025528  |   0.0279687   |         |
| RQ3  | exp1                | std_rewrite_processing_duration_s    |        3 |    0.0479791   |   0.0422731   |    0.000142627 |   0.0958156   |         |
| RQ3  | exp1                | std_rewrite_processing_duration_s    |        2 |    0.0274561   |   0.0365774   |   -0.0232376   |   0.0781498   |         |
| RQ3  | exp1                | std_rewrite_processing_duration_s    |        2 |    0.0277626   |   0.0189112   |    0.00155297  |   0.0539722   |         |
| RQ3  | exp1                | std_rewrite_processing_duration_s    |        3 |    0.013548    |   0.0111836   |    0.000892534 |   0.0262034   |         |
| RQ3  | exp1                | std_rewrite_processing_duration_s    |        3 |    0.0134707   |   0.00954563  |    0.00266883  |   0.0242726   |         |
| RQ3  | exp1                | std_rewrite_processing_duration_s    |        3 |    0.035165    |   0.033718    |   -0.00299045  |   0.0733205   |         |
| RQ3  | exp1                | std_rewrite_processing_duration_s    |        4 |    0.0507079   |   0.0399078   |    0.0115983   |   0.0898176   |         |
| RQ3  | exp1                | std_rewrite_processing_duration_s    |        2 |    0.0308181   |   0.0241486   |   -0.00265015  |   0.0642864   |         |
| RQ3  | exp1                | std_rewrite_processing_duration_s    |        3 |    0.0174903   |   0.0165754   |   -0.00126659  |   0.0362471   |         |
| RQ3  | exp1                | std_rewrite_processing_duration_s    |        3 |    0.0197189   |   0.0212161   |   -0.00428938  |   0.0437271   |         |
| RQ3  | exp1                | std_rewrite_processing_duration_s    |        3 |    0.0490052   |   0.0445567   |   -0.00141541  |   0.0994259   |         |
| RQ3  | exp1                | std_rewrite_processing_duration_s    |        3 |    0.0471541   |   0.0409648   |    0.000798052 |   0.0935101   |         |
| RQ3  | exp1                | std_rewrite_processing_duration_s    |        3 |    0.0131969   |   0.0112489   |    0.000467661 |   0.0259262   |         |
| RQ3  | exp1                | std_rewrite_processing_duration_s    |        3 |    0.0175937   |   0.0139623   |    0.0017938   |   0.0333935   |         |
| RQ3  | exp1                | std_rewrite_processing_duration_s    |        3 |    0.0212048   |   0.0166526   |    0.00236062  |   0.040049    |         |
| RQ3  | exp2                | std_rewrite_processing_duration_s    |        1 |    0.0321967   | nan           |  nan           | nan           |         |
| RQ3  | exp2                | std_rewrite_processing_duration_s    |        1 |    0.0124618   | nan           |  nan           | nan           |         |
| RQ3  | exp2                | std_rewrite_processing_duration_s    |        1 |    0.0346497   | nan           |  nan           | nan           |         |
| RQ3  | flame_blind         | std_rewrite_processing_duration_s    |        1 |    0.00306153  | nan           |  nan           | nan           |         |
| RQ3  | exp1                | update_space_usage_rate              |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | update_space_usage_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | update_space_usage_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | update_space_usage_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | update_space_usage_rate              |        4 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | update_space_usage_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | update_space_usage_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | update_space_usage_rate              |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | update_space_usage_rate              |        5 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | update_space_usage_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | update_space_usage_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | update_space_usage_rate              |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | update_space_usage_rate              |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | update_space_usage_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | update_space_usage_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | update_space_usage_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | update_space_usage_rate              |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | update_space_usage_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | update_space_usage_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | update_space_usage_rate              |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | update_space_usage_rate              |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | update_space_usage_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | update_space_usage_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | update_space_usage_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | update_space_usage_rate              |        4 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | update_space_usage_rate              |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | update_space_usage_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | update_space_usage_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | update_space_usage_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | update_space_usage_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | update_space_usage_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | update_space_usage_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | update_space_usage_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp2                | update_space_usage_rate              |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp2                | update_space_usage_rate              |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp2                | update_space_usage_rate              |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | flame_blind         | update_space_usage_rate              |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | wire_compatibility_rate              |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | wire_compatibility_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | wire_compatibility_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | wire_compatibility_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | wire_compatibility_rate              |        4 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | wire_compatibility_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | wire_compatibility_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | wire_compatibility_rate              |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | wire_compatibility_rate              |        5 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | wire_compatibility_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | wire_compatibility_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | wire_compatibility_rate              |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | wire_compatibility_rate              |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp1                | wire_compatibility_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | wire_compatibility_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | wire_compatibility_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | wire_compatibility_rate              |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | wire_compatibility_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | wire_compatibility_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | wire_compatibility_rate              |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | wire_compatibility_rate              |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | wire_compatibility_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | wire_compatibility_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | wire_compatibility_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | wire_compatibility_rate              |        4 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | wire_compatibility_rate              |        2 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | wire_compatibility_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | wire_compatibility_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | wire_compatibility_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | wire_compatibility_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | wire_compatibility_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | wire_compatibility_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp1                | wire_compatibility_rate              |        3 |    1           |   0           |    1           |   1           | ratio   |
| RQ3  | exp2                | wire_compatibility_rate              |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp2                | wire_compatibility_rate              |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | exp2                | wire_compatibility_rate              |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ3  | flame_blind         | wire_compatibility_rate              |        1 |    1           | nan           |  nan           | nan           | ratio   |
| RQ4  | exp1                | mean_aggregation_duration_s          |        1 |    0.011004    | nan           |  nan           | nan           | s       |
| RQ4  | exp1                | mean_aggregation_duration_s          |        1 |    0.00241437  | nan           |  nan           | nan           | s       |
| RQ4  | exp1                | mean_aggregation_duration_s          |        2 |    0.0213115   |   0.00580667  |    0.0132639   |   0.0293591   | s       |
| RQ4  | exp1                | mean_aggregation_duration_s          |        1 |    0.0181029   | nan           |  nan           | nan           | s       |
| RQ4  | exp1                | mean_aggregation_duration_s          |        1 |    0.0265762   | nan           |  nan           | nan           | s       |
| RQ4  | exp1                | mean_aggregation_duration_s          |        1 |    0.0260381   | nan           |  nan           | nan           | s       |
| RQ4  | exp1                | mean_aggregation_duration_s          |        1 |    0.0255991   | nan           |  nan           | nan           | s       |
| RQ4  | exp1                | mean_aggregation_duration_s          |        1 |    0.0137034   | nan           |  nan           | nan           | s       |
| RQ4  | exp1                | mean_aggregation_duration_s          |        1 |    0.00167114  | nan           |  nan           | nan           | s       |
| RQ4  | exp1                | mean_aggregation_duration_s          |        2 |    0.00774905  |   0.00770369  |   -0.00292771  |   0.0184258   | s       |
| RQ4  | exp1                | mean_aggregation_duration_s          |        1 |    0.0538505   | nan           |  nan           | nan           | s       |
| RQ4  | exp1                | mean_aggregation_duration_s          |        1 |    0.0549531   | nan           |  nan           | nan           | s       |
| RQ4  | exp1                | mean_aggregation_duration_s          |        1 |    0.0549663   | nan           |  nan           | nan           | s       |
| RQ4  | exp1                | mean_aggregation_duration_s          |        1 |    0.0543576   | nan           |  nan           | nan           | s       |
| RQ4  | exp1                | mean_aggregation_duration_s          |        1 |    0.0541739   | nan           |  nan           | nan           | s       |
| RQ4  | exp1                | mean_aggregation_duration_s          |        1 |    0.0144345   | nan           |  nan           | nan           | s       |
| RQ4  | exp1                | mean_aggregation_duration_s          |        1 |    0.00249473  | nan           |  nan           | nan           | s       |
| RQ4  | exp1                | mean_aggregation_duration_s          |        1 |    0.0544971   | nan           |  nan           | nan           | s       |
| RQ4  | exp1                | mean_aggregation_duration_s          |        1 |    0.0105847   | nan           |  nan           | nan           | s       |
| RQ4  | exp1                | mean_aggregation_duration_s          |        1 |    0.0362979   | nan           |  nan           | nan           | s       |
| RQ4  | exp1                | mean_aggregation_duration_s          |        1 |    0.0366543   | nan           |  nan           | nan           | s       |
| RQ4  | exp1                | mean_aggregation_duration_s          |        1 |    0.0273802   | nan           |  nan           | nan           | s       |
| RQ4  | exp2                | mean_aggregation_duration_s          |        1 |    0.0107609   | nan           |  nan           | nan           | s       |
| RQ4  | exp2                | mean_aggregation_duration_s          |        1 |    0.0248361   | nan           |  nan           | nan           | s       |
| RQ4  | exp2                | mean_aggregation_duration_s          |        1 |    0.0136954   | nan           |  nan           | nan           | s       |
| RQ4  | exp2                | mean_aggregation_duration_s          |        1 |    0.00180804  | nan           |  nan           | nan           | s       |
| RQ4  | exp2                | mean_aggregation_duration_s          |        1 |    0.0536797   | nan           |  nan           | nan           | s       |
| RQ4  | exp2                | mean_aggregation_duration_s          |        1 |    0.0145288   | nan           |  nan           | nan           | s       |
| RQ4  | fedavg_blind        | mean_aggregation_duration_s          |       10 |    0.0017632   |   0.000190024 |    0.00164542  |   0.00188098  | s       |
| RQ4  | fedavg_run_01       | mean_aggregation_duration_s          |       15 |    0.00925197  |   0.00145204  |    0.00851714  |   0.0099868   | s       |
| RQ4  | flame_blind         | mean_aggregation_duration_s          |       12 |    0.00284429  |   0.00037027  |    0.00263479  |   0.00305379  | s       |
| RQ4  | flame_blind         | mean_aggregation_duration_s          |        1 |    0.00334203  | nan           |  nan           | nan           | s       |
| RQ4  | flame_run_01        | mean_aggregation_duration_s          |        8 |    0.0209086   |   0.00457971  |    0.0177351   |   0.0240822   | s       |
| RQ4  | krum_blind          | mean_aggregation_duration_s          |        9 |    0.00210629  |   0.000201997 |    0.00197432  |   0.00223826  | s       |
| RQ4  | krum_run_01         | mean_aggregation_duration_s          |       11 |    0.0108378   |   0.00175326  |    0.00980167  |   0.0118739   | s       |
| RQ4  | median_blind        | mean_aggregation_duration_s          |       10 |    0.00304266  |   0.000150045 |    0.00294966  |   0.00313566  | s       |
| RQ4  | median_run_01       | mean_aggregation_duration_s          |        7 |    0.0392159   |   0.000462775 |    0.0388731   |   0.0395587   | s       |
| RQ4  | multi_krum_blind    | mean_aggregation_duration_s          |       12 |    0.00192906  |   0.000411762 |    0.00169608  |   0.00216204  | s       |
| RQ4  | multi_krum_run_01   | mean_aggregation_duration_s          |       10 |    0.0123068   |   0.00217839  |    0.0109566   |   0.013657    | s       |
| RQ4  | trimmed_mean_blind  | mean_aggregation_duration_s          |       10 |    0.00281848  |   0.000274508 |    0.00264834  |   0.00298862  | s       |
| RQ4  | trimmed_mean_run_01 | mean_aggregation_duration_s          |       11 |    0.031406    |   0.00496383  |    0.0284726   |   0.0343394   | s       |
| RQ4  | exp1                | mean_flame_main_cluster_size         |        2 |    3.12        |   0.0282843   |    3.0808      |   3.1592      | count   |
| RQ4  | exp1                | mean_flame_main_cluster_size         |        1 |    3.08        | nan           |  nan           | nan           | count   |
| RQ4  | exp1                | mean_flame_main_cluster_size         |        1 |    3.01        | nan           |  nan           | nan           | count   |
| RQ4  | exp1                | mean_flame_main_cluster_size         |        1 |    3.09        | nan           |  nan           | nan           | count   |
| RQ4  | exp1                | mean_flame_main_cluster_size         |        1 |    3.08        | nan           |  nan           | nan           | count   |
| RQ4  | exp2                | mean_flame_main_cluster_size         |        1 |    3.04        | nan           |  nan           | nan           | count   |
| RQ4  | flame_blind         | mean_flame_main_cluster_size         |       12 |    3.18333     |   0.0795822   |    3.13831     |   3.22836     | count   |
| RQ4  | flame_blind         | mean_flame_main_cluster_size         |        1 |    3.21        | nan           |  nan           | nan           | count   |
| RQ4  | flame_run_01        | mean_flame_main_cluster_size         |        8 |    3.10125     |   0.0814928   |    3.04478     |   3.15772     | count   |
| RQ4  | exp1                | mean_flame_rejected_count            |        2 |    1.88        |   0.0282843   |    1.8408      |   1.9192      | count   |
| RQ4  | exp1                | mean_flame_rejected_count            |        1 |    1.92        | nan           |  nan           | nan           | count   |
| RQ4  | exp1                | mean_flame_rejected_count            |        1 |    1.99        | nan           |  nan           | nan           | count   |
| RQ4  | exp1                | mean_flame_rejected_count            |        1 |    1.91        | nan           |  nan           | nan           | count   |
| RQ4  | exp1                | mean_flame_rejected_count            |        1 |    1.92        | nan           |  nan           | nan           | count   |
| RQ4  | exp2                | mean_flame_rejected_count            |        1 |    1.96        | nan           |  nan           | nan           | count   |
| RQ4  | flame_blind         | mean_flame_rejected_count            |       12 |    1.81583     |   0.0785619   |    1.77138     |   1.86028     | count   |
| RQ4  | flame_blind         | mean_flame_rejected_count            |        1 |    1.79        | nan           |  nan           | nan           | count   |
| RQ4  | flame_run_01        | mean_flame_rejected_count            |        8 |    1.89875     |   0.0814928   |    1.84228     |   1.95522     | count   |
| RQ4  | exp1                | mean_inferred_suspicious_count       |        1 |    0.21        | nan           |  nan           | nan           | count   |
| RQ4  | exp1                | mean_inferred_suspicious_count       |        1 |    0.19        | nan           |  nan           | nan           | count   |
| RQ4  | exp1                | mean_inferred_suspicious_count       |        2 |    1.88        |   0.0282843   |    1.8408      |   1.9192      | count   |
| RQ4  | exp1                | mean_inferred_suspicious_count       |        1 |    1.92        | nan           |  nan           | nan           | count   |
| RQ4  | exp1                | mean_inferred_suspicious_count       |        1 |    1.99        | nan           |  nan           | nan           | count   |
| RQ4  | exp1                | mean_inferred_suspicious_count       |        1 |    1.91        | nan           |  nan           | nan           | count   |
| RQ4  | exp1                | mean_inferred_suspicious_count       |        1 |    1.92        | nan           |  nan           | nan           | count   |
| RQ4  | exp1                | mean_inferred_suspicious_count       |        1 |    0.29        | nan           |  nan           | nan           | count   |
| RQ4  | exp1                | mean_inferred_suspicious_count       |        1 |    0.6         | nan           |  nan           | nan           | count   |
| RQ4  | exp1                | mean_inferred_suspicious_count       |        2 |    0.225       |   0.120208    |    0.0584      |   0.3916      | count   |
| RQ4  | exp1                | mean_inferred_suspicious_count       |        1 |    0.14        | nan           |  nan           | nan           | count   |
| RQ4  | exp1                | mean_inferred_suspicious_count       |        1 |    0.14        | nan           |  nan           | nan           | count   |
| RQ4  | exp1                | mean_inferred_suspicious_count       |        1 |    0.36        | nan           |  nan           | nan           | count   |
| RQ4  | exp1                | mean_inferred_suspicious_count       |        1 |    0.28        | nan           |  nan           | nan           | count   |
| RQ4  | exp1                | mean_inferred_suspicious_count       |        1 |    0.62        | nan           |  nan           | nan           | count   |
| RQ4  | exp1                | mean_inferred_suspicious_count       |        1 |    0.29        | nan           |  nan           | nan           | count   |
| RQ4  | exp1                | mean_inferred_suspicious_count       |        1 |    0.24        | nan           |  nan           | nan           | count   |
| RQ4  | exp1                | mean_inferred_suspicious_count       |        1 |    0.11        | nan           |  nan           | nan           | count   |
| RQ4  | exp1                | mean_inferred_suspicious_count       |        1 |    0.86        | nan           |  nan           | nan           | count   |
| RQ4  | exp1                | mean_inferred_suspicious_count       |        1 |    0.38        | nan           |  nan           | nan           | count   |
| RQ4  | exp1                | mean_inferred_suspicious_count       |        1 |    0.38        | nan           |  nan           | nan           | count   |
| RQ4  | exp1                | mean_inferred_suspicious_count       |        1 |    0.51        | nan           |  nan           | nan           | count   |
| RQ4  | exp2                | mean_inferred_suspicious_count       |        1 |    0.19        | nan           |  nan           | nan           | count   |
| RQ4  | exp2                | mean_inferred_suspicious_count       |        1 |    1.96        | nan           |  nan           | nan           | count   |
| RQ4  | exp2                | mean_inferred_suspicious_count       |        1 |    0.19        | nan           |  nan           | nan           | count   |
| RQ4  | exp2                | mean_inferred_suspicious_count       |        1 |    0           | nan           |  nan           | nan           | count   |
| RQ4  | exp2                | mean_inferred_suspicious_count       |        1 |    0.17        | nan           |  nan           | nan           | count   |
| RQ4  | exp2                | mean_inferred_suspicious_count       |        1 |    0.2         | nan           |  nan           | nan           | count   |
| RQ4  | fedavg_blind        | mean_inferred_suspicious_count       |       10 |    0.259       |   0.146625    |    0.168121    |   0.349879    | count   |
| RQ4  | fedavg_run_01       | mean_inferred_suspicious_count       |       15 |    0.376       |   0.258921    |    0.244968    |   0.507032    | count   |
| RQ4  | flame_blind         | mean_inferred_suspicious_count       |       12 |    1.81583     |   0.0785619   |    1.77138     |   1.86028     | count   |
| RQ4  | flame_blind         | mean_inferred_suspicious_count       |        1 |    1.79        | nan           |  nan           | nan           | count   |
| RQ4  | flame_run_01        | mean_inferred_suspicious_count       |        8 |    1.89875     |   0.0814928   |    1.84228     |   1.95522     | count   |
| RQ4  | krum_blind          | mean_inferred_suspicious_count       |        9 |    0.318889    |   0.189898    |    0.194822    |   0.442955    | count   |
| RQ4  | krum_run_01         | mean_inferred_suspicious_count       |       11 |    0.571818    |   0.499576    |    0.276588    |   0.867049    | count   |
| RQ4  | median_blind        | mean_inferred_suspicious_count       |       10 |    0.218       |   0.0345768   |    0.196569    |   0.239431    | count   |
| RQ4  | median_run_01       | mean_inferred_suspicious_count       |        7 |    0.397143    |   0.223362    |    0.231674    |   0.562612    | count   |
| RQ4  | multi_krum_blind    | mean_inferred_suspicious_count       |       12 |    0.359167    |   0.220349    |    0.234492    |   0.483841    | count   |
| RQ4  | multi_krum_run_01   | mean_inferred_suspicious_count       |       10 |    0.646       |   0.383527    |    0.408287    |   0.883713    | count   |
| RQ4  | trimmed_mean_blind  | mean_inferred_suspicious_count       |       10 |    0.196       |   0.0620394   |    0.157548    |   0.234452    | count   |
| RQ4  | trimmed_mean_run_01 | mean_inferred_suspicious_count       |       11 |    0.670909    |   0.662185    |    0.279583    |   1.06224     | count   |
| RQ4  | exp1                | mean_selected_suspicious_count       |        1 |    0.21        | nan           |  nan           | nan           | count   |
| RQ4  | exp1                | mean_selected_suspicious_count       |        1 |    0.19        | nan           |  nan           | nan           | count   |
| RQ4  | exp1                | mean_selected_suspicious_count       |        2 |    0           |   0           |    0           |   0           | count   |
| RQ4  | exp1                | mean_selected_suspicious_count       |        1 |    0           | nan           |  nan           | nan           | count   |
| RQ4  | exp1                | mean_selected_suspicious_count       |        1 |    0           | nan           |  nan           | nan           | count   |
| RQ4  | exp1                | mean_selected_suspicious_count       |        1 |    0           | nan           |  nan           | nan           | count   |
| RQ4  | exp1                | mean_selected_suspicious_count       |        1 |    0           | nan           |  nan           | nan           | count   |
| RQ4  | exp1                | mean_selected_suspicious_count       |        1 |    0           | nan           |  nan           | nan           | count   |
| RQ4  | exp1                | mean_selected_suspicious_count       |        1 |    0           | nan           |  nan           | nan           | count   |
| RQ4  | exp1                | mean_selected_suspicious_count       |        2 |    0           |   0           |    0           |   0           | count   |
| RQ4  | exp1                | mean_selected_suspicious_count       |        1 |    0.14        | nan           |  nan           | nan           | count   |
| RQ4  | exp1                | mean_selected_suspicious_count       |        1 |    0.14        | nan           |  nan           | nan           | count   |
| RQ4  | exp1                | mean_selected_suspicious_count       |        1 |    0.36        | nan           |  nan           | nan           | count   |
| RQ4  | exp1                | mean_selected_suspicious_count       |        1 |    0.28        | nan           |  nan           | nan           | count   |
| RQ4  | exp1                | mean_selected_suspicious_count       |        1 |    0.62        | nan           |  nan           | nan           | count   |
| RQ4  | exp1                | mean_selected_suspicious_count       |        1 |    0           | nan           |  nan           | nan           | count   |
| RQ4  | exp1                | mean_selected_suspicious_count       |        1 |    0.04        | nan           |  nan           | nan           | count   |
| RQ4  | exp1                | mean_selected_suspicious_count       |        1 |    0.11        | nan           |  nan           | nan           | count   |
| RQ4  | exp1                | mean_selected_suspicious_count       |        1 |    0.06        | nan           |  nan           | nan           | count   |
| RQ4  | exp1                | mean_selected_suspicious_count       |        1 |    0.38        | nan           |  nan           | nan           | count   |
| RQ4  | exp1                | mean_selected_suspicious_count       |        1 |    0.38        | nan           |  nan           | nan           | count   |
| RQ4  | exp1                | mean_selected_suspicious_count       |        1 |    0.51        | nan           |  nan           | nan           | count   |
| RQ4  | exp2                | mean_selected_suspicious_count       |        1 |    0.19        | nan           |  nan           | nan           | count   |
| RQ4  | exp2                | mean_selected_suspicious_count       |        1 |    0           | nan           |  nan           | nan           | count   |
| RQ4  | exp2                | mean_selected_suspicious_count       |        1 |    0           | nan           |  nan           | nan           | count   |
| RQ4  | exp2                | mean_selected_suspicious_count       |        1 |    0           | nan           |  nan           | nan           | count   |
| RQ4  | exp2                | mean_selected_suspicious_count       |        1 |    0.17        | nan           |  nan           | nan           | count   |
| RQ4  | exp2                | mean_selected_suspicious_count       |        1 |    0.03        | nan           |  nan           | nan           | count   |
| RQ4  | fedavg_blind        | mean_selected_suspicious_count       |       10 |    0.259       |   0.146625    |    0.168121    |   0.349879    | count   |
| RQ4  | fedavg_run_01       | mean_selected_suspicious_count       |       15 |    0.376       |   0.258921    |    0.244968    |   0.507032    | count   |
| RQ4  | flame_blind         | mean_selected_suspicious_count       |       12 |    0           |   0           |    0           |   0           | count   |
| RQ4  | flame_blind         | mean_selected_suspicious_count       |        1 |    0           | nan           |  nan           | nan           | count   |
| RQ4  | flame_run_01        | mean_selected_suspicious_count       |        8 |    0           |   0           |    0           |   0           | count   |
| RQ4  | krum_blind          | mean_selected_suspicious_count       |        9 |    0           |   0           |    0           |   0           | count   |
| RQ4  | krum_run_01         | mean_selected_suspicious_count       |       11 |    0           |   0           |    0           |   0           | count   |
| RQ4  | median_blind        | mean_selected_suspicious_count       |       10 |    0.218       |   0.0345768   |    0.196569    |   0.239431    | count   |
| RQ4  | median_run_01       | mean_selected_suspicious_count       |        7 |    0.397143    |   0.223362    |    0.231674    |   0.562612    | count   |
| RQ4  | multi_krum_blind    | mean_selected_suspicious_count       |       12 |    0.055       |   0.027798    |    0.0392718   |   0.0707282   | count   |
| RQ4  | multi_krum_run_01   | mean_selected_suspicious_count       |       10 |    0.053       |   0.0533437   |    0.0199372   |   0.0860628   | count   |
| RQ4  | trimmed_mean_blind  | mean_selected_suspicious_count       |       10 |    0.196       |   0.0620394   |    0.157548    |   0.234452    | count   |
| RQ4  | trimmed_mean_run_01 | mean_selected_suspicious_count       |       11 |    0.670909    |   0.662185    |    0.279583    |   1.06224     | count   |
| RQ5  | exp1                | aulc_global_accuracy                 |        1 |    0.349419    | nan           |  nan           | nan           | ratio   |
| RQ5  | fedavg_blind        | aulc_global_accuracy                 |       10 |    0.590455    |   0.0246678   |    0.575166    |   0.605744    | ratio   |
| RQ5  | fedavg_run_01       | aulc_global_accuracy                 |        8 |    0.536602    |   0.0549837   |    0.4985      |   0.574704    | ratio   |
| RQ5  | flame_blind         | aulc_global_accuracy                 |       12 |    0.552644    |   0.0272113   |    0.537248    |   0.56804     | ratio   |
| RQ5  | flame_run_01        | aulc_global_accuracy                 |        5 |    0.384393    |   0.0766851   |    0.317175    |   0.45161     | ratio   |
| RQ5  | krum_blind          | aulc_global_accuracy                 |        9 |    0.505024    |   0.0388581   |    0.479637    |   0.530412    | ratio   |
| RQ5  | krum_run_01         | aulc_global_accuracy                 |        7 |    0.211347    |   0.0133749   |    0.201439    |   0.221255    | ratio   |
| RQ5  | median_blind        | aulc_global_accuracy                 |       10 |    0.576278    |   0.0224277   |    0.562377    |   0.590178    | ratio   |
| RQ5  | median_run_01       | aulc_global_accuracy                 |        7 |    0.482232    |   0.0542804   |    0.442021    |   0.522444    | ratio   |
| RQ5  | multi_krum_blind    | aulc_global_accuracy                 |       12 |    0.570877    |   0.030116    |    0.553838    |   0.587917    | ratio   |
| RQ5  | multi_krum_run_01   | aulc_global_accuracy                 |        6 |    0.442946    |   0.0342524   |    0.415538    |   0.470353    | ratio   |
| RQ5  | trimmed_mean_blind  | aulc_global_accuracy                 |       10 |    0.573255    |   0.0317049   |    0.553604    |   0.592906    | ratio   |
| RQ5  | trimmed_mean_run_01 | aulc_global_accuracy                 |        6 |    0.45996     |   0.132825    |    0.353678    |   0.566242    | ratio   |
| RQ5  | exp1                | aulc_global_macro_f1                 |        1 |    0.259318    | nan           |  nan           | nan           | ratio   |
| RQ5  | fedavg_blind        | aulc_global_macro_f1                 |       10 |    0.552038    |   0.028916    |    0.534116    |   0.569961    | ratio   |
| RQ5  | fedavg_run_01       | aulc_global_macro_f1                 |        8 |    0.48058     |   0.0669056   |    0.434217    |   0.526944    | ratio   |
| RQ5  | flame_blind         | aulc_global_macro_f1                 |       12 |    0.514808    |   0.0291587   |    0.49831     |   0.531306    | ratio   |
| RQ5  | flame_run_01        | aulc_global_macro_f1                 |        5 |    0.292916    |   0.0873495   |    0.21635     |   0.369481    | ratio   |
| RQ5  | krum_blind          | aulc_global_macro_f1                 |        9 |    0.467057    |   0.0393021   |    0.44138     |   0.492735    | ratio   |
| RQ5  | krum_run_01         | aulc_global_macro_f1                 |        7 |    0.0928763   |   0.0181555   |    0.0794265   |   0.106326    | ratio   |
| RQ5  | median_blind        | aulc_global_macro_f1                 |       10 |    0.540144    |   0.022937    |    0.525928    |   0.554361    | ratio   |
| RQ5  | median_run_01       | aulc_global_macro_f1                 |        7 |    0.430484    |   0.0618172   |    0.384689    |   0.476278    | ratio   |
| RQ5  | multi_krum_blind    | aulc_global_macro_f1                 |       12 |    0.533629    |   0.034316    |    0.514213    |   0.553045    | ratio   |
| RQ5  | multi_krum_run_01   | aulc_global_macro_f1                 |        6 |    0.363595    |   0.0466646   |    0.326256    |   0.400934    | ratio   |
| RQ5  | trimmed_mean_blind  | aulc_global_macro_f1                 |       10 |    0.540452    |   0.0329702   |    0.520017    |   0.560887    | ratio   |
| RQ5  | trimmed_mean_run_01 | aulc_global_macro_f1                 |        6 |    0.391244    |   0.160098    |    0.263139    |   0.519349    | ratio   |
| RQ5  | exp1                | best_global_accuracy                 |        1 |    0.5427      | nan           |  nan           | nan           | ratio   |
| RQ5  | fedavg_blind        | best_global_accuracy                 |       10 |    0.782016    |   0.0374712   |    0.758791    |   0.805241    | ratio   |
| RQ5  | fedavg_run_01       | best_global_accuracy                 |        8 |    0.674525    |   0.0559478   |    0.635755    |   0.713295    | ratio   |
| RQ5  | flame_blind         | best_global_accuracy                 |       12 |    0.743015    |   0.0495481   |    0.714981    |   0.77105     | ratio   |
| RQ5  | flame_run_01        | best_global_accuracy                 |        5 |    0.53726     |   0.0547194   |    0.489296    |   0.585224    | ratio   |
| RQ5  | krum_blind          | best_global_accuracy                 |        9 |    0.696377    |   0.0690318   |    0.651276    |   0.741477    | ratio   |
| RQ5  | krum_run_01         | best_global_accuracy                 |        7 |    0.322129    |   0.0791554   |    0.263489    |   0.380768    | ratio   |
| RQ5  | median_blind        | best_global_accuracy                 |       10 |    0.762945    |   0.047441    |    0.733541    |   0.79235     | ratio   |
| RQ5  | median_run_01       | best_global_accuracy                 |        7 |    0.625814    |   0.0751695   |    0.570128    |   0.681501    | ratio   |
| RQ5  | multi_krum_blind    | best_global_accuracy                 |       12 |    0.754779    |   0.0602966   |    0.720663    |   0.788895    | ratio   |
| RQ5  | multi_krum_run_01   | best_global_accuracy                 |        6 |    0.52965     |   0.0361995   |    0.500684    |   0.558616    | ratio   |
| RQ5  | trimmed_mean_blind  | best_global_accuracy                 |       10 |    0.755209    |   0.0594185   |    0.718381    |   0.792037    | ratio   |
| RQ5  | trimmed_mean_run_01 | best_global_accuracy                 |        6 |    0.580583    |   0.172308    |    0.442708    |   0.718458    | ratio   |
| RQ5  | exp1                | best_global_macro_f1                 |        1 |    0.456479    | nan           |  nan           | nan           | ratio   |
| RQ5  | fedavg_blind        | best_global_macro_f1                 |       10 |    0.778777    |   0.0417509   |    0.752899    |   0.804654    | ratio   |
| RQ5  | fedavg_run_01       | best_global_macro_f1                 |        8 |    0.65738     |   0.0630634   |    0.61368     |   0.701081    | ratio   |
| RQ5  | flame_blind         | best_global_macro_f1                 |       12 |    0.738555    |   0.0507152   |    0.70986     |   0.76725     | ratio   |
| RQ5  | flame_run_01        | best_global_macro_f1                 |        5 |    0.47281     |   0.07308     |    0.408752    |   0.536867    | ratio   |
| RQ5  | krum_blind          | best_global_macro_f1                 |        9 |    0.68825     |   0.0789493   |    0.63667     |   0.73983     | ratio   |
| RQ5  | krum_run_01         | best_global_macro_f1                 |        7 |    0.215914    |   0.0914574   |    0.148161    |   0.283667    | ratio   |
| RQ5  | median_blind        | best_global_macro_f1                 |       10 |    0.760313    |   0.0478773   |    0.730638    |   0.789988    | ratio   |
| RQ5  | median_run_01       | best_global_macro_f1                 |        7 |    0.603483    |   0.0859921   |    0.539779    |   0.667187    | ratio   |
| RQ5  | multi_krum_blind    | best_global_macro_f1                 |       12 |    0.750921    |   0.0639258   |    0.714752    |   0.787091    | ratio   |
| RQ5  | multi_krum_run_01   | best_global_macro_f1                 |        6 |    0.468963    |   0.0452387   |    0.432765    |   0.505162    | ratio   |
| RQ5  | trimmed_mean_blind  | best_global_macro_f1                 |       10 |    0.752717    |   0.0603424   |    0.715316    |   0.790118    | ratio   |
| RQ5  | trimmed_mean_run_01 | best_global_macro_f1                 |        6 |    0.542149    |   0.203004    |    0.379712    |   0.704586    | ratio   |
| RQ5  | exp1                | client_disconnect_count              |      242 |    0           |   0           |    0           |   0           | count   |
| RQ5  | exp1                | client_disconnect_count              |        1 |    0           | nan           |  nan           | nan           | count   |
| RQ5  | exp2                | client_disconnect_count              |       56 |    0           |   0           |    0           |   0           | count   |
| RQ5  | exp3                | client_disconnect_count              |       20 |    0           |   0           |    0           |   0           | count   |
| RQ5  | exp4                | client_disconnect_count              |       20 |    0           |   0           |    0           |   0           | count   |
| RQ5  | exp5                | client_disconnect_count              |       20 |    0           |   0           |    0           |   0           | count   |
| RQ5  | exp6                | client_disconnect_count              |        1 |    0           | nan           |  nan           | nan           | count   |
| RQ5  | exp7                | client_disconnect_count              |        1 |    0           | nan           |  nan           | nan           | count   |
| RQ5  | exp1                | client_grpc_error_count              |      242 |    0           |   0           |    0           |   0           | count   |
| RQ5  | exp1                | client_grpc_error_count              |        1 |    0           | nan           |  nan           | nan           | count   |
| RQ5  | exp2                | client_grpc_error_count              |       56 |    0           |   0           |    0           |   0           | count   |
| RQ5  | exp3                | client_grpc_error_count              |       20 |    0           |   0           |    0           |   0           | count   |
| RQ5  | exp4                | client_grpc_error_count              |       20 |    0           |   0           |    0           |   0           | count   |
| RQ5  | exp5                | client_grpc_error_count              |       20 |    0           |   0           |    0           |   0           | count   |
| RQ5  | exp6                | client_grpc_error_count              |        1 |    0           | nan           |  nan           | nan           | count   |
| RQ5  | exp7                | client_grpc_error_count              |        1 |    0           | nan           |  nan           | nan           | count   |
| RQ5  | exp1                | client_retry_count                   |      242 |    0           |   0           |    0           |   0           | count   |
| RQ5  | exp1                | client_retry_count                   |        1 |    0           | nan           |  nan           | nan           | count   |
| RQ5  | exp2                | client_retry_count                   |       56 |    0           |   0           |    0           |   0           | count   |
| RQ5  | exp3                | client_retry_count                   |       20 |    0           |   0           |    0           |   0           | count   |
| RQ5  | exp4                | client_retry_count                   |       20 |    0           |   0           |    0           |   0           | count   |
| RQ5  | exp5                | client_retry_count                   |       20 |    0           |   0           |    0           |   0           | count   |
| RQ5  | exp6                | client_retry_count                   |        1 |    0           | nan           |  nan           | nan           | count   |
| RQ5  | exp7                | client_retry_count                   |        1 |    0           | nan           |  nan           | nan           | count   |
| RQ5  | exp1                | final_client_accuracy                |       62 |    0.567581    |   0.0807483   |    0.547481    |   0.587681    | ratio   |
| RQ5  | exp2                | final_client_accuracy                |       18 |    0.597222    |   0.039676    |    0.578893    |   0.615552    | ratio   |
| RQ5  | exp1                | final_client_f1_score                |       62 |    0.551741    |   0.084706    |    0.530656    |   0.572827    | ratio   |
| RQ5  | exp2                | final_client_f1_score                |       18 |    0.582357    |   0.0477724   |    0.560287    |   0.604427    | ratio   |
| RQ5  | exp1                | final_client_loss                    |       62 |    1.2444      |   0.182277    |    1.19903     |   1.28977     | loss    |
| RQ5  | exp2                | final_client_loss                    |       18 |    1.14933     |   0.107441    |    1.0997      |   1.19897     | loss    |
| RQ5  | exp1                | final_global_accuracy                |        1 |    0.3047      | nan           |  nan           | nan           | ratio   |
| RQ5  | fedavg_blind        | final_global_accuracy                |       10 |    0.770309    |   0.0380735   |    0.746711    |   0.793907    | ratio   |
| RQ5  | fedavg_run_01       | final_global_accuracy                |        8 |    0.550687    |   0.0703508   |    0.501937    |   0.599438    | ratio   |
| RQ5  | flame_blind         | final_global_accuracy                |       12 |    0.70272     |   0.0675125   |    0.664521    |   0.740919    | ratio   |
| RQ5  | flame_run_01        | final_global_accuracy                |        5 |    0.4147      |   0.120265    |    0.309284    |   0.520116    | ratio   |
| RQ5  | krum_blind          | final_global_accuracy                |        9 |    0.618746    |   0.0795234   |    0.566791    |   0.670701    | ratio   |
| RQ5  | krum_run_01         | final_global_accuracy                |        7 |    0.192229    |   0.00523759  |    0.188349    |   0.196109    | ratio   |
| RQ5  | median_blind        | final_global_accuracy                |       10 |    0.753003    |   0.0469311   |    0.723915    |   0.782091    | ratio   |
| RQ5  | median_run_01       | final_global_accuracy                |        7 |    0.535029    |   0.0861115   |    0.471236    |   0.598821    | ratio   |
| RQ5  | multi_krum_blind    | final_global_accuracy                |       12 |    0.736172    |   0.059107    |    0.702729    |   0.769615    | ratio   |
| RQ5  | multi_krum_run_01   | final_global_accuracy                |        6 |    0.47245     |   0.0394091   |    0.440916    |   0.503984    | ratio   |
| RQ5  | trimmed_mean_blind  | final_global_accuracy                |       10 |    0.746013    |   0.0653575   |    0.705504    |   0.786522    | ratio   |
| RQ5  | trimmed_mean_run_01 | final_global_accuracy                |        6 |    0.457617    |   0.153082    |    0.335126    |   0.580108    | ratio   |
| RQ5  | exp1                | final_global_loss                    |        1 |    8.37105     | nan           |  nan           | nan           | loss    |
| RQ5  | fedavg_blind        | final_global_loss                    |       10 |    1.03257     |   0.109055    |    0.964972    |   1.10016     | loss    |
| RQ5  | fedavg_run_01       | final_global_loss                    |        8 |    4.52949     |   3.49097     |    2.11036     |   6.94861     | loss    |
| RQ5  | flame_blind         | final_global_loss                    |       12 |    1.187       |   0.290915    |    1.0224      |   1.3516      | loss    |
| RQ5  | flame_run_01        | final_global_loss                    |        5 |    6.37285     |   3.46199     |    3.33828     |   9.40741     | loss    |
| RQ5  | krum_blind          | final_global_loss                    |        9 |    1.87917     |   0.817938    |    1.34479     |   2.41356     | loss    |
| RQ5  | krum_run_01         | final_global_loss                    |        7 |   22.4089      |   8.66539     |   15.9895      |  28.8283      | loss    |
| RQ5  | median_blind        | final_global_loss                    |       10 |    1.05208     |   0.171608    |    0.945721    |   1.15845     | loss    |
| RQ5  | median_run_01       | final_global_loss                    |        7 |    3.93133     |   2.44642     |    2.119       |   5.74367     | loss    |
| RQ5  | multi_krum_blind    | final_global_loss                    |       12 |    1.24519     |   0.218863    |    1.12135     |   1.36902     | loss    |
| RQ5  | multi_krum_run_01   | final_global_loss                    |        6 |   27.4877      |  32.0919      |    1.8088      |  53.1666      | loss    |
| RQ5  | trimmed_mean_blind  | final_global_loss                    |       10 |    1.15078     |   0.28254     |    0.975662    |   1.3259      | loss    |
| RQ5  | trimmed_mean_run_01 | final_global_loss                    |        6 |    5.27955     |   2.88572     |    2.97049     |   7.5886      | loss    |
| RQ5  | exp1                | final_global_macro_f1                |        1 |    0.227451    | nan           |  nan           | nan           | ratio   |
| RQ5  | fedavg_blind        | final_global_macro_f1                |       10 |    0.767927    |   0.0406649   |    0.742723    |   0.793132    | ratio   |
| RQ5  | fedavg_run_01       | final_global_macro_f1                |        8 |    0.494311    |   0.0929442   |    0.429904    |   0.558718    | ratio   |
| RQ5  | flame_blind         | final_global_macro_f1                |       12 |    0.697448    |   0.0704512   |    0.657587    |   0.73731     | ratio   |
| RQ5  | flame_run_01        | final_global_macro_f1                |        5 |    0.319127    |   0.125167    |    0.209413    |   0.428841    | ratio   |
| RQ5  | krum_blind          | final_global_macro_f1                |        9 |    0.611937    |   0.0800711   |    0.559624    |   0.66425     | ratio   |
| RQ5  | krum_run_01         | final_global_macro_f1                |        7 |    0.066913    |   0.00296235  |    0.0647184   |   0.0691075   | ratio   |
| RQ5  | median_blind        | final_global_macro_f1                |       10 |    0.751327    |   0.0470886   |    0.722142    |   0.780513    | ratio   |
| RQ5  | median_run_01       | final_global_macro_f1                |        7 |    0.485321    |   0.0943738   |    0.415408    |   0.555234    | ratio   |
| RQ5  | multi_krum_blind    | final_global_macro_f1                |       12 |    0.733709    |   0.0621407   |    0.69855     |   0.768868    | ratio   |
| RQ5  | multi_krum_run_01   | final_global_macro_f1                |        6 |    0.381185    |   0.0559114   |    0.336447    |   0.425923    | ratio   |
| RQ5  | trimmed_mean_blind  | final_global_macro_f1                |       10 |    0.744828    |   0.0656601   |    0.704131    |   0.785524    | ratio   |
| RQ5  | trimmed_mean_run_01 | final_global_macro_f1                |        6 |    0.390413    |   0.185849    |    0.241703    |   0.539123    | ratio   |
| RQ5  | exp1                | mean_analyzer_cpu_percent            |       87 |   61.9704      |  24.2869      |   56.8669      |  67.0739      | percent |
| RQ5  | exp1                | mean_analyzer_cpu_percent            |        1 |   88.6482      | nan           |  nan           | nan           | percent |
| RQ5  | exp1                | mean_analyzer_cpu_percent            |        1 |   77.049       | nan           |  nan           | nan           | percent |
| RQ5  | exp1                | mean_analyzer_cpu_percent            |        1 |   33.2164      | nan           |  nan           | nan           | percent |
| RQ5  | exp1                | mean_analyzer_cpu_percent            |        1 |   89.703       | nan           |  nan           | nan           | percent |
| RQ5  | exp1                | mean_analyzer_cpu_percent            |        1 |   81.7177      | nan           |  nan           | nan           | percent |
| RQ5  | exp1                | mean_analyzer_cpu_percent            |        1 |   89.2118      | nan           |  nan           | nan           | percent |
| RQ5  | exp1                | mean_analyzer_cpu_percent            |        1 |   81.3863      | nan           |  nan           | nan           | percent |
| RQ5  | exp1                | mean_analyzer_cpu_percent            |        1 |   81.5357      | nan           |  nan           | nan           | percent |
| RQ5  | exp1                | mean_analyzer_cpu_percent            |        1 |   80.9449      | nan           |  nan           | nan           | percent |
| RQ5  | exp1                | mean_analyzer_cpu_percent            |        1 |   79.4881      | nan           |  nan           | nan           | percent |
| RQ5  | exp1                | mean_analyzer_cpu_percent            |        1 |   89.7112      | nan           |  nan           | nan           | percent |
| RQ5  | exp1                | mean_analyzer_cpu_percent            |        1 |   82.5382      | nan           |  nan           | nan           | percent |
| RQ5  | exp2                | mean_analyzer_cpu_percent            |       15 |   66.4051      |  25.2511      |   53.6262      |  79.1839      | percent |
| RQ5  | exp2                | mean_analyzer_cpu_percent            |        1 |   89.8712      | nan           |  nan           | nan           | percent |
| RQ5  | exp2                | mean_analyzer_cpu_percent            |        1 |   88.6273      | nan           |  nan           | nan           | percent |
| RQ5  | exp2                | mean_analyzer_cpu_percent            |        1 |   89.2231      | nan           |  nan           | nan           | percent |
| RQ5  | exp2                | mean_analyzer_cpu_percent            |        1 |   93.4458      | nan           |  nan           | nan           | percent |
| RQ5  | exp3                | mean_analyzer_cpu_percent            |        6 |   36.6383      |   1.24358     |   35.6432      |  37.6334      | percent |
| RQ5  | exp4                | mean_analyzer_cpu_percent            |        6 |   40.5152      |   6.73189     |   35.1286      |  45.9018      | percent |
| RQ5  | exp5                | mean_analyzer_cpu_percent            |        6 |   36.8854      |   2.38475     |   34.9772      |  38.7936      | percent |
| RQ5  | exp1                | mean_analyzer_decision_lag_ms        |       72 |  238.849       | 176.109       |  198.17        | 279.528       | ms      |
| RQ5  | exp1                | mean_analyzer_decision_lag_ms        |        1 |  503.557       | nan           |  nan           | nan           | ms      |
| RQ5  | exp1                | mean_analyzer_decision_lag_ms        |        1 |   27.5284      | nan           |  nan           | nan           | ms      |
| RQ5  | exp1                | mean_analyzer_decision_lag_ms        |        1 |  625.06        | nan           |  nan           | nan           | ms      |
| RQ5  | exp1                | mean_analyzer_decision_lag_ms        |        1 |  261.806       | nan           |  nan           | nan           | ms      |
| RQ5  | exp1                | mean_analyzer_decision_lag_ms        |        1 |  255.796       | nan           |  nan           | nan           | ms      |
| RQ5  | exp1                | mean_analyzer_decision_lag_ms        |        1 |  246.394       | nan           |  nan           | nan           | ms      |
| RQ5  | exp1                | mean_analyzer_decision_lag_ms        |        1 |  325.428       | nan           |  nan           | nan           | ms      |
| RQ5  | exp1                | mean_analyzer_decision_lag_ms        |        1 |  341.438       | nan           |  nan           | nan           | ms      |
| RQ5  | exp2                | mean_analyzer_decision_lag_ms        |        2 |  351.739       |  84.3387      |  234.852       | 468.626       | ms      |
| RQ5  | exp1                | mean_client_evaluation_duration_s    |       62 |    0.0751535   |   0.0523538   |    0.0621216   |   0.0881855   | s       |
| RQ5  | exp2                | mean_client_evaluation_duration_s    |       18 |    0.0761948   |   0.0522031   |    0.0520782   |   0.100311    | s       |
| RQ5  | exp1                | mean_client_fit_duration_s           |       62 |    2.14364     |   1.66485     |    1.72923     |   2.55805     | s       |
| RQ5  | exp2                | mean_client_fit_duration_s           |       18 |    2.17889     |   1.65102     |    1.41616     |   2.94162     | s       |
| RQ5  | exp1                | mean_client_train_duration_s         |       62 |    2.04587     |   1.59903     |    1.64784     |   2.4439      | s       |
| RQ5  | exp2                | mean_client_train_duration_s         |       18 |    2.08017     |   1.58544     |    1.34773     |   2.81261     | s       |
| RQ5  | exp1                | mean_proxy_process_cpu_percent       |        2 |    8.27919     |   1.60062     |    6.06084     |  10.4975      | percent |
| RQ5  | exp1                | mean_proxy_process_cpu_percent       |        3 |    5.36976     |   3.48792     |    1.42281     |   9.31671     | percent |
| RQ5  | exp1                | mean_proxy_process_cpu_percent       |        3 |    4.96127     |   4.08779     |    0.335498    |   9.58705     | percent |
| RQ5  | exp1                | mean_proxy_process_cpu_percent       |        4 |    4.90118     |   3.0997      |    1.86348     |   7.93888     | percent |
| RQ5  | exp1                | mean_proxy_process_cpu_percent       |        2 |    5.9523      |   1.29185     |    4.16188     |   7.74271     | percent |
| RQ5  | exp1                | mean_proxy_process_cpu_percent       |        1 |    0.938211    | nan           |  nan           | nan           | percent |
| RQ5  | exp1                | mean_proxy_process_cpu_percent       |        2 |    6.22188     |   1.90165     |    3.58633     |   8.85743     | percent |
| RQ5  | exp1                | mean_proxy_process_cpu_percent       |        4 |    2.75006     |   2.29293     |    0.502991    |   4.99713     | percent |
| RQ5  | exp1                | mean_proxy_process_cpu_percent       |        2 |    3.30004     |   1.9697      |    0.570168    |   6.02991     | percent |
| RQ5  | exp1                | mean_proxy_process_cpu_percent       |        2 |    4.17377     |   2.918       |    0.129626    |   8.21791     | percent |
| RQ5  | exp1                | mean_proxy_process_cpu_percent       |        1 |    0.603535    | nan           |  nan           | nan           | percent |
| RQ5  | exp1                | mean_proxy_process_cpu_percent       |        1 |    1.56438     | nan           |  nan           | nan           | percent |
| RQ5  | exp1                | mean_proxy_process_cpu_percent       |        2 |    7.53632     |   1.48483     |    5.47845     |   9.59418     | percent |
| RQ5  | exp1                | mean_proxy_process_cpu_percent       |        2 |    8.4559      |   1.50492     |    6.37019     |  10.5416      | percent |
| RQ5  | exp1                | mean_proxy_process_cpu_percent       |        3 |    3.94489     |   2.95252     |    0.603791    |   7.28598     | percent |
| RQ5  | exp1                | mean_proxy_process_cpu_percent       |        2 |    4.36149     |   4.61081     |   -2.02877     |  10.7517      | percent |
| RQ5  | exp1                | mean_proxy_process_cpu_percent       |        3 |    4.95982     |   3.42731     |    1.08146     |   8.83819     | percent |
| RQ5  | exp1                | mean_proxy_process_cpu_percent       |        3 |    5.63802     |   3.58101     |    1.58573     |   9.69031     | percent |
| RQ5  | exp1                | mean_proxy_process_cpu_percent       |        2 |    3.9278      |   4.60142     |   -2.44944     |  10.305       | percent |
| RQ5  | exp1                | mean_proxy_process_cpu_percent       |        2 |    5.80602     |   1.74082     |    3.39337     |   8.21868     | percent |
| RQ5  | exp1                | mean_proxy_process_cpu_percent       |        3 |    4.70497     |   3.22548     |    1.05499     |   8.35494     | percent |
| RQ5  | exp1                | mean_proxy_process_cpu_percent       |        3 |    4.48493     |   2.67839     |    1.45405     |   7.51581     | percent |
| RQ5  | exp1                | mean_proxy_process_cpu_percent       |        3 |    5.29191     |   3.7385      |    1.0614      |   9.52242     | percent |
| RQ5  | exp1                | mean_proxy_process_cpu_percent       |        4 |    5.47954     |   3.06684     |    2.47404     |   8.48504     | percent |
| RQ5  | exp1                | mean_proxy_process_cpu_percent       |        1 |    6.61516     | nan           |  nan           | nan           | percent |
| RQ5  | exp1                | mean_proxy_process_cpu_percent       |        3 |    4.85784     |   3.71125     |    0.65816     |   9.05751     | percent |
| RQ5  | exp1                | mean_proxy_process_cpu_percent       |        3 |    4.3006      |   2.83481     |    1.09272     |   7.50849     | percent |
| RQ5  | exp1                | mean_proxy_process_cpu_percent       |        2 |    3.8525      |   3.75455     |   -1.35104     |   9.05603     | percent |
| RQ5  | exp1                | mean_proxy_process_cpu_percent       |        2 |    5.05069     |   2.3396      |    1.80818     |   8.29321     | percent |
| RQ5  | exp1                | mean_proxy_process_cpu_percent       |        3 |    3.00163     |   2.18412     |    0.530069    |   5.4732      | percent |
| RQ5  | exp1                | mean_proxy_process_cpu_percent       |        2 |    2.94854     |   2.46703     |   -0.470595    |   6.36767     | percent |
| RQ5  | exp1                | mean_proxy_process_cpu_percent       |        3 |    4.34331     |   2.80771     |    1.16608     |   7.52053     | percent |
| RQ5  | exp2                | mean_proxy_process_cpu_percent       |        1 |    7.59647     | nan           |  nan           | nan           | percent |
| RQ5  | exp2                | mean_proxy_process_cpu_percent       |        1 |    4.31699     | nan           |  nan           | nan           | percent |
| RQ5  | exp1                | mean_proxy_rss_mb                    |        2 |  356.313       |  75.7712      |  251.3         | 461.327       | MB      |
| RQ5  | exp1                | mean_proxy_rss_mb                    |        3 |  254.845       | 175.346       |   56.4224      | 453.268       | MB      |
| RQ5  | exp1                | mean_proxy_rss_mb                    |        3 |  262.003       | 179.984       |   58.3315      | 465.674       | MB      |
| RQ5  | exp1                | mean_proxy_rss_mb                    |        4 |  277.951       | 156.934       |  124.155       | 431.746       | MB      |
| RQ5  | exp1                | mean_proxy_rss_mb                    |        2 |  356.17        |  78.9113      |  246.804       | 465.535       | MB      |
| RQ5  | exp1                | mean_proxy_rss_mb                    |        1 |   57.9824      | nan           |  nan           | nan           | MB      |
| RQ5  | exp1                | mean_proxy_rss_mb                    |        2 |  352.969       |  68.3688      |  258.215       | 447.724       | MB      |
| RQ5  | exp1                | mean_proxy_rss_mb                    |        4 |  124.778       | 124.284       |    2.98007     | 246.577       | MB      |
| RQ5  | exp1                | mean_proxy_rss_mb                    |        2 |  193.892       | 183.853       |  -60.9157      | 448.699       | MB      |
| RQ5  | exp1                | mean_proxy_rss_mb                    |        2 |  199.141       | 188.283       |  -61.8058      | 460.087       | MB      |
| RQ5  | exp1                | mean_proxy_rss_mb                    |        1 |   56.5432      | nan           |  nan           | nan           | MB      |
| RQ5  | exp1                | mean_proxy_rss_mb                    |        1 |   62.6325      | nan           |  nan           | nan           | MB      |
| RQ5  | exp1                | mean_proxy_rss_mb                    |        2 |  352.651       |  71.2142      |  253.953       | 451.349       | MB      |
| RQ5  | exp1                | mean_proxy_rss_mb                    |        2 |  371.187       |  80.0958      |  260.18        | 482.194       | MB      |
| RQ5  | exp1                | mean_proxy_rss_mb                    |        3 |  284.129       | 198.563       |   59.4343      | 508.824       | MB      |
| RQ5  | exp1                | mean_proxy_rss_mb                    |        2 |  250.029       | 268.608       | -122.242       | 622.3         | MB      |
| RQ5  | exp1                | mean_proxy_rss_mb                    |        3 |  266.157       | 186.235       |   55.4132      | 476.902       | MB      |
| RQ5  | exp1                | mean_proxy_rss_mb                    |        3 |  257.102       | 173.296       |   60.9995      | 453.205       | MB      |
| RQ5  | exp1                | mean_proxy_rss_mb                    |        2 |  174.756       | 168.173       |  -58.3198      | 407.831       | MB      |
| RQ5  | exp1                | mean_proxy_rss_mb                    |        2 |  320.823       | 116.364       |  159.551       | 482.096       | MB      |
| RQ5  | exp1                | mean_proxy_rss_mb                    |        3 |  274.256       | 193.888       |   54.8514      | 493.661       | MB      |
| RQ5  | exp1                | mean_proxy_rss_mb                    |        3 |  264.025       | 173.998       |   67.1271      | 460.922       | MB      |
| RQ5  | exp1                | mean_proxy_rss_mb                    |        3 |  247.74        | 168.594       |   56.9578      | 438.523       | MB      |
| RQ5  | exp1                | mean_proxy_rss_mb                    |        4 |  285.558       | 157.122       |  131.578       | 439.537       | MB      |
| RQ5  | exp1                | mean_proxy_rss_mb                    |        1 |  414.376       | nan           |  nan           | nan           | MB      |
| RQ5  | exp1                | mean_proxy_rss_mb                    |        3 |  250.253       | 168.121       |   60.0057      | 440.5         | MB      |
| RQ5  | exp1                | mean_proxy_rss_mb                    |        3 |  275.889       | 193.663       |   56.7385      | 495.04        | MB      |
| RQ5  | exp1                | mean_proxy_rss_mb                    |        2 |  183.679       | 173.82        |  -57.2226      | 424.581       | MB      |
| RQ5  | exp1                | mean_proxy_rss_mb                    |        2 |  180.648       | 170.139       |  -55.1531      | 416.448       | MB      |
| RQ5  | exp1                | mean_proxy_rss_mb                    |        3 |  257.311       | 178.509       |   55.3082      | 459.313       | MB      |
| RQ5  | exp1                | mean_proxy_rss_mb                    |        2 |  257.026       | 277.284       | -127.271       | 641.322       | MB      |
| RQ5  | exp1                | mean_proxy_rss_mb                    |        3 |  275.477       | 194.144       |   55.7831      | 495.172       | MB      |
| RQ5  | exp2                | mean_proxy_rss_mb                    |        1 |  410.777       | nan           |  nan           | nan           | MB      |
| RQ5  | exp2                | mean_proxy_rss_mb                    |        1 |  304.053       | nan           |  nan           | nan           | MB      |
| RQ5  | exp1                | mean_server_aggregation_duration_s   |        1 |    0.0181029   | nan           |  nan           | nan           | s       |
| RQ5  | fedavg_blind        | mean_server_aggregation_duration_s   |       10 |    0.0017632   |   0.000190024 |    0.00164542  |   0.00188098  | s       |
| RQ5  | fedavg_run_01       | mean_server_aggregation_duration_s   |        8 |    0.00794357  |   0.000132104 |    0.00785203  |   0.00803511  | s       |
| RQ5  | flame_blind         | mean_server_aggregation_duration_s   |       12 |    0.00284429  |   0.00037027  |    0.00263479  |   0.00305379  | s       |
| RQ5  | flame_run_01        | mean_server_aggregation_duration_s   |        5 |    0.0176335   |   0.000263846 |    0.0174023   |   0.0178648   | s       |
| RQ5  | krum_blind          | mean_server_aggregation_duration_s   |        9 |    0.00210629  |   0.000201997 |    0.00197432  |   0.00223826  | s       |
| RQ5  | krum_run_01         | mean_server_aggregation_duration_s   |        7 |    0.00957677  |   9.4577e-05  |    0.0095067   |   0.00964683  | s       |
| RQ5  | median_blind        | mean_server_aggregation_duration_s   |       10 |    0.00304266  |   0.000150045 |    0.00294966  |   0.00313566  | s       |
| RQ5  | median_run_01       | mean_server_aggregation_duration_s   |        7 |    0.0392159   |   0.000462775 |    0.0388731   |   0.0395587   | s       |
| RQ5  | multi_krum_blind    | mean_server_aggregation_duration_s   |       12 |    0.00192906  |   0.000411762 |    0.00169608  |   0.00216204  | s       |
| RQ5  | multi_krum_run_01   | mean_server_aggregation_duration_s   |        6 |    0.0106296   |   0.000102914 |    0.0105473   |   0.010712    | s       |
| RQ5  | trimmed_mean_blind  | mean_server_aggregation_duration_s   |       10 |    0.00281848  |   0.000274508 |    0.00264834  |   0.00298862  | s       |
| RQ5  | trimmed_mean_run_01 | mean_server_aggregation_duration_s   |        6 |    0.0271106   |   0.00049503  |    0.0267145   |   0.0275067   | s       |
| RQ5  | exp1                | mean_server_evaluation_duration_s    |        1 |    1.31134     | nan           |  nan           | nan           | s       |
| RQ5  | fedavg_blind        | mean_server_evaluation_duration_s    |       10 |    0.280165    |   0.0304026   |    0.261322    |   0.299009    | s       |
| RQ5  | fedavg_run_01       | mean_server_evaluation_duration_s    |        8 |    1.32418     |   0.00933554  |    1.31771     |   1.33065     | s       |
| RQ5  | flame_blind         | mean_server_evaluation_duration_s    |       12 |    0.267698    |   0.00404711  |    0.265408    |   0.269988    | s       |
| RQ5  | flame_run_01        | mean_server_evaluation_duration_s    |        5 |    1.32485     |   0.0175146   |    1.3095      |   1.3402      | s       |
| RQ5  | krum_blind          | mean_server_evaluation_duration_s    |        9 |    0.266916    |   0.00300286  |    0.264955    |   0.268878    | s       |
| RQ5  | krum_run_01         | mean_server_evaluation_duration_s    |        7 |    1.32385     |   0.00501886  |    1.32013     |   1.32757     | s       |
| RQ5  | median_blind        | mean_server_evaluation_duration_s    |       10 |    0.27074     |   0.0100952   |    0.264483    |   0.276997    | s       |
| RQ5  | median_run_01       | mean_server_evaluation_duration_s    |        7 |    1.32524     |   0.0101712   |    1.3177      |   1.33277     | s       |
| RQ5  | multi_krum_blind    | mean_server_evaluation_duration_s    |       12 |    0.26749     |   0.00286405  |    0.265869    |   0.26911     | s       |
| RQ5  | multi_krum_run_01   | mean_server_evaluation_duration_s    |        6 |    1.32877     |   0.0171131   |    1.31507     |   1.34246     | s       |
| RQ5  | trimmed_mean_blind  | mean_server_evaluation_duration_s    |       10 |    0.272599    |   0.0125167   |    0.264841    |   0.280357    | s       |
| RQ5  | trimmed_mean_run_01 | mean_server_evaluation_duration_s    |        6 |    1.31849     |   0.013714    |    1.30751     |   1.32946     | s       |
| RQ5  | exp1                | mean_server_phase_duration_s         |        1 |    2.29711     | nan           |  nan           | nan           | s       |
| RQ5  | fedavg_blind        | mean_server_phase_duration_s         |       10 |    0.305765    |   0.0303626   |    0.286946    |   0.324584    | s       |
| RQ5  | fedavg_run_01       | mean_server_phase_duration_s         |        8 |    2.30255     |   0.0114624   |    2.29461     |   2.31049     | s       |
| RQ5  | flame_blind         | mean_server_phase_duration_s         |       12 |    0.294273    |   0.00379399  |    0.292126    |   0.296419    | s       |
| RQ5  | flame_run_01        | mean_server_phase_duration_s         |        5 |    2.29911     |   0.0154159   |    2.2856      |   2.31262     | s       |
| RQ5  | krum_blind          | mean_server_phase_duration_s         |        9 |    0.292349    |   0.00308976  |    0.290331    |   0.294368    | s       |
| RQ5  | krum_run_01         | mean_server_phase_duration_s         |        7 |    2.22097     |   0.0351734   |    2.19491     |   2.24703     | s       |
| RQ5  | median_blind        | mean_server_phase_duration_s         |       10 |    0.297168    |   0.0101724   |    0.290863    |   0.303473    | s       |
| RQ5  | median_run_01       | mean_server_phase_duration_s         |        7 |    2.31194     |   0.0101102   |    2.30445     |   2.31943     | s       |
| RQ5  | multi_krum_blind    | mean_server_phase_duration_s         |       12 |    0.293014    |   0.00288201  |    0.291383    |   0.294645    | s       |
| RQ5  | multi_krum_run_01   | mean_server_phase_duration_s         |        6 |    2.29585     |   0.0152866   |    2.28362     |   2.30809     | s       |
| RQ5  | trimmed_mean_blind  | mean_server_phase_duration_s         |       10 |    0.299444    |   0.012616    |    0.291625    |   0.307264    | s       |
| RQ5  | trimmed_mean_run_01 | mean_server_phase_duration_s         |        6 |    2.29513     |   0.00953274  |    2.2875      |   2.30276     | s       |
| RQ5  | exp1                | minimum_global_loss                  |        1 |    1.56305     | nan           |  nan           | nan           | loss    |
| RQ5  | fedavg_blind        | minimum_global_loss                  |       10 |    0.93399     |   0.0736848   |    0.888319    |   0.97966     | loss    |
| RQ5  | fedavg_run_01       | minimum_global_loss                  |        8 |    1.02476     |   0.136325    |    0.930296    |   1.11923     | loss    |
| RQ5  | flame_blind         | minimum_global_loss                  |       12 |    0.995291    |   0.161323    |    0.904014    |   1.08657     | loss    |
| RQ5  | flame_run_01        | minimum_global_loss                  |        5 |    1.71276     |   0.458428    |    1.31093     |   2.11459     | loss    |
| RQ5  | krum_blind          | minimum_global_loss                  |        9 |    1.11654     |   0.108381    |    1.04573     |   1.18734     | loss    |
| RQ5  | krum_run_01         | minimum_global_loss                  |        7 |    2.65585     |   0.862804    |    2.01668     |   3.29502     | loss    |
| RQ5  | median_blind        | minimum_global_loss                  |       10 |    0.965465    |   0.0951992   |    0.90646     |   1.02447     | loss    |
| RQ5  | median_run_01       | minimum_global_loss                  |        7 |    1.2343      |   0.226405    |    1.06658     |   1.40203     | loss    |
| RQ5  | multi_krum_blind    | minimum_global_loss                  |       12 |    0.984742    |   0.133722    |    0.909082    |   1.0604      | loss    |
| RQ5  | multi_krum_run_01   | minimum_global_loss                  |        6 |    2.37428     |   0.0794137   |    2.31074     |   2.43783     | loss    |
| RQ5  | trimmed_mean_blind  | minimum_global_loss                  |       10 |    1.01069     |   0.175685    |    0.9018      |   1.11958     | loss    |
| RQ5  | trimmed_mean_run_01 | minimum_global_loss                  |        6 |    1.36053     |   0.599824    |    0.880576    |   1.84049     | loss    |
| RQ5  | exp1                | p95_analyzer_decision_lag_ms         |       72 |  451.455       | 278.812       |  387.053       | 515.857       | ms      |
| RQ5  | exp1                | p95_analyzer_decision_lag_ms         |        1 |  860.333       | nan           |  nan           | nan           | ms      |
| RQ5  | exp1                | p95_analyzer_decision_lag_ms         |        1 |   96.2795      | nan           |  nan           | nan           | ms      |
| RQ5  | exp1                | p95_analyzer_decision_lag_ms         |        1 | 1216.47        | nan           |  nan           | nan           | ms      |
| RQ5  | exp1                | p95_analyzer_decision_lag_ms         |        1 |  692.248       | nan           |  nan           | nan           | ms      |
| RQ5  | exp1                | p95_analyzer_decision_lag_ms         |        1 |  627.082       | nan           |  nan           | nan           | ms      |
| RQ5  | exp1                | p95_analyzer_decision_lag_ms         |        1 |  610.637       | nan           |  nan           | nan           | ms      |
| RQ5  | exp1                | p95_analyzer_decision_lag_ms         |        1 |  645.3         | nan           |  nan           | nan           | ms      |
| RQ5  | exp1                | p95_analyzer_decision_lag_ms         |        1 |  812.762       | nan           |  nan           | nan           | ms      |
| RQ5  | exp2                | p95_analyzer_decision_lag_ms         |        2 |  625.491       |  22.415       |  594.426       | 656.557       | ms      |
| RQ5  | exp1                | p95_analyzer_rss_mb                  |       87 |   53.5779      |   0.156755    |   53.545       |  53.6108      | MB      |
| RQ5  | exp1                | p95_analyzer_rss_mb                  |        1 |   53.7266      | nan           |  nan           | nan           | MB      |
| RQ5  | exp1                | p95_analyzer_rss_mb                  |        1 |   53.668       | nan           |  nan           | nan           | MB      |
| RQ5  | exp1                | p95_analyzer_rss_mb                  |        1 |   53.5273      | nan           |  nan           | nan           | MB      |
| RQ5  | exp1                | p95_analyzer_rss_mb                  |        1 |   53.8789      | nan           |  nan           | nan           | MB      |
| RQ5  | exp1                | p95_analyzer_rss_mb                  |        1 |   53.6562      | nan           |  nan           | nan           | MB      |
| RQ5  | exp1                | p95_analyzer_rss_mb                  |        1 |   53.6992      | nan           |  nan           | nan           | MB      |
| RQ5  | exp1                | p95_analyzer_rss_mb                  |        1 |   53.8203      | nan           |  nan           | nan           | MB      |
| RQ5  | exp1                | p95_analyzer_rss_mb                  |        1 |   53.832       | nan           |  nan           | nan           | MB      |
| RQ5  | exp1                | p95_analyzer_rss_mb                  |        1 |   53.7383      | nan           |  nan           | nan           | MB      |
| RQ5  | exp1                | p95_analyzer_rss_mb                  |        1 |   53.8281      | nan           |  nan           | nan           | MB      |
| RQ5  | exp1                | p95_analyzer_rss_mb                  |        1 |   53.6875      | nan           |  nan           | nan           | MB      |
| RQ5  | exp1                | p95_analyzer_rss_mb                  |        1 |   53.7109      | nan           |  nan           | nan           | MB      |
| RQ5  | exp2                | p95_analyzer_rss_mb                  |       15 |   53.4604      |   0.179225    |   53.3697      |  53.5511      | MB      |
| RQ5  | exp2                | p95_analyzer_rss_mb                  |        1 |   53.7852      | nan           |  nan           | nan           | MB      |
| RQ5  | exp2                | p95_analyzer_rss_mb                  |        1 |   53.7188      | nan           |  nan           | nan           | MB      |
| RQ5  | exp2                | p95_analyzer_rss_mb                  |        1 |   53.8164      | nan           |  nan           | nan           | MB      |
| RQ5  | exp2                | p95_analyzer_rss_mb                  |        1 |   53.7578      | nan           |  nan           | nan           | MB      |
| RQ5  | exp3                | p95_analyzer_rss_mb                  |        6 |   53.4251      |   0.0874657   |   53.3551      |  53.4951      | MB      |
| RQ5  | exp4                | p95_analyzer_rss_mb                  |        6 |   53.3659      |   0.0722674   |   53.3081      |  53.4237      | MB      |
| RQ5  | exp5                | p95_analyzer_rss_mb                  |        6 |   53.321       |   0.0638247   |   53.2699      |  53.372       | MB      |
| RQ5  | exp1                | p95_proxy_process_cpu_percent        |        2 |   34.65        |   4.73762     |   28.084       |  41.216       | percent |
| RQ5  | exp1                | p95_proxy_process_cpu_percent        |        3 |   20.1         |  14.0082      |    4.24822     |  35.9518      | percent |
| RQ5  | exp1                | p95_proxy_process_cpu_percent        |        3 |   18.3167      |  14.5482      |    1.8538      |  34.7795      | percent |
| RQ5  | exp1                | p95_proxy_process_cpu_percent        |        4 |   16.25        |  10.4043      |    6.05376     |  26.4462      | percent |
| RQ5  | exp1                | p95_proxy_process_cpu_percent        |        2 |   19.575       |   0.601041    |   18.742       |  20.408       | percent |
| RQ5  | exp1                | p95_proxy_process_cpu_percent        |        1 |    4           | nan           |  nan           | nan           | percent |
| RQ5  | exp1                | p95_proxy_process_cpu_percent        |        2 |   29.775       |   5.97505     |   21.494       |  38.056       | percent |
| RQ5  | exp1                | p95_proxy_process_cpu_percent        |        4 |    9.75        |   9.53502     |    0.405677    |  19.0943      | percent |
| RQ5  | exp1                | p95_proxy_process_cpu_percent        |        2 |   13.4         |  11.8794      |   -3.064       |  29.864       | percent |
| RQ5  | exp1                | p95_proxy_process_cpu_percent        |        2 |   14.5         |  12.0208      |   -2.16        |  31.16        | percent |
| RQ5  | exp1                | p95_proxy_process_cpu_percent        |        1 |    3           | nan           |  nan           | nan           | percent |
| RQ5  | exp1                | p95_proxy_process_cpu_percent        |        1 |    5           | nan           |  nan           | nan           | percent |
| RQ5  | exp1                | p95_proxy_process_cpu_percent        |        2 |   30.5         |   4.94975     |   23.64        |  37.36        | percent |
| RQ5  | exp1                | p95_proxy_process_cpu_percent        |        2 |   31.5325      |  11.8546      |   15.1028      |  47.9622      | percent |
| RQ5  | exp1                | p95_proxy_process_cpu_percent        |        3 |   16.6867      |  12.3505      |    2.71077     |  30.6626      | percent |
| RQ5  | exp1                | p95_proxy_process_cpu_percent        |        2 |   15.875       |  16.7938      |   -7.4         |  39.15        | percent |
| RQ5  | exp1                | p95_proxy_process_cpu_percent        |        3 |   16.6667      |  11.3725      |    3.79749     |  29.5358      | percent |
| RQ5  | exp1                | p95_proxy_process_cpu_percent        |        3 |   21.85        |  15.2058      |    4.64297     |  39.057       | percent |
| RQ5  | exp1                | p95_proxy_process_cpu_percent        |        2 |   13.5         |  14.8492      |   -7.08        |  34.08        | percent |
| RQ5  | exp1                | p95_proxy_process_cpu_percent        |        2 |   26.45        |   7.70746     |   15.768       |  37.132       | percent |
| RQ5  | exp1                | p95_proxy_process_cpu_percent        |        3 |   16.35        |  10.9894      |    3.91429     |  28.7857      | percent |
| RQ5  | exp1                | p95_proxy_process_cpu_percent        |        3 |   13.7         |   9.23418     |    3.25055     |  24.1495      | percent |
| RQ5  | exp1                | p95_proxy_process_cpu_percent        |        3 |   20.3333      |  14.2244      |    4.23692     |  36.4297      | percent |
| RQ5  | exp1                | p95_proxy_process_cpu_percent        |        4 |   21.7625      |  14.7261      |    7.33089     |  36.1941      | percent |
| RQ5  | exp1                | p95_proxy_process_cpu_percent        |        1 |   27           | nan           |  nan           | nan           | percent |
| RQ5  | exp1                | p95_proxy_process_cpu_percent        |        3 |   17.6667      |  13.3167      |    2.59745     |  32.7359      | percent |
| RQ5  | exp1                | p95_proxy_process_cpu_percent        |        3 |   16.1667      |  10.7742      |    3.97451     |  28.3588      | percent |
| RQ5  | exp1                | p95_proxy_process_cpu_percent        |        2 |   14.4         |  14.7078      |   -5.984       |  34.784       | percent |
| RQ5  | exp1                | p95_proxy_process_cpu_percent        |        2 |   15.4         |  16.122       |   -6.944       |  37.744       | percent |
| RQ5  | exp1                | p95_proxy_process_cpu_percent        |        3 |   12.2333      |   8.0102      |    3.16894     |  21.2977      | percent |
| RQ5  | exp1                | p95_proxy_process_cpu_percent        |        2 |   11.5         |  10.6066      |   -3.2         |  26.2         | percent |
| RQ5  | exp1                | p95_proxy_process_cpu_percent        |        3 |   15.8333      |  10.3963      |    4.0688      |  27.5979      | percent |
| RQ5  | exp2                | p95_proxy_process_cpu_percent        |        1 |   38           | nan           |  nan           | nan           | percent |
| RQ5  | exp2                | p95_proxy_process_cpu_percent        |        1 |   18           | nan           |  nan           | nan           | percent |
| RQ5  | exp1                | p95_proxy_rss_mb                     |        2 |  415.4         | 104.947       |  269.951       | 560.85        | MB      |
| RQ5  | exp1                | p95_proxy_rss_mb                     |        3 |  292.52        | 198.625       |   67.7547      | 517.284       | MB      |
| RQ5  | exp1                | p95_proxy_rss_mb                     |        3 |  320.44        | 229.302       |   60.9606      | 579.92        | MB      |
| RQ5  | exp1                | p95_proxy_rss_mb                     |        4 |  329.865       | 184.248       |  149.303       | 510.428       | MB      |
| RQ5  | exp1                | p95_proxy_rss_mb                     |        2 |  418.502       |  69.5699      |  322.083       | 514.921       | MB      |
| RQ5  | exp1                | p95_proxy_rss_mb                     |        1 |   70.9727      | nan           |  nan           | nan           | MB      |
| RQ5  | exp1                | p95_proxy_rss_mb                     |        2 |  398.45        |  81.4454      |  285.572       | 511.328       | MB      |
| RQ5  | exp1                | p95_proxy_rss_mb                     |        4 |  147.244       | 151.04        |   -0.775044    | 295.264       | MB      |
| RQ5  | exp1                | p95_proxy_rss_mb                     |        2 |  223.842       | 215.007       |  -74.1433      | 521.827       | MB      |
| RQ5  | exp1                | p95_proxy_rss_mb                     |        2 |  236.874       | 236.866       |  -91.4064      | 565.153       | MB      |
| RQ5  | exp1                | p95_proxy_rss_mb                     |        1 |   63.3217      | nan           |  nan           | nan           | MB      |
| RQ5  | exp1                | p95_proxy_rss_mb                     |        1 |   70.0414      | nan           |  nan           | nan           | MB      |
| RQ5  | exp1                | p95_proxy_rss_mb                     |        2 |  417.15        |  75.6466      |  312.31        | 521.991       | MB      |
| RQ5  | exp1                | p95_proxy_rss_mb                     |        2 |  427.744       | 101.207       |  287.478       | 568.01        | MB      |
| RQ5  | exp1                | p95_proxy_rss_mb                     |        3 |  323.301       | 230.457       |   62.5142      | 584.087       | MB      |
| RQ5  | exp1                | p95_proxy_rss_mb                     |        2 |  293.406       | 320.231       | -150.411       | 737.224       | MB      |
| RQ5  | exp1                | p95_proxy_rss_mb                     |        3 |  314.766       | 220.268       |   65.5091      | 564.022       | MB      |
| RQ5  | exp1                | p95_proxy_rss_mb                     |        3 |  291.676       | 198.02        |   67.595       | 515.757       | MB      |
| RQ5  | exp1                | p95_proxy_rss_mb                     |        2 |  198.449       | 181.898       |  -53.6496      | 450.547       | MB      |
| RQ5  | exp1                | p95_proxy_rss_mb                     |        2 |  443.182       |  84.3971      |  326.213       | 560.15        | MB      |
| RQ5  | exp1                | p95_proxy_rss_mb                     |        3 |  328.672       | 236.064       |   61.5407      | 595.804       | MB      |
| RQ5  | exp1                | p95_proxy_rss_mb                     |        3 |  317.288       | 216.559       |   72.2279      | 562.348       | MB      |
| RQ5  | exp1                | p95_proxy_rss_mb                     |        3 |  279.848       | 192.086       |   62.4816      | 497.214       | MB      |
| RQ5  | exp1                | p95_proxy_rss_mb                     |        4 |  329.737       | 180.3         |  153.043       | 506.432       | MB      |
| RQ5  | exp1                | p95_proxy_rss_mb                     |        1 |  497.828       | nan           |  nan           | nan           | MB      |
| RQ5  | exp1                | p95_proxy_rss_mb                     |        3 |  290.911       | 195.216       |   70.0035      | 511.819       | MB      |
| RQ5  | exp1                | p95_proxy_rss_mb                     |        3 |  334.656       | 238.567       |   64.692       | 604.62        | MB      |
| RQ5  | exp1                | p95_proxy_rss_mb                     |        2 |  214.176       | 202.139       |  -65.9741      | 494.326       | MB      |
| RQ5  | exp1                | p95_proxy_rss_mb                     |        2 |  207.807       | 196.026       |  -63.8716      | 479.485       | MB      |
| RQ5  | exp1                | p95_proxy_rss_mb                     |        3 |  296.856       | 196.828       |   74.1237      | 519.588       | MB      |
| RQ5  | exp1                | p95_proxy_rss_mb                     |        2 |  295.521       | 315.941       | -142.351       | 733.394       | MB      |
| RQ5  | exp1                | p95_proxy_rss_mb                     |        3 |  315.594       | 221.754       |   64.6559      | 566.532       | MB      |
| RQ5  | exp2                | p95_proxy_rss_mb                     |        1 |  463.832       | nan           |  nan           | nan           | MB      |
| RQ5  | exp2                | p95_proxy_rss_mb                     |        1 |  414.938       | nan           |  nan           | nan           | MB      |
| RQ5  | fedavg_run_01       | server_failure_count                 |        2 |    1           |   1.41421     |   -0.96        |   2.96        | count   |
| RQ5  | flame_blind         | server_failure_count                 |        1 |    1           | nan           |  nan           | nan           | count   |
| RQ5  | fedavg_run_01       | server_failure_recovery_rate         |        1 |    0           | nan           |  nan           | nan           | ratio   |
| RQ5  | flame_blind         | server_failure_recovery_rate         |        1 |    0           | nan           |  nan           | nan           | ratio   |

## Data quality notes

INFO: RQ1 bundle_0001 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0001 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0002 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0002 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0002 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0003 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0003 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0004 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0004 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0005 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0005 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0006 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0006 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0007 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0007 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0007 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0008 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0008 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0009 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0009 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0010 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0010 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0011 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0011 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0011 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0012 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0012 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0013 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0013 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0014 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0014 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0015 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0015 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0016 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0016 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0016 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0017 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0017 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0018 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0018 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0019 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0019 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0020 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0020 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0021 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0021 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0022 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0022 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0022 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0023 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0023 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0024 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0024 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0025 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0025 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0026 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0026 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0026 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0027 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0027 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0027 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0028 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0028 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0029 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0029 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0030 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0030 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0031 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0031 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0032 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0032 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0033 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0033 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0034 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0034 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0035 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0035 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0036 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0036 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0036 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0037 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0037 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0038 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0038 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0039 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0039 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0040 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0040 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0041 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0041 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0041 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0042 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0042 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0043 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0043 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0044 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0044 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0045 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0045 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0046 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0046 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0046 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0047 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0047 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0048 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0048 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0049 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0049 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0050 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0050 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0051 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0051 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0052 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0052 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0052 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0053 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0053 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0054 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0054 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0055 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0055 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0056 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0056 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0057 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0057 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0057 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0058 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0058 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0058 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0059 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0059 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0060 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0060 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0061 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0061 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0062 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0062 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0063 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0063 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0064 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0064 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0065 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0065 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0066 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0066 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0066 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0067 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0067 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0068 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0068 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0069 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0069 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0070 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0070 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0071 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0071 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0071 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0072 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0072 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0073 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0073 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0074 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0074 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0075 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0075 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0076 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0076 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0077 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0077 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0077 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0078 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0078 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0079 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0079 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0080 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0080 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0081 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0081 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0082 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0082 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0083 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0083 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0083 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0084 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0084 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0084 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0085 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0085 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0086 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0086 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0087 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0087 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0088 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0088 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0089 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0089 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0090 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0090 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0091 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0091 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0092 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0092 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0093 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0093 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0093 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0094 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0094 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0094 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0095 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0095 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0096 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0096 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0097 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0097 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0098 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0098 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0099 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0099 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0100 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0100 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0101 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0101 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0101 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0102 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0102 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0103 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0103 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0104 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0104 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0104 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0105 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0105 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0106 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0106 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0107 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0107 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0108 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0108 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0109 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0109 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0110 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0110 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0111 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0111 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0111 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0112 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0112 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0113 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0113 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0114 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0114 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0115 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0115 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0116 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0116 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0117 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0117 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0118 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0118 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0119 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0119 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0119 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0120 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0120 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0120 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0121 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0121 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0121 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0122 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0122 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0123 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0123 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0123 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0124 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0124 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0125 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0125 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0125 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0126 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0126 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0127 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0127 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0128 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0128 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0129 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0129 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0130 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0130 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0131 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0131 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0132 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0132 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0133 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0133 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0134 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0134 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0135 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0135 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0136 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0136 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0137 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0137 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0138 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0138 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0139 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0139 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0140 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0140 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0141 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0141 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0142 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0142 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0142 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0143 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0143 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0144 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0144 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0145 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0145 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0146 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0146 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0147 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0147 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0147 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0148 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0148 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0149 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0149 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0150 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0150 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0151 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0151 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0152 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0152 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0153 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0153 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0153 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0154 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0154 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0155 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0155 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0156 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0156 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0157 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0157 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0158 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0158 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0159 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0159 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0159 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0160 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0160 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0161 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0161 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0162 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0162 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0163 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0163 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0164 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0164 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0165 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0165 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0165 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0166 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0166 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0167 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0167 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0168 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0168 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0169 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0169 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ3 bundle_0169 No modified proxy updates were logged.
ERROR: evaluation bundle_0169 KeyError: 'attack_ground_truth'
INFO: RQ1 bundle_0170 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0170 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0171 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0171 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0172 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0172 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0172 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0173 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0173 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0174 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0174 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0175 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0175 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0176 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0176 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0177 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0177 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0178 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0178 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0178 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0179 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0179 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0180 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0180 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0181 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0181 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0182 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0182 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0183 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0183 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0184 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0184 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0185 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0185 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0186 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0186 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0187 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0187 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0188 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0188 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0188 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0189 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0189 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0189 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0190 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0190 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0190 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0191 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0191 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0192 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0192 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0193 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0193 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0194 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0194 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0195 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0195 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0196 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0196 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0197 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0197 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0198 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0198 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0199 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0199 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0200 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0200 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
ERROR: evaluation bundle_0200 KeyError: 'attack_ground_truth'
INFO: RQ1 bundle_0201 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0201 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0202 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0202 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0203 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0203 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0204 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0204 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0204 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0205 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0205 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0206 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0206 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0207 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0207 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0208 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0208 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0209 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0209 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0210 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0210 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0211 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0211 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0212 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0212 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0212 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0213 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0213 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0213 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0214 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0214 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0215 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0215 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0216 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0216 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0217 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0217 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0218 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0218 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0219 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0219 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0220 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0220 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0221 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0221 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0222 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0222 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0222 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0223 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0223 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0224 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0224 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0225 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0225 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0226 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0226 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0227 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0227 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0228 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0228 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0228 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0229 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0229 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0230 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0230 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0231 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0231 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0232 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0232 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0233 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0233 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0234 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0234 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0235 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0235 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0236 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0236 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0236 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0237 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0237 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0237 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0238 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0238 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0239 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0239 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0240 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0240 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0241 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0241 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0242 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0242 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0243 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0243 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0244 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0244 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0245 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0245 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0245 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0246 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0246 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0247 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0247 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0248 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0248 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0249 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0249 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0250 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0250 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0251 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0251 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0251 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0252 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0252 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0253 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0253 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0254 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0254 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0255 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0255 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0256 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0256 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0257 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0257 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0258 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0258 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0258 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0259 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0259 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0259 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0260 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0260 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0261 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0261 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0262 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0262 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0263 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0263 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0264 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0264 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0265 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0265 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0266 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0266 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0267 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0267 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0268 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0268 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0269 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0269 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0270 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0270 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0270 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0271 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0271 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0271 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0272 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0272 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0273 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0273 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0274 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0274 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0275 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0275 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0276 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0276 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0277 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0277 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0278 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0278 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0279 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0279 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0280 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0280 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0280 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0281 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0281 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0282 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0282 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0283 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0283 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0284 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0284 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0285 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0285 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0286 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0286 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0286 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0287 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0287 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0288 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0288 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0289 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0289 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0290 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0290 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0291 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0291 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0292 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0292 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0292 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0293 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0293 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0294 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0294 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0295 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0295 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0296 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0296 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
ERROR: evaluation bundle_0296 KeyError: 'attack_ground_truth'
INFO: RQ1 bundle_0297 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0297 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0298 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0298 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0299 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0299 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0300 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0300 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0301 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0301 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0302 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0302 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0303 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0303 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0304 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0304 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0304 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0305 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0305 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0306 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0306 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0307 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0307 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0308 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0308 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0309 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0309 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0310 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0310 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0310 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0311 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0311 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0312 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0312 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0313 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0313 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0314 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0314 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0315 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0315 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0316 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0316 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0316 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0317 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0317 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0318 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0318 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0319 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0319 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
WARNING: RQ1 bundle_0320 No explicit predicted client fingerprint field was found. Flow IP identity is not treated as classifier output.
WARNING: RQ2 bundle_0320 Upload timing uses client serialization intervals rather than independent wire transfer intervals.
INFO: RQ3 bundle_0320 No modified proxy updates were logged.
ERROR: evaluation bundle_0320 KeyError: 'attack_ground_truth'
INFO: RQ1 bundle_0321 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0321 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0321 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0322 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0322 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0322 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0323 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0323 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0323 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0324 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0324 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0324 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0325 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0325 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0325 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0326 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0326 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0326 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0327 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0327 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0327 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0328 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0328 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0328 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0329 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0329 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0330 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0330 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0331 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0331 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0331 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0332 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0332 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0332 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0333 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0333 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0334 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0334 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0335 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0335 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0336 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0336 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0337 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0337 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0338 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0338 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0339 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0339 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0340 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0340 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0341 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0341 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0342 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0342 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0343 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0343 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0343 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0344 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0344 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0344 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0345 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0345 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0345 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0346 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0346 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0347 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0347 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0348 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0348 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0349 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0349 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0350 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0350 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0351 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0351 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0352 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0352 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0353 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0353 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0354 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0354 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0355 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0355 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0356 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0356 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0357 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0357 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0358 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0358 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0359 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0359 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0360 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0360 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0360 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0361 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0361 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0362 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0362 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0363 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0363 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0364 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0364 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0365 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0365 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0366 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0366 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0366 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0367 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0367 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0368 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0368 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0369 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0369 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0370 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0370 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0371 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0371 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0372 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0372 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0373 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0373 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0374 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0374 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0374 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0375 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0375 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0375 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0376 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0376 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0377 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0377 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0378 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0378 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0379 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0379 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0380 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0380 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0381 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0381 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0382 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0382 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0383 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0383 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0384 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0384 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0385 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0385 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0386 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0386 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0387 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0387 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0387 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0388 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0388 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0388 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0389 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0389 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0389 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0390 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0390 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0390 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0391 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0391 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0392 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0392 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0393 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0393 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0394 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0394 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0395 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0395 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0396 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0396 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0397 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0397 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0398 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0398 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0399 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0399 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0400 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0400 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
WARNING: RQ4 bundle_0400 Proxy and server files were bundled but no round and client identities joined.
INFO: RQ1 bundle_0401 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0401 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0402 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0402 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0403 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0403 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0404 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0404 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0405 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0405 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0405 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0406 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0406 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0406 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0407 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0407 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0408 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0408 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0409 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0409 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0410 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0410 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0411 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0411 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0412 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0412 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0413 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0413 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0414 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0414 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0415 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0415 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0416 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0416 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0416 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0417 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0417 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0417 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0418 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0418 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0419 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0419 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0420 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0420 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0421 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0421 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0422 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0422 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0423 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0423 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0424 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0424 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0425 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0425 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0426 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0426 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0426 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0427 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0427 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0428 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0428 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0429 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0429 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0430 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0430 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0431 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0431 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0432 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0432 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0433 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0433 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
WARNING: RQ4 bundle_0433 Proxy and server files were bundled but no round and client identities joined.
INFO: RQ1 bundle_0434 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0434 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
WARNING: RQ4 bundle_0434 Proxy and server files were bundled but no round and client identities joined.
INFO: RQ1 bundle_0435 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0435 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
WARNING: RQ4 bundle_0435 Proxy and server files were bundled but no round and client identities joined.
INFO: RQ1 bundle_0436 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0436 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
WARNING: RQ4 bundle_0436 Proxy and server files were bundled but no round and client identities joined.
INFO: RQ1 bundle_0437 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0437 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
WARNING: RQ4 bundle_0437 Proxy and server files were bundled but no round and client identities joined.
INFO: RQ1 bundle_0438 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0438 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0439 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0439 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0440 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0440 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0441 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0441 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0442 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0442 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0443 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0443 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0444 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0444 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0444 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0445 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0445 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0445 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0446 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0446 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0446 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0447 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0447 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
ERROR: evaluation bundle_0447 KeyError: 'attack_ground_truth'
INFO: RQ1 bundle_0448 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0448 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
ERROR: evaluation bundle_0448 KeyError: 'attack_ground_truth'
INFO: RQ1 bundle_0449 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0449 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
ERROR: evaluation bundle_0449 KeyError: 'attack_ground_truth'
INFO: RQ1 bundle_0450 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0450 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
ERROR: evaluation bundle_0450 KeyError: 'attack_ground_truth'
INFO: RQ1 bundle_0451 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0451 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
ERROR: evaluation bundle_0451 KeyError: 'attack_ground_truth'
INFO: RQ1 bundle_0452 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0452 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
ERROR: evaluation bundle_0452 KeyError: 'attack_ground_truth'
INFO: RQ1 bundle_0453 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0453 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
ERROR: evaluation bundle_0453 KeyError: 'attack_ground_truth'
INFO: RQ1 bundle_0454 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0454 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0455 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0455 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0456 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0456 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0457 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0457 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0458 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0458 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0458 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0459 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0459 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0459 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0460 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0460 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
ERROR: evaluation bundle_0460 KeyError: 'attack_ground_truth'
INFO: RQ1 bundle_0461 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0461 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
ERROR: evaluation bundle_0461 KeyError: 'attack_ground_truth'
INFO: RQ1 bundle_0462 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0462 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0463 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0463 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0463 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0464 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0464 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0465 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0465 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0466 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0466 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0467 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0467 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0467 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0468 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0468 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0469 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0469 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0470 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0470 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0471 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0471 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0471 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0472 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0472 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0473 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0473 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0474 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0474 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0475 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0475 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0475 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0476 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0476 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0477 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0477 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0478 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0478 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0479 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0479 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0479 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0480 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0480 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0481 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0481 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0482 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0482 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0482 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0483 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0483 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0484 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0484 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0485 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0485 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0486 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0486 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0487 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0487 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0487 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0488 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0488 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0489 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0489 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0490 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0490 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0491 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0491 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0491 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0492 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0492 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0493 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0493 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0494 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0494 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0495 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0495 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0495 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0496 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0496 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0497 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0497 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0498 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0498 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0499 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0499 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0499 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0500 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0500 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0501 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0501 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0502 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0502 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0503 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0503 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0503 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0504 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0504 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0505 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0505 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0506 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0506 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0507 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0507 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0507 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0508 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0508 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0509 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0509 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0510 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0510 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0511 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0511 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0512 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0512 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0512 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0513 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0513 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0514 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0514 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0515 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0515 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0516 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0516 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0517 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0517 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0518 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0518 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0519 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0519 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0519 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0520 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0520 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0520 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0521 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0521 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0522 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0522 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0523 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0523 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0524 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0524 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0525 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0525 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0526 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0526 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0527 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0527 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0527 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0528 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0528 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0529 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0529 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0530 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0530 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0530 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0531 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0531 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0532 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0532 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0533 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0533 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0534 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0534 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0535 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0535 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0536 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0536 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0537 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0537 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0537 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0538 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0538 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0539 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0539 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0540 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0540 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0541 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0541 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0542 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0542 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0542 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0543 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0543 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0544 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0544 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0545 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0545 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0546 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0546 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0547 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0547 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0547 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0548 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0548 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0549 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0549 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0550 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0550 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0551 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0551 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0552 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0552 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0552 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0553 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0553 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0554 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0554 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0555 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0555 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0556 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0556 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0557 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0557 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0557 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0558 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0558 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0559 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0559 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0560 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0560 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0561 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0561 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0562 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0562 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0562 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0563 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0563 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0564 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0564 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0565 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0565 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0566 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0566 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0567 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0567 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0567 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0568 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0568 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0569 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0569 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0570 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0570 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0571 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0571 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0572 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0572 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0572 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0573 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0573 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0574 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0574 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
WARNING: RQ1 bundle_0575 No explicit predicted client fingerprint field was found. Flow IP identity is not treated as classifier output.
WARNING: RQ2 bundle_0575 Upload timing uses client serialization intervals rather than independent wire transfer intervals.
ERROR: evaluation bundle_0575 KeyError: 'attack_ground_truth'
INFO: RQ1 bundle_0576 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0576 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0577 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0577 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0578 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0578 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0578 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0579 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0579 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0580 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0580 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0581 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0581 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0582 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0582 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0583 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0583 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0583 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0584 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0584 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0585 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0585 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0586 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0586 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0587 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0587 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0588 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0588 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0588 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0589 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0589 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0590 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0590 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0591 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0591 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0592 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0592 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0593 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0593 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0593 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0594 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0594 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0595 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0595 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0596 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0596 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0597 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0597 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0598 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0598 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0598 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0599 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0599 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0600 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0600 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0601 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0601 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0602 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0602 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0603 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0603 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0603 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0604 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0604 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0605 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0605 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0606 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0606 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0607 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0607 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0608 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0608 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0608 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0609 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0609 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0610 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0610 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0611 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0611 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0612 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0612 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0613 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0613 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0613 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0614 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0614 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0615 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0615 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
WARNING: RQ1 bundle_0616 No explicit predicted client fingerprint field was found. Flow IP identity is not treated as classifier output.
WARNING: RQ2 bundle_0616 Upload timing uses client serialization intervals rather than independent wire transfer intervals.
ERROR: evaluation bundle_0616 KeyError: 'attack_ground_truth'
INFO: RQ1 bundle_0617 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0617 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0618 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0618 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0619 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0619 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0619 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0620 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0620 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0621 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0621 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0622 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0622 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0623 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0623 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0624 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0624 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0624 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0625 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0625 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0626 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0626 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0627 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0627 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0628 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0628 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0629 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0629 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0629 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0630 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0630 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0631 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0631 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0632 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0632 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0633 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0633 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0634 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0634 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0634 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0635 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0635 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0636 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0636 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0637 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0637 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0638 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0638 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0639 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0639 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0639 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0640 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0640 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0641 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0641 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0642 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0642 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0643 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0643 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0644 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0644 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0644 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0645 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0645 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0646 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0646 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
WARNING: RQ1 bundle_0647 No explicit predicted client fingerprint field was found. Flow IP identity is not treated as classifier output.
WARNING: RQ2 bundle_0647 Upload timing uses client serialization intervals rather than independent wire transfer intervals.
ERROR: evaluation bundle_0647 KeyError: 'attack_ground_truth'
WARNING: RQ1 bundle_0648 No explicit predicted client fingerprint field was found. Flow IP identity is not treated as classifier output.
WARNING: RQ2 bundle_0648 Upload timing uses client serialization intervals rather than independent wire transfer intervals.
INFO: RQ1 bundle_0649 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0649 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0650 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0650 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0651 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0651 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0652 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0652 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0653 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0653 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0654 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0654 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0655 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0655 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0656 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0656 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0657 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0657 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0658 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0658 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0659 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0659 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0660 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0660 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0661 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0661 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0662 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0662 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0663 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0663 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0664 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0664 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0665 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0665 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0666 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0666 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0667 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0667 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0668 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0668 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0669 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0669 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0670 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0670 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0671 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0671 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0672 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0672 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0672 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0673 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0673 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0674 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0674 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0675 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0675 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0676 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0676 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0677 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0677 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0678 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0678 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0679 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0679 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0680 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0680 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0681 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0681 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0682 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0682 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0683 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0683 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0684 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0684 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0685 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0685 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0686 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0686 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0687 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0687 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0688 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0688 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0689 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0689 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0690 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0690 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0691 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0691 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0692 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0692 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0693 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0693 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0694 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0694 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0695 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0695 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0696 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0696 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0697 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0697 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0698 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0698 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0699 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0699 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0700 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0700 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0701 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0701 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0702 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0702 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0703 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0703 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0704 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0704 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0705 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0705 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0706 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0706 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ1 bundle_0707 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0707 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0707 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0708 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0708 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0708 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0709 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0709 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0709 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0710 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0710 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0710 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.
INFO: RQ1 bundle_0711 Phase confusion requires matched analyzer decision and client metric files.
INFO: RQ2 bundle_0711 Exact trigger precision and recall require a matched analyzer or proxy run and client upload ground truth.
INFO: RQ4 bundle_0711 Server defense diagnostics are available, but malicious admission metrics require a matched proxy ground truth file.