"""Build decentralized, topology-local observations for GART inference."""

from dataclasses import dataclass
import math


def _finite(value, default=0.0):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return float(default)
    return value if math.isfinite(value) else float(default)


def _loss_ratio(value):
    value = max(_finite(value), 0.0)
    if value > 1.0:
        value /= 100.0
    return min(value, 1.0)


def _edge_value(edge, names, default):
    for name in names:
        if name in edge and edge[name] is not None:
            return edge[name]
    return default


def normalize_edge(edge):
    """Normalize controller/list edges to a common dynamic-link schema."""
    if isinstance(edge, dict):
        src = int(edge.get("src"))
        dst = int(edge.get("dst"))
        capacity = max(_finite(_edge_value(
            edge, ("capacity", "bw", "bandwidth", "max_capacity"), 1.0), 1.0), 1e-12)
        utilization = _finite(edge.get("utilization", 0.0))
        if utilization > 1.0:
            utilization /= 100.0
        utilization = max(0.0, min(1.0, utilization))
        available = _edge_value(
            edge,
            ("available_bandwidth", "residual_bandwidth", "available_bw"),
            capacity * (1.0 - utilization),
        )
        delay = max(_finite(_edge_value(edge, ("delay", "latency", "weight"), 1.0), 1.0), 0.0)
        loss = _loss_ratio(edge.get("loss", edge.get("loss_rate", 0.0)))
        enabled = (
            bool(edge.get("enabled", True))
            and edge.get("status", "up") != "down"
            and capacity > 0.0
        )
    else:
        src = int(edge[0])
        dst = int(edge[1])
        delay = max(_finite(edge[2] if len(edge) > 2 else 1.0, 1.0), 0.0)
        capacity = max(_finite(edge[3] if len(edge) > 3 else 1.0, 1.0), 1e-12)
        loss = _loss_ratio(edge[4] if len(edge) > 4 else 0.0)
        available = capacity
        enabled = True

    return {
        "src": src,
        "dst": dst,
        "capacity": capacity,
        "available_bandwidth": max(_finite(available), 0.0),
        "delay": delay,
        "loss": loss,
        "enabled": bool(enabled),
    }


@dataclass
class GARTObservation:
    node_ids: list
    node_features: list
    adjacency: list
    action_mask: list
    flow_features: list
    current_index: int
    destination_index: int

    def to_tensors(self, device=None):
        """Convert an observation lazily so controller-only imports need no torch."""
        import torch

        return {
            "node_features": torch.tensor(self.node_features, dtype=torch.float32, device=device).unsqueeze(0),
            "adjacency": torch.tensor(self.adjacency, dtype=torch.bool, device=device).unsqueeze(0),
            "action_mask": torch.tensor(self.action_mask, dtype=torch.bool, device=device).unsqueeze(0),
            "flow_features": torch.tensor(self.flow_features, dtype=torch.float32, device=device).unsqueeze(0),
            "current_node": torch.tensor([self.current_index], dtype=torch.long, device=device),
        }


def build_gart_observation(topo_edges, current_node, destination_node,
                           visited_nodes=None, deadline_ms=200.0,
                           max_deadline_ms=200.0):
    """Create capacity/delay/loss node features and a valid-next-hop mask.

    The tensors contain the graph for efficient batched computation, while a
    two-layer GAT means the current node embedding only receives information
    from its bounded two-hop receptive field, as required by the paper.
    """
    edges = [normalize_edge(edge) for edge in (topo_edges or [])]
    node_ids = {int(current_node), int(destination_node)}
    for edge in edges:
        node_ids.add(edge["src"])
        node_ids.add(edge["dst"])
    node_ids = sorted(node_ids)
    index = {node_id: position for position, node_id in enumerate(node_ids)}
    size = len(node_ids)

    adjacency = [[False] * size for _ in range(size)]
    for position in range(size):
        adjacency[position][position] = True

    outgoing = {node_id: [] for node_id in node_ids}
    max_delay = max([edge["delay"] for edge in edges] + [1.0])
    for edge in edges:
        if not edge["enabled"]:
            continue
        src_index = index[edge["src"]]
        dst_index = index[edge["dst"]]
        adjacency[src_index][dst_index] = True
        outgoing[edge["src"]].append(edge)

    node_features = []
    for node_id in node_ids:
        links = outgoing[node_id]
        if not links:
            node_features.append([0.0, 1.0, 1.0])
            continue
        residual = sum(min(link["available_bandwidth"] / link["capacity"], 1.0) for link in links) / len(links)
        delay = sum(link["delay"] / max_delay for link in links) / len(links)
        loss = sum(link["loss"] for link in links) / len(links)
        node_features.append([residual, min(delay, 1.0), min(loss, 1.0)])

    # In agent i's local observation, each direct neighbor feature represents
    # the i->j link itself (capacity, delay, loss), matching O_i in Section III.
    for link in outgoing[int(current_node)]:
        neighbor_index = index[link["dst"]]
        node_features[neighbor_index] = [
            min(link["available_bandwidth"] / link["capacity"], 1.0),
            min(link["delay"] / max_delay, 1.0),
            min(link["loss"], 1.0),
        ]

    visited = {int(node) for node in (visited_nodes or [])}
    action_mask = [False] * size
    available_neighbors = []
    for edge in outgoing[int(current_node)]:
        neighbor = edge["dst"]
        available_neighbors.append(neighbor)
        if neighbor not in visited or neighbor == int(destination_node):
            action_mask[index[neighbor]] = True

    # A stale path history should not make the categorical distribution empty.
    if not any(action_mask):
        for neighbor in available_neighbors:
            action_mask[index[neighbor]] = True

    destination_index = index[int(destination_node)]
    destination_feature = destination_index / float(max(size - 1, 1))
    deadline_feature = max(0.0, min(_finite(deadline_ms) / max(_finite(max_deadline_ms, 200.0), 1e-12), 1.0))

    return GARTObservation(
        node_ids=node_ids,
        node_features=node_features,
        adjacency=adjacency,
        action_mask=action_mask,
        flow_features=[destination_feature, deadline_feature],
        current_index=index[int(current_node)],
        destination_index=destination_index,
    )


def load_topology_edges(path):
    """Load the repository Topology.txt format as bidirectional link records."""
    with open(path, "r", encoding="utf-8") as handle:
        first = handle.readline().split()
        if len(first) < 2:
            raise ValueError("invalid topology header in %s" % path)
        _, edge_count = map(int, first[:2])
        edges = []
        for _ in range(edge_count):
            src, dst, delay, capacity, loss = handle.readline().split()[:5]
            record = {
                "src": int(src),
                "dst": int(dst),
                "delay": float(delay),
                "capacity": float(capacity),
                "available_bandwidth": float(capacity),
                "loss": float(loss),
            }
            edges.append(record)
            reverse = dict(record)
            reverse["src"], reverse["dst"] = record["dst"], record["src"]
            edges.append(reverse)
    return edges
