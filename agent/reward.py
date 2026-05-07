"""Plan E — programmatic reward injector."""
from typing import Optional
import numpy as np


class RewardChannel:
    """Programmatic reward injector. fire_positive / fire_negative inject a
    burst of vibrations at the reward port with explicit s_reward_polarity
    tag (+1 or -1). Atoms that bind from these vibrations carry the polarity
    via the k_reward_polarity propagation rule in bind_nodes_upward."""

    def __init__(
        self,
        port_origin: tuple[float, float, float] = (45.0, 45.0, 0.0),
        port_size: tuple[float, float, float] = (15.0, 15.0, 15.0),
        burst_size: int = 12,
        burst_freq: float = 30000.0,
        rng: Optional[np.random.Generator] = None,
    ):
        self.port_origin = port_origin
        self.port_size = port_size
        self.burst_size = burst_size
        self.burst_freq = burst_freq
        self.rng = rng if rng is not None else np.random.default_rng()

    def fire_positive(self, world) -> int:
        return self._fire(world, polarity=True, reward_polarity=1)

    def fire_negative(self, world) -> int:
        return self._fire(world, polarity=False, reward_polarity=-1)

    def _fire(self, world, polarity: bool, reward_polarity: int) -> int:
        free_idx = np.where(~world.s_alive)[0][:self.burst_size]
        n = len(free_idx)
        if n == 0:
            return 0
        for i in free_idx:
            world.s_pos[i] = (
                self.port_origin[0] + self.rng.random() * self.port_size[0],
                self.port_origin[1] + self.rng.random() * self.port_size[1],
                self.port_origin[2] + self.rng.random() * self.port_size[2],
            )
            world.s_vel[i] = 0.0
            world.s_freq[i] = float(self.burst_freq)
            world.s_pol[i] = polarity
            world.s_alive[i] = True
            world.s_reward_polarity[i] = reward_polarity
        if n > 0:
            world.n_alive = max(world.n_alive, int(free_idx.max()) + 1)
        return n

    def is_in_reward_port(self, position: np.ndarray) -> bool:
        ox, oy, oz = self.port_origin
        sx, sy, sz = self.port_size
        return (ox <= position[0] <= ox + sx
                and oy <= position[1] <= oy + sy
                and oz <= position[2] <= oz + sz)
