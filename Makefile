# Makefile — A THIN WRAPPER. IT CONTAINS NO BUILD LOGIC, DELIBERATELY.
#
# CONTEXT.md §16: every target is one line that delegates to Python, so a reviewer with
# no `make` — on any OS — runs `python -m whetstone_gate.tasks <target>` and gets a
# byte-identical result. §20's "one command" box is satisfied by EITHER form, and the
# README documents both side by side.
#
# `make` is not on this machine's PATH by default. C0 installs a shim:
#     mkdir -p ~/bin && cp /c/MinGW/bin/mingw32-make.exe ~/bin/make.exe && make --version
# (~/bin is already first on PATH.) Verified 2026-08-30: GNU Make 3.82.90 runs a recipe.
#
# ⚠️ IF YOU ARE ABOUT TO ADD LOGIC HERE, PUT IT IN src/whetstone_gate/tasks.py INSTEAD.
# Logic in this file is logic a reviewer without `make` cannot run, which silently
# breaks the reproducibility claim in CONTEXT.md §20.

PYTHON ?= python

.PHONY: test eval selftest check-prereg check-roles help

help:
	@$(PYTHON) -m whetstone_gate.tasks --help

test:
	@$(PYTHON) -m whetstone_gate.tasks test

eval:
	@$(PYTHON) -m whetstone_gate.tasks eval

selftest:
	@$(PYTHON) -m whetstone_gate.tasks selftest

check-prereg:
	@$(PYTHON) -m whetstone_gate.tasks check-prereg

check-roles:
	@$(PYTHON) -m whetstone_gate.tasks check-roles
