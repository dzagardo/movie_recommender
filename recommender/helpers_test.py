import pytest
from helpers import get_iid_dict_from_json, get_uid_dict_from_json, get_watched_movies_dict_from_json, get_avg_inference_time
from ml_model import get_file
import pandas as pd

#test comment

def test_get_iid_dict_from_json():
    res = {"a+very+social+secretary+2005": 0, "asfalto+2000": 1, "chaotic+ana+2007": 2, "children+2006": 3, "for+the+birds+2000": 4, "home+alone+2+lost+in+new+york+1992": 5, "keeping+the+promise+1997": 6, "mascara+1999": 7, "paths+of+hate+2011": 8, "prinsessa+2010": 9, "season+for+assassins+1975": 10, "so+much+so+fast+2006": 11, "sweepers+1999": 12, "the+bleeding+2009": 13, "the+madagascar+penguins+in+a+christmas+caper+2005": 14, "the+manzanar+fishing+club+2012": 15, "the+true+meaning+of+christmas+specials+2002": 16, "thrill+ride+the+science+of+fun+1997": 17, "vincent+1982": 18}
    assert(get_iid_dict_from_json() == res)

def test_get_uid_dict_from_json():
    res = {"6581": 0, "14243": 1, "25252": 2, "37923": 3, "52307": 4, "56874": 5, "66948": 6, "113057": 7, "122147": 8, "132023": 9, "134311": 10, "155588": 11, "159203": 12, "168290": 13, "173398": 14, "190825": 15, "194627": 16, "211819": 17, "222891": 18, "225378": 19}
    assert(get_uid_dict_from_json() == res)

def test_get_watched_movied_dict_from_json():
    res = {"0": [9], "1": [5], "2": [11], "3": [14], "4": [2], "5": [3], "6": [8], "7": [15], "8": [7], "9": [1], "10": [16], "11": [13], "12": [10], "13": [17], "14": [0], "15": [18], "16": [15], "17": [4], "18": [6], "19": [12]}
    assert(get_watched_movies_dict_from_json() == res)

# online evaluation
def test_get_avg_inference_time():
    telemetry_online_file="data/Telemetry_Online_test.csv"
    dtypes = {'Modelname': 'str', 'TimeToPredict': 'float'}
    parse_dates = ['Timestamp']
    df = pd.read_csv(telemetry_online_file, dtype=dtypes, parse_dates=parse_dates)
    
    df_len = len(df.index)
    mask = [True] * df_len

    expected_result = 103.824125

    assert get_avg_inference_time(df, mask) == expected_result
