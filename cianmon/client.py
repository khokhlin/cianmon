import logging
import re
import sys
from time import sleep
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from  bs4 import BeautifulSoup
from cianmon.config import PAUSE, URL


logger = logging.getLogger(__name__)


def get_flat_page(flat_id):
    uri = URL.format(flat_id)
    print("Requesting {}".format(uri))
    resp = requests.get(uri, verify=False)
    if resp.status_code != requests.codes.ok:
        print("Server responded with %s status", resp.status_code)
        sys.exit()
    return resp.text


def parse_float(value):
    return float(value.split(" ")[0].replace(',', '.'))


INFO_MAP = {
    "Общая": {"total_square": parse_float},
    "Жилая": {"live_square": parse_float},
    "Кухня": {"kitchen_square": parse_float},
    "Построен": {"build_year": int},
    "Этаж": {
        "floor": lambda x: x.split(" из ")[0],
        "floors": lambda x: x.split(" из ")[1]
    }
}


def parse_page(flat_id, soup):
    try:
        resp = {"flat_id": flat_id}
        title_el = soup.find("h1", class_=re.compile(".*--title--.*"))
        resp["title"] = title_el.text
        descr_elem = soup.find("div", {"id": "description"})
        resp["description"] = descr_elem.find(
            class_=re.compile(".*--description-text--.*")).text.strip()

        elems = descr_elem.findAll(class_=re.compile(".*--info--.*"))
        for elem in elems:
            title = elem.find(class_=re.compile(".*--info-title--.*"))
            title_text = title.text
            for name, parse_fun in INFO_MAP[title_text].items():
                value = title.find_next("div").text
                resp[name] = parse_fun(value)

        price_elem = soup.find("span", class_=re.compile(".*--price_value--.*"))
        price_value = price_elem.find_next("span").text
        resp["price"] = re.sub(r"\D", "", price_value)
        geo_el = soup.find("div", class_=re.compile(".*--geo--.*")).find_next("span")
        resp["geo"] = geo_el.attrs.get("content") if geo_el else None

    except AttributeError:
        logger.error("Unable to parse %s flat page", flat_id)
        return {}
    else:
        return resp


def get_flat_info(flat_id):
    content = get_flat_page(flat_id)
    soup = BeautifulSoup(content, "html.parser")
    flat_info = parse_page(flat_id, soup)
    return flat_info


def get_updates(ids):
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    cnt = len(ids)
    for flat_id in ids:
        yield get_flat_info(flat_id)
        if cnt > 0:
            sleep(PAUSE)
        cnt -= 1
