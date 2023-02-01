from datetime import datetime
import requests
import csv
from kafka import KafkaConsumer
from prometheus_client import (
  Counter,
  Summary,
  start_http_server
)

# Expose metrics to prometheus through the below port
start_http_server(8766)

#Counter, Gauge, Histogram, Summaries
AM_RECOMMENDATION_COUNT = Counter(
  'adult_movies_recommended_count_to_children',
  'Adult movies recommendation count to children',
  ['movie_name']
)

def getKafkaMessages():
    topic = 'movielog4'
    consumer = KafkaConsumer(
    topic,
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='latest',
    enable_auto_commit=True,
)
    messages = []
    # max_message_limit = 5000
    for i, message in enumerate(consumer):
        # if i > max_message_limit:
        #     break
        messages.append(message.value.decode())
        parse_request(message.value.decode())
    return messages
 
 
def read_from_kafka():
    parsed_messages = []
    for message in getKafkaMessages():
        parsed_messages.append(parse_request(message))
    return parsed_messages
 
#check that msg starts with 'status' followed by a space, then a number
#accepts: 'status 200'
#rejects: 'status invalid'
#rejects: 'stat 200' 
def well_formed_status_msg(statusMsg):
    spaceIdx = statusMsg.index(" ")
    if (not statusMsg.startswith("status")):
        return False
    try:
        int(statusMsg[spaceIdx+1:])
    except:
        return False
    return True
 
#checks that starts with a number, then a space followed by 'ms'
#accepted: 200 ms
#rejected: two ms
#rejected: 2 s 
def well_formed_response_time(response_time):
    if (not response_time.endswith("ms")):
        return False
    msIdx = response_time.index(" ms")
    time = response_time[:msIdx]
    try:
        int(time)
    except:
        return False
    return True

#format of input    
#recommendation request <server>, status <200 for success>, result: <recommendations>, <responsetime>
def parse_recommendation_req(request_str):
    str_start = "recommendation request 17645-team04.isri.cmu.edu:8082"
    try:
        #check that requests starts with 'recommendation request' followed by our server
        if (request_str.index(str_start) != 0):
            return None
        splitByComma = request_str.split(",")
        statusMsg = splitByComma[1].strip()
        #check status part of msg is the right format 
        if (not well_formed_status_msg(statusMsg)):
            return None
        result = ",".join(splitByComma[2:-1])
        response_time = splitByComma[-1].strip()
        #check response time part of msg is the right format 
        if (not well_formed_response_time(response_time)):
            return None
        recs = result[len("result: "):].strip()
        return {"status": statusMsg[statusMsg.index("status ") + len("status "):], "recommendations": recs, "response_time":response_time}
    except:
        return None
 
#format
#<time>,<userid>,GET /data/m/<movieid>/<minute>.mpg
def parse_movie_req(request_str):
    watchMovieReqStart = "GET /data/m/"
    try:
        if (request_str.index(watchMovieReqStart) != 0):
            return None
        afterReqStart = request_str[len(watchMovieReqStart):]
        slashIdx = afterReqStart.index("/")
        movieId = afterReqStart[:slashIdx]
        minute = afterReqStart[slashIdx + 1:]
        #minute part of input must end with .mpg
        if (not minute.endswith(".mpg")):
            return None
        mpgIdx = minute.index(".mpg")
        minuteNum = int(minute[:mpgIdx].strip())
        #numeric part of minute needs to be a nonnegative integer
        if (minuteNum < 0):
            return
        return afterReqStart[:slashIdx]
    except:
        return None

#format:
#<time>,<userid>,GET /rate/<movieid>=<rating>
def parse_rating_req(request_str):
    rateMovieReqStart = "GET /rate/"
    try:
        if (request_str.index(rateMovieReqStart) != 0):
            return None
        afterReqStart = request_str[len(rateMovieReqStart):]
        #movieid and rating must be separated by =
        equalsIdx = afterReqStart.index("=")
        movieId = afterReqStart[:equalsIdx]
        rating = afterReqStart[equalsIdx+1:].strip()
        #rating must be between 1 and 5
        if (int(rating) < 1 or int(rating) > 5):
            return
        return {movieId: rating}
    except:
        return None
 
def well_formed_msg_start(msgs):
    if (len(msgs) < 2):
        return False
    #check that <time> part of request is valid
    try:
        tIdx = msgs[0].index("T")
        beforeT = msgs[0][:tIdx]
        format = "%Y-%m-%d"
        datetime.strptime(beforeT, format)
    except:
        return False
    #check that <userid> part of request is valid
    try:
        if (int(msgs[1]) < 0):
            return False
    except ValueError:
        return False
    return True
 
 
def parse_request(message: str):
    recommendationReqStart = "recommendation request"
    watchMovieReqStart = "GET /data/m/"
    rateMovieReqStart = "GET /rate/"
    splitByComma = message.split(",")
    # return early if message does not at least have <time>,<userid>
    if (not well_formed_msg_start(splitByComma)):
        return None
    userId = splitByComma[1]
    if (not userId in children_ids):
        return
    requestStr = ",".join(splitByComma[2:])
    if (requestStr.startswith(recommendationReqStart)):
        rec_req = parse_recommendation_req(requestStr)
        if (rec_req != None):
            if userId in children_ids:
                for id in rec_req['recommendations'].split(","):
                    response = requests.get("http://128.2.204.215:8080/movie/" + id.strip())
                    json_response = response.json()
                    try: 
                        isAdult = f"{json_response['adult']}"
                        #need string cmp bc parsing json
                        if (isAdult == "True"):
                            adult_movies_recommended[userId].append(id.strip())
                    except:
                        print("oof")
            return {userId: rec_req}
    elif (requestStr.startswith(watchMovieReqStart)):
        movie_req = parse_movie_req(requestStr)
        if (movie_req != None):
            if (userId in children_ids):
                stripped_req = movie_req.strip()
                response = requests.get("http://128.2.204.215:8080/movie/" + stripped_req)
                try: 
                    isAdult = f"{response.json()['adult']}"
                    #need string cmp bc parsing json
                    if (isAdult == "True" and stripped_req in adult_movies_recommended[userId]):
                        adult_movies_recommended_count += 1
                        AM_RECOMMENDATION_COUNT.labels(f"{response.json()['title']}").inc()
                except:
                    print("oof")
        return {userId: movie_req}
    elif (requestStr.startswith(rateMovieReqStart)):
        rate_movie_req = parse_rating_req(requestStr)
        #only write to kafka txt if request is correctly parsed 
        if (rate_movie_req != None):
            return {userId: rate_movie_req}
    else:
        return None

children_ids = []
adult_movies_recommended = {}
adult_movies_recommended_count = 0
with open("data/children_data.csv") as f:
    reader = csv.reader(f, delimiter="\t")
    for i in reader:
        children_ids.append(i[0].split(",")[0])
for id in children_ids:
    adult_movies_recommended[id] = [] 

read_from_kafka()
