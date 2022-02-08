import pandas as pd
from data_set import dataset
from tensorflow.keras.preprocessing import timeseries_dataset_from_array
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Input, LSTM, Dense
from app import time_set, date_set, user_ID, folder_name,save_folder_name

def lstm():
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
