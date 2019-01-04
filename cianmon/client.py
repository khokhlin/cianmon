import re
import sys
from time import sleep
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from  bs4 import BeautifulSoup
from cianmon.config import PAUSE, URL


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
    try:
        title = soup.find("h1", class_=re.compile("title.*")).text
        descr_elem = soup.find("div", {"id": "description"})
        description = descr_elem.find(
            class_=re.compile("description-text.*")).text

        elems = descr_elem.findAll(class_=re.compile("info-text.*"))
        elem_count = len(elems)
        total_square = float(elems[0].text) if elem_count >= 1 else None
        live_square = float(elems[1].text) if elem_count >= 2 else None
        kitchen_square = float(elems[2].text) if elem_count >= 3 else None
        if elem_count >= 4:
            floor, floors = (int(val) for val in re.split(r"\D+", elems[3].text))
        if elem_count >= 5:
            match = re.search(r"\d{4}", elems[4].text)
            build_year = int(match.group()) if match else None
        else:
            build_year = None

        price_el = soup.find("span", class_=re.compile("price_value.*"))
        price = re.sub(r"\D", "", price_el.text)
        geo = soup.find("div", class_=re.compile("geo.*")).text
    except AttributeError:
        return {}
    else:
        return {
            "flat_id": flat_id,
            "title": title,
            "description": description,
            "total_square": total_square,
            "kitchen_square": kitchen_square,
            "live_square": live_square,
            "floor": floor,
            "floors": floors,
            "build_year": build_year,
            "price": price,
            "geo": geo,
        }


def get_updates(ids):
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    cnt = len(ids)
    for flat_id in ids:
        yield get_flat_info(flat_id)
        if cnt > 0:
            sleep(PAUSE)
        cnt -= 1
