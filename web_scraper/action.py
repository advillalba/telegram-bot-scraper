import re
from enum import Enum
from uuid import uuid4

from web_scraper import QUESTION


class Status(str, Enum):
    CHAT_IN_PROGRESS = 'CHAT_IN_PROGRESS'
    CHAT_SUCCESS = 'CHAT_SUCCESS'
    CHAT_FAILED = 'CHAT_FAILED'
    SCRAPER_IN_PROGRESS = 'scraper_IN_PROGRESS'
    SCRAPER_SUCCESS = 'scraper_SUCCESS'
    SCRAPER_ERROR = 'scraper_ERROR'


class Action:
    question = QUESTION['start']

    def __init__(self, chat_id: int, chat_name: str, user_id: int,
                 user_name: str, **kwargs):
        self.id = str(uuid4())

        self.chat_id = chat_id
        self.chat_name = chat_name
        self.user_id = user_id
        self.user_name = user_name
        self.status = Status.CHAT_IN_PROGRESS
        self.errors = 0
        self.new_child_class = None
        self.type = 'generic'

    def validate_question(self, text: str):
        if re.match(self.question['validation'], text):
            if text == 'help' or text == 'status' or text.startswith('stop'):
                self.status = Status.CHAT_SUCCESS
                self.type = text
            elif text == 'new_scraper':
                self.new_child_class = Scraper
        else:
            self.errors += 1

    def is_finished(self):
        return self.status != Status.CHAT_IN_PROGRESS


class Scraper(Action):

    def __init__(self, scraper):
        super().__init__(**scraper.__dict__)
        if isinstance(scraper, Scraper):
            self.url = scraper.url
            self.interval = scraper.interval
            self.scraper_function = scraper.scraper_function
        else:
            self.url = None
            self.interval = None
            self.scraper_function = None
        self.question = QUESTION['interval']
        self.type = 'scraper'

    def validate_question(self, text: str):
        if text is None or re.match(self.question['validation'],
                                    str(text)) is None:
            self.errors += 1
            if self.errors >= 3:
                self.status = Status.CHAT_FAILED
        else:
            if self.question['id'] == 'interval':
                self.interval = int(text)
                self.question = QUESTION['url']
            elif self.question['id'] == 'url':
                self.url = re.search(self.question['validation'], text).group(
                    1)
                self.question = QUESTION['scraper_type']
            elif self.question['id'] == 'scraper_type':
                if text == 'default_scraper':
                    self.new_child_class = DefaultScraper
                elif text == 'custom_scraper':
                    self.new_child_class = CustomScraper
                elif text == 'jsonpath_scraper':
                    self.new_child_class = JsonPathScraper
                elif text == 'xpath_scraper':
                    self.new_child_class = XPathScraper
                self.errors = 0


class DefaultScraper(Scraper):
    def __init__(self, scraper: Scraper = None):
        if scraper is not None:
            super().__init__(scraper)
            self.question = QUESTION['default_scraper']
        self.type = 'default_scraper'

    def validate_question(self, text: str):
        if re.match(self.question['validation'], text) is not None:
            self.status = Status.CHAT_SUCCESS
            self.scraper_function = text
            self.errors = 0
        else:
            self.errors += 1
            if self.errors >= 3:
                self.status = Status.CHAT_FAILED

    def __str__(self):
        return f'DefaultScraper(' \
               f'url={self.url}, ' \
               f'interval={self.interval}, ' \
               f'scraper_function={self.scraper_function})'


class CustomScraper(Scraper):
    def __init__(self, scraper: Scraper = None):
        if scraper is not None:
            super().__init__(scraper)
            self.query = None
            self.scraper_function = 'custom_scraper'
            self.question = QUESTION['text_to_find']
        self.type = 'custom_scraper'

    def validate_question(self, text: str):
        self.query = text
        self.status = Status.CHAT_SUCCESS

    def __str__(self):
        return f'Customscraper(' \
               f'url={self.url}, ' \
               f'interval={self.interval}, ' \
               f'query={self.query})'


class JsonPathScraper(Scraper):
    def __init__(self, scraper: Scraper = None):
        if scraper is not None:
            super().__init__(scraper)
            self.query = None
            self.scraper_function = 'jsonpath'
            self.question = QUESTION['query']
        self.type = 'json_scraper'

    def validate_question(self, query: str):
        self.query = query
        self.status = Status.CHAT_SUCCESS

    def __str__(self):
        return f'Jsonscraper(' \
               f'url={self.url}, ' \
               f'interval={self.interval}, ' \
               f'query={self.query})'


class XPathScraper(Scraper):
    def __init__(self, scraper: Scraper = None):
        if scraper is not None:
            super().__init__(scraper)
            self.query = None
            self.scraper_function = 'xpath'
            self.question = QUESTION['query']
        self.type = 'xml_scraper'

    def validate_question(self, query: str):
        self.query = query
        self.status = Status.CHAT_SUCCESS

    def __str__(self):
        return f'Xmlscraper(' \
               f'url={self.url}, ' \
               f'interval={self.interval}, ' \
               f'query={self.query})'
