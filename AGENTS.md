# Project Notes

- Always use the `rpimedia` virtual environment for Python project commands. The environment lives at `/home/mxc/.virtualenvs/rpimedia`.
- Files in `apps/remote` run on the QtPy under CircuitPython. Do not assume regular CPython-only libraries are available there.
- When adding CircuitPython dependencies for `apps/remote`, add them to `apps/remote/requirements-circuitpython.txt` so `invoke remote-libs` installs them to the board.
