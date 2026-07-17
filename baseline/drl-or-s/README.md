# DRL-OR-S baseline

This directory contains the original DRL-OR-S implementation retained only as
a reproducibility and deployment-compatibility baseline for GART.

The primary implementation lives in the repository-level `gart/` package.
The legacy Military topology is stored locally under `topology/Military/`;
paper evaluation topologies live in the repository-level `topology/` directory.

Legacy checkpoints are stored in `model/Military_mininet/`. To select this
baseline explicitly, run the GART path service with:

```bash
python3 -m gart.path_service \
  --algorithm baseline \
  --model baseline/drl-or-s/model/Military_mininet
```
