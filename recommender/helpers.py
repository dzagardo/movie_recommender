import json
import pickle
import os

# worth testing?
def get_model_from_pickle(recommender_model):
  model_path = os.path.join(".", "recommender_models")
  with open(f"{model_path}/{recommender_model}.pickle", "rb") as model_to_read:
    loaded_model = pickle.load(model_to_read)
    print("HELPER HI", loaded_model)
    return loaded_model


def read_json(file_path):
  with open(f"{file_path}") as json_file:
    json_dict = json.load(json_file)
  return json_dict

def get_iid_dict_from_json():
  file_path = os.path.join(".", "data")
  return read_json(f"{file_path}/iid_dict.json")

def get_uid_dict_from_json():
  file_path = os.path.join(".", "data")
  return read_json(f"{file_path}/uid_dict.json")

def get_watched_movies_dict_from_json():
  file_path = os.path.join(".", "data")
  return read_json(f"{file_path}/Users_Watched_Movies.json")

def get_avg_inference_time(df, mask):
  return sum(df.loc[mask]['TimeToPredict'])/len(df.loc[mask])
