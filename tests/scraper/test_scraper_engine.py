from importlib import reload
from unittest import TestCase
from unittest.mock import patch, MagicMock

from freezegun import freeze_time
from requests import HTTPError

from tests.mocks import mock_scraper, response_html


@patch.dict('os.environ', {'TELEGRAM_BOT_KEY': '1234:abcd', 'OWNER_ID': '1'})
@patch('web_scraper.utils.schedule', MagicMock(return_value=lambda x: x))
@freeze_time("2012-01-01 12:00:30")
class TestScraperEngine(TestCase):

    def test_add_new_scraper_with_none_existing(self):
        from web_scraper.action import Status
        scraper_module = TestScraperEngine.reload_module_class()
        scraper_engine = scraper_module.ScraperEngine()
        new_scraper = mock_scraper(Status.CHAT_SUCCESS)
        scraper_engine.add(new_scraper)
        new_scraper.status = Status.SCRAPER_IN_PROGRESS

        assert scraper_engine.in_progress == \
               {30: {123: {'https://www.random_website_a.com': new_scraper}}}

    def test_get_actions(self):
        from web_scraper.action import Status
        scraper_module = TestScraperEngine.reload_module_class()
        scraper_engine = scraper_module.ScraperEngine()
        new_scraper = mock_scraper(Status.CHAT_SUCCESS)
        scraper_engine.add(new_scraper)
        new_scraper.status = Status.SCRAPER_IN_PROGRESS
        actions = scraper_engine.get_actions(new_scraper.chat_id)
        assert actions == [new_scraper]

    def test_get_all_actions(self):
        from web_scraper.action import Status
        scraper_module = TestScraperEngine.reload_module_class()
        scraper_engine = scraper_module.ScraperEngine()
        new_scraper = mock_scraper(Status.CHAT_SUCCESS)
        scraper_engine.add(new_scraper)
        new_scraper.status = Status.SCRAPER_IN_PROGRESS
        actions = scraper_engine.get_all_actions()
        assert actions == [new_scraper]

    def test_is_monitoring_url(self):
        from web_scraper.action import Status
        scraper_module = TestScraperEngine.reload_module_class()
        scraper_engine = scraper_module.ScraperEngine()
        new_scraper = mock_scraper(Status.CHAT_SUCCESS)
        scraper_engine.add(new_scraper)
        assert scraper_engine.is_monitoring_url(new_scraper.chat_id,
                                                new_scraper.url)
        assert not scraper_engine.is_monitoring_url(new_scraper.chat_id,
                                                    'XX')

    def test_is_monitoring_id(self):
        from web_scraper.action import Status
        scraper_module = TestScraperEngine.reload_module_class()
        scraper_engine = scraper_module.ScraperEngine()
        new_scraper = mock_scraper(Status.CHAT_SUCCESS)
        scraper_engine.add(new_scraper)
        assert scraper_engine.is_monitoring_id(new_scraper.chat_id,
                                               new_scraper.id)
        assert not scraper_engine.is_monitoring_id(new_scraper.chat_id,
                                                   '14678')

    def test_stop_monitoring(self):
        from web_scraper.action import Status
        scraper_module = TestScraperEngine.reload_module_class()
        scraper_engine = scraper_module.ScraperEngine()
        new_scraper = mock_scraper(Status.CHAT_SUCCESS)
        scraper_engine.add(new_scraper)
        new_scraper.status = Status.SCRAPER_IN_PROGRESS
        assert scraper_engine.stop_monitoring(new_scraper.chat_id,
                                              new_scraper.id)
        assert len(scraper_engine.in_progress[new_scraper.interval][
                       new_scraper.chat_id]) == 0

    @patch('requests.get', MagicMock(return_value=response_html))
    def test_monitor(self):
        from web_scraper.action import Status
        scraper_module = TestScraperEngine.reload_module_class()
        scraper_engine = scraper_module.ScraperEngine()
        new_scraper = mock_scraper(Status.CHAT_SUCCESS)
        scraper_engine.add(new_scraper)
        new_scraper.status = Status.SCRAPER_IN_PROGRESS
        scraper_engine.monitor()
        assert scraper_engine.success.qsize() == 1

    @patch('requests.get', MagicMock(side_effect=HTTPError))
    def test_max_errors(self):
        from web_scraper.action import Status
        scraper_module = TestScraperEngine.reload_module_class()
        scraper_engine = scraper_module.ScraperEngine()
        scraper_engine.error_limit = 1
        new_scraper = mock_scraper(Status.CHAT_SUCCESS)
        scraper_engine.add(new_scraper)
        new_scraper.status = Status.SCRAPER_IN_PROGRESS
        scraper_engine.monitor()
        assert scraper_engine.failed.qsize() == 1

    @staticmethod
    def reload_module_class():
        from web_scraper.scraper import scraper_engine
        reload(scraper_engine)
        return scraper_engine
