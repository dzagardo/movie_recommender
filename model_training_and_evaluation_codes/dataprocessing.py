# DataPreProcessing.py

import pandas as pd
import numpy as np
import pickle
from collections import defaultdict
import json

def make_Dictionaries(processed_data_file="/content/drive/MyDrive/Collab Codes/MLIP/preprocessed.csv",dictionary_storage_location="/content/drive/MyDrive/Collab Codes/MLIP/"):
  Data=pd.read_csv(processed_data_file)

    
  # Function to return a default
  # values for keys that is not
  # present
  def def_value():
      return "Not Present"
        
  # Defining the dict
  iid_dict = defaultdict(def_value)
  uid_dict = defaultdict(def_value)
  sort_movies=Data['MovieName'].unique()
  sort_movies.sort()
  for i in range(len(sort_movies)):
    iid_dict[sort_movies[i]]=i

  sort_users=Data['UserID'].unique()
  sort_users.sort()
  for i in range(len(sort_users)):
    uid_dict[int(sort_users[i])]=i

  with open(dictionary_storage_location+"iid_dict.json", "w") as outfile:
    json.dump(iid_dict, outfile)
  with open(dictionary_storage_location+"uid_dict.json", "w") as outfile:
    json.dump(uid_dict, outfile)

  return True

def DataInitialProcessing(file):
  df=pd.read_csv(file,header=None)
  df.columns=["Timestamp","UserID","Log"]
  df["MovieName=Rating"]=df["Log"].apply(lambda x: x.split("/")[2])
  df["MovieName"]=df["MovieName=Rating"].apply(lambda x: x.split("=")[0])
  df["rating"]=df["MovieName=Rating"].apply(lambda x: x.split("=")[1])
  Data=df[["UserID","MovieName","rating","Timestamp"]]
  return Data

def DataRemapping(processed_data_file="/content/drive/MyDrive/Collab Codes/MLIP/preprocessed.csv",dictionary_storage_location="/content/drive/MyDrive/Collab Codes/MLIP/"):
  # Opening JSON file
  with open(dictionary_storage_location+'iid_dict.json') as json_file:
      iid_dict = json.load(json_file)
  with open(dictionary_storage_location+'uid_dict.json') as json_file:
      uid_dict = json.load(json_file)
  def def_value():
      return "Not Present"
        
  # Defining the dict
  iid_dict = defaultdict(int,iid_dict)
  uid_dict = defaultdict(int,uid_dict)
  
  Data=pd.read_csv(processed_data_file)
  Data['item']=Data['MovieName'].apply(lambda x: iid_dict[x])
  Data['user']=Data['UserID'].apply(lambda x: uid_dict[str(x)])
  # print(Data.head())
  Data_selected=Data[['user','item','rating']]
  # print(Data_selected.head())
  Data_selected.to_csv(dictionary_storage_location+"RemappedData.csv")
  
  User_watched_movies=Data_selected.groupby('user')['item'].apply(list)
  User_watched_movies=dict(User_watched_movies)
  with open(dictionary_storage_location+"Users_Watched_Movies.json", "w") as outfile:
    json.dump(User_watched_movies, outfile)
  
  return True

def DataPreProcessing(file_path="/content/drive/MyDrive/Collab Codes/MLIP/kafka_ratings.txt",save_as="/content/drive/MyDrive/Collab Codes/MLIP/preprocessed.csv"):
  df=pd.read_csv(file_path,header=None)
  
  df.columns=["Timestamp","UserID","Log"]
  df["MovieName=Rating"]=df["Log"].apply(lambda x: x.split("/")[2])
  df["MovieName"]=df["MovieName=Rating"].apply(lambda x: x.split("=")[0])
  df["rating"]=df["MovieName=Rating"].apply(lambda x: x.split("=")[1])
  Data=df[["UserID","MovieName","rating","Timestamp"]]
  return Data

def dropping_duplicates(Data):
  return Data.drop_duplicates(subset=['UserID', 'MovieName'],keep="last")

def DataPreProcessing(file_path="/content/drive/MyDrive/Collab Codes/MLIP/kafka_ratings.txt",save_as="/content/drive/MyDrive/Collab Codes/MLIP/preprocessed.csv"):

  Data=DataInitialProcessing(file_path)
  
  # Data sort on timestamp

  # Few duplicates of user-> movie were dropped, the lateset was picked
  Data= dropping_duplicates(Data)
  print("Data.shape",Data.shape)
  
  #Exception handling for data save
  try : 
    Data.to_csv(save_as)
    print("Saved at: ",save_as)
    return True
  except:
    print("Unable to save at: ",save_as)
    return False


#Codes to store the model into pickle 
def store_model_into_pickle(algo,algo_name,dest_location="/content/drive/MyDrive/Collab Codes/MLIP/"):
  file1 = open(dest_location+algo_name+".pickle", "wb")
  pickle.dump(algo, file1)
  file1.close()
  print(algo_name+" Stored at/as :"+dest_location+algo_name+".pickle")
  return True

#Codes to get the model from pickle 
def get_model_from_pickle(algo_name,file_location="/content/drive/MyDrive/Collab Codes/MLIP/"):
  file_to_read = open(file_location+algo_name+".pickle", "rb")
  loaded_object = pickle.load(file_to_read)
  file_to_read.close()
  print("returned model object")
  return loaded_object