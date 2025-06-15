.PHONY: run black ruff mypy

run:
	cd app && flask run

black:
	black app

ruff:
	ruff check app --fix

mypy:
	mypy app