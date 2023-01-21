import hashlib
import json
import logging
import urllib.parse
from queue import Queue

import requests

from web_scraper import CONSTANTS, BOT_KEY
from web_scraper.action import Action
from web_scraper.utils import schedule


class Telegram:
    _url = 'https://api.telegram.org'

    def __init__(self) -> None:
        logging.info('Starting Telegram')
        self._bot_name = requests.get(f'{self.url}/getMe').json()['result'][
            'username']
        self.finished_conversations = Queue()
        self._offset = 0
        self._conversations: dict[str, Action] = {}

    @property
    def url(self):
        return f'{self._url}/bot{BOT_KEY}'

    @property
    def send_message_url(self):
        return f'{self.url}/sendMessage'

    @schedule(interval=1)
    def monitor(self):
        self.__get_updates()

    def send_message(self, chat_id: int, message: str,
                     silent: bool = False) -> None:
        chat = f'chat_id={chat_id}'
        text = f'text={urllib.parse.quote(message)}'
        notification = f'disable_notification={str(silent).lower()}'
        requests.get(f'{self.send_message_url}?&{chat}&{text}&{notification}')

    def send_keyboard(self, chat_id: int, message: str,
                      keyboard: dict) -> None:
        chat = f'chat_id={chat_id}'
        text = f'text={urllib.parse.quote(message)}'
        markup = f'reply_markup={json.dumps(keyboard)}'
        notification = 'disable_notification=true'
        requests.get(
            f'{self.send_message_url}?&{chat}&{text}&{markup}&{notification}')

    def __get_updates(self):
        url = f'{self.url}/getUpdates?offset={self._offset}'

        try:
            response = requests.get(url).json()
        except Exception as e:
            logging.error(f'Error getting updates: {e}')
            response = None
        if response is not None and 'result' in response and len(
                response['result']) > 0:
            logging.debug(response)
            for result in response['result']:
                self._offset = result['update_id'] + 1
                if Telegram.__is_message(result):
                    self._message(result)
                elif 'callback_query' in result:
                    self.__callback(result)

    def _message(self, result: dict):
        message = result['message']
        chat_name = message['chat']['title'] if 'title' in message[
            'chat'] else 'Private'
        self.__process_message(chat_id=message['chat']['id'],
                               user_id=message['from']['id'],
                               chat_name=chat_name,
                               user=message['from']['username'],
                               text=message['text'])

    def __callback(self, result):
        message = result['callback_query']['message']

        chat_name = Telegram.__get_chat_name(message, result)

        self.__process_message(chat_id=message['chat']['id'],
                               user_id=result['callback_query']['from']['id'],
                               chat_name=chat_name,
                               user=result['callback_query']['from'][
                                   'username'],
                               text=result['callback_query']['data'])

    def __process_message(self, chat_id: int, user_id: int, chat_name: str,
                          user: str, text: str):
        key = Telegram.__conversation_key(chat_id, user_id)

        if key in self._conversations:
            action = self._conversations[key]
        else:
            action = Action(chat_id, chat_name, user_id, user)
            self._conversations[key] = action

        if Telegram.__validate_and_finish_action(action, text):
            self.finished_conversations.put(self._conversations.pop(key))
        else:
            if action.new_child_class is not None:
                action = action.new_child_class(action)
                self._conversations[key] = action
            self.__send_question(action)

    def __send_question(self, action: Action):
        if action.errors > 0:
            message = action.question['error_message']
        else:
            message = action.question['text']

        self.send_keyboard(action.chat_id, message,
                           action.question['options'])

    @staticmethod
    def __conversation_key(chat_id, user_id):
        return hashlib.md5(str({"chat_id": chat_id, "user_id": user_id})
                           .encode('UTF-8')).hexdigest()

    @staticmethod
    def __is_message(message):
        return 'message' in message and 'text' in message['message']

    @classmethod
    def __get_chat_name(cls, message, result):
        if 'title' in result['callback_query']['message']['chat']:
            return message['chat']['title']
        else:
            return CONSTANTS['private']

    @staticmethod
    def __validate_and_finish_action(action, text):
        action.validate_question(text)
        return action.is_finished()
