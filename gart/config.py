"""Paper-aligned configuration for GART.

Defaults mirror Table II and Table III of the GART paper.  Reward coefficients
that are defined symbolically, but not assigned numerical values in the paper,
remain explicit configuration fields instead of being hidden constants.
"""

from dataclasses import asdict, dataclass, fields


PAPER_FLOW_PROFILES = {
    "EU": {"proportion": 0.05, "deadline_ms": 20.0},
    "MU": {"proportion": 0.15, "deadline_ms": 50.0},
    "LU": {"proportion": 0.70, "deadline_ms": 100.0},
    "RT": {"proportion": 0.10, "deadline_ms": 200.0},
}


@dataclass(frozen=True)
class GARTConfig:
    """Model, PPO, and dual-reward settings from the paper."""

    node_feature_dim: int = 3  # capacity, delay, loss
    flow_feature_dim: int = 2  # normalized destination, deadline

    gat_layers: int = 2
    attention_heads: int = 4
    embedding_dim_per_head: int = 16
    gat_dropout: float = 0.1
    leaky_relu_slope: float = 0.2

    actor_hidden: tuple = (64, 64)
    critic_hidden: tuple = (64, 64)

    learning_rate: float = 1e-5
    discount_factor: float = 0.99
    gae_lambda: float = 0.95
    ppo_clip: float = 0.1
    ppo_epochs: int = 10
    rollout_length: int = 2048
    mini_batch_size: int = 64
    entropy_coefficient: float = 0.01
    value_loss_coefficient: float = 0.5
    max_gradient_norm: float = 0.5

    local_reward_weight: float = 0.5
    global_reward_weight: float = 0.5

    # Eq. (2) coefficients. The paper leaves these values configurable.
    loop_penalty: float = -1.0
    no_ack_penalty: float = -1.0
    residual_bandwidth_weight: float = 1.0

    # Eq. (3) coefficients alpha, beta, gamma, and epsilon.  The paper does
    # not publish their numerical values, so reproducible defaults are exposed.
    deadline_reward_weight: float = 1.0
    throughput_reward_weight: float = 1.0
    loss_penalty_weight: float = 1.0
    global_reward_bias: float = 0.0

    max_deadline_ms: float = 200.0

    @property
    def embedding_dim(self):
        return self.attention_heads * self.embedding_dim_per_head

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, values):
        values = dict(values or {})
        allowed = {item.name for item in fields(cls)}
        clean = {key: value for key, value in values.items() if key in allowed}
        for key in ("actor_hidden", "critic_hidden"):
            if key in clean:
                clean[key] = tuple(clean[key])
        return cls(**clean)
