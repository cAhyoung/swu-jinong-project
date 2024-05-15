import requests
# import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import json
import os

def get_api_data(url, params):
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # 오류 발생 시 예외 발생
        data = response.json()  # JSON 형식으로 응답 데이터 파싱
        return data
    except requests.exceptions.RequestException as e:
        print("API 요청 중 오류 발생:", e)
        return None
    
def save_to_file(data, filename):
    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)  # JSON 형식으로 데이터 저장
        print(f"데이터를 성공적으로 파일 '{filename}'에 저장했습니다.")
    except IOError as e:
        print("파일에 저장하는 중 오류 발생:", e)

def delete_all_txt_files(directory):
    try:
        for filename in os.listdir(directory):
            if filename.endswith(".txt"):
                filepath = os.path.join(directory, filename)
                os.remove(filepath)
        print("디렉토리 내의 모든 txt 파일을 삭제했습니다.")
    except Exception as e:
        print("파일 삭제 중 오류 발생:", e)

def main():
    url = "https://at.agromarket.kr/openApi/price/dateWhsalPumSale.do"
    service_key = "3DDA52F946374514A6A3F35C06F8619A"
    directory = "/home/ubuntu/drive/dashboard/money_api/monthly_dataset"

    # 디렉토리 내의 모든 txt 파일 삭제
    delete_all_txt_files(directory)
    
    # 현재 날짜를 기준으로 6개월 전 날짜 계산
    end_date = datetime.now()
    start_date = end_date - timedelta(days=6*30)  # 6개월 전
    
    # 각 월의 데이터를 가져와서 파일로 저장
    for i in range(6):
        # 시작일과 종료일 설정
        start_month = (start_date + relativedelta(months=i)).replace(day=1)
        end_month = (start_month + relativedelta(months=1)) - timedelta(days=1)
        
        # API 요청을 위한 날짜 문자열 생성
        start_date_str = start_month.strftime("%Y%m%d")
        end_date_str = end_month.strftime("%Y%m%d")
        
        # API 요청 및 데이터 저장
        params = {
            "serviceKey": service_key,
            "apiType": "json",
            "strDate": start_date_str,
            "endDate": end_date_str,
            "large": "08",
            "mid": "04"
        }
        api_data = get_api_data(url, params)
        if api_data:
            filename = f"/home/ubuntu/drive/dashboard/money_api/monthly_dataset/api_data_{start_date_str}_{end_date_str}.txt"
            save_to_file(api_data, filename)
        else:
            print(f"{start_date_str} ~ {end_date_str} 기간의 API 요청에 실패했습니다.")

if __name__ == "__main__":
    main()