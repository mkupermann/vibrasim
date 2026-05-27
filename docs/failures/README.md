# Deliberate Simplifications — What Each Module Ignores and Why

Each module in this project is the thinnest operational shell over a
deep field. This directory documents what was deliberately left out
and why. The purpose is not self-flagellation but a decision log:
knowing what you simplified helps you judge when the simplification
breaks.

Format: one file per major module/mechanism. Each answers:
1. What does a non-thin version require that we deliberately ignored?
2. What would break if the simplification is wrong?
3. Under what conditions should we revisit?
