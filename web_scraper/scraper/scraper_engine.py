import concurrent
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from queue import Queue
from threading import Thread

import requests


from web_scraper.action import Scraper, Status
from web_scraper.scraper.scraper_functions import scraper_functions
from web_scraper.utils import schedule


class ScraperEngine:
    error_limit = 10

    def __init__(self):
        logging.info('Starting scraper')
        self.in_progress = {}
        self.success = Queue()
        self.failed = Queue()
        self.warns = Queue()

    @schedule(interval=1)
    def monitor(self):
        for interval, chats in self.in_progress.items():
            if len(chats) > 0 and ScraperEngine.__mod_seconds(interval):
                Thread(target=self.__apply_monitors, args=(chats,)).run()

    def add(self, action: Scraper):
        logging.debug(f'Adding {action.url} to scrapping')
        if action.interval not in self.in_progress:
            self.in_progress[action.interval] = {}
        if action.chat_id not in self.in_progress[action.interval]:
            self.in_progress[action.interval][action.chat_id] = {}
            action.question = {}
        action.status = Status.SCRAPER_IN_PROGRESS
        self.in_progress[action.interval][action.chat_id][action.url] = action

    def get_actions(self, chat_id) -> list[Scraper]:
        actions = []
        for interval, chats in self.in_progress.items():
            if chat_id in chats:
                actions.extend(chats[chat_id].values())
        return actions

    def get_all_actions(self):
        actions = []
        for chats in self.in_progress.values():
            for chat, in_progress_actions in chats.items():
                actions.extend(in_progress_actions.values())

        return actions

    def is_monitoring_url(self, chat_id, url) -> bool:
        for chats in self.in_progress.values():
            for chat, actions in chats.items():
                if chat == chat_id:
                    for action in actions.values():
                        if action.url == url:
                            return True
        return False

    def is_monitoring_id(self, chat_id: int, action_id: str) -> bool:
        actions = self.get_actions(chat_id)
        for action in actions:
            if action.id == action_id:
                return True
        return False

    def stop_monitoring(self, chat_id: int, action_id: str):
        logging.debug(f'Stopping monitoring {action_id}')
        actions = self.get_actions(chat_id)
        for action in actions:
            if action.id == action_id:
                interval = action.interval
                return self.in_progress[interval][chat_id].pop(action.url)

    @staticmethod
    def __mod_seconds(interval: int):
        now = datetime.now()
        minutes = int(now.strftime('%M'))
        seconds = int(now.strftime('%S'))
        mod = ((minutes * 60) + seconds) % int(interval) == 0
        return mod

    def __apply_monitors(self, chats):
        with ThreadPoolExecutor(max_workers=5) as executor:
            for chat in chats.values():
                responses = {}
                for action in chat.values():
                    responses[executor.submit(self.__run, action)] = action
                for future in concurrent.futures.as_completed(responses):
                    action: Scraper = future.result()
                    interval = action.interval
                    chat_id = action.chat_id
                    url = action.url
                    if action.status == Status.SCRAPER_SUCCESS:
                        logging.info(f'Success scrapping {url}')
                        self.in_progress[interval][chat_id].pop(url)
                        self.success.put(action)
                    else:
                        if action.errors >= self.error_limit:
                            logging.error(f'Failed scrapping {url}')
                            self.in_progress[interval][chat_id].pop(url)
                            self.failed.put(action)

    def __run(self, action):
        try:
            response = requests.get(action.url)
            scrap = scraper_functions[action.scraper_function.lower()]
            if action.type == 'default_scraper':
                success = scrap(response.text)
            else:
                success = scrap(response.text, action.query)
            action.errors = 0
            if success:
                action.status = Status.SCRAPER_SUCCESS
        except Exception as e:
            logging.warning(f'Error while scrapping {action.url}: {e}')
            action.errors += 1
            self.warns.put(action)
        return action
