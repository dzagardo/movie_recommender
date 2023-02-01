import pytest
from model_training_pipe0 import parse_movie_req, parse_rating_req, parse_recommendation_req, parse_request

def assertDictEqual(d1, d2):
    if len(d1.items()) != len (d2.items()):
        return False
    for e in d1:
        try:
            if d1[e] != d2[e]:
                return False 
        except:
            return False
    return True

def test_parse_movie_req():
    req = "GET /data/m/153/50.mpg"
    assert(parse_movie_req(req) == "153")

def test_parse_movie_req_bad_data():
    req = "GET /data/m153/50.mpg"
    assert(parse_movie_req(req) == None)

def test_parse_rating_req():
    req = "GET /rate/harry+potter=3"
    assert(parse_rating_req(req) == {"harry+potter": "3"})

def test_parse_rating_req_bad_data():
    req = "GET /rate/53.4"
    assert(parse_rating_req(req) == None)

def test_parse_recommendation_request():
    req = "recommendation request 17645-team04.isri.cmu.edu:8082, status 200, result: harry potter,star wars, 5 ms"
    expected_res = {"status": "200", "recommendations": "harry potter,star wars", "response_time": "5 ms"}
    res = parse_recommendation_req(req)
    print(res)
    assert(assertDictEqual(expected_res, parse_recommendation_req(req)))

def test_parse_request_movie_req():
    req = "2022-09-29T23:24:55,3,GET /data/m/153/50.mpg"
    parsed = parse_request(req)
    assert(parsed == {"3": "153"})

def test_parse_request_rating_req():
    req = "2022-09-29T23:24:55,3,GET /rate/star+wars=3"
    parsed = parse_request(req)
    assert(parsed == {"3": {"star+wars": "3"}})

def test_parse_request_recommendation_req_good_one():
    req = "2022-09-29T23:24:55,3,recommendation request 17645-team04.isri.cmu.edu:8082, status 200, result: harry potter,star wars, 5 ms"
    parsed = parse_request(req)
    print(parsed)
    assert(parsed == {"3": {"status": "200", "recommendations": "harry potter,star wars", "response_time": "5 ms"}})

def test_parse_request_recommendation_req_good_two():
    req = "2022-09-29T23:24,3,recommendation request 17645-team04.isri.cmu.edu:8082, status 200, result: harry potter,star wars, 5 ms"
    parsed = parse_request(req)
    print(parsed)
    assert(parsed == {"3": {"status": "200", "recommendations": "harry potter,star wars", "response_time": "5 ms"}})


def test_parse_request_recommendation_req_bad_one():
    req = "2022-09-29T23:24:55,3,recommendation request 17645-team04.isri.cmu.edu:8082, status 200, result: harry potter,star wars 5 ms"
    parsed = parse_request(req)
    print(parsed)
    assert(parsed == None)

def test_parse_request_recommendation_req_bad_two():
    req = "2022-09-29T23:24:55,3,recommendation request 17645-team04.isri.cmu.edu:8082, status 200, star wars 5 ms"
    parsed = parse_request(req)
    print(parsed)
    assert(parsed == None)

def test_parse_request_recommendation_req_bad_three():
    req = "2022-09-29T23:24:55,3,recommendation request 17645-team04.isri.cmu.edu:8083, status 200, result: harry potter,star wars, 5 ms"
    parsed = parse_request(req)
    print(parsed)
    assert(parsed == None)

def test_parse_request_recommendation_req_bad_four():
    req = "2022-09-2923:24:55,3,recommendation request 17645-team04.isri.cmu.edu:8082, status 200, result: harry potter,star wars, 5 ms"
    parsed = parse_request(req)
    print(parsed)
    assert(parsed == None)

def test_parse_request_recommendation_req_bad_five():
    req = "2022-09-29T23:24:55,3,recommendation request 17645-team04.isri.cmu.edu:8082, status 200, result: harry potter,star wars, 5ms"
    parsed = parse_request(req)
    print(parsed)
    assert(parsed == None)

def test_parse_request_recommendation_req_bad_six():
    req = "2022-09-29T23:24:55,3,recommendation request 17645-team04.isri.cmu.edu:8082, status 200, result: harry potter,star wars 5 ms"
    parsed = parse_request(req)
    print(parsed)
    assert(parsed == None)