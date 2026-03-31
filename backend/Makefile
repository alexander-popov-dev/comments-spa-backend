.PHONY: install test lint lint-fix migrate makemigrations shell

test:
	poetry run pytest

lint:
	poetry run ruff check .

lint-fix:
	poetry run ruff check --fix .

migrate:
	poetry run python manage.py migrate

makemigrations:
	poetry run python manage.py makemigrations

shell:
	poetry run python manage.py shell
