import main

# Note: running test resets whole DB!!!!
main.db.drop_all()
main.db.create_all()
client = main.app.test_client()


def test_empty_db():
    res = client.get('/shifts/10')
    assert res.status_code == 200
    assert b'[]' in res.data


def test_add_shift1_worker10():
    res = client.post('/shifts/10', json={"begin": "2021-02-17T08:00:00",
                                          "end": "2021-02-17T16:00:00"})
    assert res.status_code == 200
    res2 = client.get('/shifts/10')
    j = res2.get_json()
    assert j[0]["worker_id"] == 10
    assert j[0]["begin"] == "2021-02-17T08:00:00" #timezone not in resultts!
    assert j[0]["end"] == "2021-02-17T16:00:00"

def test_add_shift2_worker10():
    res = client.post('/shifts/10', json={"begin": "2021-02-18T08:00:00",
                                          "end": "2021-02-18T16:00:00"})
    assert res.status_code == 200
    res2 = client.get('/shifts/10')
    j = res2.get_json()
    assert j[1]["worker_id"] == 10
    assert j[1]["begin"] == "2021-02-18T08:00:00" #timezone not in resultts!
    assert j[1]["end"] == "2021-02-18T16:00:00"

def test_add_shift1_worker11():
    # same(overalpping) as shift1 for worker 10
    res = client.post('/shifts/11', json={"begin": "2021-02-17T08:00:00",
                                          "end": "2021-02-17T16:00:00"})
    assert res.status_code == 200
    res2 = client.get('/shifts/11')
    j = res2.get_json()
    assert j[0]["worker_id"] == 11
    assert j[0]["begin"] == "2021-02-17T08:00:00"
    assert j[0]["end"] == "2021-02-17T16:00:00"

def test_get_not_existsing_shift():
    res = client.get('/shifts/12/1')
    assert res.status_code == 404

def test_add_overlapping_shift1():
    res = client.post('/shifts/10', json={"begin": "2021-02-17T07:00:00",
                                          "end": "2021-02-17T15:00:00"})
    assert res.status_code == 422

def test_add_overlapping_shift2():
    res = client.post('/shifts/10', json={"begin": "2021-02-17T08:00:00",
                                          "end": "2021-02-17T10:00:00"})
    assert res.status_code == 422

def test_add_overlapping_shift2():
    res = client.post('/shifts/10', json={"begin": "2021-02-17T15:00:00",
                                          "end": "2021-02-17T23:00:00"})
    assert res.status_code == 422

def test_adjacent_shift1():
    res = client.post('/shifts/10', json={"begin": "2021-02-17T00:00:00",
                                          "end": "2021-02-17T08:00:00"})
    assert res.status_code == 422

def test_adjacent_shift2():
    res = client.post('/shifts/10', json={"begin": "2021-02-17T16:00:00",
                                          "end": "2021-02-17T23:00:00"})
    assert res.status_code == 422
