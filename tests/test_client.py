import pytest
from cianmon.client import get_flat_info


@pytest.mark.datafiles("./tests/data/response.html")
def test_get_flat_info(mocker, response_html):
    retval = mocker.Mock(status_code=200, text=response_html)
    mocker.patch("cianmon.client.requests.get", return_value=retval)
    resp = get_flat_info(1)
    expected = {
        'build_year': 1972,
        'description': 'Lorem ipsum...',
        'flat_id': 1,
        'floor': '4',
        'floors': '12',
        'geo': 'Москва',
        'kitchen_square': 15.0,
        'live_square': 40.2,
        'price': '8800000',
        'title': '2-комн. квартира, 80 м²',
        'total_square': 80.0
    }
    assert resp == expected

    retval = mocker.Mock(status_code=200, text="test")
    mocker.patch("cianmon.client.requests.get", return_value=retval)
    resp = get_flat_info(1)
    assert resp == {}
