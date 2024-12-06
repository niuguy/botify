install:
	uv pip install -e .
run:
	python -m botify.main
format:
	ruff check . --fix
	ruff format .
