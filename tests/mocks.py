class MockResponse(object):
    def __init__(self, json_data=None, text=None, status_code=200):
        self.json_data = json_data
        self.status_code = status_code
        self.text = text

    def json(self):
        return self.json_data

    def text(self):
        return self.text


response_get_me = MockResponse({'result': {'username': 'John Doe'}}, 200)
response_new_conversation = MockResponse({
    "ok": True,
    "result": [
        {
            "update_id": 1,
            "message": {
                "message_id": 10,
                "from": {
                    "id": 1,
                    "is_bot": False,
                    "first_name": "John Doe",
                    "username": "johndoe",
                    "language_code": "es"
                },
                "chat": {
                    "id": 123,
                    "first_name": "John Doe",
                    "username": "johndoe",
                    "type": "private"
                },
                "date": 1672952962,
                "text": "start"
            }
        }
    ]
}, 200)
response_new_scraper = MockResponse({
    "ok": True,
    "result": [
        {
            "update_id": 378636756,
            "callback_query": {
                "id": "3968759636392764294",
                "from": {
                    "id": 1,
                    "is_bot": False,
                    "first_name": "John Doe",
                    "username": "johndoe",
                    "language_code": "es"
                },
                "message": {
                    "message_id": 7196,
                    "from": {
                        "id": 1,
                        "is_bot": False,
                        "first_name": "John Doe",
                        "username": "johndoe",
                        "language_code": "es"
                    },
                    "chat": {
                        "id": 123,
                        "first_name": "John Doe",
                        "username": "johndoe",
                        "type": "private"
                    },
                    "date": 1672955508,
                    "text": "Hola, ¿Qué necesitas?",
                    "reply_markup": {
                        "inline_keyboard": [
                            [
                                {
                                    "text": "Ayuda",
                                    "callback_data": "help"
                                },
                                {
                                    "text": "scrapers activos",
                                    "callback_data": "status"
                                }
                            ],
                            [
                                {
                                    "text": "Nuevo scraper",
                                    "callback_data": "new_scraper"
                                },
                                {
                                    "text": "Parar scraper",
                                    "callback_data": "stop"
                                }
                            ]
                        ]
                    }
                },
                "chat_instance": "1",
                "data": "new_scraper"
            }
        }
    ]
}, 200)

response_status = MockResponse({
    "ok": True,
    "result": [
        {
            "update_id": 378636756,
            "callback_query": {
                "id": "3968759636392764294",
                "from": {
                    "id": 1,
                    "is_bot": False,
                    "first_name": "John Doe",
                    "username": "johndoe",
                    "language_code": "es"
                },
                "message": {
                    "message_id": 7196,
                    "from": {
                        "id": 1,
                        "is_bot": False,
                        "first_name": "John Doe",
                        "username": "johndoe",
                        "language_code": "es"
                    },
                    "chat": {
                        "id": 123,
                        "first_name": "John Doe",
                        "username": "johndoe",
                        "type": "private"
                    },
                    "date": 1672955508,
                    "text": "Hola, ¿Qué necesitas?",
                    "reply_markup": {
                        "inline_keyboard": [
                            [
                                {
                                    "text": "Ayuda",
                                    "callback_data": "help"
                                },
                                {
                                    "text": "scrapers activos",
                                    "callback_data": "status"
                                }
                            ],
                            [
                                {
                                    "text": "Nuevo scraper",
                                    "callback_data": "new_scraper"
                                },
                                {
                                    "text": "Parar scraper",
                                    "callback_data": "stop"
                                }
                            ]
                        ]
                    }
                },
                "chat_instance": "1",
                "data": "status"
            }
        }
    ]
}, 200)

response_send_message = MockResponse({'ok': True}, 200)

response_html = MockResponse(status_code=200, text="""
<html><head><title>Page title</title></head>
<body><h1>My Page</h1></body></html>
""")

jsonpath_payload = """
                    {
                      "colors": [
                        {
                          "values": [
                            {
                              "name": "red",
                              "primary": true
                            },
                            {
                              "name": "grey",
                              "primary": false
                            }
                          ]
                        }
                      ]
                    }
        """
xpath_payload = """<?xml version="1.0" encoding="UTF-8" ?>
<root>
  <colors>
    <values>
      <name>red</name>
      <primary>true</primary>
    </values>
    <values>
      <name>grey</name>
      <primary>false</primary>
    </values>
  </colors>
</root>
"""


def action_start():
    from web_scraper.action import Action
    action = Action(123, 'Private', 1, 'johndoe')
    action.id = '268c4952-5389-4d09-a195-f3b36c0ba935'
    return action


def mock_scraper(status):
    from web_scraper.action import CustomScraper, Scraper
    action = action_start()
    scraper = CustomScraper(Scraper(action))
    scraper.id = action.id
    scraper.status = status
    scraper.errors = 0
    scraper.url = 'https://www.random_website_a.com'
    scraper.interval = 30
    scraper.scraper_function = 'custom_scraper'
    scraper.query = 'Page'
    return scraper


def mock_final_action(text: str):
    from web_scraper.action import Action, Status
    action = Action(123, 'chat_name', 1, 'user_name')
    action.type = text
    action.status = Status.CHAT_SUCCESS
    return action


def mock_in_progress(scraper):
    in_progress = {scraper.interval: {}}
    in_progress[scraper.interval][scraper.chat_id] = {}
    in_progress[scraper.interval][scraper.chat_id][scraper.url] = scraper
    return in_progress
