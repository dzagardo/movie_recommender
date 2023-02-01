import os
import sys
from datetime import datetime
from json import dumps, loads
from os import path
from random import randint
from time import sleep
from dateutil import parser
 
from kafka import KafkaConsumer, KafkaProducer
 
def getKafkaMessages():
    topic = 'movielog4'
    consumer = KafkaConsumer(
    topic,
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='latest',
    enable_auto_commit=True,
)
    messages = []
    max_message_limit = 100000
    for i, message in enumerate(consumer):
        if i > max_message_limit:
            break
        messages.append(message.value.decode())
        parse_request(message.value.decode())
    return messages
 
 
def read_from_kafka():
    parsed_messages = []
    for message in getKafkaMessages():
        parsed_messages.append(parse_request(message))
    print('Data stored')
    return parsed_messages
 
#check that msg starts with 'status' followed by a space, then a number
#accepts: 'status 200'
#rejects: 'status invalid'
#rejects: 'stat 200' 
def well_formed_status_msg(statusMsg):
    spaceIdx = statusMsg.index(" ")
    print(statusMsg)
    if (not statusMsg.startswith("status")):
        print("here")
        return False
    try:
        int(statusMsg[spaceIdx+1:])
    except:
        print("there")
        return False
    return True
 
#checks that starts with a number, then a space followed by 'ms'
#accepted: 200 ms
#rejected: two ms
#rejected: 2 s 
def well_formed_response_time(response_time):
    if (not response_time.endswith("ms")):
        print("bad end")
        return False
    print("here", response_time)
    msIdx = response_time.index(" ms")
    print("there")
    time = response_time[:msIdx]
    print("time", time)
    try:
        int(time)
    except:
        return False
    print("GOOD")
    return True

#format of input    
#recommendation request <server>, status <200 for success>, result: <recommendations>, <responsetime>
def parse_recommendation_req(request_str):
    str_start = "recommendation request 17645-team04.isri.cmu.edu:8082"
    try:
        #check that requests starts with 'recommendation request' followed by our server
        if (request_str.index(str_start) != 0):
            print("bad start")
            return None
        splitByComma = request_str.split(",")
        statusMsg = splitByComma[1].strip()
        #check status part of msg is the right format 
        if (not well_formed_status_msg(statusMsg)):
            print("not well formed msg")
            return None
        result = ",".join(splitByComma[2:-1])
        response_time = splitByComma[-1].strip()
        #check response time part of msg is the right format 
        if (not well_formed_response_time(response_time)):
            print("bad response time")
            return None
        return {"status": statusMsg[statusMsg.index("status ") + len("status "):], "recommendations": result[len("result: "):].strip(), "response_time":response_time}
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
        print(movieId, rating)
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
        print("VALUE ERROR", msgs[0])
        return False
    print("PASSED---------------------")
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
    requestStr = ",".join(splitByComma[2:])
    if (requestStr.startswith(recommendationReqStart)):
        rec_req = parse_recommendation_req(requestStr)
        if (rec_req != None):
            return {userId: rec_req}
    elif (requestStr.startswith(watchMovieReqStart)):
        movie_req = parse_movie_req(requestStr)
        if (movie_req != None):
            return {userId: movie_req}
    elif (requestStr.startswith(rateMovieReqStart)):
        rate_movie_req = parse_rating_req(requestStr)
        #only write to kafka txt if request is correctly parsed 
        if (rate_movie_req != None):
            file1 = open("data/kafka_ratings.txt", "a")  # append mode
            file1.write(message + "\n")
            file1.close()
            return {userId: rate_movie_req}
    else:
        return None
 
read_from_kafka()

