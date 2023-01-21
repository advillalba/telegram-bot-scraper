from importlib import reload
from unittest import TestCase
from unittest.mock import patch

from tests.mocks import jsonpath_payload, xpath_payload


@patch.dict('os.environ', {'TELEGRAM_BOT_KEY': '1234:abcd', 'OWNER_ID': '1'})
class ScraperFunctionTest(TestCase):
    def test_search_ok(self):
        scraper_functions = ScraperFunctionTest.reload()
        self.assertTrue(scraper_functions.search('test', 'test'))

    def test_search_fail(self):
        scraper_functions = ScraperFunctionTest.reload()
        self.assertFalse(scraper_functions.search('test', 'fail'))

    def test_jsonpath_ok(self):
        scraper_functions = ScraperFunctionTest.reload()
        query = "colors[0].values[?name == `red` && primary]"
        self.assertTrue(scraper_functions.jsonpath(jsonpath_payload, query))

    def test_jsonpath_fail(self):
        scraper_functions = ScraperFunctionTest.reload()
        query = "colors[0].values[?name == `blue` && primary]"
        self.assertFalse(scraper_functions.jsonpath(jsonpath_payload, query))

    def test_xpath_ok(self):
        scraper_functions = ScraperFunctionTest.reload()
        query = "/root/colors[1]/values[name = 'red' and primary='true']"
        self.assertTrue(scraper_functions.xpath(xpath_payload, query))

    @staticmethod
    def reload():
        from web_scraper.scraper import scraper_functions
        return reload(scraper_functions)
