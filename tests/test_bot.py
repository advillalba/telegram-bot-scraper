from importlib import reload
from queue import Queue
from unittest import TestCase
from unittest.mock import patch, MagicMock, call, mock_open

from tests.mocks import mock_scraper, mock_final_action


@patch.dict('os.environ', {'OWNER_ID': '123'})
@patch('web_scraper.utils.schedule', MagicMock(return_value=lambda x: x))
@patch('builtins.open', mock_open(read_data="data"))
@patch('json.dumps', MagicMock(return_value={}))
@patch('json.load', MagicMock(return_value={}))
class BotTest(TestCase):
    @patch('web_scraper.scraper.scraper_engine.ScraperEngine')
    @patch('web_scraper.communication.telegram.Telegram')
    def test_bot_wrong_request(self, telegram_class, scraper_class):
        from web_scraper import MESSAGE
        from web_scraper.action import Status
        bot = BotTest.reload_bot()
        telegram, scraper = BotTest.reload_mocks(telegram_class,
                                                 scraper_class)

        action = mock_final_action('dasd')
        action.status = Status.CHAT_FAILED

        telegram.finished_conversations.put(action)

        help_message = MESSAGE['wrong_request']

        bot.start()
        telegram.send_message.assert_called_with(123, help_message,
                                                 silent=True)

    @patch('web_scraper.scraper.scraper_engine.ScraperEngine')
    @patch('web_scraper.communication.telegram.Telegram')
    def test_bot_help(self, telegram_class, scraper_class):
        from web_scraper import MESSAGE
        bot = BotTest.reload_bot()
        telegram, scraper = BotTest.reload_mocks(telegram_class,
                                                 scraper_class)

        help_action = mock_final_action('help')
        telegram.finished_conversations.put(help_action)

        help_message = MESSAGE['help']

        bot.start()
        telegram.send_message.assert_called_with(123, help_message,
                                                 silent=True)

    @patch('web_scraper.scraper.scraper_engine.ScraperEngine')
    @patch('web_scraper.communication.telegram.Telegram')
    def test_bot_status(self, telegram_class, scraper_class):
        from web_scraper.action import Status
        from web_scraper import MESSAGE
        bot = BotTest.reload_bot()
        telegram, scraper = BotTest.reload_mocks(telegram_class,
                                                 scraper_class)

        status_action = mock_final_action('status')
        telegram.finished_conversations.put(status_action)

        in_progress_scraper = mock_scraper(Status.SCRAPER_IN_PROGRESS)
        scraper.get_actions.return_value = [in_progress_scraper]

        message = MESSAGE['describe_current_scraper'].format(
            user=in_progress_scraper.user_name) + "\n\n"
        message += MESSAGE['current_scraper'].format(
            interval=in_progress_scraper.interval,
            url=in_progress_scraper.url)
        bot.start()
        scraper.get_actions.assert_called_with(123)
        telegram.send_message.assert_called_with(123, message, silent=True)

    @patch('web_scraper.scraper.scraper_engine.ScraperEngine')
    @patch('web_scraper.communication.telegram.Telegram')
    def test_bot_status_no_scrapers(self, telegram_class, scraper_class):
        from web_scraper import MESSAGE
        bot = BotTest.reload_bot()
        telegram, scraper = BotTest.reload_mocks(telegram_class,
                                                 scraper_class)

        status_action = mock_final_action('status')
        telegram.finished_conversations.put(status_action)

        scraper.get_actions.return_value = []

        message = MESSAGE['no_scraper']
        bot.start()
        scraper.get_actions.assert_called_with(123)
        telegram.send_message.assert_called_with(123, message, silent=True)

    @patch('web_scraper.scraper.scraper_engine.ScraperEngine')
    @patch('web_scraper.communication.telegram.Telegram')
    def test_bot_new_scraper(self, telegram_class, scraper_class):
        from web_scraper import MESSAGE
        from web_scraper.action import Status
        bot = BotTest.reload_bot()
        telegram, scraper = BotTest.reload_mocks(telegram_class,
                                                 scraper_class)

        new_scraper = mock_scraper(Status.CHAT_SUCCESS)
        telegram.finished_conversations.put(new_scraper)

        scraper.is_monitoring_url.return_value = False
        new_scraper_message = MESSAGE['scraper_start'].format(
            url='https://www.random_website_a.com',
            interval=30)

        bot.start()
        telegram.send_message.assert_called_with(123, new_scraper_message,
                                                 silent=True)

        scraper.is_monitoring_url \
            .assert_called_with(123, 'https://www.random_website_a.com')
        scraper.add.assert_called_with(new_scraper)

    @patch('web_scraper.scraper.scraper_engine.ScraperEngine')
    @patch('web_scraper.communication.telegram.Telegram')
    def test_bot_new_scraper_exists(self, telegram_class, scraper_class):
        from web_scraper import MESSAGE
        from web_scraper.action import Status
        bot = BotTest.reload_bot()
        telegram, scraper = BotTest.reload_mocks(telegram_class,
                                                 scraper_class)

        new_scraper = mock_scraper(Status.CHAT_SUCCESS)
        telegram.finished_conversations.put(new_scraper)

        scraper.is_monitoring_url.return_value = True
        scraper_exists = MESSAGE['scraper_exists'].format(
            user=new_scraper.user_name,
            interval=30)

        bot.start()
        telegram.send_message.assert_called_with(123, scraper_exists,
                                                 silent=True)

        scraper.is_monitoring_url \
            .assert_called_with(123, 'https://www.random_website_a.com')
        assert not scraper.add.called

    @patch('web_scraper.scraper.scraper_engine.ScraperEngine')
    @patch('web_scraper.communication.telegram.Telegram')
    def test_bot_scraper_success(self, telegram_class, scraper_class):
        from web_scraper import MESSAGE
        from web_scraper.action import Status
        bot = BotTest.reload_bot()
        telegram, scraper = BotTest.reload_mocks(telegram_class,
                                                 scraper_class)
        scraper_success = mock_scraper(Status.SCRAPER_SUCCESS)
        scraper.success.put(scraper_success)

        success_message = MESSAGE['scraper_success'].format(
            user=scraper_success.user_name,
            url='https://www.random_website_a.com')

        bot.start()
        telegram.send_message.assert_has_calls(
            [call(123, success_message)] * 5)

    @patch('web_scraper.scraper.scraper_engine.ScraperEngine')
    @patch('web_scraper.communication.telegram.Telegram')
    def test_bot_scraper_error(self, telegram_class, scraper_class):
        from web_scraper import MESSAGE
        from web_scraper.action import Status
        bot = BotTest.reload_bot()
        telegram, scraper = BotTest.reload_mocks(telegram_class,
                                                 scraper_class)

        scraper_error = mock_scraper(Status.SCRAPER_ERROR)
        scraper.failed.put(scraper_error)

        error_message = MESSAGE['scraper_fail'].format(
            user=scraper_error.user_name,
            url='https://www.random_website_a.com')

        bot.start()
        telegram.send_message.assert_called_with(123, error_message)

    @patch('web_scraper.scraper.scraper_engine.ScraperEngine')
    @patch('web_scraper.communication.telegram.Telegram')
    def test_bot_scraper_warn(self, telegram_class, scraper_class):
        from web_scraper import MESSAGE
        from web_scraper.action import Status
        bot = BotTest.reload_bot()
        telegram, scraper = BotTest.reload_mocks(telegram_class,
                                                 scraper_class)
        scraper.error_limit = 10
        scraper_error = mock_scraper(Status.SCRAPER_IN_PROGRESS)
        scraper_error.errors = 1
        scraper.warns.put(scraper_error)

        warn_message = MESSAGE['scraper_warn'].format(
            errors=1,
            limit=10,
            url='https://www.random_website_a.com')

        bot.start()
        telegram.send_message.assert_called_with(123, warn_message,
                                                 silent=True)

    @patch('web_scraper.scraper.scraper_engine.ScraperEngine')
    @patch('web_scraper.communication.telegram.Telegram')
    def test_bot_stop_no_scrapers(self, telegram_class, scraper_class):
        from web_scraper import MESSAGE
        bot = BotTest.reload_bot()
        telegram, scraper = BotTest.reload_mocks(telegram_class,
                                                 scraper_class)

        status_action = mock_final_action('stop')
        telegram.finished_conversations.put(status_action)

        scraper.get_actions.return_value = []

        message = MESSAGE['no_scraper']
        bot.start()
        telegram.send_message.assert_called_with(123, message, silent=True)

    @patch('web_scraper.scraper.scraper_engine.ScraperEngine')
    @patch('web_scraper.communication.telegram.Telegram')
    def test_bot_stop(self, telegram_class, scraper_class):
        from web_scraper.action import Status
        from web_scraper import MESSAGE
        bot = BotTest.reload_bot()
        telegram, scraper = BotTest.reload_mocks(telegram_class,
                                                 scraper_class)

        stop_action = mock_final_action('stop')
        telegram.finished_conversations.put(stop_action)

        in_progress_scraper = mock_scraper(Status.SCRAPER_IN_PROGRESS)
        scraper.get_actions.return_value = [in_progress_scraper]
        keyboard = {
            'inline_keyboard': [
                [
                    {'text': in_progress_scraper.url,
                     'callback_data': f'stop {in_progress_scraper.id}'}
                ]
            ]
        }
        message = MESSAGE['choose_scraper_stop']
        bot.start()
        scraper.get_actions.assert_called_with(123)
        telegram.send_keyboard.assert_called_with(123, message, keyboard)

    @patch('web_scraper.scraper.scraper_engine.ScraperEngine')
    @patch('web_scraper.communication.telegram.Telegram')
    def test_bot_stop_ask_confirmation(self, telegram_class, scraper_class):
        from web_scraper.action import Status
        from web_scraper import MESSAGE, CONSTANTS
        bot = BotTest.reload_bot()
        telegram, scraper = BotTest.reload_mocks(telegram_class,
                                                 scraper_class)
        in_progress_scraper = mock_scraper(Status.SCRAPER_IN_PROGRESS)

        stop_action = mock_final_action(f'stop {in_progress_scraper.id}')
        telegram.finished_conversations.put(stop_action)

        scraper.is_monitoring_id.return_value = True
        keyboard = {
            'inline_keyboard': [
                [
                    {'text': CONSTANTS['yes'],
                     'callback_data': f'stop {in_progress_scraper.id} yes'},
                    {'text': CONSTANTS['no'],
                     'callback_data': f'stop {in_progress_scraper.id} no'}
                ]
            ]
        }
        message = MESSAGE['scraper_stop_confirmation']
        bot.start()
        scraper.is_monitoring_id.assert_called_with(123,
                                                    in_progress_scraper.id)
        telegram.send_keyboard.assert_called_with(123, message, keyboard)

    @patch('web_scraper.scraper.scraper_engine.ScraperEngine')
    @patch('web_scraper.communication.telegram.Telegram')
    def test_bot_stop_confirmed(self, telegram_class, scraper_class):
        from web_scraper.action import Status
        from web_scraper import MESSAGE
        bot = BotTest.reload_bot()
        telegram, scraper = BotTest.reload_mocks(telegram_class,
                                                 scraper_class)
        in_progress_scraper = mock_scraper(Status.SCRAPER_IN_PROGRESS)

        stop_action = mock_final_action(f'stop {in_progress_scraper.id} yes')
        telegram.finished_conversations.put(stop_action)

        scraper.is_monitoring_id.return_value = True
        scraper.stop_monitoring.return_value = in_progress_scraper
        message = MESSAGE['scraper_stop'].format(
            user=in_progress_scraper.user_name,
            url=in_progress_scraper.url)
        bot.start()

        scraper.is_monitoring_id.assert_called_with(123,
                                                    in_progress_scraper.id)
        scraper.stop_monitoring.assert_called_with(123,
                                                   in_progress_scraper.id)
        telegram.send_message.assert_called_with(123, message)

    @patch('web_scraper.scraper.scraper_engine.ScraperEngine')
    @patch('web_scraper.communication.telegram.Telegram')
    def test_bot_stop_not_confirmed(self, telegram_class, scraper_class):
        from web_scraper.action import Status
        from web_scraper import MESSAGE
        bot = BotTest.reload_bot()
        telegram, scraper = BotTest.reload_mocks(telegram_class,
                                                 scraper_class)
        in_progress_scraper = mock_scraper(Status.SCRAPER_IN_PROGRESS)

        stop_action = mock_final_action(f'stop {in_progress_scraper.id} no')
        telegram.finished_conversations.put(stop_action)

        scraper.is_monitoring_id.return_value = True
        message = MESSAGE['scraper_stop_cancel']
        bot.start()

        scraper.is_monitoring_id.assert_called_with(123,
                                                    in_progress_scraper.id)
        telegram.send_message.assert_called_with(123, message)

    @staticmethod
    def reload_bot():
        from web_scraper import bot
        bot = reload(bot)
        return bot

    @staticmethod
    def reload_mocks(telegram_class, scraper_class):
        telegram = telegram_class()
        scraper = scraper_class()
        scraper.success = Queue()
        scraper.failed = Queue()
        scraper.warns = Queue()
        scraper.in_progress = {}
        telegram.finished_conversations = Queue()
        return telegram, scraper
