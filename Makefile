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
	docker build -t scraper .

start-image:
	- docker stop scraper
	- docker rm scraper
	docker run -d --name scraper\
			-e TELEGRAM_BOT_KEY=${TELEGRAM_BOT_KEY} \
			-e OWNER_ID=${TELEGRAM_BOT_OWNER} \
			-e BACKUP_PATH="/shared" \
			-e LOG_PATH="/shared" \
			-v ~/volumes/scraper/:/shared/ scraper