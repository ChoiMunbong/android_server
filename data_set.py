import pandas as pd
from pyarrow import csv
from datetime import datetime, timedelta
import os.path
from app import time_set, date_set, user_ID, folder_name,save_folder_name

column_names = ['date', 'time', 'Region', 'Sub_Region', 'Customer_number', 'Contract', 'Contract_Power', 'Supply_type', 'High-Low', 'Active_Energy', 'Lagging_Reactive_Energy ', 'Leading_Reactive_Energy']

def convert(row): #인공지능 학습을 위한 datetime 작업입니다.
    try:
        time = str(row["time"]) if str(row["time"]) != "2400" else "0000"
        x = str(row["date"]) + " " + time
        return datetime.strptime(x, '%Y%m%d %H%M')
    except:
        print(x)

def dataset() :  # 데이터를 받기위한 준비단계
    all_files = os.listdir(folder_name)
    li = []

    #날짜	시간  시/도	읍_면_동   고객번호	계약종별	계약전력	공급방식	고저압구분	유효전력량	지상무효전력량	진상무효전력량
    for filename in all_files:    # 데이터를 읽는 부분입니다
        try:
            df = csv.read_csv(folder_name + filename, read_options=csv.ReadOptions(encoding='CP949', skip_rows=1, column_names=column_names)).to_pandas()
            li.append(df)
        except:
            continue

    frame = pd.concat(li, axis=0, ignore_index=True) # 읽은 데이터 합치는 작업입니다.

    frame = frame[['date', 'time', 'Customer_number', 'Contract', 'Contract_Power', 'Active_Energy', 'Region', 'Sub_Region']]  #필요한 column만 추출하였습니다
    is_customer_number = frame['Customer_number'] == user_ID # 필요한 userID만 가져옵니다.
    frame = frame[is_customer_number]

    frame["datetime"] = frame.apply(lambda x: convert(x), axis=1)
    return frame


