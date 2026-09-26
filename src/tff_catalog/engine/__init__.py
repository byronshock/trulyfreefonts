"""The ranking engine (design-m1 §6, methodology §3-§6). Owners: agents P7 and P7b.

Pure functions over plain mappings: no I/O, no config loading and no clock, so
the property tests can drive them directly. ``surveys`` and ``confidence``
assemble them into ranks. Deterministic for the same inputs, whatever the
iteration order of the mappings passed in.
"""
