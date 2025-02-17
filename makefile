.PHONY: setup run lint

setup:
	@pip install -r requirements.txt

run:
	@uvicorn app.main:app --reload --port 8000


lint:
	@black app/
	@isort app/

clean:
	@find . -type d -name "__pycache__" -exec rm -r {} +
	@find . -type f -name "*.pyc" -delete