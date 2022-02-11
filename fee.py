import json
import user_info

date = user_info.date_set - 68
date_temp = str(date)
target_month = int(date_temp[4:6])
temp_date = date - 100

def fee(data):
    data_results = [recode for recode in data.data()]

    sum_low = float()  # 22 ~ 7 시
    sum_mid = float()  # 8 ~ 15 시
    sum_high = float()  # 16 ~ 21 시

    for row in data_results:
        if (row['u']['time'] >= 0 and row['u']['time'] < 800) or (row['u']['time'] >= 2200):
            sum_low += float(row['u']['Active_Energy'])
        elif (row['u']['time'] >= 800 and row['u']['time'] < 1500):
            sum_mid += float(row['u']['Active_Energy'])
        else:
            sum_high += float(row['u']['Active_Energy'])

    normal_charge = sum_low + sum_mid + sum_high

    if (3 <= target_month < 6) or (9 <= target_month < 11):
        unit_price_low = 94.1
        unit_price_mid = 122.1
        unit_price_high = 140.7
    else:
        unit_price_low = 107
        unit_price_mid = 153
        unit_price_high = 188

    price_low = sum_low * unit_price_low
    price_mid = sum_mid * unit_price_mid
    price_high = sum_high * unit_price_high

    TOU_price = price_low + price_mid + price_high

    CCost1_total = 0  # 전력량 요금 총액(기존)
    Coef1_400 = 274.6  # 400 kWh 초과 시 274.6 원/kWh
    Coef1_200 = 182.9  # 200 kWh 초과 시 182.9 원/kWh
    Coef1_0 = 88.3  # 200 kWh 이하 시   88.3 원/kWh

    if normal_charge > 400:
        CCost1_res3 = Coef1_400 * normal_charge
        CCost1_res2 = Coef1_200 * 200
        CCost1_res1 = Coef1_0 * 200
        CCost1_total = CCost1_res3 + CCost1_res2 + CCost1_res1
    elif normal_charge > 200:
        CCost1_res2 = Coef1_200 * normal_charge
        CCost1_res1 = Coef1_0 * 200
        CCost1_total = CCost1_res2 + CCost1_res1
    else:
        CCost1_res1 = Coef1_0 * normal_charge
        CCost1_total = CCost1_res1

    BCost1 = 0  # 기본 요금 초기치(원/호)
    BCost1_res1 = 910  # 200 kWh 이하 사용 기본 요금(원/호)
    BCost1_res2 = 1600  # 200 kWh 초과  400 kWh 이하 사용 기본 요금(원/호)
    BCost1_res3 = 7300  # 400 kWh 초과 사용 기본 요금(원/호)

    if normal_charge <= 200:  # 전력량 200 kWh 이하 사용
        BCost1 = BCost1_res1  # 200 kWh 이하 사용 기본 요금(원/호)
    elif 200 < normal_charge <= 400:  # 전력량 200 kWh 초과 400 kWh 이하 사용
        BCost1 = BCost1_res2  # 200 kWh 초과  400 kWh 이하 사용 기본 요금(원/호)
    else:  # 전력량 400 kWh 초과 사용
        BCost1 = BCost1_res3  # 400 kWh 초과 사용 기본 요금(원/호)

    BCost2_res1 = 4310  # (원/kW)
    Cont2 = 3  # 계약전력 (kW)
    BCost2 = BCost2_res1 * Cont2

    Cost1 = BCost1 + CCost1_total
    Cost2 = BCost2 + TOU_price

    Cost1 = Cost1 - (Cost1 % 10)  # 누진세
    Cost2 = Cost2 - (Cost2 % 10)  # TOU

    params = {
        'price': [Cost2, Cost1]
    }
    print(params)
    return json.dumps(params, indent=4, ensure_ascii=False)
