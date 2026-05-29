install:
	uv sync

run:
	uv run python pac-man.py config.json

clean:
	rm -rf __pycache__ .mypy_cache */**/__pycache__

lint:
	uv run flake8 . --exclude=.venv
	uv run mypy . --exclude=.venv

lint-strict:
	uv run flake8 . --exclude=.venv
	uv run mypy . --exclude=.venv --strict
