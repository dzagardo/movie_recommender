from dataprocessing import *

import time
import sys
import json



def main(source_path, destination_path_folder,sample_size=170000):
    print("Running the data processing steps on the pulled data")
    
    start_time = time.time()
    DataPreProcessing(source_path, destination_path_folder+"preprocessed.csv")
    end_time=time.time()
    time_for_dataProcessing=(time.time() - start_time)
    print("Data has been processed and saved")
    print("It took this much time :",time_for_dataProcessing)    
    
    df=pd.read_csv(destination_path_folder+"preprocessed.csv")
    #sample size can also be passed as argument
    sampled_df=df.sample(sample_size)
    sampled_df.to_csv(destination_path_folder+"sampled_170kpreprocessed.csv")
    print("Data has been sampled and saved to ", destination_path_folder+"sampled_170kpreprocessed.csv")
    
    make_Dictionaries(destination_path_folder+"sampled_170kpreprocessed.csv",destination_path_folder)
    print("Data has been processed to make dictionary and saved to folder :", destination_path_folder+" as iid_dict.json and uid_dict.json")
    DataRemapping(destination_path_folder+"sampled_170kpreprocessed.csv",destination_path_folder)
    print("Data has been processed to ReMap and saved to folder :", destination_path_folder+" as RemappedData.csv and Users_Watched_Movies.json")

# e.g. command Windows : python model_training_and_evaluation_codes\data_processing_pipe1.py model_training_and_evaluation_codes\data\kafka_ratings.txt model_training_and_evaluation_codes\data\
# e.g. command Windows : python model_training_and_evaluation_codes\data_processing_pipe1.py model_training_and_evaluation_codes\data\kafka_ratings_test.txt model_training_and_evaluation_codes\data\

# This file needs to be provided with three paths as arguments, the source of kafka rating and then the desired destination of the processed file and destination path of sampled file
if __name__ == "__main__":
    source_path, destination_path =sys.argv[1:]
    main(source_path, destination_path)