from unittest import TestCase
from unittest.mock import patch

from tests.mocks import action_start


@patch.dict('os.environ', {'OWNER_ID': '123'})
class ActionTest(TestCase):
    def test_no_valid_scraper(self):
        from web_scraper.action import Scraper
        scraper = Scraper(action_start())
        scraper.validate_question('40')
        scraper.validate_question('40')
        scraper.validate_question('40')
        assert scraper.status == 'CHAT_FAILED'

    def test_ask_interval_and_url_and_scraper_type(self):
        from web_scraper.action import Scraper, DefaultScraper
        from web_scraper import QUESTION
        scraper = Scraper(action_start())
        scraper.question = QUESTION['interval']
        scraper.validate_question('30')
        scraper.validate_question('https://www.random_website_a.com')
        scraper.validate_question('default_scraper')
        assert scraper.new_child_class is DefaultScraper

    def test_ask_interval_and_url_and_custom_type(self):
        from web_scraper.action import Scraper, CustomScraper
        scraper = Scraper(action_start())
        scraper.validate_question('30')
        scraper.validate_question('https://www.random_website_a.com')
        scraper.validate_question('custom_scraper')
        assert scraper.new_child_class is CustomScraper

    def test_default_scraper(self):
        from web_scraper.action import DefaultScraper
        scraper = DefaultScraper(action_start())
        scraper.validate_question('to_do')
        assert scraper.status == 'CHAT_SUCCESS'

    def test_default_scraper_error(self):
        from web_scraper.action import DefaultScraper
        scraper = DefaultScraper(action_start())
        scraper.validate_question('to_d')
        scraper.validate_question('to_d')
        scraper.validate_question('to_d')
        assert scraper.status == 'CHAT_FAILED'

    def test_custom_scraper(self):
        from web_scraper.action import CustomScraper
        scraper = CustomScraper(action_start())
        scraper.validate_question('search_text')
        print(scraper)
        assert scraper.status == 'CHAT_SUCCESS'

    def test_json_scraper(self):
        from web_scraper.action import JsonPathScraper
        scraper = JsonPathScraper(action_start())
        scraper.validate_question('query')
        assert scraper.status == 'CHAT_SUCCESS'

    def test_xml_scraper(self):
        from web_scraper.action import XPathScraper
        scraper = XPathScraper(action_start())
        scraper.validate_question('query')
        assert scraper.status == 'CHAT_SUCCESS'
