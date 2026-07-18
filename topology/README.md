# Paper evaluation topologies

This directory contains the four topologies reported by the GART paper. Run
`python3 tools/build_paper_topologies.py` to regenerate every fixture.

`Topology.txt` stores physical links as:

```text
source destination delay capacity loss
```

The loader expands each physical link into two directed links. `TM.txt` is a
square row-major traffic matrix. See each `metadata.json` for provenance and
the distinction between paper-published facts and repository fixtures.
