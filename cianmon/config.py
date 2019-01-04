import os

URL = """https://cian.ru/sale/flat/{}/"""
PAUSE = 3  # A pause needed to prevent a captcha check.
CFG_DIR = os.path.expanduser("~/.cianmon/")
DATABASE = os.path.join(CFG_DIR, "cian.db")
