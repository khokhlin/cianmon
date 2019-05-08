from cianmon.model import Flat


def test_can_save_data():
    flat_info = {
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
    Flat.save_many([flat_info])
    flats = Flat.select()
    assert flats.count() == 1
    expected = {
        'live_square': 2,
        'price': 11111,
        'title': 'Title',
        'flat_id': 1,
        'total_square': 1
    }
    assert flats[0].to_dict() == expected
