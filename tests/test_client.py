import pytest
from cianmon.client import get_flat_info


@pytest.mark.datafiles("./tests/data/response.html")
def test_get_flat_info(mocker, response_html):
    retval = mocker.Mock(status_code=200, text=response_html)
    mocker.patch("cianmon.client.requests.get", return_value=retval)
    resp = get_flat_info(1)
    expected = {
       'flat_id': 1,
        'floor': '6',
        'floors': '31',
        'geo': 'Москва, ЮЗАО, р-н Южное Бутово, ул. Поляны, 5',
        'kitchen_square': 7.3,
        'live_square': 31.1,
        'price': '7690000',
        'title': '2-комн. квартира, 56,7 м²',
        'total_square': 56.7
    }
    descr = resp.pop("description")
    assert resp == expected
    assert len(descr) == 1205
    retval = mocker.Mock(status_code=200, text="test")
    mocker.patch("cianmon.client.requests.get", return_value=retval)
    resp = get_flat_info(1)
    assert resp == {}
