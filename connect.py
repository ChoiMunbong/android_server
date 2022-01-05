import json

from itertools import zip_longest
from neo4j import GraphDatabase
import pandas as pd
from pyarrow import csv
from datetime import datetime
from tensorflow.keras.preprocessing import timeseries_dataset_from_array
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, LSTM, Dense
from app import time_set, date_set, user_ID, save_folder_name
from data_set import dataset
import show_data
import fee


# price = {
#     'TouPrice': {"TouPrice": "45450.0"},
#     'ElecPrice': {"ElecPrice": "56410.0"}
# }
# show_data = {
#     'sum': {"task": "0.8239W"},
#     'beforeWeek': {"task": "24.3517W"},
#     'predictWatt': {"task": "3.3517W"}
# }

class connectDBMS: #DB와 연결 및 서버시작
    def __init__(self, uri, user, password): #연결설정 해 줍니다.
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self): #연결을 해제합니다.
        self.driver.close()

    def show_data(self, user, date): #데이터베이스에 저장된 user 데이터를 보여줍니다.
        with self.driver.session() as session:
            greeting = session.write_transaction(self._show_data_, user, date)
            return greeting

    def insert_data(self): #데이터베이스에 csv 데이터를 삽입합니다.
        with self.driver.session() as session:
            greeting = session.write_transaction(self._insert_data_)
            return greeting

    def delete_data(self): #데이터베이스 내용 전체를 삭제합니다.
        with self.driver.session() as session:
            greeting = session.write_transaction(self._delete_data_)
            return greeting

    def compare_data(self): #저번 달과의 사용전력량을 비교합니다.
        with self.driver.session() as session:
            greeting = session.write_transaction(self._compare_data_)
            return greeting

    def get_predict(self): #예측 csv 파일을 만들어냅니다.
        with self.driver.session() as session:
            greeting = session.write_transaction(self._get_predict_)
            return greeting

    def insert_predict(self):  # 예측 csv 파일을 사용하여 데이터베이스에 삽입합니다.
        with self.driver.session() as session:
            greeting = session.write_transaction(self._insert_predict_)
            return greeting

    def co2_emission(self): # 이산화탄소 배출량을 계산하여 보여줍니다.
        with self.driver.session() as session:
            greeting = session.write_transaction(self._co2_emission_)
            return greeting

    def fee(self):  # 요금제를 추천하고, 요금제를 비교합니다.
        with self.driver.session() as session:
            greeting = session.write_transaction(self._fee_)
            return greeting

    def year_used(self):  # 1년동안 사용되는 데이터를 보여줍니다.
        with self.driver.session() as session:
            greeting = session.write_transaction(self._year_used_)
            return greeting

    def predict_day(self):  # 하루 뒤에 예측 사용량을 보여줍니다.
        with self.driver.session() as session:
            greeting = session.write_transaction(self._predict_day_)
            return greeting

    def predict_week(self):  # 일주일 동안의 예측 사용량을 보여줍니다.
        with self.driver.session() as session:
            greeting = session.write_transaction(self._predict_week_)
            return greeting

    @staticmethod
    def _show_data_(tx, user, date):
        a = tx.run("MATCH (u: user) "
                   "WHERE u.Customer_number = $user and u.date = $date and u.time <= $time "
                   "RETURN u "
                   "ORDER BY u.date, u.time ", user=user, date=date, time=time_set)  # 데이터베이스에서 파일을 추출합니다.
        params_json = show_data.show_data(a)
        return params_json

    @staticmethod
    def _delete_data_(tx):
        tx.run(
            "MATCH (n) " 
            "DELETE n "
        )
        return "Delete done!"

    @staticmethod
    def _insert_data_(tx):
        frame = dataset()
        for index, row in frame.iterrows():
            if int(row['date']) >= date_set and int(row['time']) >= time_set :
                continue
            else :
                tx.run(
                    "CREATE (u:user{Customer_number:$Customer_number, Active_Energy:$Active_Energy, time:$time, date:$date, Region : $Region, Sub_Region : $Sub_Region}) "
                , Customer_number=str(row['Customer_number']), Active_Energy=float(row['Active_Energy']), time= int(row['time']), date= int(row['date']), Region= str(row['Region']), Sub_Region= str(row['Sub_Region']))
        return "Insert done!"

    @staticmethod
    def _compare_data_(tx): # 데이터를 비교합니다.
        # graph = Graph(database_local, user=db_id, password=db_pw)
        # tx = graph.begin()

        yesterday_date = date_set - 1
        yesterday = tx.run( #어제의 데이터를 불러옵니다
            "MATCH (u:user) "
            "WHERE u.date = $date "
            "RETURN u "
            "ORDER BY u.time ", date=yesterday_date)
        yesterday_results = [recode for recode in yesterday.data()]

        today = tx.run(
            "MATCH (u:user) "#오늘의 데이터를 불러옵니다.
            "WHERE u.date = $date and u.time <= $time "
            "RETURN u "
            "ORDER BY u.time ", time = time_set, date=date_set)
        today_results = [recode for recode in today.data()]

        yes_sum = float()
        to_sum = float()
        yesterday_insert_json = []
        today_insert_json = []
        insert_time = []
        i = 0

        #데이터를 삽입할 때 yesterday와 today를 합쳐 보내고, 만약 값이 없으면 0을 기본값을 넣습니다.
        for yes_row, to_row in zip_longest(yesterday_results, today_results, fillvalue=0):
            i = i + 1 #time
            if i % 4 == 0:
                time = int(i / 4)
                if time < 10:
                    temp = "0" + str(time) + "h"
                else:
                    temp = str(time) + "h"
                yesterday_insert_json.append(yes_sum)
                today_insert_json.append(to_sum)
                insert_time.append(temp)
                yes_sum = 0
                to_sum = 0

            else:
                try:
                    yes_sum += float(yes_row['u']['Active_Energy'])
                    to_sum += float(to_row['u']['Active_Energy'])
                except:
                    yes_sum += 0
                    to_sum += 0

        params = {
            'name': "전력사용량",
            'yesterday_data': yesterday_insert_json,
            'today_data': today_insert_json,
            'time': insert_time
        }
        params_json = json.dumps(params, indent=4, ensure_ascii=False)
        return params_json

    @staticmethod
    def _get_predict_(tx):
        frame = dataset()
        frame['Active_Power'] = 4 * frame['Active_Energy']

        df = pd.pivot_table(frame, index='datetime', columns = 'Customer_number', values='Active_Power') # 피봇테이블 설정
        df2 = df[[user_ID]] # user_ID 고객에 대한 데이터 출력 및 예측
        # df2.columns.values[0] = 'ID_spec'
        df2.fillna(method='ffill', inplace=True)
        df_cust = df2[[user_ID]]

        train_split_idx = 109 * 96  # 8월 25일 행 인덱스 18, 19일이 들어감 다음 7일간 예측 일수 :109, 24시간 * 4
        window_size = 7 * 96  # 1주간 데이터를 학습데이터로 이용
        future = 1  # 1시간 이후 타깃 예측

        X_train = df_cust.iloc[:train_split_idx - window_size - future]
        y_train = df_cust.iloc[window_size + future: train_split_idx]

        X_test = df_cust.iloc[:]
        y_test = df_cust.iloc[:]

        X_train_scaled = X_train.loc[:]
        X_test_scaled = X_test.loc[:]

        train_data = timeseries_dataset_from_array(X_train_scaled, y_train, sequence_length=window_size, batch_size=12)
        test_data = timeseries_dataset_from_array(X_test_scaled, y_test, sequence_length=window_size, batch_size=12)

        for batch in test_data.take(1):
            inputs, targets = batch

            print("Input:", inputs.numpy().shape)
            print("Target:", targets.numpy().shape)

        model = Sequential()
        model.add(Input(shape=[1, 1]))

        model.add(LSTM(units=32, return_sequences=False))
        model.add(Dense(units=1, activation='linear'))

        model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        # model.summary()

        # 모델 훈련
        y_pred = model.predict(test_data)
        pred = y_pred
        df3 = df2[train_split_idx + window_size - 1:]
        df3['pred'] = pred
        df3.to_csv(save_folder_name + "pred_LSTM.csv", mode='w')

        return "predict done!"

    @staticmethod
    def _insert_predict_(tx) :
        column_names2 = ['datetime', 'ID_spec', 'pred', 'a', 'b', 'c', 'd']
        df = csv.read_csv(save_folder_name + "pred_LSTM.csv", read_options=csv.ReadOptions(encoding='CP949', skip_rows=1, column_names=column_names2)).to_pandas()
        for index, row in df.iterrows():
            date_to_compare = datetime.strptime(str(date_set), '%Y%m%d').date()
            convert = datetime.strptime(row['datetime'][0:10], "%Y-%m-%d").date()
            if (date_to_compare - convert).days < 0:
                tx.run(
                    "CREATE (u:predict{datetime:$datetime, predict:$Active_Energy, ID_spec : $ID_spec }) "
                , datetime = str(row['datetime']), Active_Energy=float(row['pred']), ID_spec=float(row['ID_spec']))
        return "Predict insert done!"

    @staticmethod
    def _co2_emission_(tx):
        date = date_set - 68
        temp_date = date - 100
        data = tx.run(
            "MATCH (u:user) "
            "WHERE u.date < $date and u.date > $temp_date "
            "RETURN u ", date=date, temp_date=temp_date)
        data_results = [recode for recode in data.data()]
        sum = float()
        for row in data_results :
            sum += float(row['u']['Active_Energy'])
        E_cons = sum
        E_cons_MWh = E_cons / 1000
        Coef_tCO2 = 0.4567
        tCO2 = Coef_tCO2 * E_cons_MWh
        params = {
            'tCO2': tCO2
        }
        params_json = json.dumps(params, indent=4, ensure_ascii=False)
        return params_json

    @staticmethod
    def _fee_(tx): # 요금 계산

        data = tx.run(
            "MATCH (u:user) "
            "WHERE u.date < $date and u.date > $temp_date "
            "RETURN u ", date= fee.date, temp_date=fee.temp_date)

        params_json = fee.fee(data)
        return params_json

    @staticmethod
    def _year_used_(tx): # 1년치 데이터 불러오기
        data = tx.run(
            "MATCH (u:user) "
            "return u.date, u.Active_Energy"
        )
        ###################################
        date_max = date_set + 31 # 20200857
        may = date_max - 400 # 20200457
        jun = date_max - 300 # 20200557
        jul = date_max - 200 # 20200657
        aug = date_max - 100 # 20200757

        may_data = float()
        jun_data = float()
        jul_data = float()
        sum_data = float()
        ###################################
        data_results = [recode for recode in data.data()]
        li = []
        for row in data_results :
            if row['u.date'] < aug and row['u.date'] > jul:
                sum_data += row['u.Active_Energy']
            elif row['u.date'] < jul and row['u.date'] > jun:
                jul_data += row['u.Active_Energy']
            elif row['u.date'] < jun and row['u.date'] > may:
                jun_data += row['u.Active_Energy']
            else :
                may_data += row['u.Active_Energy']

        li.append(sum_data)
        li.append(jul_data)
        li.append(jun_data)
        li.append(may_data)
        for i in range(8) :
            li.append(0)
        print(li)
        params = {
            'data': li
        }
        params_json = json.dumps(params, indent=4, ensure_ascii=False)
        return params_json

    @staticmethod
    def _predict_day_(tx):
        day = tx.run("MATCH (u: predict) " 
                   "RETURN u "
                   )

        results = [recode for recode in day.data()]
        i = 1
        insert_json =[]
        insert_time = []
        sum = 0
        for row in results:
            date_to_compare = datetime.strptime(str(date_set), '%Y%m%d').date()
            convert = datetime.strptime(row['u']['datetime'][0:10], "%Y-%m-%d").date()
            if (date_to_compare - convert).days == -1:
                i = i + 1
                if i % 4 == 0:
                    time = int(i/4)
                    insert_json.append(sum)
                    insert_time.append(time)
                    sum = 0
                else:
                    try:
                        sum += float(row['u']['predict'])
                    except:
                        sum += 0
        params = {
            'data' : insert_json,
            'time' : insert_time
        }
        params_json = json.dumps(params, indent=4, ensure_ascii=False)
        return params_json

    @staticmethod
    def _predict_week_(tx):
        week = tx.run("MATCH (u: predict) "
                     "RETURN u "
                     )

        results = [recode for recode in week.data()]
        i = 1
        insert_json = []
        insert_time = []
        sum = 0
        for row in results:
            date_to_compare = datetime.strptime(str(date_set), '%Y%m%d').date()
            convert = datetime.strptime(row['u']['datetime'][0:10], "%Y-%m-%d").date()
            if (convert - date_to_compare ).days < 7:
                i = i + 1
                if i % 96 == 0:
                    insert_json.append(sum)
                    insert_time.append(convert.day)
                    sum = 0
                else:
                    try:
                        sum += float(row['u']['predict'])
                    except:
                        sum += 0
        params = {
            'data': insert_json,
            'day': insert_time
        }
        params_json = json.dumps(params, indent=4, ensure_ascii=False)
        return params_json
