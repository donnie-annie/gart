# Military topology (legacy baseline only)

This 47-node, 60-link scenario belongs to the historical DRL-OR-S project. It
is retained only for baseline compatibility and is not a GART paper topology.

- `Topology.txt`: legacy physical-link structure
- `TM.txt`: legacy 47 x 47 traffic matrix
- `link_weight.json`: legacy directed link weights

Use it only with `--algorithm baseline` and the checkpoints in
`baseline/drl-or-s/model/Military_mininet/`.
