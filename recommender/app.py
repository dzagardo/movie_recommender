from extensions import flask_app
import json
from flask import Response
from datetime import datetime
import os
import random
import requests
import marshal
from prometheus_client import (
  Counter,
  Histogram,
  Summary,
  Enum,
  start_http_server
)


# Expose metrics to prometheus through the below port
start_http_server(8765)

#Counter, Gauge, Histogram, Summaries
REQUEST_COUNT = Counter(
  'request_count',
  'Recommendation Request Count',
  ['http_status']
)
REQUEST_LATENCY = Summary(
  'request_latency_seconds',
  'Request latency'
)
RECOMMEND_RATING_SCORE = Summary(
  'recommend_rating_score',
  'Recommendation rating score'
)
AVAILABILITY_STATES = ['starting', 'running', 'stopped']
LOAD_BALANCER_STATE = Enum(
  'load_balancer_state',
  'state of load balancer', 
  states=AVAILABILITY_STATES
)
MODEL_A_STATE = Enum(
  'model_a_state', 
  'state of load balancer',
  states=AVAILABILITY_STATES
)
MODEL_B_STATE = Enum(
  'model_b_state',
  'state of load balancer',
  states=AVAILABILITY_STATES
)


probability = 0.5
users_to_experiment = {}
dummy_response = "the+magnificent+seven+1960,explorers+1985,keep+the+aspidistra+flying+1997,the+patsy+1928,rango+2011,1114+2003,man+of+the+west+1958,son+of+rambow+2007,secondhand+lions+2003,the+burmese+harp+1956,predator+2+1990,summer+of+blood+2014,the+four+2012,the+nest+2002,disorganized+crime+1989,digging+to+china+1997,pauline+at+the+beach+1983,pauline+dtective+2012,the+mighty+macs+2009,movie+days+1994"
def checkHealth(ip_addr):
    return os.system('nc -vz '+ip_addr) == 0

# ===================================================================
#                          Initializations
# ===================================================================

# The only endpoint exposed which provides the recommendation for a user
# Returns top 20 movie recommendations for a user given their ID
@flask_app.route("/recommend/<uid>", methods=["GET"])
def recommend(uid):
  try:
    #Make sure uid is a number
    uid_num = int(uid)
    #needs to be nonneg
    if (uid_num < 0):
      return Response(
        "Bad request",
        status=400,
    )
  except:
      return Response(
        "Bad request",
        status=400,
      )

  #Rerouting for docker 
  start_time = datetime.now()
  A_server_up = checkHealth('0.0.0.0 7004')
  if A_server_up:
    MODEL_A_STATE.state('running')
  else:
    MODEL_A_STATE.state('stopped')
  B_server_up = checkHealth('0.0.0.0 7005')
  if B_server_up:
    MODEL_B_STATE.state('running')
  else:
    MODEL_B_STATE.state('stopped')
  obj = {
    "uid": uid
  }
  request_mod_2 = random.randint(0,9)%2
  status_code = None
  rating_score = None
  if A_server_up and B_server_up:
    request = None 
    if uid in users_to_experiment:
      request = users_to_experiment[uid]
    else:
      if request_mod_2 == 0:
        request = "A"
        users_to_experiment[uid] = "A"
      else:
        request = "B"
        users_to_experiment[uid] = "B"
    if request == "A":
      obj["model"] = "A"
      response = requests.post('http://0.0.0.0:7004/recommend', json = obj)
      status_code = response.status_code
      rating_score = response.json()['score']
      response = f"{response.json()['movies']}"
    else:
      obj["model"] = "B"
      response = requests.post('http://0.0.0.0:7005/recommend', json = obj)
      status_code = response.status_code
      rating_score = response.json()['score']
      response = f"{response.json()['movies']}"
  elif A_server_up and not B_server_up:
    obj["model"] = "A"
    response = requests.post('http://0.0.0.0:7004/recommend', json = obj)
    status_code = response.status_code
    rating_score = response.json()['score']
    response = f"{response.json()['movies']}"
  elif B_server_up and not A_server_up:
    obj["model"] = "B"
    response = requests.post('http://0.0.0.0:7005/recommend', json = obj)
    status_code = response.status_code
    rating_score = response.json()['score']
    response = f"{response.json()['movies']}"
  else:
    response = dummy_response
    status_code = 200
    rating_score = float(3.00)

  end_time = datetime.now()
  REQUEST_COUNT.labels(f"{status_code}").inc()
  total_time = end_time - start_time
  REQUEST_LATENCY.observe(total_time.total_seconds())
  RECOMMEND_RATING_SCORE.observe(rating_score)
  LOAD_BALANCER_STATE.state('running')
  return f"{response}"

if __name__ == "__main__":
  flask_app.run(host='0.0.0.0', port=8082, debug=False)
