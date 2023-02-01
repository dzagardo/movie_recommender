from surprise import Reader
from surprise import SVDpp
from surprise import Dataset
import pandas as pd
from surprise.accuracy import rmse
from surprise.model_selection import KFold
import numpy as np
from sklearn.model_selection import train_test_split

def train_svdpp(processed_data_file="/content/drive/MyDrive/Collab Codes/MLIP/RemappedData.csv"):
  # Code below was inspired from MLIP recitation
    
  Data_selected=pd.read_csv(processed_data_file)

  reader = Reader(rating_scale=(1, 5))

  # Loads Pandas dataframe
  df2=Data_selected[["user", "item", "rating"]]

  train,test = train_test_split(df2, test_size=0.33, shuffle=False)

  data = Dataset.load_from_df(df2, reader)
  train = Dataset.load_from_df(train, reader)
  test = Dataset.load_from_df(test, reader)
  svd_algo = SVDpp()
  # Train
  trainingSet = data.build_full_trainset()
  testingSet = test.build_full_trainset()
  fullSet = data.build_full_trainset()
  svd_algo.fit(trainingSet)
  predictions = svd_algo.test(testingSet.build_testset())
  er=rmse(predictions)
  print("ERROR",er)
  return svd_algo,np.mean(er)