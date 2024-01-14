"""Модуль предоставляющий вспомогательный функционал и сущности"""
import re
import requests
import os
import json
from urllib.parse import quote
from pydantic import BaseModel


DATABASE = 'database.json'
PHONE_PATERN = re.compile(r'7\d{10}')


class DataForMessage(BaseModel):
    """Валидация данных для отправки нового сообщения через веб интерыейс."""

    message_text: str
    from_phone: str
    username: str


class RequestWildberriesAPI:
    """Класс логики запросов к маркету."""

    search_url = 'https://search.wb.ru/exactmatch/ru/common/v4/search'
    details_url = 'https://www.wildberries.ru/catalog/{}/detail.aspx'
    referer = 'https://www.wildberries.ru/catalog/0/search.aspx?search={}'
    headers = {
        'Accept': '*/*',
        'Origin': 'https://www.wildberries.ru',
        'Pragma': 'no-cache',
        'Referer': '',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
    }

    params = {
        'TestGroup': 'no_test',
        'TestID': 'no_test',
        'appType': '1',
        'curr': 'rub',
        'dest': '-1257786',
        'query': '',
        'resultset': 'catalog',
        'sort': 'popular',
        'spp': '29',
        'suppressSpellcheck': 'false',
    }

    def __init__(self, product) -> None:
        self.encoded_product = quote(product, encoding='utf-8')
        self.product = product

    def make_request(self) -> list[tuple]:
        """Сделать запрос для получения списка предложений по товару."""
        self.headers['Referer'] = self.referer.format(self.encoded_product)
        self.params['query'] = self.product
        res = requests.get(
            self.search_url,
            params=self.params,
            headers=self.headers,
            timeout=10,
        )

        # взять первые 10 товаров
        dataproducts = [
            (self.details_url.format(i['id']), i['brand'])
            for i in res.json()['data']['products']
        ][:10]

        return dataproducts


def open_database() -> dict:
    """Чтение данных из json  бд."""
    data = {}
    if os.path.exists(DATABASE):
        with open(
            DATABASE,
            'r',
            encoding='utf-8',
        ) as f:
            data = json.load(f)
    return data


def save_to_database(companion_id: str, phone: str, data_dict: dict) -> None:
    """Сохранение данных в json  бд."""
    data = open_database()

    if phone in data and companion_id in data[phone]:
        data[phone][companion_id].append(data_dict)
    else:
        if phone not in data:
            data[phone] = {}
        if companion_id not in data[phone]:
            data[phone][companion_id] = [data_dict]
        else:
            data[phone][companion_id].append(data_dict)

    with open(DATABASE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
