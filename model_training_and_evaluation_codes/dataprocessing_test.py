
import datetime
import os
import re
import pytest
from dateutil import parser
from dataprocessing import DataInitialProcessing, dropping_duplicates, DataPreProcessing

test_file_1 = './data/kafka_scripts.txt'
test_save_file = './data/preprocessed_test.csv'
sample_size = 5
def test_DataInitialProcessing_check_size():
    data = DataInitialProcessing(test_file_1)
    assert(data.size == 48)

def test_DataInitialProcessing_check_size_for_each_col():
    data = DataInitialProcessing(test_file_1)
    assert(data['UserID'].size == 12)

def test_cols_present():
    data = DataInitialProcessing(test_file_1)
    assert('UserID' in data)
    assert('MovieName' in data)
    assert('rating' in data)
    assert('Timestamp' in data)

def test_duplicates_dropped():
    data1 = DataInitialProcessing(test_file_1)
    data2 = dropping_duplicates(data1)
    assert(data1.size != data2.size)

def test_size_after_dropping_dupes():
    data1 = DataInitialProcessing(test_file_1)
    data2 = dropping_duplicates(data1)
    assert(data2.size == 40)

def test_file_save():
    if os.path.isfile(test_save_file):
        os.remove(test_save_file)
    assert(not os.path.isfile(test_save_file))
    DataPreProcessing(test_file_1, test_save_file)
    assert(os.path.isfile(test_save_file))
    if os.path.isfile(test_save_file):
        os.remove(test_save_file)

def test_sampling():
    data = DataInitialProcessing(test_file_1)
    new_expected_size = sample_size * 4
    assert(data.size != new_expected_size)
    data = data.sample(sample_size)
    assert(data.size == new_expected_size)


# test that rating is 1-5 and it can be converted to numbers
def test_rating():
    data = DataInitialProcessing(test_file_1)
    valid_rating = True
    for rate in data['rating']:
        if( int(rate) > 5 or int(rate) < 0):
            valid_rating = False
            break
    assert(valid_rating)

# test the movie format--- 
def test_movie_name_format():
    data = DataInitialProcessing(test_file_1)
    valid_movie = True
    rex = re.compile('[a-zA-Z][+]+[0-9]')
    for movie in data['MovieName']:
        if(rex.search(movie) == None):
            valid_movie = False
            break
    assert(valid_movie)


# test that timestamp is valid
def test_timestamp_format():
    data = DataInitialProcessing(test_file_1)
    valid_date = True
    rex = re.compile('[1-2][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]T[0-2][0-9]:[0-6][0-9]:[0-6][0-9]')
    for date in data['Timestamp']:
        if(not rex.match(date)):
            valid_date = False
            break
    assert(valid_date)

# test that user id is a valid number
def test_user_id():
    data = DataInitialProcessing(test_file_1)
    valid_user = True
    for user in data['UserID']:
        valid_user = str(user).isnumeric()
        if valid_user == False:
            break
    assert(valid_user)