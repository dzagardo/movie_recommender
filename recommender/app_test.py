import pytest 
from flask import Flask, json
from extensions import flask_app
from helpers import get_model_from_pickle

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

def test_get_movies_mocked_one(client, mocker):
    mocker.patch('helpers.get_model_from_pickle', return_value = None)
    mocker.patch('app.recommend_top_20_movies_for_user', return_value = "harry+potter,star+wars")
    response = client.get('/recommend/2')
    assert(response.status == '200 OK')
    assert(response.text == "harry+potter,star+wars")

def test_get_movies_mocked_two(client, mocker):
    mocker.patch('helpers.get_model_from_pickle', return_value = None)
    mocker.patch('app.recommend_top_20_movies_for_user', return_value = "harry+potter,star+wars")
    response = client.get('/recommend/-2')
    assert(response.status == '400 BAD REQUEST')

def test_get_movies_mocked_three(client, mocker):
    mocker.patch('helpers.get_model_from_pickle', return_value = None)
    mocker.patch('app.recommend_top_20_movies_for_user', return_value = "harry+potter,star+wars")
    response = client.get('/recommend/badinput')
    assert(response.status == '400 BAD REQUEST')

def test_get_movies_bad_unmocked_one(client, mocker):
    mocker.patch('helpers.get_model_from_pickle', return_value = get_model_from_pickle("svd_model"))
    response = client.get('/recommend/-2')
    assert(response.status == '400 BAD REQUEST')

def test_get_movies_unmocked(client, mocker):
    mocker.patch('app.get_model', return_value = get_model_from_pickle("svd_model"))
    response = client.get('/recommend/2')
    assert(response.status == '200 OK')
    res = "thrill+ride+the+science+of+fun+1997,vincent+1982,chaotic+ana+2007,for+the+birds+2000,a+very+social+secretary+2005,keeping+the+promise+1997,sweepers+1999,the+madagascar+penguins+in+a+christmas+caper+2005,the+true+meaning+of+christmas+specials+2002,asfalto+2000,the+bleeding+2009,mascara+1999,the+manzanar+fishing+club+2012,paths+of+hate+2011,season+for+assassins+1975,children+2006,so+much+so+fast+2006,home+alone+2+lost+in+new+york+1992"
    assert(response.text == res)

def test_get_movies_bad_two_unmocked(client, mocker):
    mocker.patch('app.get_model', return_value = get_model_from_pickle("svd_model"))
    response = client.get('/recommend/invalid')
    assert(response.status == '400 BAD REQUEST')
    