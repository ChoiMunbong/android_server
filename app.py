import json

from itertools import zip_longest
import numpy as np
from flask import Flask, request, make_response
from neo4j import GraphDatabase
from py2neo import Graph
import pandas as pd
from pyarrow import csv
from datetime import datetime, timedelta
import tensorflow as tf
from tensorflow.keras.preprocessing import timeseries_dataset_from_array
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, LSTM, Dense, SimpleRNN
import matplotlib.pyplot as plt
from tqdm import tqdm_notebook, tqdm_pandas
import os.path
from flask_cors import CORS, cross_origin
from tqdm.notebook import tqdm_notebook
from flask_restful import Resource, Api, reqparse, abort


tqdm_notebook.pandas()

folder_name = "C:\\Users\\ChoiMunBong\\Downloads\\drive-download-20210820T075144Z-001\\"  # 파일이 있는 디렉토리로 변경해주십쇼
save_folder_name = "./"


user_ID = 'a98458d37c' #고객 type : string
date_set = 20200826 # 임시 날짜설정 type : int
time_set = 2345 #임시 시간설정 type : int

##########################################################################################
##################################변경 가능한 부분##########################################
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' #텐서플로우 속도향상을 위한 CPU 요청 무시

database_local = "bolt://localhost:7687"
db_id = "neo4j" #데이터베이스 명
db_pw = "1234" #

##########################################################################################

#################################################################################################################
################################################서버_구동_부분#####################################################
#################################################################################################################

import connect
app = Flask(__name__)
CORS(app)

greeter = connect.connectDBMS(database_local, db_id, db_pw) #DB 설정입니다. 원하시는 DB로 바꿔주세요

@app.route('/login_confirm', method = ['POST'])
def login_confirm():
    id_ = request.form['id_']
    pw_ = request.form['pw_']


@app.route('/', methods=['GET','POST','OPTIONS'])
def hello_newton_():
    return 'Welcome to Newton!'
@app.route('/show_data', methods=['GET','POST','OPTIONS'])
def print_database_():
    gt = greeter.show_data(user_ID, date_set)
    # fls = flask.Response(gt)
    # fls.headers['Access-Control-Allow-Origin'] = "*"
    return app.response_class(gt, content_type='application/json')
@app.route('/insert_data')
def insert_data():
    gt = greeter.insert_data()
    return gt

@app.route('/delete_data')
def delete_data():
    gt = greeter.delete_data()
    return gt

@app.route('/CO2_emission', methods=['GET','POST','OPTIONS'])
def CO2_emission():
    gt = greeter.co2_emission()
    return app.response_class(gt, content_type='application/json')
@app.route('/compare_yesterday', methods=['GET','POST','OPTIONS'])
def compare_data():
    gt = greeter.compare_data()
    return app.response_class(gt, content_type='application/json')
@app.route('/get_predict')
def get_predict_():
    gt = greeter.get_predict()
    return gt

@app.route('/insert_predict')
def insert_predict_():
    gt = greeter.insert_predict()
    return gt
@app.route('/tou', methods=['GET','POST','OPTIONS'])
def tou_():
    gt = greeter.fee()
    return app.response_class(gt, content_type='application/json')
@app.route('/year_used', methods=['GET','POST','OPTIONS'])
def year_used_():
    gt = greeter.year_used()
    return app.response_class(gt, content_type='application/json')
@app.route('/predict_day', methods=['GET','POST','OPTIONS'])
def predict_day_():
    gt = greeter.predict_day()
    return app.response_class(gt, content_type='application/json')
@app.route('/predict_week', methods=['GET','POST','OPTIONS'])
def predict_week_():
    gt = greeter.predict_week()
    return app.response_class(gt, content_type='application/json')
#api = Api(app)
#
# class PriceList(Resource):
#     def get(self):
#         return price
#
# class ShowList(Resource):
#     def get(self):
#         return show_data
# api.add_resource(PriceList, '/tou/')
# api.add_resource(ShowList, '/show_data/')

if __name__ == "__main__":
    app.run(host='127.0.0.1', port='5000', debug=True)
