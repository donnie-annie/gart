# GART Routing Suite

GART is a standalone decentralized routing project built around graph
attention, PPO, dual rewards, and bounded local observations. The main
implementation lives in `gart/`; the historical DRL-OR-S code is isolated
under `baseline/drl-or-s/` for optional comparisons.

## Topology set

| Dataset | Nodes | Physical links | Directed links | Intended scale |
|---|---:|---:|---:|---|
| `nsfnet` | 14 | 21 | 42 | small |
| `geant2` | 23 | 36 | 72 | medium |
| `renater2010` | 43 | 56 | 112 | medium |
| `synthetic300` | 300 | 669 | 1,338 | large |

Every physical link in `Topology.txt` is loaded in both directions. The
Synthetic-300 fixture uses a fixed degree-preferential generator seed and has
average out-degree 4.46. Dataset sources and normalization details are recorded
in each `topology/<dataset>/metadata.json`.

## Project layout

| Path | Purpose |
|---|---|
| `gart/` | GART observation, dual reward, GAT Actor-Critic, PPO and path service |
| `topology/` | Benchmark topologies and runnable traffic fixtures |
| `models/` | Per-topology GART checkpoint output |
| `testbed/topology_launcher.py` | Generic Mininet launcher for topology fixtures |
| `baseline/drl-or-s/` | Legacy DRL-OR-S code, Military topology and checkpoints |
| `tests/` | Unit and integration tests |

Each routing decision builds the current agent's two-hop induced subgraph,
which matches the configured two-layer GAT receptive field.
Remote destinations remain flow features and are not inserted into the local
GAT graph. PPO pads variable local graphs only within each rollout batch.

## Install

```bash
pip3 install -r requirements.txt
```

Mininet and Open vSwitch must be installed as system packages on the Linux
testbed.

## Train GART

NSFNet is the default dataset:

```bash
python3 -m gart.train \
  --dataset nsfnet \
  --traffic-intensity 0.7 \
  --interactions 100000 \
  --seed 1
```

The checkpoint is written to `models/nsfnet/gart.pt`. Select `geant2`,
`renater2010`, or `synthetic300` with `--dataset`; the topology, traffic matrix,
and output path follow automatically. Multiple seeds and traffic intensities
can be used for repeated light/heavy-load benchmarks.

The bundled traffic matrices are deterministic runnable fixtures. Supply a
custom matrix with `--traffic-matrix` when evaluating another workload.

## Run

```bash
./start_suite.sh
```

This starts NSFNet by default. Choose another topology with:

```bash
GART_TOPOLOGY=renater2010 ./start_suite.sh
```

The corresponding default checkpoint is `models/<topology>/gart.pt`. If it is
missing, the path service reports the reason and falls back to Dijkstra.

## Baseline comparison

The Military scenario is available only for explicit DRL-OR-S baseline runs:

```bash
python3 -m gart.path_service \
  --topo Military \
  --algorithm baseline \
  --model baseline/drl-or-s/model/Military_mininet
```

## Validation

```bash
python3 -m pytest -q
python3 tools/build_topologies.py
git diff --exit-code -- topology
```

Chinese deployment notes are in `RUN_TESTING_CN.md`.
