# Telegram WebScraper

This is a Telegram Bot that scrapes the web and alerts you when something
changes.
It offers the possibility to search for a specific term in the given website,
to use a custom XPath expression to extract the data,
to use a JsonPath expression to connect an API or you can build your own
functions to extract the data and create alerts.

## How to use

1. Create a Telegram Bot and get the
   token. [Guide](https://core.telegram.org/bots#6-botfather)
2. Build the Docker image.

```bash
docker build -t telegram-bot-scraper .

```

3. Run the Docker image, you have to pass your Telegram Bot Key.

```bash
docker run -d -e TELEGRAM_BOT_KEY={YOUR_KEY}  telegram-bot-scraper
```

Environment variables to configure the bot:

* **TELEGRAM_BOT_KEY**(*Mandatory*): Telegram Bot Key,
* **OWNER_ID**(*Optional*): Telegram user id of the owner of the bot, if set
  the bot will message the owner on bot start.
* **BACKUP_PATH**(*Optional*): Path to the backup file, if set the bot will
  save the working scrapers in the given path.

4. Example with all environment variables:

```bash
docker run -d -v ~/volumes/scraper/:/app/shared -e TELEGRAM_BOT_KEY={YOUR_KEY} \
  -e OWNER_ID={YOUR_USER_ID} -e BACKUP_PATH=/app/shared \
  --name telegram-bot-scraper telegram-bot-scraper

```

## Add custom functions

To add new scraper functions, modify this files:

* web_scraper/resources/questions.yml: From `default_scraper` modify the inline
  keyboard and validation.
* web_scraper/scraper/scraper_functions.py: Add your custom functions and
  modify `scraper_functions` dictionary, the key is the inline_keyboard
  callback.