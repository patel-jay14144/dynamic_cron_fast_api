start-server:
	uvicorn app:app --reload

sort-imports:
	poetry run isort .

format-code:
	poetry run black .