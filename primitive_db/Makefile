.PHONY: install project lint build publish package-install

install:
	poetry install

project:
	poetry run project

lint:
	poetry run ruff check .
	poetry run mypy primitive_db tests

build:
	poetry build

publish:
	poetry publish --repository testpypi

package-install:
	pip install dist/*.whl
