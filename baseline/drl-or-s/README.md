# DRL-OR-S baseline

This directory contains the original DRL-OR-S implementation retained only as
a deployment-compatibility and comparison baseline for GART.

The primary implementation lives in the repository-level `gart/` package.
The legacy Military topology is stored locally under `topology/Military/`;
GART benchmark topologies live in the repository-level `topology/` directory.

Legacy checkpoints are stored in `model/Military_mininet/`. To select this
baseline explicitly, run the GART path service with:

```bash
python3 -m gart.path_service \
  --algorithm baseline \
  --model baseline/drl-or-s/model/Military_mininet
```
