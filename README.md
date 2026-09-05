# Federated Learning Security Evaluation Framework

This repository contains a controlled experimental framework for studying security vulnerabilities and defensive mechanisms in federated learning systems.

The project investigates how network observable operational state can be combined with federated learning protocol knowledge to evaluate availability, model integrity, update provenance, poisoning resilience, transport behavior, and defensive controls.

The framework is intended for authorized academic research, reproducible experimentation, and defensive security evaluation.

## Research Objective

Federated learning reduces the need to centralize raw training data, but the communication process itself may expose information about the learning lifecycle.

Observable characteristics such as traffic direction, timing, transfer volume, burst behavior, silence periods, and recurring communication cycles can reveal when a participant is receiving a global model, performing local training, uploading an update, or waiting for synchronization.

This project studies the security consequences of that exposure.

The broader research objective is to determine how operational state information can affect federated learning confidentiality, integrity, provenance, availability, and resilience, and to evaluate defenses that reduce those risks.

## Research Scope

The framework supports controlled experiments involving federated learning clients, aggregation servers, network observation, state inference, model exchange analysis, experimental intervention, validation, and defensive mechanisms.

The research examines several connected problems.

### Operational State Inference

The system analyzes observable communication behavior to identify federated learning phases and track the learning process across rounds.

The research includes temporal inference methods designed to distinguish communication phases from periods of local computation in which little or no traffic may be visible.

### Phase Aware Security Evaluation

Operational state information can be used experimentally to determine whether intervention at a particular point in the learning lifecycle produces a different effect from indiscriminate network disruption.

The framework therefore supports controlled evaluation of timing sensitive availability and integrity scenarios.

### Model and Update Analysis

Federated learning clients receive a global model, perform local training, and return a locally updated model.

The research distinguishes the complete returned model from the mathematical contribution produced during local learning.

This distinction allows experiments to examine model reconstruction, update reconstruction, validation, and protocol compatibility.

### Update Provenance

A statistically plausible update is not necessarily proof that the object received by the server is identical to the object produced by the claimed client.

The project therefore studies the distinction between statistical robustness and communication provenance.

This motivates defensive mechanisms that verify participant identity, round context, freshness, integrity, and compatibility before an update becomes an aggregation input.

### Robust Aggregation

The experimental environment supports evaluation of federated learning aggregation and defensive strategies under controlled benign and adversarial conditions.

The objective is not to claim that one defense or attack applies universally.

Instead, the framework records how different mechanisms behave under specific workloads, participation patterns, attack conditions, and system assumptions.

### Defensive Evaluation

The repository contains defensive evaluation components organized for multiple workload classes, including:

`Autoencoder`

`CNN`

`RNN`

The defensive research examines mechanisms operating at different layers of the federated learning system, including communication behavior, intervention tolerance, update validation, aggregation behavior, and model integrity.

## Experimental Architecture

A typical experiment contains four logical components.

### Federated Learning Client

The client receives a global model, performs local training, evaluates the resulting model, and returns a model update or locally trained model according to the experiment configuration.

### Federated Learning Server

The server coordinates learning rounds, distributes global model state, receives client submissions, validates experiment conditions, and performs aggregation.

### Network Observation and Analysis

The analysis components observe permitted network metadata and infer operational behavior without assuming access to private client training data.

### Controlled Security Evaluation

Authorized experimental components reproduce selected communication path conditions so that attack effects and defensive behavior can be measured under repeatable laboratory conditions.

## Validation and Reproducibility

The repository includes validation artifacts used to verify implementation consistency and experiment integrity.

Examples include:

`VALIDATION_REPORT.json`

`VALIDATION_RESULTS.txt`

`TRANSPORT_ISOLATION_VALIDATION.json`

`RESNET18_62TENSOR_VALIDATION.json`

`SHA256SUMS_V27_1.txt`

These files support verification of implementation assumptions, transport isolation, model tensor contracts, experiment artifacts, and reproducibility.

SHA256 records are used where appropriate to verify that experiment artifacts remain unchanged between generation and analysis.

## Transport Isolation

Transport behavior is treated as part of the experimental methodology.

The repository includes transport isolation validation so that experimental observations can be separated from unrelated communication artifacts.

This is particularly important when network behavior itself is being analyzed as a research signal.

## Workload Coverage

The current research environment includes experiments using multiple artificial intelligence workload families.

The repository contains defensive evaluation structures for Autoencoder, convolutional neural network, and recurrent neural network workloads.

Results are interpreted within the workload, system configuration, network condition, and experimental assumptions under which they were produced.

## Research Principles

This project follows several methodological principles.

Ground truth information from clients and servers is used for validation and evaluation and should not be silently introduced into attacker observable predictors.

Experimental attack components are used only in controlled and authorized research environments.

Network observations and model manipulation experiments are conducted against systems operated for research purposes.

Results obtained from a particular testbed are not represented as universal guarantees.

Negative results, failed attacks, rejected updates, incomplete runs, and defense limitations are retained when they are relevant to scientific interpretation.

## Responsible Use

This repository is provided for academic research, controlled security testing, defensive evaluation, and reproducibility.

Do not use the software to intercept, manipulate, disrupt, or access systems without explicit authorization.

Users are responsible for complying with institutional requirements, applicable law, network policies, research ethics requirements, and security procedures.

The project is intended to improve understanding of distributed artificial intelligence security and to support the design of more resilient federated learning systems.

## Related Research

This repository forms part of a broader research program on secure and resilient distributed artificial intelligence.

The research progression includes network based AI fingerprinting, federated learning phase inference, temporal state tracking, controlled intervention, model and update reconstruction, provenance analysis, defensive aggregation, state concealment, and authenticated model exchange.

The associated AI fingerprinting research repository is available at:

https://github.com/oyalaw/Fingerprinting

The broader experimental AI workload testbed is available at:

https://github.com/oyalaw/AI-Fingerprinting

## Researcher

**Oyaniyi Lawrence Olanrewaju**

PhD Candidate and Adjunct Faculty I  
Department of Computer and Information Sciences  
Towson University  
Maryland, United States

Research interests include secure distributed artificial intelligence, federated learning security, network side channels, AI workload fingerprinting, model integrity, provenance, and resilient edge intelligence.

## Citation

If you use this repository or its experimental methodology in scholarly work, please cite the relevant publication associated with the experiment and reference this repository where appropriate.

## Status

This is an active research repository.

Experimental interfaces, configuration parameters, evaluation methods, and defensive mechanisms may change as the research progresses.
