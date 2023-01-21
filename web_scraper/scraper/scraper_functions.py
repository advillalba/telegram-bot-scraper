import json

import jmespath
from lxml import etree


def to_do(response: str) -> bool:
    return False


def search(response: str, keyword) -> bool:
    return keyword in response


def jsonpath(response: str, path) -> bool:
    return len(jmespath.search(path, json.loads(response))) > 0


def xpath(response: str, path) -> bool:
    return len(etree.fromstring(response.encode('utf-8')).xpath(path)) > 0


scraper_functions = {
    'to_do': to_do,
    'custom_scraper': search,
    'jsonpath': jsonpath,
    'xpath': xpath,
}
