import logging
import os
from logging import StreamHandler, INFO
from os.path import join

import yaml

BACKUP = os.getenv('BACKUP_PATH', default='.') + '/in_progress_actions.json'
BOT_KEY = os.environ['TELEGRAM_BOT_KEY']
BOT_OWNER = os.getenv('OWNER_ID', default=None)

current_path = os.path.dirname(__file__)

_file_questions = open(join(current_path, 'resources', 'questions.yml'), 'r')
QUESTION = yaml.load(_file_questions, Loader=yaml.FullLoader)
_file_questions.close()

_file_messages = open(join(current_path, 'resources', 'messages.yml'))
MESSAGE = yaml.load(_file_messages, Loader=yaml.FullLoader)
_file_messages.close()

__file_actions = open(join(current_path, 'resources', 'constants.yml'))
CONSTANTS = yaml.load(__file_actions, Loader=yaml.FullLoader)
__file_actions.close()


def __configure_logging():
    logging_handlers = [StreamHandler()]
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=INFO, handlers=logging_handlers,
                        format=log_format)


__configure_logging()
