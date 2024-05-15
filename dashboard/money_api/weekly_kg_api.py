import requests
# import pandas as pd
from datetime import datetime, timedelta
import json
import os
import time

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
    url = "https://at.agromarket.kr/openApi/price/sale.do"
    service_key = "3DDA52F946374514A6A3F35C06F8619A"
    directory = "/home/ubuntu/drive/dashboard/money_api/weekly_kg_dataset"
    # markets = ["110001", "350301", "340101"]  # 선택된 도매시장 코드
    small_codes = ["13", "99"]  # 선택된 소분류 코드

    # 디렉토리 내의 모든 txt 파일 삭제
    delete_all_txt_files(directory)
    
    # 현재 날짜를 기준으로 7일간의 날짜 생성
    end_date = datetime.now()
    start_date = end_date - timedelta(days=6)

    # 각 날짜와 도매시장 코드에 대해 API 요청하여 데이터 저장
    for i in range(7):
        date_str = (start_date + timedelta(days=i)).strftime("%Y%m%d")
        # for market_code in markets:
        for small_code in small_codes:
            params = {
                "serviceKey": service_key,
                "apiType": "json",
                "pageNo": "1",
                "whsalCd": "110001", # 가락시장 기준
                "saleDate": date_str,
                "largeCd": "08",
                "midCd": "04",
                "smallCd": small_code  # 소분류코드
            }
            api_data = get_api_data(url, params)
            if api_data:
                filename = os.path.join(directory, f"api_data_{date_str}_{small_code}.txt")
                save_to_file(api_data, filename)
            else:
                print(f"{date_str}에 대한 API 요청에 실패했습니다.")

if __name__ == "__main__":
    main()

