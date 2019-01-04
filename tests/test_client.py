import pytest
from cianmon.client import get_flat_info


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


def test_get_flat_info(mocker):
    retval = mocker.Mock(status_code=200, text="test")
    mocker.patch("cianmon.client.requests.get", return_value=retval)
    resp = get_flat_info(1)
    assert resp == {}

    retval = mocker.Mock(status_code=200, text=RESPONSE_TEXT)
    mocker.patch("cianmon.client.requests.get", return_value=retval)
    resp = get_flat_info(1)
    expected = {
        "build_year": 2018,
        "title": "Title",
        "total_square": 1.0,
        "live_square": 2.0,
        "kitchen_square": 3.0,
        "description": "description",
        "geo": "geo text",
        "price": "11111",
        "flat_id": 1,
        "floor": 4,
        "floors": 5
    }
    assert resp == expected
