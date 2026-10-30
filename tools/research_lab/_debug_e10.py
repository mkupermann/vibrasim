import sys
sys.path.insert(0, "tools/research_lab")
from core import make_state, step_law_R, N_STEPS

chis = [-0.8, -0.5, -0.3, -0.15, 0.0, 0.15, 0.3, 0.5, 0.8, 1.2]
seeds = range(350, 353)


def curve(rectified, drive_on):
    out = []
    for chi in chis:
        vals = []
        for seed in seeds:
            s = make_state(seed)
            for _ in range(N_STEPS):
                step_law_R(s, chi, drive_on=drive_on, rectified=rectified)
            vals.append(s.bond_time)
        out.append(sum(vals) / len(vals))
    return out


rect_on = curve(True, True)
signed_on = curve(False, True)
rect_off = curve(True, False)
signed_off = curve(False, False)


def spread(v):
    return max(v) - min(v)


def peak(v):
    return chis[v.index(max(v))]


print("chis     ", chis)
print("rect_on  ", [round(x, 1) for x in rect_on])
print("signed_on", [round(x, 1) for x in signed_on])
print("rect_off ", [round(x, 1) for x in rect_off])
print("signed_off", [round(x, 1) for x in signed_off])
print("F10.1 rect spread", round(spread(rect_on), 2), spread(rect_on) >= 5)
print("F10.2 signed spread", round(spread(signed_on), 2), spread(signed_on) >= 5)
print("F10.3 peaks", peak(rect_on), peak(signed_on),
      abs(peak(rect_on)) <= 0.5, abs(peak(signed_on)) <= 0.5)
print("F10.4 off spreads", round(spread(rect_off), 2), round(spread(signed_off), 2),
      spread(rect_off) < 2, spread(signed_off) < 2)
