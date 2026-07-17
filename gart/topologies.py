"""Paper evaluation topology catalog and path resolution helpers."""

from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TOPOLOGY = "nsfnet"


@dataclass(frozen=True)
class PaperTopology:
    name: str
    nodes: int
    directed_links: int

    @property
    def directory(self):
        return PROJECT_ROOT / "topology" / self.name

    @property
    def topology_path(self):
        return self.directory / "Topology.txt"

    @property
    def traffic_matrix_path(self):
        return self.directory / "TM.txt"

    @property
    def default_model_path(self):
        return PROJECT_ROOT / "models" / self.name / "gart.pt"


PAPER_TOPOLOGIES = {
    item.name: item
    for item in (
        PaperTopology("nsfnet", 14, 42),
        PaperTopology("geant2", 23, 72),
        PaperTopology("renater2010", 43, 112),
        PaperTopology("synthetic300", 300, 1338),
    )
}


def get_paper_topology(name=DEFAULT_TOPOLOGY):
    key = (name or DEFAULT_TOPOLOGY).strip().lower()
    try:
        return PAPER_TOPOLOGIES[key]
    except KeyError as exc:
        choices = ", ".join(PAPER_TOPOLOGIES)
        raise ValueError("unknown paper topology %r; choose one of: %s" % (name, choices)) from exc
