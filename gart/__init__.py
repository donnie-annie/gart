"""GART routing components described in the accompanying paper.

The lightweight modules exported here intentionally do not import PyTorch.  This
keeps configuration, reward, and observation utilities usable by controllers
and tests even when the training runtime is installed in a separate process.
"""

from .config import GARTConfig, PAPER_FLOW_PROFILES
from .rewards import DualRewardConfig, DualReward

__all__ = [
    "GARTConfig",
    "PAPER_FLOW_PROFILES",
    "DualRewardConfig",
    "DualReward",
]
