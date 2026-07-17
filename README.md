# GART Routing Suite

Paper-aligned implementation of **GART: Decentralized Intelligent Routing with
Dual Rewards for Mission-Critical Industrial IoT Networks**. GART is the primary
routing implementation in this repository; the historical DRL-OR-S code is
isolated under `baseline/drl-or-s/` for comparison and compatibility only.

## Project layout

| Path | Purpose |
|---|---|
| `gart/` | GART observations, dual rewards, GAT Actor-Critic, PPO trainer and online path service |
| `topology/Military/` | Shared 47-node topology and traffic matrix |
| `models/GART_Military/` | Output directory for trained `gart.pt` checkpoints |
| `baseline/drl-or-s/` | Legacy implementation and its packaged checkpoints |
| `controller.py`, `server_agent.py` | Ryu/controller integration and routing API |
| `testbed/` | Military Mininet topology and hybrid physical attachment |
| `tests/` | Unit and integration tests |

## Install

```bash
pip3 install -r requirements.txt
```

Mininet and Open vSwitch must be installed as system packages in the Linux
testbed environment.

## Train GART

The defaults match Tables II-III of the paper: 100,000 interactions, two GAT
layers, four 16-dimensional heads, PPO clip 0.1, rollout length 2048,
mini-batch size 64 and ten PPO epochs.

```bash
python3 -m gart.train \
  --topology topology/Military/Topology.txt \
  --traffic-matrix topology/Military/TM.txt \
  --traffic-intensity 0.7 \
  --interactions 100000 \
  --seed 1 \
  --output models/GART_Military/gart.pt
```

Run seeds 1-5 independently to reproduce the paper's five-run averages. Reward
coefficients that are symbolic but not numerically specified in the manuscript
are explicit in `gart/config.py`.

## Run

```bash
./start_suite.sh
```

The launcher uses GART by default and reads
`models/GART_Military/gart.pt`. If the checkpoint is missing or inference is
unavailable, routing safely falls back to Dijkstra.

Useful endpoints:

- controller/server socket: `6001`
- Web UI: `http://localhost:6009`
- GART path service: `127.0.0.1:8889`

For hybrid virtual/physical switch communication:

```bash
./start_suite.sh eno1
```

This attaches `eno1` to Mininet `s1:port20`. Runtime settings can be overridden
with environment variables:

```bash
PATH_SERVICE_PYTHON=/path/to/python \
PATH_SERVICE_MODEL=models/GART_Military/gart.pt \
SERVER_AGENT_ROUTE_MODE=shadow \
./start_suite.sh eno1
```

Stop all components with:

```bash
./stop_suite.sh
```

## Baseline comparison

The legacy implementation is not part of the primary GART package. Select it
explicitly when a comparison run is required:

```bash
python3 -m gart.path_service \
  --topo Military \
  --port 8889 \
  --algorithm baseline \
  --model baseline/drl-or-s/model/Military_mininet
```

## Validation

```bash
python3 -m pytest -q
```

Chinese deployment and troubleshooting instructions are in
`RUN_TESTING_CN.md`.
