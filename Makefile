install:
	pip install -r requirements_test.txt

test:
	python -m unittest discover -s ./tests -t ./tests

test-with-coverage:
	coverage run -m unittest discover -s ./tests -t ./tests
	coverage report -m

lint:
	flake8 app.py web_scraper/ tests/

run:
	python app.py

build-image:
	docker build -t telegram-bot-scraper .



