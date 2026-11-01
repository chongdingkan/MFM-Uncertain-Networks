# Table V: cost sensitivity and HEU component ablation

This directory contains the Table V sensitivity and HEU component-ablation
workflow, configuration, statistical aggregation, and tests.

The workflow covers the 16 Table V configurations only. It is not an archive of
all experiments in the paper and makes no claim about the adaptive-submodularity
guarantee of ADP. The original root `code.py` is preserved without modification.

## Download

Download [TableV_sensitivity_ablation_reconstructed.zip](TableV_sensitivity_ablation_reconstructed.zip) and extract it into a new folder. The archive contains the source files under `experiments/table_v/`, the preserved root `code.py`, and the required EU-Email dataset. Run the commands below from the extracted root.

## Setup and commands

Use Python 3.10 or newer. From the repository root:

```sh
python -m pip install -r experiments/table_v/requirements.txt
python experiments/table_v/run.py
python -m unittest discover -s experiments/table_v -p "test_*.py" -v
```

The first command installs the pinned dependencies. The second is a **dry run**:
it reads the dataset, selects the graph, and prints the plan without simulating
any attack-defense interaction or creating numerical results. The tests exercise
small, artificial fixtures; their outputs are not paper results.

To execute the configurations:

```sh
python experiments/table_v/run.py --execute --accept-reconstruction --output table-v-output
```

This command performs 1,600 simulated engagements: 16 configurations, each with
10 source-destination pairs crossed with 10 graph realizations. The explicit
execution flag prevents accidental execution when only inspecting the package.
Existing nonempty output folders are rejected.

To recompute statistics from those generated run records, without running the
simulator again:

```sh
python experiments/table_v/run.py --aggregate-only --output table-v-output
```

To use a different documented configuration, pass `--config path/to/config.json`.
An explicit whitespace-separated list of 100 original node IDs can be supplied
with `--node-file path/to/nodes.txt`. An alternative edge list can be supplied
with `--dataset path/to/edges.txt`; a multi-member ZIP additionally requires
`--archive-member member_name`. No dataset is downloaded by this script.

## Mapping to Table V

The configuration shared by all cells is: 100-node EU-Email potential graph,
HEU defense, one attack per round, defender visibility probability 0.5,
independent link-existence draws, and 100 outcomes per cell. Capacities use a
positive Gaussian generator with nominal mean 50 and standard deviation 10.

| Analysis | Attack | Configurations | Cells |
|---|---|---|---:|
| Cost sensitivity | RA | Gaussian, Uniform, Lognormal | 3 |
| Cost sensitivity | HA | Gaussian, Uniform, Lognormal | 3 |
| Score ablation | RA | Full score, without probability, topology, capacity, cost | 5 |
| Score ablation | HA | Full score, without probability, topology, capacity, cost | 5 |

The full importance score is manuscript Eq. (24):

```text
p(u,v) * [degree(u) + degree(v) + betweenness(u) + betweenness(v)] * capacity(u,v) / cost(u,v)
```

Each ablation replaces exactly one multiplicative factor by one. Removing
topology removes the entire bracket; removing cost removes the denominator from
the *selection score*. All variants still incur the original actual probing cost.
No value is tuned to match Table V. The printed table values are not embedded in
the implementation, and are not used to construct run-level observations.

Cost generators have nominal mean 50 and standard deviation 10:

| Distribution | Parameters |
|---|---|
| Gaussian | N(50, 10²), rejecting nonpositive samples |
| Uniform | endpoints 50 − sqrt(3)·10 and 50 + sqrt(3)·10 |
| Lognormal | sigma² = log(1 + (10/50)²); mu = log(50) − sigma²/2 |

The uniform and lognormal generators match the untruncated Gaussian's target
moments. The rejected Gaussian is only approximately moment-matched. Capacity
and cost draws are separate streams; capacity remains Gaussian in every cell.

## Implementation settings

| Item | Choice in this implementation |
|---|---|
| Dataset format | Detect compression by magic bytes. The repository's `email-Eu-core.zip` is actually a gzip-compressed edge list. |
| Graph construction | Treat the input as an undirected simple graph; merge reciprocal/duplicate edges and remove self-loops. |
| 100-node extraction | BFS from the highest-degree node of the largest connected component; sorted neighbors and numeric tie-breaking. Use the induced subgraph. |
| Existence probabilities | Jaccard coefficient computed on the selected potential graph, before realization sampling. Zero coefficients remain zero; no undocumented floor is applied. |
| Topological factors | Raw endpoint degrees plus normalized, unweighted node betweenness on the potential graph, computed once. Degree normalization is configurable. |
| HEU candidate selection | Follow the public HEU function's rule: prefer unresolved edges incident to the destination; otherwise use all unresolved edges. Apply the importance score to those candidates. |
| HEU ties | Lexicographic edge order. |
| Algorithm 2 discrepancy | The public HEU function does not implement the source-path/backtracking rule in Algorithm 2. This package follows the public candidate rule, not a claimed implementation of that pseudocode. |
| Source-destination pairs | Ten uniform ordered pairs, each with distinct endpoints, drawn once and reused across realizations. Different pair draws can coincide. |
| Capacity/existence draws | Shared within each realization across pairs and configurations of the same analysis block. Sensitivity and ablation blocks have distinct named streams. |
| Cost draws | Per realization and distribution, shared across paired configurations. A cost distribution change does not change capacity or existence draws. |
| RA | A uniformly shuffled permutation of potential edges, without repeats. |
| HA | Split target counts as equally as possible across RA/PD/KD; shuffle the strategy tokens, then select the next unused edge from the corresponding ordering. Ties are randomized with a recorded stream. With a_n=1, a single round cannot itself allocate one third of an attack to each rule. |
| Attacker information | Attack order never depends on protected links, the hidden realization, or the defender's choices. Attacking an already protected link is ineffective and consumes that attack. |
| Observation | Independent Bernoulli visibility for each attempted target. An unobserved destructive attack does not remove that edge from the defender's unresolved set. |
| Probing | Attack first, then one unresolved edge is probed. Charge every probe, including absent or already destroyed edges. Only a present, not-yet-destroyed edge becomes protected. |
| Stopping/flow | Stop when the defender has no unresolved edge. Compute capacitated s-t maximum flow on the surviving protected graph, retaining isolated nodes. |
| Seed | Master seed 20261101, expanded into named SHA-256/PCG64 streams. |

## Generated records and aggregation

Execution creates the following in the selected output directory:

- `runs.csv`: one row per cell, pair, and realization, including flow, accumulated
  cost, probe count, and identifiers. Full-precision results precede rounding.
- `instances.json`: selected edge attributes and realized existence states, cost
  vectors, attack orders, and observed-target sets for checking an execution.
- `summary.csv`: arithmetic mean and **sample** standard deviation (`n-1`
  denominator) for flow and cost, with the count in each cell.
- `table_v.md`: readable table of the generated results.
- `manifest.json`: configuration, node IDs, source-destination pairs, dependency
  versions, master seed, source/data/configuration hashes, instance hash, and
  output hashes.

Aggregation rejects duplicate run IDs, missing or unexpected cells, missing
pair/realization combinations, inconsistent cell metadata, and nonfinite or
negative outcomes. It does not turn standard deviations into confidence
intervals or perform hypothesis tests. Because pairs share realizations, the 100
outcomes are not asserted to be 100 independent Monte Carlo samples; the sample
standard deviations are descriptive.

