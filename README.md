# GART Routing Suite

Paper-aligned implementation of **GART: Decentralized Intelligent Routing with
Dual Rewards for Mission-Critical Industrial IoT Networks**. GART is the main
implementation. The historical DRL-OR-S project and its 47-node Military
scenario are isolated under `baseline/drl-or-s/`.

## Paper topology set

| Dataset | Nodes | Physical links | Directed links | Paper use |
|---|---:|---:|---:|---|
| `nsfnet` | 14 | 21 | 42 | convergence and static evaluation |
| `geant2` | 23 | 36 | 72 | convergence and static evaluation |
| `renater2010` | 43 | 56 | 112 | static and Renater-like dynamic evaluation |
| `synthetic300` | 300 | 669 | 1,338 | large-scale evaluation |

Every physical link in `Topology.txt` is loaded in both directions. The
Synthetic-300 fixture uses a fixed degree-preferential generator seed and has
average out-degree 4.46. Dataset provenance and known reproduction boundaries
are recorded in each `topology/<dataset>/metadata.json`.

The paper does not publish its generated Synthetic-300 instance. It also
reports 36 physical GEANT2 links while the public 23-node traffic-measurement
snapshot contains 37. To match the paper count, this repository excludes the
snapshot's lowest-capacity non-bridge link `(6, 19)` and records that decision
in metadata.

## Project layout

| Path | Purpose |
|---|---|
| `gart/` | GART observation, dual reward, GAT Actor-Critic, PPO and path service |
| `topology/` | The four paper evaluation topologies and runnable traffic fixtures |
| `models/` | Per-topology GART checkpoint output |
| `testbed/paper_topology.py` | Generic Mininet launcher for any paper topology |
| `baseline/drl-or-s/` | Legacy DRL-OR-S code, Military topology and checkpoints |
| `tests/` | Unit, integration and paper-alignment tests |

Each routing decision builds the current agent's two-hop induced subgraph,
matching the bounded receptive field formed by the paper's two GAT layers.
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
and output path follow automatically. Use seeds 1-5 and traffic intensities 0.3
and 0.7 for the paper's five-run light/heavy-load setup.

The bundled NSFNet and GEANT2 `TM.txt` files are deterministic runnable
fixtures. Exact traffic-matrix reproduction requires replacing them with a
matrix extracted from the large dataset archives cited by the paper. Renater
2010 and Synthetic-300 use gravity-model fixtures as described in the paper.

## Run

```bash
./start_suite.sh
```

This starts NSFNet by default. Choose another paper topology with:

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
python3 tools/build_paper_topologies.py
git diff --exit-code -- topology
```

Chinese deployment notes are in `RUN_TESTING_CN.md`.
