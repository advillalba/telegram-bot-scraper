import copy
import hashlib
import json
import urllib
from importlib import reload
from unittest import TestCase
from unittest.mock import patch, call, MagicMock

from tests.mocks import response_new_conversation, \
    response_send_message, response_get_me, action_start, \
    response_new_scraper, response_status


@patch.dict('os.environ', {'TELEGRAM_BOT_KEY': '1234:abcd', 'OWNER_ID': '1'})
@patch('web_scraper.utils.schedule', MagicMock(return_value=lambda x: x))
class TelegramTest(TestCase):
    _url = 'https://api.telegram.org/bot1234:abcd'
    url_get_me = f'{_url}/getMe'
    url_get_updates = f'{_url}/getUpdates?offset='
    send_message = f'{_url}/sendMessage'

    @patch('requests.get')
    def test_send_message(self, get):
        telegram_module = TelegramTest.reload_module_class()
        get.side_effect = [
            response_get_me,
            response_send_message]
        telegram = telegram_module.Telegram()

        telegram.send_message(1, 'hello')
        get.assert_has_calls([call(self.url_get_me),
                              call(
                                  f'{self.send_message}?&chat_id=1&text=hello'
                                  f'&disable_notification=false')])

    @patch('requests.get')
    def test_new_conversation(self, get):
        from web_scraper import QUESTION
        telegram_module = TelegramTest.reload_module_class()

        get.side_effect = [
            response_get_me,
            response_new_conversation,
            response_send_message]
        telegram = telegram_module.Telegram()
        telegram.monitor()
        question = QUESTION['start']
        text = urllib.parse.quote(question['text'])
        markup = f'reply_markup={json.dumps(question["options"])}'
        notification = 'disable_notification=true'
        url = f'{self.send_message}?' \
              f'&chat_id=123&text={text}&{markup}&{notification}'
        get.assert_has_calls([call(self.url_get_me),
                              call(self.url_get_updates + '0'),
                              call(url)])

    @patch('requests.get')
    def test_error_getting_updates(self, get):
        telegram_module = TelegramTest.reload_module_class()
        get.side_effect = [
            response_get_me,
            Exception('Error getting updates')]
        telegram = telegram_module.Telegram()
        telegram.monitor()
        get.assert_has_calls([call(self.url_get_me),
                              call(self.url_get_updates + '0')])

    @patch('requests.get')
    def test_ask_status(self, get):
        telegram_module = TelegramTest.reload_module_class()

        get.side_effect = [
            response_get_me,
            response_status]
        telegram = telegram_module.Telegram()
        telegram._offset = 1
        action = action_start()
        key = hashlib.md5(str({"chat_id": action.chat_id,
                               "user_id": action.user_id}).encode('UTF-8')) \
            .hexdigest()
        telegram._conversations[key] = action
        telegram.monitor()
        _url_get_updates = self.url_get_updates + '1'
        get.assert_has_calls([call(self.url_get_me),
                              call(_url_get_updates)])
        assert len(telegram._conversations) == 0
        assert telegram.finished_conversations.qsize() == 1
        assert telegram._offset == 378636757

    @patch('requests.get')
    def test_new_scraper(self, get):
        from web_scraper import QUESTION
        telegram_module = TelegramTest.reload_module_class()

        get.side_effect = [
            response_get_me,
            response_new_scraper,
            response_send_message]
        telegram = telegram_module.Telegram()
        telegram._offset = 1
        action = action_start()
        key = hashlib.md5(str({"chat_id": action.chat_id,
                               "user_id": action.user_id}).encode('UTF-8')) \
            .hexdigest()
        telegram._conversations[key] = action
        telegram.monitor()
        question = QUESTION['interval']
        text = urllib.parse.quote(question['text'])
        markup = f'reply_markup={json.dumps(question["options"])}'
        notification = 'disable_notification=true'
        url = f'{self.send_message}?' \
              f'&chat_id=123&text={text}&{markup}&{notification}'

        get.assert_has_calls([call(self.url_get_me),
                              call(self.url_get_updates + '1'),
                              call(url)])

    @patch('requests.get')
    def test_new_scraper_group_wrong_response(self, get):
        from web_scraper import QUESTION
        telegram_module = TelegramTest.reload_module_class()
        wrong_response = copy.deepcopy(response_new_scraper)
        wrong_response.json_data['result'][0]['callback_query']['message'][
            'chat'][
            'type'] = 'group'
        wrong_response.json_data['result'][0]['callback_query']['message'][
            'chat'][
            'title'] = 'new_group'
        wrong_response.json_data['result'][0]['callback_query'][
            'data'] = 'wrong_answer'
        get.side_effect = [
            response_get_me,
            wrong_response,
            response_send_message]
        telegram = telegram_module.Telegram()
        telegram._offset = 1
        action = action_start()
        action.chat_name = 'new_group'
        key = hashlib.md5(str({"chat_id": action.chat_id,
                               "user_id": action.user_id}).encode('UTF-8')) \
            .hexdigest()
        telegram._conversations[key] = action
        telegram.monitor()
        question = QUESTION['start']
        text = urllib.parse.quote(question['error_message'])
        markup = f'reply_markup={json.dumps(question["options"])}'
        notification = 'disable_notification=true'
        url = f'{self.send_message}?' \
              f'&chat_id=123&text={text}&{markup}&{notification}'
        get.assert_has_calls([call(self.url_get_me),
                              call(self.url_get_updates + '1'),
                              call(url)])

    @staticmethod
    def reload_module_class():
        from web_scraper.communication import telegram
        reload(telegram)
        return telegram
