
# MLIP team 4 code
# Code to get a model's performace, wrt :
# 1.Avg. Training time 
# 2.RMSE on a K-Folded Cross Validation Process
# 3.Inference time
# 4.Model Size
#  
# Assumption that a model has been trained earlier, however, this below process only uses the architecture and not the trained model. It will re-fit the data again.
# Hence, Data Location is essential.
# The purpose of this code is only model evaualtion for the sake of seperation of concerns.

from surprise import Reader
from surprise import NMF
from surprise import SVDpp
from surprise import SVD
from surprise import Dataset
from surprise.accuracy import rmse
from surprise.model_selection import KFold
import numpy as np
import pandas as pd
import pickle 
import os
#Please update your desitination location if its different

#Codes to store the model into pickle 
def store_model_into_pickle(algo,algo_name,dest_location="/content/drive/MyDrive/Collab Codes/MLIP/"):
  file1 = open(dest_location+algo_name+".pickle", "wb")
  pickle.dump(algo,file1)
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


def get_avg_throughputtime(data_location="/content/drive/MyDrive/Collab Codes/MLIP/preprocessed.csv"):
  df=pd.read_csv(data_location)
  request_list=['http://128.2.205.106:8082/recommend/'+str(i) for i in np.unique(df.UserID.sample(500))]

  times=[]
  # Making a get request
  for i in request_list:
    response = requests.get(i)
    times.append(response.elapsed.total_seconds())

  print("AVG Throughput",np.mean(times))
  return np.mean(times)

#code to get the model size (i.e. the pickle file size)
def get_model_size(location="/content/drive/MyDrive/Collab Codes/MLIP/svdpp_model.pickle"):
  return (os.stat("/content/drive/MyDrive/Collab Codes/MLIP/svdpp_model.pickle").st_size / (1024 * 1024))

# An existing model architechture chan be passed to the below code, and the code will re-fit the model on the k-folded data and give the most realistic k-fold cross validation RMSE
def evaluate_model(model_name="svdpp_model",processed__test_data_file="/content/drive/MyDrive/Collab Codes/MLIP/RemappedData.csv"):

  algo=get_model_from_pickle(model_name)
  Data_selected=pd.read_csv(processed__test_data_file)
  reader = Reader(rating_scale=(1, 5))

  # Loads Pandas dataframe
  data = Dataset.load_from_df(Data_selected[["user", "item", "rating"]], reader)

  #KFold helps us to spit the dataset into n folds, this will help us seperate training and testing splits while calculating testing erros

  kf = KFold(n_splits=4)
  errors=[]
  training_time=[]
  for trainset, testset in kf.split(data):
    start_time = time.time()
    #Fitting
    algo.fit(trainset)      
    end_time=time.time()               
    time_for_fitting=(time.time() - start_time)

    # we are checking for test rmse only, and computing avg of all CV in the k splits
    predictions = algo.test(testset)
    #appending results to a list for future references
    errors.append(rmse(predictions))
    training_time.append(time_for_fitting)
    
  # This code only returns the avg RMSE error and avg training time for a k folded dataset
  return np.mean(errors),np.mean(training_time)