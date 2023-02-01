from dataprocessing import *
from system_measures import *
from datetime import datetime
import sys
from train_svd import *
from train_svdpp import *
import pandas as pd
import numpy as np
import pickle


def main(destination_path):
    
    print("Running the data to fit model and save")
    
    start_time1 = datetime.now()
    svdpp_algo,avgerror_svdpp=train_svdpp(destination_path+"RemappedData.csv")
    end_time= datetime.now()
    time_for_svdpp=(end_time- start_time1).total_seconds() * 1000
    store_model_into_pickle(svdpp_algo,"svdpp_model",destination_path)
    
    print("SVD PP Model has been Fit and saved")
    print("It took this much time :",time_for_svdpp)    
    print("Avg Error Was (Validate/Test):",avgerror_svdpp)
    

    start_time2 = datetime.now()
    svd_algo,avgerror_svd=train_SVD_wGridSearch(destination_path+"RemappedData.csv")
    end_time=datetime.now()
    time_for_SVD=(end_time - start_time2).total_seconds() * 1000

    store_model_into_pickle(svd_algo,"svd_model",destination_path)
    print("SVD Model has been Fit and saved")
    print("It took this much time :",time_for_SVD)    
    print("Avg Error Was (Validate/Test):",avgerror_svd)

    telemetry_offline_file="model_training_and_evaluation_codes\Telemetry\Telemetry_Offline.csv"
    try:
        print("Existing Telemetry File offline eval found, hence APPENDED")
        offline_eval=pd.read_csv(telemetry_offline_file)
        df1 = {'Timestamp': start_time1 , 'Modelname':'svd', 'TimeToTrain':time_for_SVD,  'RMSE_test':avgerror_svd}
        df2 = {'Timestamp': start_time2 , 'Modelname':'svdpp', 'TimeToTrain':time_for_svdpp, 'RMSE_test':avgerror_svdpp}
        offline_eval = offline_eval.append(df1, ignore_index = True)
        offline_eval = offline_eval.append(df2, ignore_index = True)
        offline_eval.to_csv(telemetry_offline_file,index=False)
    except:
        offline_eval=pd.DataFrame()
        print("Existing Telemetry File offline eval not found, hence created new")
        print("Created at",telemetry_offline_file)
        df1 = {'Timestamp': start_time1 , 'Modelname':'svd', 'TimeToTrain':time_for_SVD, 'RMSE_test':avgerror_svd}
        df2 = {'Timestamp': start_time2 , 'Modelname':'svdpp', 'TimeToTrain':time_for_svdpp, 'RMSE_test':avgerror_svdpp}
        offline_eval = offline_eval.append(df1, ignore_index = True)
        offline_eval = offline_eval.append(df2, ignore_index = True)
        offline_eval.to_csv(telemetry_offline_file,index=False)
    


    

# e.g. cmd : python model_training_and_evaluation_codes\model_training_pipe2.py model_training_and_evaluation_codes\data\
# This file needs to be provided with 1 path as arguments, the source of processed data and that also becomes the desired destination of the processed file

if __name__ == "__main__":
    destination_path =sys.argv[1:][0]
    main(destination_path )