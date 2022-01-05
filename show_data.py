import json

def show_data(a) :
    results = [recode for recode in a.data()]
    # 결과값 변환힙니다.
    sum = float()
    insert_json = []
    insert_time = []
    i = 0
    for row in results:
        i = i + 1
        if i % 4 == 0:  # 15분 단위로 쪼개져 있는 데이터를 4번에 걸쳐 더하여 1시간단위로 만들어 준 후 insert_json 리스트에 추가합니다.
            time = int(i / 4)
            if time < 10:
                temp = "0" + str(time) + "h"
            else:
                temp = str(time) + "h"
            insert_json.append(sum)
            insert_time.append(temp)
            sum = 0
        else:
            try:
                sum += float(row['u']['Active_Energy'])
            except:
                sum += 0
    params = {
        'name': "전력사용량",
        'data': insert_json,
        'time': insert_time
    }
    return json.dumps(params, indent=4, ensure_ascii=False)  # json으로 덮어서 보냅니다.

