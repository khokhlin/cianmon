"""cian.ru parser"""
import argparse

from cianmon.client import get_updates
from cianmon.model import check_database
from cianmon.model import Flat


def parse_args():
    parser = argparse.ArgumentParser(prog="cianmon")
    subs = parser.add_subparsers(dest="action")
    subs.required = True
    sub = subs.add_parser("history")
    sub = subs.add_parser("update")
    sub.add_argument("--ids-file", type=str, help="Text file with flats ids")
    sub.add_argument("--ids", type=int, nargs="*", default=[], help="Flats ids")
    return parser.parse_args()


def update(ids_file=None, ids=None):
    ids = set(ids) if ids else set()
    if ids_file:
        for line in open(ids_file):
            ids.add(int(line.strip()))
    flats = get_updates(ids)
    Flat.save_flats(flats)


def history(ids=None):
    items = Flat.get_flats(ids)
    print([item.to_dict() for item in items])


def main():
    args = vars(parse_args())
    action = globals().get(args.pop("action"))
    check_database()
    action(**args)


if __name__ == "__main__":
    main()
