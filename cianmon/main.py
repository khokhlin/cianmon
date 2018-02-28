"""cian.ru parser"""
import sys
import re
import argparse
import sqlite3
from collections import namedtuple
from  bs4 import BeautifulSoup
import requests


URL = """https://cian.ru/sale/flat/{}/"""


def parse_args():
    parser = argparse.ArgumentParser(prog="cian")
    parser.add_argument("flat_id", type=int)
    return parser.parse_args()


def save_flats(flats):
    conn = sqlite3.connect('data/cian.db')
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS cian (flat_id INT PRIMARY KEY, title TEXT, "
        "square_total INT, square_live INT, square_kitchen INT, floor INT, "
        "floors INT, build_year INT, description TEXT, price INT, geo TEXT)")
    cursor.executemany(
        "INSERT INTO cian (flat_id, title, square_total, square_live, "
        "square_kitchen, floor, floors, build_year, description, price, geo) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", flats)
    conn.commit()
    conn.close()


def get_flat(flat_id):
    Flat = namedtuple("Flat", [
        "flat_id", "title", "square_total", "square_live", "square_kitchen",
        "floor", "floors", "build_year", "description", "price", "geo"
    ])

    resp = requests.get(URL.format(flat_id), verify=False)
    if resp.status_code != requests.codes.ok:
        print("Cian responded with %s status", resp.status_code)
        sys.exit()
    soup = BeautifulSoup(resp.text, "lxml")
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
                floor, floors, build_year, description, price, geo)



def main():
    args = parse_args()
    flat = get_flat(args.flat_id)
    save_flats([flat])


if __name__ == "__main__":
    main()
