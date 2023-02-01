from surprise import Reader
from surprise import Dataset
import pandas as pd
import numpy as np
from surprise import SVD
from surprise.model_selection import GridSearchCV
from surprise.accuracy import rmse
from surprise.model_selection import KFold
from sklearn.model_selection import train_test_split

def train_SVD_wGridSearch(processed_data_file="/content/drive/MyDrive/Collab Codes/MLIP/RemappedData.csv"):
  
  
  Data_selected=pd.read_csv(processed_data_file)

  reader = Reader(rating_scale=(1, 5))

  # Loads Pandas dataframe
  df2=Data_selected[["user", "item", "rating"]]

  train,test = train_test_split(df2, test_size=0.33, shuffle=False)

  data = Dataset.load_from_df(df2, reader)
  train = Dataset.load_from_df(train, reader)
  test = Dataset.load_from_df(test, reader)

  best_params={'n_epochs': 10, 'lr_all': 0.005, 'reg_all': 0.4}

  svd_algo = SVD(n_epochs=best_params['n_epochs'],
                lr_all=best_params['lr_all'],
                reg_all=best_params['reg_all'])
  # Train
  trainingSet = data.build_full_trainset()
  testingSet = test.build_full_trainset()
  fullSet = data.build_full_trainset()
  svd_algo.fit(trainingSet)
  predictions = svd_algo.test(testingSet.build_testset())
  er=rmse(predictions)
  print("ERROR",er)
  return svd_algo,np.mean(er)
