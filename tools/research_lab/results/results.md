# Research lab results

Generated 2026-10-19T16:20:44.767699+00:00

## E1_LawR — score 1.00
- [PASS] `F1.1` peak |chi*| <= 0.5: observed=-0.15
- [PASS] `F1.2` left>0 and right<0: observed={'left': 116.13984168863166, 'right': -58.31464684012802}
- [PASS] `F1.3` peak-trough >= 5: observed=89.94999999998143
- [PASS] `F1.4` drive-off collapses peak: observed=0.0

## E2_Competition — score 1.00
- [PASS] `F2.1` feedback-on share gap >= 0.15: observed=0.5000000000000646
- [PASS] `F2.2` winner has higher captured income share: observed={'winner': 'A', 'capture_share_winner': 0.7, 'captured_A': 0.595, 'captured_B': 0.255}
- [PASS] `F2.3` cut feedback shrinks gap < 0.08: observed=0.0
- [PASS] `F2.4` swap flips ranking: observed={'base': 'A', 'swap': 'B'}

## E3_Lock — score 1.00
- [PASS] `F3.1` lock drop <= 0 vs no-lock: observed={'closed_deltas': [0.0, -39.94999999996934, -59.949999999979575, -69.94999999998328, -69.94999999998328, -79.94999999998129, -79.94999999998129], 'driven_deltas': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -8.181999999992556]}
- [PASS] `F3.2` closed-box drop >= driven drop: observed={'drop_closed': 79.94999999998129, 'drop_driven': 8.181999999992556}
- [PASS] `F3.3` conservative S >= dissipative at some k_f>0: observed={'cons_minus_diss': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 6.195]}
