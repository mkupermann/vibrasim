from world.state import World
from world.physics import tick, _largest_bridged_component
from tools.run_g31_membrane_channel import cfg

c = cfg(42)
w = World(c)
for t in range(1, 281):
    tick(w, c.dt)
    if t % 40 == 0:
        comp = _largest_bridged_component(w)
        nb = int(w.b_alive[: w.b_count].sum())
        print(f"tick {t}: largest_component={len(comp)} k_count={w.k_count} bridges={nb}", flush=True)
