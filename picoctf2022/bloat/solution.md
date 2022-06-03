# Bloat

Inspecting the code, we can make some informed guesses at what the functions
are doing (see `readable.py`). From there it appears decoded the flag is
guarded by a check (see `if guess ==`). If we at a `breakpoint()` call just
before this we can easily print the right-hand-side of this expression and get
the desired value.
