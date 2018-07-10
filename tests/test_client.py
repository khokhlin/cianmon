import os
import logging
from unittest import TestCase
from unittest.mock import patch
from unittest.mock import Mock

from cianmon.client import get_flat_info
from cianmon.config import URL


if os.getenv("DEBUG"):
    logging.basicConfig(level=logging.DEBUG)

RESPONSE_TEXT = """
<!DOCTYPE html>
<html><title>Untitled</title>
<body>
    <h1 class="title.bold">Title</h1>
    <div id="description">
        <span class="description-text.normal">description</span>
        <span class="info-text.normal">1</span>
        <span class="info-text.normal">2</span>
        <span class="info-text.normal">3</span>
        <span class="info-text.normal">4 5</span>
        <span class="info-text.normal">2018</span>
    </div>
    <div>
        <span class="price_value.normal">111 11</span>
        <div class="geo.normal">geo text</div>
    </div>
</body>
</html>
"""


class TestClient(TestCase):

    def get_url(self, flat_id):
        return URL.format(flat_id)

    @patch("cianmon.client.requests.get")
    def test_get_flat_info(self, rmock):
        rmock.return_value = Mock(status_code=200, text="test")
        resp = get_flat_info(1)
        self.assertEqual(resp, {})

        rmock.return_value = Mock(status_code=200, text=RESPONSE_TEXT)
        resp = get_flat_info(1)
        expected = {
            "build_year": "2018",
            "title": "Title",
            "square_total": "1",
            "square_live": "2",
            "square_kitchen": "3",
            "description": "description",
            "geo": "geo text",
            "price": "11111",
            "flat_id": 1,
            "floor": "4",
            "floors": "5"
        }
        self.assertEqual(resp, expected)
