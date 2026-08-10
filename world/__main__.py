"""Allows `python -m world` invocation.

Default substrate: Flux (F0-F1c). Use `--substrate legacy` for the original (feature-frozen; belief-path lab).
"""
import sys
from world.run import main

sys.exit(main())
