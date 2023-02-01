import pytest
from ml_model import invert_dict, get_top_20_ids, get_unseen_movies, get_top_20_movie_names, recommend_top_20_movies_for_user, plot_telemetry, get_inference_time
from helpers import get_model_from_pickle
import pandas as pd
from datetime import datetime

def get_dummy_file():
    dummy_file = pd.DataFrame(columns=['Modelname','TimeToPredict'])
    dummy_file.to_csv("dummy.csv", index=False)
    return pd.read_csv("dummy.csv")

def test_invert_dict():
    d = {"hello": "bye"}
    inverted = invert_dict(d)
    assert(inverted["bye"] == "hello")

def assertDictEqual(d1, d2):
    if len(d1.items()) != len (d2.items()):
        return False
    for e in d1:
        if d1[e] != d2[e]:
            return False 
    return True

def test_get_top_20_ids():
    d = {1 : 25, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 
         11: 11, 12: 12, 13: 13, 14: 14, 15: 15, 16: 16, 17: 17, 18: 18, 19: 19, 
         20: 20, 21: 21, 22: 22}
    top_items = {1 : 25, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 
         11: 11, 12: 12, 13: 13, 14: 14, 15: 15, 16: 16, 17: 17, 18: 18, 19: 19, 
         20: 20, 21: 21, 22: 22}
    top_20 = get_top_20_ids(d)
    assert(assertDictEqual(top_items, top_20))

def test_get_unseen_movies():
    movie_json = {1: [1, 2], 2: [1, 3]}
    model_id = 2
    all_movies = {"harry potter": 1, "star wars": 2, "endgame": 3, "dance moms": 4}
    unseen_movies = get_unseen_movies(movie_json, model_id, all_movies)
    assert({2, 4} == unseen_movies)

def test_get_top_20_movie_names():
    top_items = {1 : 25, 4: 4, 5: 5}
    movie_dict = {1: "harry potter", 2: "elmo", 3: "conjuring", 4: "star wars", 5: "dance moms"}
    top_20 = get_top_20_movie_names(top_items, movie_dict)
    assert("harry potter,star wars,dance moms" == top_20)

def test_recommend_top_20_movies_for_user():
    iid_dict = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6, "g": 7, "h": 8, "i": 9,
                "j": 10, "k": 11, "l": 12, "m": 13, "n":14, "o": 15, "p": 16, "q": 17,
                "r": 18, "s": 19, "t": 20, "u": 21, "v": 22, "w": 23, "x": 24, "y": 25, "z": 26}
    uid_dict = {"1": 1, "2": 2, "3": 3}
    watched_movies = {"1": [3, 23, 24]}
    res = recommend_top_20_movies_for_user(get_model_from_pickle("svd_model"), 1, iid_dict, uid_dict, watched_movies)
    assert(res == "q,d,g,h,a,b,m,i,f,l,n,p,s,t,u,v,y,z,o,k")

def test_plot_telemetry(mocker):
    dummy_file = get_dummy_file()
    mocker.patch('ml_model.get_file', return_value=dummy_file)
    mocker.patch('ml_model.get_path', return_value="dummy.csv")
    res = plot_telemetry(5.02)
    print("RES----", res)
    assert(res['Modelname'].iloc[0] == "default_svd")
    assert(res['TimeToPredict'].iloc[0] == 5.02)

def test_get_inference_time(mocker):
    start = datetime(2019, 4, 13, 5, 4, 3, 200000)
    now = datetime(2019, 4, 13, 5, 4, 3, 253000)
    mocker.patch('ml_model.get_now', return_value=now)
    res = get_inference_time(start)
    assert(res == 53.0)




    