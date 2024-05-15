import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import altair as alt
import matplotlib.pyplot as plt
import subprocess
import schedule
import time
from datetime import datetime
import subprocess

st.set_page_config(layout="wide")

### 사이드바 구성
with st.sidebar:
  st.header("사이드바 목록")
  st.page_link("main.py", label="통합 대시보드", icon="📶")
  st.page_link("pages/sensor1.py", label="센서 통합 정보", icon="🦾")
  st.page_link("pages/growth2.py", label="딸기 생육 정보", icon="🍓")
  st.page_link("pages/money3.py", label="도소매가 정보", icon="💰")
  st.page_link("pages/alert4.py", label="알림", icon="⚠️", disabled=True)
  st.page_link("pages/calender5.py", label="달력 메모장", icon="📆", disabled=True)

### 타이틀 구성
st.markdown("<h1 style='margin-top: -70px;'>💰도소매가 시장 정보</h1>", unsafe_allow_html=True)

# def execute_python_files(directory):
#     files = os.listdir(directory)
    
#     # 파이썬 파일들만 필터링
#     py_files = [f for f in files if f.endswith('.py')]
    
#     # 각 파이썬 파일을 실행
#     for py_file in py_files:
#         # 파이썬 파일의 경로를 생성합니다.
#         file_path = os.path.join(directory, py_file)
        
#         try:
#             # 파일 실행
#             subprocess.run(['python', file_path], check=True)
#         except subprocess.CalledProcessError as e:
#             print(f"Error executing {py_file}: {e}")

# def job():
#     execute_python_files('/home/ubuntu/drive/dashboard/money_api')

# # 매일 오전 10시에 job 함수 실행
# schedule.every().day.at("22:47").do(job)

# # 무한루프로 스케줄을 실행합니다.
# while True:
#     schedule.run_pending()
#     time.sleep(60)  # 60초마다 스케줄 확인

# 타일 생성
columns = st.columns(3)

# 첫 번째 타일: 현재 도매 가격
tile1 = columns[0].container(height=110)

directory = "/home/ubuntu/drive/dashboard/money_api/weekly_dataset"
file_names = os.listdir(directory)
file_names.sort()

# 디렉토리 안의 마지막 파일 가져오기
last_file = file_names[-4]
file_path = os.path.join(directory, last_file)

# 파일의 데이터가 있는지 확인하고 처리
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# 데이터에서 'data' 항목 추출
data_list = data.get('data', [])

# 만약 데이터가 비어있지 않다면 도매 가격을 출력
if data_list:
    # 파일 이름에서 날짜 추출
    date_str = last_file.split('_')[2].split('.')[0]
    date = datetime.strptime(date_str, "%Y%m%d").date()

    # 파일의 날짜 출력
    date_text = date.strftime("%Y년 %m월 %d일")

    # 'whsalcd'가 '110001'인 데이터 찾기
    for item in data_list:
        if item.get('whsalcd') == '110001':
            # 'totamt'를 'totqty'로 나눈 값을 출력
            totamt = item.get('totamt')
            totqty = item.get('totqty')
            if totqty != 0:
                kg_price = totamt / totqty
                tile1.metric("##### 현재 도매 가격", f"{kg_price:.2f}원")
            else:
                tile1.write("##### 현재 도매 가격")
                tile1.write("오늘 거래 내역이 없습니다.")
            break  # 찾았으면 루프 종료
    else:
        tile1.write("##### 현재 도매 가격")
        tile1.write("오늘 거래 내역이 없습니다.")
        kg_price = "no data today"
# 데이터가 비어있다면 거래 내역이 없음을 출력
else:
    tile1.write("##### 현재 도매 가격")
    tile1.write("오늘 거래 내역이 없습니다.")
    kg_price = "no data today"

# 두 번째 타일: 현재 거래 현황
tile2 = columns[1].container(height=110)

# 'whsalcd'가 '110001'인 데이터 찾기
for item in data_list:
    if item.get('whsalcd') == '110001':
        # 'totqty'값 출력
        totqty = item.get('totqty')
        if totqty != 0:
            tile2.metric("##### 현재 도매 물량", f"{totqty:.2f}kg")
        else:
            tile2.write("##### 현재 도매 물량")
            tile2.write("오늘 거래 내역이 없습니다.")
        break  # 찾았으면 루프 종료
else:
    tile2.write("##### 현재 도매 물량")
    tile2.write("오늘 거래 내역이 없습니다.")

# 세 번째 타일: 도매 가격 변화
tile3 = columns[2].container(height=110)
tile3.markdown("##### 도매 가격 변화")

# 현재 도매 가격이 "오늘 거래 내역이 없습니다."인 경우
if kg_price == "no data today":
    tile3.markdown("오늘 거래 내역이 없습니다.")
else:
    # 증가 및 감소에 따른 이모티콘 설정
    arrow_up = "⬆️"
    arrow_down = "⬇️"

    last_file = file_names[-1]
    eve_file = file_names[-2]

    directory2 = "/home/ubuntu/drive/dashboard/money_api/monthly_dataset"
    file_names2 = os.listdir(directory2)
    file_names2.sort()
    prev_month_file = file_names2[-1]

    # 전일 데이터 로드
    with open(os.path.join(directory, eve_file), 'r', encoding='utf-8') as file:
        eve_data = json.load(file)

    # 전월 데이터 로드
    with open(os.path.join(directory2, prev_month_file), 'r', encoding='utf-8') as file:
        prev_month_data = json.load(file)

    # 전일 데이터에서 whsalcd가 110001인 데이터 추출 및 가격 계산
    for item in eve_data['data']:
        if item['whsalcd'] == "110001":
            eve_price_per_kg = item['totamt'] / item['totqty']
            break

    # 전월 데이터에서 whsalcd가 110001인 데이터 추출 및 가격 계산
    for item in prev_month_data['data']:
        if item['whsalcd'] == "110001":
            prev_month_price_per_kg = item['totamt'] / item['totqty']
            break

    # 전일 가격 및 전월 가격 추출
    eve_totamt = eve_price_per_kg
    prev_month_totamt = prev_month_price_per_kg

    # 전일 대비 가격 변화 계산
    previous_day_price_change = kg_price - eve_totamt
    previous_day_price_change_percentage = (previous_day_price_change / eve_totamt) * 100

    # 전월 대비 가격 변화 계산
    previous_month_price_change = kg_price - prev_month_totamt
    previous_month_price_change_percentage = (previous_month_price_change / prev_month_totamt) * 100

    # 전날 대비 변화량에 따른 이모티콘 및 기호 설정
    change_symbol_day = "+" if previous_day_price_change > 0 else "-"
    arrow_day = arrow_up if previous_day_price_change > 0 else arrow_down

    # 전월 대비 변화량에 따른 이모티콘 및 기호 설정
    change_symbol_month = "+" if previous_month_price_change > 0 else "-"
    arrow_month = arrow_up if previous_month_price_change > 0 else arrow_down

    # 변화량 및 이모티콘을 포함한 문자열 생성
    change_text_day = f"{arrow_day} {abs(previous_day_price_change):.0f}원 ({previous_day_price_change_percentage:.2f}%)"
    change_text_month = f"{arrow_month} {abs(previous_month_price_change):.0f}원 ({previous_month_price_change_percentage:.2f}%)"

    # 변화량과 이모티콘을 포함한 문자열을 Markdown 형식으로 출력
    tile3.markdown(f"전날 대비: {change_text_day}  \n"
                   f"전월 대비: {change_text_month}")

# ----------------------------------------------------
# 전역 변수로 선택된 도매시장 목록 초기화
selected_markets_daily = []
selected_markets_monthly = []

# 저장된 텍스트 파일들의 디렉토리 경로
directory_daily = "/home/ubuntu/drive/dashboard/money_api/weekly_dataset"
directory_monthly = "/home/ubuntu/drive/dashboard/money_api/monthly_dataset"

# 디렉토리에서 모든 텍스트 파일 불러오기
files_daily = os.listdir(directory_daily)
files_monthly = os.listdir(directory_monthly)

# 데이터 로드 및 처리
data_daily = {}
for filename in files_daily:
    with open(os.path.join(directory_daily, filename), "r") as file:
        file_data = json.load(file)
        # 데이터가 있는 파일인 경우에만 처리
        if file_data["data"]:
            date = filename.split("_")[2].split(".")[0]  # 파일 이름에서 날짜 추출
            data_daily[date] = file_data["data"]

### 세부 요소 구성
with st.container():
  col1, col2 = st.columns(2)
  with col1:
    # 사용자가 선택한 도매시장 목록
    markets_daily = sorted(list(set([item["whsalname"] for date_data in data_daily.values() for item in date_data])))
    selected_markets_daily = st.multiselect("도매시장을 선택하세요", markets_daily, default=[], key="wholesale_markets_multiselect_daily")

    with st.container():
      st.markdown("##### 일별 도매 가격 정보")
      # 선택된 도매시장에 대한 그래프 그리기
      if not data_daily:
          st.write("일별 도매 시장 데이터가 없습니다.")
      else:
          if selected_markets_daily:
              df_list_daily = []
              for date, file_data in data_daily.items():
                  for item in file_data:
                      if item["whsalname"] in selected_markets_daily:
                          # 데이터를 kg당 가격으로 변환하여 저장
                          kg_price = item['totamt'] / item['totqty']
                          df_list_daily.append({"Date":date, "Market":item["whsalname"], "Kg Price": kg_price})
              df_daily = pd.DataFrame(df_list_daily)

              # 날짜 기준으로 정렬
              df_daily["Date"] = pd.to_datetime(df_daily["Date"]).dt.strftime("%Y%m%d")
              df_daily = df_daily.sort_values(by="Date")

              chart_data_daily = pd.DataFrame()
              for market in selected_markets_daily:
                  market_data = df_daily[df_daily["Market"] == market].set_index("Date")
                  chart_data_daily[market] = market_data["Kg Price"]
              st.line_chart(chart_data_daily, use_container_width=True, height=230)
          else:
              st.write("선택한 일별 도매 시장 데이터가 없습니다.")
      
    with st.container():
      st.markdown("##### 월별 도매 가격 정보")
      # 데이터 로드 및 처리
      data_monthly = {}
      for filename in files_monthly:
         with open(os.path.join(directory_monthly, filename), "r") as file:
            file_data = json.load(file)
            # 데이터가 있는 파일인 경우에만 처리
            if file_data["data"]:
               date = filename.split("_")[2].split(".")[0]  # 파일 이름에서 날짜 추출
               data_monthly[date] = file_data["data"]

         # 사용자가 선택한 도매시장 목록
         markets_monthly = sorted(list(set([item["whsalname"] for date_data in data_monthly.values() for item in date_data])))
         selected_markets_monthly = selected_markets_daily

      if not data_monthly:
        st.write("월별 도매 시장 데이터가 없습니다.")
      else:
        if selected_markets_monthly:
            df_list_monthly = []
            for date, file_data in data_monthly.items():
              for item in file_data:
                  if item["whsalname"] in selected_markets_monthly:
                    kg_price = item['totamt'] / item['totqty']
                    df_list_monthly.append({"Date": date, "Market": item["whsalname"], "Kg Price": kg_price})
            df_monthly = pd.DataFrame(df_list_monthly)

            # 날짜 기준으로 정렬
            df_monthly["Date"] = pd.to_datetime(df_monthly["Date"])
            df_monthly = df_monthly.sort_values(by="Date")

            # 월별로 데이터 집계
            df_monthly["Month"] = df_monthly['Date'].dt.to_period('M')

            # 월 데이터를 문자열로 변환
            df_monthly["Month"] = df_monthly["Month"].astype(str)         

            chart_data_monthly = pd.DataFrame()
            for market in selected_markets_monthly:
              market_data = df_monthly[df_monthly["Market"] == market].set_index("Month")
              chart_data_monthly[market] = market_data["Kg Price"]
            st.line_chart(chart_data_monthly, use_container_width=True, height=230)
        else:
            st.write("선택한 월별 도매 시장 데이터가 없습니다.")
# ------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------
  with col2:
    with st.container():
       def load_daily_data(directory):
          data_list = []
          for filename in os.listdir(directory):
              if filename.endswith(".txt"):
                  filepath = os.path.join(directory, filename)
                  with open(filepath, 'r', encoding='utf-8') as file:
                      data = json.load(file)
                  for item in data['data']:
                      data_list.append({
                          'saleDate': item['saleDate'],
                          'smallName': item['smallName'],
                          'totQty': item['totQty']
                      })
          df = pd.DataFrame(data_list)
          # 날짜 기준으로 정렬
          df['saleDate'] = pd.to_datetime(df['saleDate']).dt.strftime("%Y%m%d")
          df = df.sort_values(by="saleDate")
          df['saleDate'] = df['saleDate'].astype(str)  
          return df
       
       def visualize_daily(df, selected_small_name):
          filtered_df = df[df['smallName'] == selected_small_name]
          daily_sum = filtered_df.groupby('saleDate')['totQty'].mean()
          st.bar_chart(daily_sum,  color='#FF69B4', height=230)

       def load_monthly_data(directory):
            data_list = []
            for filename in os.listdir(directory):
                if filename.endswith(".txt"):
                    filepath = os.path.join(directory, filename)
                    with open(filepath, 'r', encoding='utf-8') as file:
                        data = json.load(file)
                    for item in data['data']:
                        data_list.append({
                            'saleDate': item['saleDate'],
                            'smallName': item['smallName'],
                            'totQty': item['totQty']
                        })
            df = pd.DataFrame(data_list)
            # 날짜 기준으로 정렬
            df['saleDate'] = pd.to_datetime(df['saleDate'])
            df = df.sort_values(by="saleDate")
            return df
       
       def visualize_monthly(df, selected_small_name):
            df['YearMonth'] = df['saleDate'].dt.to_period('M')
            df['YearMonth'] = df['YearMonth'].astype(str)  
            filtered_df = df[df['smallName'] == selected_small_name]
            monthly_sum = filtered_df.groupby('YearMonth')['totQty'].mean()
            # monthly_sum.index = monthly_sum.index.to_timestamp()  # 인덱스를 날짜 형식으로 변환
            st.bar_chart(monthly_sum,  color='#FF69B4', height=230)

       def main():
            # 파일이 저장된 디렉토리 경로
            daily_directory = "/home/ubuntu/drive/dashboard/money_api/weekly_kg_dataset"
            monthly_directory = "/home/ubuntu/drive/dashboard/money_api/monthly_kg_dataset"

            # 일별 데이터 로드
            df_daily = load_daily_data(daily_directory)

            # 월별 데이터 로드
            df_monthly = load_monthly_data(monthly_directory)

            # 품종 선택
            selected_small_name = st.selectbox('품종을 선택하세요', ['Choose an option'] + list(df_daily['smallName'].unique()), key='selectbox')

            # 일별 시각화
            st.markdown("##### 일별 거래 물량 정보")
            if selected_small_name != "Choose an option":
                visualize_daily(df_daily, selected_small_name)
            else:
                st.write("선택된 데이터가 없습니다.")

            # 월별 시각화
            st.markdown("##### 월별 거래 물량 정보")
            if selected_small_name != "Choose an option":
                visualize_monthly(df_monthly, selected_small_name)
            else:
                st.write("선택된 데이터가 없습니다.")

    if __name__ == "__main__":
            main()