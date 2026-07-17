# Military topology for GART

The shared experiment topology contains **47 nodes** and **60 bidirectional
links**, organized into a core layer and six access subnets.

## Structure

- outer core ring: nodes 1-6
- inner core: nodes 45-47
- brigade headquarters: nodes 42-44
- combat squads: nodes 7-41, split into five access groups

Backbone links use 9920 Kbps capacity, access links use 5000 Kbps and subnet
internal links use 3000 Kbps. The traffic matrix contains 47 x 47 entries with
differentiated backbone, headquarters and squad traffic.

## Files

- `Topology.txt`: node/link structure
- `TM.txt`: traffic matrix
- `link_weight.json`: directed link weights

## Train GART

Run from the repository root:

```bash
python3 -m gart.train \
  --topology topology/Military/Topology.txt \
  --traffic-matrix topology/Military/TM.txt \
  --output models/GART_Military/gart.pt
```

The historical comparison environment reads the same files from
`baseline/drl-or-s/net_env/simenv.py`.
