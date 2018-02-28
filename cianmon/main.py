"""cian.ru parser"""
import sys
import re
import argparse
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from collections import namedtuple
from  bs4 import BeautifulSoup
import requests


DATABASE = "data/cian.db"
URL = """https://cian.ru/sale/flat/{}/"""
FLATS_UPDATE_SQL = (
    "UPDATE flats SET title=?, square_total=?, square_live=?, "
    "square_kitchen=?, floor=?, floors=?, build_year=?, description=?,"
    "geo=? WHERE flat_id=?")
FLATS_INSERT_SQL = (
    "INSERT OR IGNORE INTO flats (flat_id, title, square_total, square_live, "
    "square_kitchen, floor, floors, build_year, description, geo) "
    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
PRICES_INSERT_SQL = (
    "INSERT INTO price_history (flat_id, created_at, price) VALUES (?, ?, ?)")


def parse_args():
    parser = argparse.ArgumentParser(prog="cian")
    parser.add_argument("--init-db", action="store_true", default=False)
    parser.add_argument("--history", action="store_true", default=False)
    parser.add_argument("flat_ids", type=int, nargs="*")
    return parser.parse_args()


@contextmanager
def get_cursor():
    conn = sqlite3.connect(DATABASE)
    yield conn.cursor()
    conn.commit()
    conn.close()


def init_db():
    with get_cursor() as cursor:
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS flats (flat_id INT PRIMARY KEY, "
            "title TEXT, square_total INT, square_live INT, square_kitchen "
            "INT, floor INT, floors INT, build_year INT, description TEXT, "
            "geo TEXT)")
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS price_history (flat_id INT, "
            "created_at DATE, price INT)")


def save_flats(flats):
    now = datetime.now()
    with get_cursor() as cursor:
        for flat, price in flats:
            cursor.execute(
                FLATS_UPDATE_SQL, (flat.title, flat.square_total, 
                flat.square_live, flat.square_kitchen, flat.floor,
                flat.floors, flat.build_year, flat.description,
                flat.geo, flat.flat_id))
            cursor.execute(FLATS_INSERT_SQL, flat)
            cursor.execute(PRICES_INSERT_SQL, (flat.flat_id, now, price))


def history(flat_ids):
    with get_cursor() as cursor:
        cursor.execute(
            "SELECT flat_id, created_at, price FROM price_history "
            "WHERE flat_id IN (%s)" % ", ".join("?" * len(flat_ids)), flat_ids)
        return cursor.fetchall()


def get_flat_page(flat_id):
    resp = requests.get(URL.format(flat_id), verify=False)
    if resp.status_code != requests.codes.ok:
        print("Cian responded with %s status", resp.status_code)
        sys.exit()
    return resp.text


def get_flat_info(flat_id):
    Flat = namedtuple("Flat", [
        "flat_id", "title", "square_total", "square_live", "square_kitchen",
        "floor", "floors", "build_year", "description", "geo"
    ])

    data = get_flat_page(flat_id)
    soup = BeautifulSoup(data, "lxml")
    title = soup.find("h1", class_=re.compile("title.*")).text
    descr_el = soup.find("div", {"id": "description"})
    description = descr_el.find(class_=re.compile("description-text.*")).text
    info_els = descr_el.findAll(class_=re.compile("info-text.*"))
    if len(info_els) != 5:
        raise ValueError("Wrong info elements count")
    square_total = re.sub(r"\D", "", info_els[0].text)
    square_live = re.sub(r"\D", "", info_els[1].text)
    square_kitchen = re.sub(r"\D", "", info_els[2].text)
    floor, floors = re.split(r"\D+", info_els[3].text)
    build_year = info_els[4].text

    price_el = soup.find("span", class_=re.compile("price_value.*"))
    price = re.sub(r"\D", "", price_el.text)
    geo = soup.find("div", class_=re.compile("geo.*")).text
    return Flat(flat_id, title, square_total, square_live, square_kitchen,
                floor, floors, build_year, description, geo), price


def get_flats(flat_ids):
    for flat_id in flat_ids:
        yield get_flat_info(flat_id)


def main():
    args = parse_args()
    if args.history:
        for flat_id, date, price in history(args.flat_ids):
            print(flat_id, date, price)
    elif args.init_db:
        init_db()
    else:
        save_flats(get_flats(args.flat_ids))


if __name__ == "__main__":
    main()
