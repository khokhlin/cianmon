import re
import sys
from time import sleep

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from  bs4 import BeautifulSoup
from .config import PAUSE, URL


def get_flat_page(flat_id):
    uri = URL.format(flat_id)
    print("Requesting {}".format(uri))
    resp = requests.get(uri, verify=False)
    if resp.status_code != requests.codes.ok:
        print("Server responded with %s status", resp.status_code)
        sys.exit()
    return resp.text


def get_flat_info(flat_id):
    content = get_flat_page(flat_id)
    soup = BeautifulSoup(content, "html.parser")
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
    return {
        "flat_id": flat_id,
        "title": title,
        "square_total": square_total,
        "square_live": square_live,
        "square_kitchen": square_kitchen,
        "floor": floor,
        "floors": floors,
        "build_year": build_year,
        "description": description,
        "geo": geo,
        "price": price
    }


def get_updates(ids):
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    cnt = len(ids)
    for flat_id in ids:
        yield get_flat_info(flat_id)
        if cnt > 0:
            sleep(PAUSE)
        cnt -= 1
