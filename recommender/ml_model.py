from operator import itemgetter
import json
from collections import defaultdict
from datetime import datetime, timedelta
import pandas as pd
import time
from flask import Flask, request
from helpers import get_model_from_pickle, get_iid_dict_from_json, get_uid_dict_from_json, get_watched_movies_dict_from_json
from verta import Client
from verta.utils import ModelAPI
from threading import Thread, Lock
import asyncio

mutex = Lock()

app = Flask('ml-model-server')
modelA = get_model_from_pickle("svd_model_a")
modelB = get_model_from_pickle("svd_model_b")
request_count = 0
#add comment

# Get data for movies, users, and ratings
iid_dict_from_json = get_iid_dict_from_json()
uid_dict_from_json = get_uid_dict_from_json()
Users_Watched_Movies_from_json = get_watched_movies_dict_from_json()
client = Client('http://128.2.205.106:3000/')
proj = client.set_project("A/B testing")
# Defining the dict
iid_dict = defaultdict(int,iid_dict_from_json)
uid_dict = defaultdict(int,uid_dict_from_json)

def invert_dict(d):
  return {v: k for k, v in d.items()}

#Defining inverted dictionaries
inv_uid = invert_dict(uid_dict)
inv_iid = invert_dict(iid_dict)
#iid_dict_from_json, uid_dict_from_json, Users_Watched_Movies_from_json = \
 # get_data_dictionaries()

# Predict estimated rating a user might give for a movie
def predict(algo,uid,iid,r=None):
  rating = algo.predict(int(uid),int(iid),r)
  return rating

def get_top_20_ids(preds_for_a_user):
  top20_movies = dict(sorted(preds_for_a_user.items(), key = itemgetter(1), reverse = True)[:20])
  sum_pred_score = 0
  for est_score in top20_movies.values():
    sum_pred_score += est_score
  sum_pred_score = sum_pred_score/20
  return sum_pred_score, dict(sorted(preds_for_a_user.items(), key = itemgetter(1), reverse = True)[:20])

def get_unseen_movies(Users_Watched_Movies_from_json, model_uid, iid_dict):
  all_movies_user_saw=Users_Watched_Movies_from_json[model_uid]
  all_movies = set(list(iid_dict.values()))
  movies_watched = set(all_movies_user_saw)

  # Removing movies which user has already seen
  return all_movies.difference(movies_watched)

def get_top_20_movie_names(top20movieIDs, inv_iid):
  top20movieNames=[inv_iid[i] for i in list(top20movieIDs.keys())]
  # Return comma seperated list of movies
  return ",".join(top20movieNames)

def get_now():
  return datetime.now()

def get_inference_time(start_time):
  return (get_now() - start_time).total_seconds() * 1000

def get_file():
  telemetry_online_file="data/Telemetry_Online.csv"
  dtypes = {'Modelname': 'str', 'TimeToPredict': 'float'}
  parse_dates = ['Timestamp']
  return pd.read_csv(telemetry_online_file, dtype=dtypes, parse_dates=parse_dates)

def get_path():
  return "data/Telemetry_Online.csv"

def plot_telemetry(time_for_infering):
  try:
    online_eval=get_file()
    print("online", online_eval)
    df1 = {'Modelname':'default_svd', 'TimeToPredict':time_for_infering, 'Timestamp': get_now()}
    online_eval = online_eval.append(df1, ignore_index = True)
    online_eval.to_csv(get_path(),index=False)
    return online_eval
  except:
    print("--------OOF---------")


async def write_to_verta(time, model):
  global request_count
  global client
  global mutex
  mutex.acquire()
  if request_count == 0:
    expt = client.set_experiment(model)
    run = client.set_experiment_run("AB_TEST_EXP")
    run.log_observation("prediction_mean", sum(time.values())/20)
  request_count += 1
  request_count %= 20000
  mutex.release()

# Get top 20 recommended movies
# iid_dict_from_json: dictionary where  keys are movie names, values are ids
# uid_dict_from_json: map string user ids to model uid
# Users_Watched_Movies_from_json: model uids to movie lists
def recommend_top_20_movies_for_user(algo,og_user, iid_dict_from_json, uid_dict_from_json, Users_Watched_Movies_from_json, model, destination_path="recommender\data"):
  start_time = datetime.now()
  og_user=str(og_user)
  # Default value
  def def_value():
      return "Not Present"
  model_uid=str(uid_dict[og_user])
  unseen_movies = get_unseen_movies(Users_Watched_Movies_from_json, model_uid, iid_dict)
  predictions=[]
  for movie in unseen_movies:
    # user id, movie id, r_ui, rating
    predictions.append(predict(algo,model_uid,movie)[3])
  preds_for_a_user=dict(zip(unseen_movies,predictions))
  avg_pred_score, top20movieIDs = get_top_20_ids(preds_for_a_user)
  asyncio.run(write_to_verta(top20movieIDs, model))
  return {"movies": get_top_20_movie_names(top20movieIDs, inv_iid), "score": avg_pred_score}

@app.route('/')
def healthcheck():
  return 'Server UP!'

@app.route('/recommend', methods=["POST"])
def get_top_20_movies():
  print("slayful!", request.json)
  model = None
  if (request.json['model'] == "A"):
    model = modelA
  elif(request.json['model'] == "B"):
    model = modelB
  return recommend_top_20_movies_for_user(model,
  request.json['uid'], 
  iid_dict_from_json, 
  uid_dict_from_json, 
  Users_Watched_Movies_from_json, request.json['model'])  

def main():
    app.run(host='0.0.0.0', port=8081, debug=False)

if __name__ == '__main__':
    main()
