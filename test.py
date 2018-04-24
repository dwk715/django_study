#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/4/24 上午9:40
# @Author  : Dlala
# @File    : init_db.py

from pymongo import MongoClient
import requests
import datetime
import logging

GET_GAMES_US_URL = "http://www.nintendo.com/json/content/get/filter/game?system=switch&sort=title&direction=asc&shop=ncom"
GET_GAMES_EU_URL = "http://search.nintendo-europe.com/en/select"
GET_GAMES_JP_SEARCH = "https://www.nintendo.co.jp/api/search/title?category=products&pf=switch&q="
GUESS_GAMES_GP_URL = 'https://ec.nintendo.com/JP/ja/titles/'
GET_PRICE_URL = "https://api.ec.nintendo.com/v1/price?lang=en"

GAME_LIST_LIMIT = 200
PRICE_LIST_LIMIT = 50

NSUID_REGEX_JP = r'\d{14}'
JSON_REGEX = r'NXSTORE\.titleDetail\.jsonData = ([^;]+);'

GAME_CHECK_CODE_US = 70010000000185
GAME_CHECK_CODE_EU = 70010000000184
GAME_CHECK_CODE_JP = 70010000000039

REGION_ASIA = "CN HK AE AZ HK IN JP KR MY SA SG TR TW".split(' ')
REGION_EUROPE = "AD AL AT AU BA BE BG BW CH CY CZ DE DJ DK EE ER ES FI FR GB GG GI GR HR HU IE IM IS IT JE LI LS LT LU LV MC ME MK ML MR MT MZ NA NE NL NO NZ PL PT RO RS RU SD SE SI SK SM SO SZ TD VA ZA ZM ZW".split(
    ' ')
REGION_AMERICA = "AG AI AR AW BB BM BO BR BS BZ CA CL CO CR DM DO EC GD GF GP GT GY HN HT JM KN KY LC MQ MS MX NI PA PE PY SR SV TC TT US UY VC VE VG VI".split(
    ' ')

COUNTRIES = "AT AU BE BG CA CH CY CZ DE DK EE ES FI FR GB GR HR HU IE IT JP LT LU LV MT MX NL NO NZ PL PT RO RU SE SI SK US ZA".split(
    ' ')

FIRST_NSUID = 70010000000026

# 日志设置
today = datetime.datetime.now().strftime("%Y-%m-%d")  # 记录日志用
LOG_FORMAT = "%(asctime)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d"
log_file = today + '.log'
logging.basicConfig(filename=log_file, level=logging.ERROR, format=LOG_FORMAT, datefmt=DATE_FORMAT)

# mongodb 设置
mg_client = MongoClient('localhost', 27017)
db = mg_client['games_info']
collection = db['game_info']
# 定义数据库格式
game = {
    "title": None,
    "game_code": None,
    "nsuid": None,
    "img": None,
    "excerpt": None,
    "date_from": None,
    "on_sale": False,
    "publisher": "",
    "categories": [],
    "language_availability": []
}

def getGamesEU():
    params = {
        'fl': "title, nsuid_txt, product_code_txt, pretty_date_s, image_url_sq_s, developer, excerpt, categories_txt, language_availability",
        'fq': 'system_type:nintendoswitch* AND product_code_txt:*',
        'q': '*',
        'rows': 9999,
        'sort': 'sorting_title asc',
        'start': 0,
        'wt': 'json',
    }
    try:
        res = requests.get(GET_GAMES_EU_URL, params=params)
        result = res.json()['response']['docs']
        for game_info in result:
            game_eu = game.copy()
            on_sale = True if (datetime.datetime.strptime(game_info['pretty_date_s'], "%d/%m/%Y") <= datetime.datetime.now()) else False
            game_eu.update(
                {
                    "title": game_info['title'],
                    "game_code": game_info['product_code_txt'][0],
                    "nsuid": game_info['nsuid_txt'][0],
                    "img": game_info['image_url_sq_s'],
                    "excerpt": game_info['excerpt'],
                    "date_from": game_info['pretty_date_s'],
                    "on_sale": on_sale,
                    "categories": game_info['categories_txt'],
                    "language_availability": game_info['language_availability']
                }
            )
            print(game_eu)
            collection.insert_one(game_eu)
    except TimeoutError:
        logging.error("get Europe games info timeout")
        return None
    except Exception:
        logging.error("Europe error: %s".format(Exception))
        return None


if __name__ == '__main__':
    getGamesEU()
