create & activate virtual env then install dependency:
 
with venv/virtualenv + pip:

$ python -m venv env  # use `virtualenv env` for Python2, use `python3 ...` for Python3 on Linux & macOS
$ source env/bin/activate  # use `env\Scripts\activate` on Windows
$ pip install -r requirements.txt

to run:

$ cd movie-recommender

$ flask run --host=128.2.205.106 --port=8082
running on http://127.0.0.1:5000

Step 1 :

to process full data:

$ python model_training_and_evaluation_codes\data_processing_pipe1.py model_training_and_evaluation_codes\data\kafka_ratings.txt model_training_and_evaluation_codes\data\

Step 1 :
to process test data(sample of 20):

$ python model_training_and_evaluation_codes\data_processing_pipe1.py model_training_and_evaluation_codes\data\kafka_ratings_test.txt model_training_and_evaluation_codes\data\

Step 2 :
to train on stored proceessed data:

$ python model_training_and_evaluation_codes\model_training_pipe2.py model_training_and_evaluation_codes\data\

Step 3 :
to run the CI tests on local (inside recommender folder):

$ pytest
