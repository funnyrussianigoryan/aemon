lint:
	ruff check aemon

fix:
	ruff check aemon --fix

fix-tests:
	ruff check tests --fix

type:
	mypy aemon

test:
	pytest

clean:
	rm -rf .pytest_cache/ __pycache__/ build/ dist/ *.egg-info/ .mypy_cache/
