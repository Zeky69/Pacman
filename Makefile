.PHONY: install run debug clean build package lint lint-strict

install:
	uv sync

run:
	uv run python pac-man.py config.json

debug:
	uv run python -m pdb pac-man.py config.json

clean:
	rm -rf __pycache__ .mypy_cache */**/__pycache__ build dist .venv

# Compile l'exécutable autonome (Linux) dans dist/pacman/.
# On vide build/ et dist/ d'abord : pyinstaller écrase ses fichiers mais ne
# supprime pas les fichiers parasites laissés par d'anciens builds/tests.
build:
	rm -rf build dist
	uv run pyinstaller --clean --noconfirm pacman.spec

# Build complet prêt à publier sur itch.io : exécutable + config.json éditable
# posé à côté de l'exe + archive zip de tout le dossier.
package: build
	cp config.json dist/pacman/config.json
	cd dist && rm -f pacman-linux.zip && zip -r pacman-linux.zip pacman
	@echo "Archive prête : dist/pacman-linux.zip"

lint:
	uv run flake8 .
	uv run mypy . --exclude=.venv --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	uv run flake8 .
	uv run mypy . --exclude=.venv --strict
