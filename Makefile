# Purpose: one-word commands to test, lint and regenerate every example output.
# Book: National AI Strategy in Practice, Chapters 2-12 (all tools)
# Licence: MIT (see LICENSE)
#
#   make install   install the pinned dependencies
#   make test      run the test suite
#   make lint      run the linter
#   make examples  run every tool and save its output in examples/*.md

PYTHON ?= python3

.PHONY: install test lint examples all

all: lint test examples

install:
	$(PYTHON) -m pip install PyYAML==6.0.3 openpyxl==3.1.5 pytest==9.1.1 ruff==0.17.1

test:
	$(PYTHON) -m pytest -q

lint:
	$(PYTHON) -m ruff check .

examples:
	mkdir -p examples
	$(PYTHON) readiness/score.py readiness/example-assessment.yaml > examples/readiness.md
	$(PYTHON) portfolio/score_portfolio.py portfolio/use_cases.example.csv > examples/portfolio.md
	$(PYTHON) planner/compute_planner.py > examples/planner.md
	$(PYTHON) finance/build_budget.py > examples/budget.md
	$(PYTHON) kpi/report.py kpi/example-values.yaml > examples/kpi.md
	@echo "Example outputs written to examples/"
