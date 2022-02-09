import data_set
from tqdm.notebook import tqdm_notebook
import os
import app
from sklearn.datasets import load_boston
from sklearn.model_selection import train_test_split
from sklearn import neighbors
from sklearn.metrics import mean_squared_error
from math import sqrt
import pandas as pd


tqdm_notebook.pandas()

folder_dir = app.save_folder_name  # 파일이 있는 디렉토리로 변경해주십쇼
save_folder_dir = "./"


user_ID = 'a98458d37c' #고객 type : string
date_set = 20200826 # 임시 날짜설정 type : int
time_set = 2345 #임시 시간설정 type : int

##########################################################################################
##################################변경 가능한 부분##########################################
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' #텐서플로우 속도향상을 위한 CPU 요청 무시

database_local = "bolt://localhost:7687"
db_id = "neo4j" #데이터베이스 명
db_pw = "1234" #


dataframe = data_set.dataset()
#
# def knn(ref, query, k):
boston = load_boston()
X_train, X_test, y_train, y_test = train_test_split(boston.data, boston.target, test_size=0.2)
print(len(X_train), len(X_test))

rmse_val = []  # to store rmse values for different k
for K in range(20):
    K = K + 1
    model = neighbors.KNeighborsRegressor(n_neighbors=K)
    model.fit(X_train, y_train)  # fit the model
    pred = model.predict(X_test)  # make prediction on test set
    error = sqrt(mean_squared_error(y_test, pred))  # calculate rmse
    rmse_val.append(error)  # store rmse values
    print('RMSE value for k= ', K, 'is:', error)


