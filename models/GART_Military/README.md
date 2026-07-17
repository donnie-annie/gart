# GART checkpoints

Train the paper-aligned model from the repository root and write the checkpoint
to this directory:

```bash
python3 -m gart.train \
  --topology topology/Military/Topology.txt \
  --traffic-matrix topology/Military/TM.txt \
  --output models/GART_Military/gart.pt
```

`gart.pt` is intentionally not included until a training run is completed.
