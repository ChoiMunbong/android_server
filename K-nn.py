import data_set
from tqdm.notebook import tqdm_notebook
import os
import sklearn.model_selection import train_test_split
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


dataframe = data_set.dataset()

def knn(ref, query, k):

