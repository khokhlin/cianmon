"""cian.ru parser"""
import os
import sys
import re
import argparse
import sqlite3
from time import sleep
from contextlib import contextmanager
from datetime import datetime
from collections import namedtuple
from dateutil import parser as date_parser
from  bs4 import BeautifulSoup
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning


URL = """https://cian.ru/sale/flat/{}/"""
PAUSE = 3  # A pause needed to prevent a captcha check.

CFG_DIR = os.path.expanduser("~/.cianmon/")
DATABASE = os.path.join(CFG_DIR, "cian.db")
CREATE_FLATS = (
    "CREATE TABLE IF NOT EXISTS flats (flat_id INT PRIMARY KEY, "
    "title TEXT, square_total INT, square_live INT, square_kitchen "
    "INT, floor INT, floors INT, build_year INT, description TEXT, "
    "geo TEXT)")
CREATE_PRICE_HISTORY = (
    "CREATE TABLE IF NOT EXISTS price_history (flat_id INT, "
    "created_at DATE, price INT, FOREIGN KEY (flat_id) REFERENCES "
    "flats(flat_id))")
FLATS_UPDATE = (
    "UPDATE flats SET title=?, square_total=?, square_live=?, "
    "square_kitchen=?, floor=?, floors=?, build_year=?, description=?,"
    "geo=? WHERE flat_id=?")
FLATS_INSERT = (
    "INSERT OR IGNORE INTO flats (flat_id, title, square_total, square_live, "
    "square_kitchen, floor, floors, build_year, description, geo) "
    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
PRICES_INSERT = (
    "INSERT INTO price_history (flat_id, created_at, price) VALUES (?, ?, ?)")


def parse_args():
    parser = argparse.ArgumentParser(prog="cianmon")
    subs = parser.add_subparsers(dest="action")
    subs.required = True
    sub = subs.add_parser("history")
    sub = subs.add_parser("get_prices")
    sub.add_argument("--ids-file", type=str, help="Text file with appartment ids")
    sub.add_argument("--ids", type=int, nargs="*", default=[],
                     help="Apparment ids")
    return parser.parse_args()


@contextmanager
def get_cursor():
    conn = sqlite3.connect(DATABASE)
    yield conn.cursor()
    conn.commit()
    conn.close()


def save_flats(flats):
    now = datetime.now()
    with get_cursor() as cursor:
        for flat, price in flats:
            cursor.execute(FLATS_UPDATE, (
                flat.title, flat.square_total,
                flat.square_live, flat.square_kitchen, flat.floor,
                flat.floors, flat.build_year, flat.description,
                flat.geo, flat.flat_id))
            cursor.execute(FLATS_INSERT, flat)
            cursor.execute(PRICES_INSERT, (flat.flat_id, now, price))


def get_flat_page(flat_id):
    uri = URL.format(flat_id)
    print("Requesting {}".format(uri))
    resp = requests.get(uri, verify=False)
    if resp.status_code != requests.codes.ok:
        print("Server responded with %s status", resp.status_code)
        sys.exit()
    return resp.text


def get_flat_info(flat_id):
    Flat = namedtuple("Flat", [
        "flat_id", "title", "square_total", "square_live", "square_kitchen",
        "floor", "floors", "build_year", "description", "geo"
    ])

    soup = BeautifulSoup(get_flat_page(flat_id), "html.parser")
    title = soup.find("h1", class_=re.compile("title.*")).text
    descr_el = soup.find("div", {"id": "description"})
    description = descr_el.find(class_=re.compile("description-text.*")).text

    info_els = descr_el.findAll(class_=re.compile("info-text.*"))
    infoslen = len(info_els)
    square_total = re.sub(r"\D", "", info_els[0].text) if infoslen >= 1 else None
    square_live = re.sub(r"\D", "", info_els[1].text) if infoslen >= 2 else None
    square_kitchen = re.sub(r"\D", "", info_els[2].text) if infoslen >= 3 else None
    floor, floors = re.split(r"\D+", info_els[3].text) if infoslen >= 4 else (None, None)
    if infoslen >= 5:
        match = re.search(r"\d{4}", info_els[4].text)
        build_year = match.group() if match else None
    else:
        build_year = None

    price_el = soup.find("span", class_=re.compile("price_value.*"))
    price = re.sub(r"\D", "", price_el.text)
    geo = soup.find("div", class_=re.compile("geo.*")).text
    return Flat(flat_id, title, square_total, square_live, square_kitchen,
                floor, floors, build_year, description, geo), price


def get_prices(ids):
    cnt = len(ids)
    for flat_id in ids:
        yield get_flat_info(flat_id)
        cnt -= 1
        if cnt > 0:
            sleep(PAUSE)


def init_db():
    if os.path.exists(DATABASE):
        answer = input("Database file exists. Continue? [y/n]: ")
        if answer.lower() in ("n", "no"):
            return
    if not os.path.exists(CFG_DIR):
        os.mkdir(CFG_DIR)
    with get_cursor() as cursor:
        cursor.execute(CREATE_FLATS)
        cursor.execute(CREATE_PRICE_HISTORY)


# Actions

def do_get_prices(ids_file=None, ids=None):
    ids = set(ids) if ids else set()
    if ids_file:
        with open(ids_file) as fl:
            for row in fl.readlines():
                ids.add(int(row.strip()))
    save_flats(get_prices(ids))


def do_history(ids=None):
    if ids is None:
        ids = []
    sql = ("SELECT ph.flat_id, ph.created_at, ph.price, fl.title, fl.geo "
           "FROM price_history ph LEFT JOIN flats fl ON "
           "fl.flat_id = ph.flat_id {where} ORDER BY ph.created_at DESC")
    where = "WHERE flat_id IN (%s)" % ", ".join("?" * len(ids)) if ids else ""
    with get_cursor() as cursor:
        cursor.execute(sql.format_map(vars()), ids)
        for flat_id, created_at, price, title, geo in cursor.fetchall():
            created_at = date_parser.parse(created_at).strftime("%d.%m.%Y %H:%M")
            print("Appartments {flat_id}, price {price}, created "
                  "{created_at}, ({title}, {geo})".format_map(vars()))


def main():
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    if not os.path.exists(DATABASE):
        init_db()
    args = vars(parse_args())
    action = "do_" + args.pop("action")
    action = globals().get(action)
    action(**args)


if __name__ == "__main__":
    main()
