"""cian.ru parser"""

import re
import argparse
from collections import namedtuple
from  bs4 import BeautifulSoup
import requests


URL = """https://cian.ru/sale/flat/{}/"""

Flat = namedtuple("Flat", "title description price geo")


def parse_args():
    parser = argparse.ArgumentParser(prog="cian")
    parser.add_argument("flat_id", type=int)
    return parser.parse_args()


def get_flat(flat_id):
    resp = requests.get(URL.format(flat_id), verify=False)
    soup = BeautifulSoup(data, "lxml")
    title = soup.find("h1", class_=re.compile("title.*")).text
    description = soup.find("div", {"id": "description"}).text
    price = soup.find("span", class_=re.compile("price_value.*"))
    price = re.sub("\D", "", price.text)
    geo = soup.find("div", class_=re.compile("geo.*")).text
    return Flat(title, description, price, geo)


def main():
    args = parse_args()
    flat = get_flat(args.flat_id)
    print(flat)


if __name__ == "__main__":
    main()
