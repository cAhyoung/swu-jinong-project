# 센서 데이터 csv에서 json으로 변환
# 컬럼이 꾸준하다는 조건

import csv
import json
import datetime
import pandas as pd

## csv 파일을 json 파일로 변환
def csv_to_json(csv_path, save_file = False):
    '''
    csv 파일을 json 파일로 변환하는 함수

    parameters: csv_path(변환하고자 하는 csv 파일 경로), save_file(bool)
    return: json 파일(리스트 혹 딕셔너리가 있는 형태)
    + 필요하다면 csv 파일의 경로와 같되 확장자명만 json으로 바꿔 저장하게 됨
    (저장도 하고, 리턴도 하는)
    '''
    
    # 결과 저장 변수
    res_data = []

    # 받은 경로로 파일을 열고 json으로 변환
    with open(csv_path, 'r') as f:
        csv_reader = csv.DictReader(f)
        
        res_data = [row for row in csv_reader]

    # 필요하다면 json 파일로 저장
    # csv 파일과 같은 경로, 같은 이름이되 확장자명만 json으로 바꿔 저장
    if save_file:
        json_path = csv_path[:-3] + "json"
        with open(json_path, 'w') as f:
            json.dump(res_data, f, indent=4)

    return res_data

## json 파일을 DataFrame으로 변환
def json_to_df(json_path, save_file = False):
    '''
    json 파일을 csv (dataframe) 파일로 변환하는 함수

    parameters: json_path(str, 변환하고자 하는 json 파일 경로), save_file(bool)
    return: DataFrame
    + json 파일의 경로와 같되 확장자명만 csv로 바꿔 저장하게 됨
    (저장도 하고, 리턴도 하는)
    '''
    # 받은 경로로 파일 열기
    with open(json_path, 'r') as f:
        json_reader = json.load(f)
    
    # dataframe 형태로 변환
    res_df = pd.json_normalize(json_reader)

    # 필요하다면 csv 파일로 저장
    # json 파일과 같은 경로, 같은 이름이되 확장자명만 csv로 바꿔 저장
    if save_file:
        csv_path = json_path[:-4] + "csv"
        res_df.to_csv(csv_path, index=False)

    # DataFrame 반환
    return res_df


## 가까운 분은 어디인지 반환
def nearest_10_minutes_datetime(dt_str):
    '''
    이미지 데이터의 촬영 일시는 시시각각이므로 
    그 일시가 어떤 센서 측정 시간에 가까운지 판단할 수 있어야 한다
    e.g., img dt: 2024-04-04 11:33:10 <-> sensor dt: 2024-04-04 11:30:00

    parameters: dt_str (string) e.g., 2024-04-04 11:33:10
    return: 가까운 10분 단위의 dt (string) e.g., 2024-04-04 11:30:00

    - 입출력 형식: yyyy-mm-dd hh:mm:ss
    '''

    # string -> datetime
    dt = datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    
    # 주어진 시간에서 분 단위를 반올림하여 가장 가까운 10분 단위 시간을 계산
    nearest_minute = round(dt.minute / 10) * 10

    if nearest_minute == 60:
        # 시간이 60분이 되면 다음 시간으로 넘어감
        nearest_minute = 0
        dt += datetime.timedelta(hours=1)
    
    # 시간을 조정하여 가장 가까운 10분 단위 시간을 반환
    return dt.replace(minute=nearest_minute, second=0, microsecond=0).strftime("%Y-%m-%d %H:%M:%S")

import os

## 구역 단위 순회 후 image_info.json 파일 경로 가져오기
def get_image_info_paths_area(farm_folder):
    '''
    parameter: farm_folder(~~/farm_code/area_code)
    return: 경로 모음 리스트 (image_info_paths)
    '''
    image_info_paths = []

    # 구역
    for area_code in os.listdir(farm_folder):
        area_folder_path = os.path.join(farm_folder, area_code)
        
        if os.path.isdir(area_folder_path):
            # 각 파일 폴더
            for file in os.listdir(area_folder_path):
                if file.endswith(".json"):
                    image_info_paths.append(os.path.join(area_folder_path, file))

    return image_info_paths

## json 파일 경로를 받아서 파일 합치기
def merge_json(file_paths):
    '''
    parameter: file_paths (병합하려는 json 파일 경로가 모인 리스트)
    return: 합쳐진 json (리스트 안에 딕셔너리가 모여진 형태)
    '''
    total_json = []

    for path in file_paths:
        with open(path, 'r') as f:
            total_json.append(json.load(f))

    return total_json
    
## 센서 데이타와 이미지 데이터 병합
def merge_dataset(sensor_df, img_info_df):
    '''
    센서 데이터와 이미지 데이터 결합
    parameters: sensor_df(DataFrame), img_info_df(DataFrame)
    return: DataFrame (병합 결과)

    - 이미지 데이터는 Image Info Data 기준으로
    - 결합 기준: 농장 코드, 구역 코드, 일시
    - Image Info의 shot_datetime과 가장 가까운 10분 단위의 시간이 언제인지 계산할 필요 존재
        -> nearest_10_minutes_datetime(dt) 구현
    '''

    # 각 이미지의 가장 가까운 센서 측정 시간(10분 단위) 기록 후 저장
    img_info_df["near_dt"] = [nearest_10_minutes_datetime(value) for value in img_info_df["shot_datetime"]]
    
    # image info + sensor join
    # farm_code, area_code, check_datetime(sensor) - near_dt(img_info)
    result = sensor_df.merge(
                        img_info_df, 
                        how="outer", 
                        left_on = ["farm_code", "check_datetime"], 
                        right_on = ["farm_code", "near_dt"]
                        )

    # 결합용 컬럼 삭제
    result.drop("near_dt", axis=1, inplace=True)

    # 병합 결과 리턴
    return result


## merge_dataset 실행 함수
def run_merge_dataset(sensor_path, farm_code, area_code, to_file = False, res_path = "result.csv"):
    '''
    parameter: sensor_path (센서 데이터 csv 파일 경로),
                farm_code (합치려는 농장 코드),
                area_code (합치려는 구역 코드),
                to_file (file로 저장할 것인지),
                res_path (file로 저장한다면 경로는 어떻게 할 것인지)
    
    return: 합친 csv
    + 필요하다면 파일로 저장
    '''
    ## Sensor Data 세팅
    sensor = pd.read_csv(sensor_path)
    
    ## Image Info Data 세팅 (csv로 변환)
    # 입력받은 code 기반으로 구역 폴더 경로 생성
    img_folder_path = os.path.join('/home/ubuntu/drive/dataset/SAM_result2', farm_code, area_code)
    # 구역 내 image_info.json 경로 모두 가져오고, 하나의 json으로 합치기
    img_info_total = merge_json(get_image_info_paths_area(img_folder_path))
    # csv로 변환
    img_info_csv = pd.json_normalize(img_info_total)

    result = merge_dataset(sensor, img_info_csv)

    # 필요하다면 파일로 저장
    if to_file:
        result.to_csv(res_path, index=False)
    
    return result


sensor_path = '/home/ubuntu/drive/dataset/sensor/sensor_final.csv'
farm_code = "F0017"
area_code = "C101"
run_merge_dataset(sensor_path, farm_code, area_code, to_file=True, res_path="final_f0017.csv")