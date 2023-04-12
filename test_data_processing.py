import pytest
from data_processing import update_last_extremum, add_new_extr

@pytest.fixture
def extremum_list():
     return [
        [0, '2023-03-19 19:00:00', 28255.1, 'mx', 28170.3347],
        [3, '2023-03-19 20:00:00', 29255.1, 'mx', 28170.3347],
        [6, '2023-03-19 21:00:00', 30255.1, 'mx', 28170.3347],
        [9, '2023-03-19 22:00:00', 31255.1, 'mx', 28170.3347]
        ]
@pytest.fixture
def new_extr():
    return [12, '2023-03-19 19:01:00', 30999.1, 'mx', 30906, 1027]

def test_update_last_extremum(extremum_list, new_extr):
    update_last_extremum(extremum_list, new_extr)
    assert extremum_list == [
                            [0, '2023-03-19 19:00:00', 28255.1, 'mx', 28170.3347],
                            [3, '2023-03-19 20:00:00', 29255.1, 'mx', 28170.3347],
                            [6, '2023-03-19 21:00:00', 30255.1, 'mx', 28170.3347],
                            [12, '2023-03-19 19:01:00', 30999.1, 'mx', 30906, 1027]]

def test_add_new_extr(extremum_list, new_extr):
    add_new_extr(extremum_list, new_extr)
    assert extremum_list == [
        [0, '2023-03-19 19:00:00', 28255.1, 'mx', 28170.3347],
        [3, '2023-03-19 20:00:00', 29255.1, 'mx', 28170.3347],
        [6, '2023-03-19 21:00:00', 30255.1, 'mx', 28170.3347],
        [9, '2023-03-19 22:00:00', 31255.1, 'mx', 28170.3347],
        [12, '2023-03-19 19:01:00', 30999.1, 'mx', 30906, 1027]
    ]