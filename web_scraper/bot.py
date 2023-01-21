import json
import logging
import os.path

from web_scraper import BOT_OWNER, MESSAGE, BACKUP, CONSTANTS
from web_scraper.action import Status, CustomScraper, \
    DefaultScraper, JsonPathScraper, XPathScraper
from web_scraper.communication.telegram import Telegram
from web_scraper.scraper.scraper_engine import ScraperEngine
from web_scraper.utils import schedule

telegram = Telegram()
scraper_engine = ScraperEngine()


def start():
    logging.info('Starting bot')
    if BOT_OWNER is not None:
        telegram.send_message(BOT_OWNER, 'Bot started', silent=True)

    telegram.monitor()
    scraper_engine.monitor()
    __reload_scrapers()
    __process_actions()


@schedule(interval=1)
def __process_actions():
    __process_successful_actions()
    __process_pending_actions()
    __process_failed_actions()
    __process_warns_actions()


def __process_chat_success(action):
    if action.type == 'help':
        telegram.send_message(action.chat_id, MESSAGE['help'], silent=True)
    elif action.type == 'status':
        __send_status(action.chat_id)
    elif action.type.startswith('stop'):
        __stop_request(action)
    elif action.type.endswith('scraper'):
        __create_scraper(action)


def __process_pending_actions():
    while telegram.finished_conversations.qsize() > 0:
        action = telegram.finished_conversations.get()
        logging.debug(f'Processing pending actions {action}')
        if action.status == Status.CHAT_SUCCESS:
            __process_chat_success(action)
        elif action.status == Status.CHAT_FAILED:
            telegram.send_message(action.chat_id, MESSAGE['wrong_request'],
                                  silent=True)

        telegram.finished_conversations.task_done()


def __process_successful_actions():
    while scraper_engine.success.qsize() > 0:
        action = scraper_engine.success.get()
        message = MESSAGE['scraper_success'].format(user=action.user_name,
                                                    url=action.url)
        for i in range(0, 5):
            telegram.send_message(action.chat_id, message)
        scraper_engine.success.task_done()
        __backup_actions()


def __process_failed_actions():
    while scraper_engine.failed.qsize() > 0:
        action = scraper_engine.failed.get()
        message = MESSAGE['scraper_fail'].format(user=action.user_name,
                                                 url=action.url)
        telegram.send_message(action.chat_id, message)
        scraper_engine.failed.task_done()
        __backup_actions()


def __process_warns_actions():
    while scraper_engine.warns.qsize() > 0:
        action = scraper_engine.warns.get()
        message = MESSAGE['scraper_warn'] \
            .format(errors=action.errors,
                    limit=scraper_engine.error_limit,
                    url=action.url)
        telegram.send_message(action.chat_id, message, silent=True)
        scraper_engine.warns.task_done()


def __send_status(chat_id):
    actions = scraper_engine.get_actions(chat_id)
    if len(actions) > 0:
        message = MESSAGE['describe_current_scraper'].format(
            user=actions[0].user_name) + '\n'
        for action in actions:
            message += '\n' + MESSAGE['current_scraper'].format(
                interval=action.interval, url=action.url)

        telegram.send_message(chat_id, message, silent=True)
    else:
        telegram.send_message(chat_id, MESSAGE['no_scraper'], silent=True)


def __stop_request(stop_action):
    maybe_action_id = stop_action.type.split(' ')
    if len(maybe_action_id) == 1:
        __display_scrapers_to_stop(stop_action)
    else:
        action_id = maybe_action_id[1]
        if scraper_engine.is_monitoring_id(stop_action.chat_id, action_id):
            if len(maybe_action_id) == 2:
                __request_stop_confirmation(action_id, stop_action)
            elif len(maybe_action_id) == 3:
                confirmation = maybe_action_id[2]
                __stop_scraper(action_id, stop_action, confirmation)


def __create_scraper(action):
    if scraper_engine.is_monitoring_url(action.chat_id, action.url):
        message = MESSAGE['scraper_exists'].format(user=action.user_name,
                                                   interval=action.interval)
        telegram.send_message(action.chat_id, message, silent=True)
    else:
        logging.info(f'Starting scraper {action}')
        scraper_engine.add(action)
        __backup_actions()
        message = MESSAGE['scraper_start'].format(url=action.url,
                                                  interval=action.interval)
        telegram.send_message(action.chat_id, message, silent=True)


def __display_scrapers_to_stop(stop_action):
    actions = scraper_engine.get_actions(stop_action.chat_id)
    if len(actions) == 0:
        telegram.send_message(stop_action.chat_id, MESSAGE['no_scraper'],
                              silent=True)
    else:
        keyboard = {
            'inline_keyboard': [[{'text': action.url,
                                  'callback_data': f'stop {action.id}'}]
                                for action in actions]}
        telegram.send_keyboard(stop_action.chat_id,
                               MESSAGE['choose_scraper_stop'],
                               keyboard)


def __request_stop_confirmation(action_id, stop_action):
    keyboard_confirmation = {
        'inline_keyboard': [[{'text': CONSTANTS['yes'],
                              'callback_data': f'stop {action_id} yes'},
                             {'text': CONSTANTS['no'],
                              'callback_data': f'stop {action_id} no'}]]}
    telegram.send_keyboard(stop_action.chat_id,
                           MESSAGE['scraper_stop_confirmation'],
                           keyboard_confirmation)


def __stop_scraper(action_id, stop_action, confirmation):
    if confirmation == 'yes':
        logging.info(f'Stopping scraper {action_id}')
        action = scraper_engine.stop_monitoring(stop_action.chat_id,
                                                action_id)
        __backup_actions()
        telegram.send_message(action.chat_id,
                              MESSAGE['scraper_stop'].format(
                                  user=action.user_name,
                                  url=action.url))

    elif confirmation == 'no':
        telegram.send_message(stop_action.chat_id,
                              MESSAGE['scraper_stop_cancel'])


def __backup_actions():
    actions = scraper_engine.get_all_actions()
    with open(BACKUP, 'w') as file:
        json.dump([action.__dict__ for action in actions], file)


def __reload_scrapers():
    if os.path.exists(BACKUP):
        file = open(BACKUP)
        backup = json.load(file)
        file.close()
        logging.info(f'Reloading {len(backup)} scrapers')
        for payload in backup:
            if payload['type'] == 'default_scraper':
                action = DefaultScraper()
            elif payload['type'] == 'custom_scraper':
                action = CustomScraper()
            elif payload['type'] == 'json_scraper':
                action = JsonPathScraper()
            elif payload['type'] == 'xpath_scraper':
                action = XPathScraper()
            else:
                logging.error(f'Unknown action type {payload["type"]}')
                continue
            action.__dict__.update(payload)
            scraper_engine.add(action)
            logging.info(f'Starting scraper {action}')
