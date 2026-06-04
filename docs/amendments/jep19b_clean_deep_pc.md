# JEP-19b — clean multi-layer PC vs backprop, MATCHED (isolate credit assignment)

## Fixes over JEP-19
- MATCHED: both learners use the SAME loss (MSE to one-hot), SAME activation (tanh), SAME optimizer (plain SGD,
  same lr). The ONLY difference is credit assignment: exact BACKPROP vs PREDICTIVE-CODING inference (local).
- Carefully re-derived hierarchical PC (input clamped, target clamped at top; relax hidden value nodes; local
  Hebbian weight updates). VALIDATE on MNIST first (must reach ~0.95 at 1- AND 2-hidden) before Fashion-MNIST.

## Pre-registration (locked BEFORE run)
- Datasets: MNIST (sanity) then Fashion-MNIST. Nets: 1-hidden (784-512-10) and 2-hidden (784-512-512-10).
- Bars: (sanity) backprop AND PC both >= 0.95 on MNIST at both depths -> implementation valid. Then on
  Fashion-MNIST: backprop >= 0.86 both depths; PC within 0.04 of backprop at EACH depth. PASS = local PC matches
  backprop with depth under a MATCHED comparison. PARTIAL if PC matches at 1-hidden but degrades at 2-hidden
  (then it is a real, fair depth finding). NULL if implementation still fails sanity. Predictive coding
  (Whittington-Bogacz 2017) established - named as such.
