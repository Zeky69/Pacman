install:
	uv sync

run:
	uv run python pac-man.py config.json

debug:
	uv run python -m pdb pac-man.py config.json

clean:
	rm -rf __pycache__ .mypy_cache */**/__pycache__

lint:
	uv run flake8 .
	uv run mypy . --exclude=.venv --exclude=debug --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	uv run flake8 .
	uv run mypy . --exclude=.venv --exclude=debug --strict
