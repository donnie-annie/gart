# GART paper alignment

This package implements **GART: Decentralized Intelligent Routing with Dual
Rewards for Mission-Critical Industrial IoT Networks** while keeping the old
DRL-OR-S model available as a deployment fallback.

## Paper-to-code map

| Paper component | Implementation |
|---|---|
| Local observation: capacity, delay, loss | `observation.py` |
| Available-neighbor action mask, Eq. (1) | `observation.py` and `model.py` |
| Local reward, Eq. (2) | `rewards.py::DualReward.local` |
| Deadline/throughput/loss global reward, Eq. (3) | `rewards.py::DualReward.global_reward` |
| Terminal dual reward, Eq. (4) | `rewards.py::DualReward.combined` |
| Multi-head GAT, Eqs. (5)-(7) | `model.py::MultiHeadGATLayer` |
| Flow-conditioned Actor-Critic, Algorithm 1 | `model.py::GARTActorCritic` |
| GAE and rollout, Eqs. (9)-(10) | `rollout.py` |
| PPO loss, Eqs. (12)-(15) | `ppo.py` |
| Multi-agent/per-flow training loop, Algorithm 2 | `train.py` |
| Dynamic topology training backend | `topology_env.py` |
| Decentralized online next-hop execution | `../path_service.py` |

The model uses two GAT layers. Each layer has four attention heads with a
16-dimensional output per head. Actor and Critic MLPs both use hidden widths
64/64. Embeddings are L2-normalized after every GAT layer, and invalid or
already-visited next hops are masked before sampling.

The global reward is attached only to the terminal transition. GAE then
propagates its effect to earlier per-hop decisions, matching the manuscript.

## Reproduction notes

- Flow classes follow Table II: EU 5%/20 ms, MU 15%/50 ms, LU 70%/100 ms,
  and RT 10%/200 ms.
- `GARTConfig` contains every Table III value.
- The paper defines `P_loop`, `P_noACK`, `w_b`, `alpha`, `beta`, `gamma`, and
  `epsilon` symbolically but does not publish numerical values. They are exposed
  in `GARTConfig`; the defaults are deliberately simple and reproducible.
- CPU is the default training device, matching the paper's reported setup.
- `TopologyRoutingEnv` is the offline trainer. Online evaluation continues to
  run through Mininet/Ryu and the existing routing suite.
