import atexit
import logging
import signal

from web_scraper import bot


def main():
    atexit.register(__exit_handler)
    bot.start()
    signal.pause()


def __exit_handler():
    logging.error('Shutting down bot')


if __name__ == '__main__':
    main()
