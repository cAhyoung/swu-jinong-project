import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from weather_api import weather_main
import json


### session state 설정
if "farm_code" not in st.session_state:
    st.session_state.farm_code = "F0016"

farm_code = st.session_state.farm_code

st.set_page_config(layout="wide")
df = pd.read_csv('/home/ubuntu/drive/dataset/sensor/sensor_final.csv')

default = '2024-03-20'
# 기준 날짜를 datetime 형식으로 변환
default_date = pd.to_datetime(default)

# 기준 날짜로부터 7일 후의 날짜 계산
end_date = default_date + timedelta(days=7)

# 데이터프레임의 '측정일자' 컬럼을 datetime 형식으로 변환
df['측정일자'] = pd.to_datetime(df['측정일자'])
df['check_datetime'] = pd.to_datetime(df['check_datetime'])

# 데이터프레임 필터링
filtered_df = df[(df['구역명'] == '1구역') & 
                 (df['farm_code'] == farm_code) & 
                 (df['측정일자'] >= default_date) & 
                 (df['측정일자'] <= end_date)]
### 사이드바 구성
with st.sidebar:
  st.header("대시보드 목록")
  st.page_link("main.py", label="통합 대시보드", icon="📶")
  st.page_link("pages/sensor1.py", label="센서 통합 정보", icon="🦾")
  st.page_link("pages/growth2.py", label="딸기 생육 정보", icon="🍓")
  st.page_link("pages/money3.py", label="도소매가 정보", icon="💰")
  st.page_link("pages/alert4.py", label="알림", icon="⚠️", disabled=True)
  st.page_link("pages/calender5.py", label="달력 메모장", icon="📆", disabled=True)

def adjusted_emoji(emoji, size=60):
    return f"<div style='text-align: center; margin-top: -20px; margin-left: -10px; font-size: {size}px;'>{emoji}</div>"

def centered_text_with_size(text, font_size=30):
    return f"<div style='text-align: center; font-size: {font_size}px;'>{text}</div>"

def left_text_with_size(text, font_size=30):
    return f"<div style='text-align: left; font-size: {font_size}px;'>{text}</div>"

def styled_text_with_size_and_color(value, unit='', font_size=30):
    value = float(value.split()[0])
    if value > 0:
        colored_text = f"<span style='color:green'>+{value:.2f} {unit}</span>"
    elif value < 0:
        colored_text = f"<span style='color:red'>{value:.2f} {unit}</span>"
    else:
        colored_text = f"{value:.2f} {unit}"
    return f"<div style='text-align: left; font-size: {font_size}px;'>{colored_text}</div>"

### 메인 타이틀
# col1, col2, col3, col4 = st.columns([0.65, 0.1, 0.15, 0.3], gap = 'small')
col1, col2, col3, col4 = st.columns([0.5, 0.1, 0.15, 0.25])
# col1, col2, col3, col4 = st.columns(4)

# 첫 번째 열(col1)
with col1:
    st.markdown("<h1 style='margin-top: -70px;'>센서 데이터 모아보기</h1>", unsafe_allow_html=True)
    # st.title("센서 데이터 모아보기")

# 두 번째 열(col2)
with col2:
    year = st.checkbox('전년도')
    st.markdown(
        """
        <style>
        .stCheckbox { margin-top: -25px; }
        </style>
        """,
        unsafe_allow_html=True
    )

# 세 번째 열(col3)
with col3:
    data = st.checkbox('표준 센서값', disabled=True)

# 네 번째 열(col4)
with col4:
    d = st.date_input("날짜 선택", datetime.date(2024, 3, 20))
    # d = st.date_input(datetime.date(2023, 12, 20))
    st.markdown(
        """
        <style>
        .stDateInput { margin-top: -50px; }
        </style>
        """,
        unsafe_allow_html=True
    )

if d != default_date:
  default = d
  default_date = pd.to_datetime(default)

  # 기준 날짜로부터 7일 후의 날짜 계산
  end_date = default_date + timedelta(days=7)

  # 데이터프레임 필터링
  filtered_df = df[(df['구역명'] == '1구역') & 
                  (df['farm_code'] == farm_code) & 
                  (df['측정일자'] >= default_date) & 
                  (df['측정일자'] <= end_date)]
### 화면 분리하기
mcol1, mcol2 = st.columns([0.67, 0.33])

if year:
  default_date = default_date - timedelta(days=365)
  # 기준 날짜로부터 7일 후의 날짜 계산
  end_date = default_date + timedelta(days=7)
  # 데이터프레임 필터링
  filtered_df = df[(df['구역명'] == '1구역') & 
                  (df['farm_code'] == farm_code) & 
                  (df['측정일자'] >= default_date) & 
                  (df['측정일자'] <= end_date)]

### 첫번째 컬럼 기준으로
with mcol1:
  ### 주요 지표를 담을 부분 구성
  with st.container():
    do1, do2 = st.columns([0.55, 0.45])
    with do1:
      st.markdown("#### 오늘의 주요 지표")
    with do2:
      aa = st.radio(label = 'Radio buttons', options =["전년도 기준", "표준 센서값 기준"],  horizontal=True, label_visibility='collapsed', index = 0, disabled=True)
    
    today_filtered_df = df[(df['구역명'] == '1구역') & 
                (df['farm_code'] == farm_code) & 
                (df['측정일자'] == '2024-03-20')]
    # 'check_datetime' 열을 datetime 형식으로 변환합니다.
    aaa = today_filtered_df
    # aaa['check_datetime'] = pd.to_datetime(aaa['check_datetime'])
    bbb = pd.to_datetime('2024-03-20')

    # default_date에서 년도, 월, 일을 추출합니다.
    default_date_year = 2024
    default_date_month = 3
    default_date_day = 20

    # 측정일자가 default_date와 동일한 데이터를 추출합니다.
    same_date_data = aaa[(aaa['측정일자'].dt.year == default_date_year) & 
                                (aaa['측정일자'].dt.month == default_date_month) & 
                                (aaa['측정일자'].dt.day == default_date_day)]
    
    # check_datetime에서 시간 부분만 추출합니다.
    same_date_data['check_time'] = same_date_data['check_datetime'].dt.time

    # 측정일자가 1년 전 데이터를 추출합니다.
    one_year_ago_data = df[(df['측정일자'].dt.year == default_date_year-1) & 
                                (df['측정일자'].dt.month == default_date_month) & 
                                (df['측정일자'].dt.day == default_date_day)]

    # check_datetime에서 시간 부분만 추출합니다.
    one_year_ago_data['check_time'] = one_year_ago_data['check_datetime'].dt.time

    # target_time을 datetime 객체로 변환합니다.
    target_datetime = bbb.replace(hour=12, minute=0, second=0)

    # check_time과 target_time 사이의 차이를 계산하고 출력합니다.
    difference = (same_date_data['check_datetime'] - target_datetime).abs()
    difference_one = (one_year_ago_data['check_datetime'] - target_datetime).abs()

    # 차이가 가장 작은 인덱스를 찾습니다.
    nearest_index = difference.idxmin()
    nearest_index_one = difference_one.idxmin()

    # 가장 가까운 데이터를 선택합니다.
    nearest_row = same_date_data.loc[nearest_index]
    nearest_row_one = one_year_ago_data.loc[nearest_index_one]

    corrent_t = nearest_row['내부온도']
    corrent_h = nearest_row['내부습도']
    corrent_co2 = nearest_row['내부CO2']
    corrent_solar = nearest_row['내부순간일사량']
    corrent_root = nearest_row['근권온도']

    dif_t = corrent_t - nearest_row_one['내부온도']
    dif_h = corrent_h - nearest_row_one['내부습도']
    dif_co2 = corrent_co2 - nearest_row_one['내부CO2']
    dif_solar = corrent_solar - nearest_row_one['내부순간일사량']
    dif_root = corrent_root - nearest_row_one['근권온도']
    
    cor1, cor2, cor3, cor4, cor5 = st.columns(5)
    if aa == '전년도 기준':
      with cor1:
        st.markdown(left_text_with_size("내부 온도", 15), unsafe_allow_html=True)
        st.markdown(left_text_with_size(f"{corrent_t} °C", 30), unsafe_allow_html=True)
        st.markdown(styled_text_with_size_and_color(f"{dif_t:.2f}",'°C', 18), unsafe_allow_html=True)
      with cor2:
        st.markdown(left_text_with_size("내부 습도", 15), unsafe_allow_html=True)
        st.markdown(left_text_with_size(f"{corrent_h} mph", 30), unsafe_allow_html=True)
        st.markdown(styled_text_with_size_and_color(f"{dif_h:.2f}",'mph', 18), unsafe_allow_html=True)
      with cor3:
        st.markdown(left_text_with_size("내부 CO2", 15), unsafe_allow_html=True)
        st.markdown(left_text_with_size(f"{corrent_co2} ppm", 30), unsafe_allow_html=True)
        st.markdown(styled_text_with_size_and_color(f"{dif_co2:.2f}",'ppm', 18), unsafe_allow_html=True)
      with cor4:
        st.markdown(left_text_with_size("내부 순간 일사량", 15), unsafe_allow_html=True)
        st.markdown(left_text_with_size(f"{corrent_solar} W", 30), unsafe_allow_html=True)
        st.markdown(styled_text_with_size_and_color(f"{dif_solar:.2f}",'W', 18), unsafe_allow_html=True)
      with cor5:
        st.markdown(left_text_with_size("근권온도", 15), unsafe_allow_html=True)
        st.markdown(left_text_with_size(f"{corrent_root} °C", 30), unsafe_allow_html=True)
        st.markdown(styled_text_with_size_and_color(f"{dif_root:.2f}", '°C', 18), unsafe_allow_html=True)
    elif aa == "표준 센서값 기준":
      with cor1:
        st.markdown(left_text_with_size("내부 온도", 15), unsafe_allow_html=True)
        st.markdown(left_text_with_size(f"{corrent_t} °C", 30), unsafe_allow_html=True)
        st.markdown(styled_text_with_size_and_color(f"{dif_t:.2f}",'°C', 18), unsafe_allow_html=True)
      with cor2:
        st.markdown(left_text_with_size("내부 습도", 15), unsafe_allow_html=True)
        st.markdown(left_text_with_size(f"{corrent_h} mph", 30), unsafe_allow_html=True)
        st.markdown(styled_text_with_size_and_color(f"{dif_h:.2f}",'mph', 18), unsafe_allow_html=True)
      with cor3:
        st.markdown(left_text_with_size("내부 CO2", 15), unsafe_allow_html=True)
        st.markdown(left_text_with_size(f"{corrent_co2} ppm", 30), unsafe_allow_html=True)
        st.markdown(styled_text_with_size_and_color(f"{dif_co2:.2f}",'ppm', 18), unsafe_allow_html=True)
      with cor4:
        st.markdown(left_text_with_size("내부 순간 일사량", 15), unsafe_allow_html=True)
        st.markdown(left_text_with_size(f"{corrent_solar} W", 30), unsafe_allow_html=True)
        st.markdown(styled_text_with_size_and_color(f"{dif_solar:.2f}",'W', 18), unsafe_allow_html=True)
      with cor5:
        st.markdown(left_text_with_size("근권온도", 15), unsafe_allow_html=True)
        st.markdown(left_text_with_size(f"{corrent_root} °C", 30), unsafe_allow_html=True)
        st.markdown(styled_text_with_size_and_color(f"{dif_root:.2f}", '°C', 18), unsafe_allow_html=True)
    else:
      with cor1:
        st.markdown(left_text_with_size("내부 온도", 15), unsafe_allow_html=True)
        st.markdown(left_text_with_size(f"{corrent_t} °C", 30), unsafe_allow_html=True)
        st.markdown(styled_text_with_size_and_color(f"{dif_t:.2f}",'°C', 18), unsafe_allow_html=True)
      with cor2:
        st.markdown(left_text_with_size("내부 습도", 15), unsafe_allow_html=True)
        st.markdown(left_text_with_size(f"{corrent_h} mph", 30), unsafe_allow_html=True)
        st.markdown(styled_text_with_size_and_color(f"{dif_h:.2f}",'mph', 18), unsafe_allow_html=True)
      with cor3:
        st.markdown(left_text_with_size("내부 CO2", 15), unsafe_allow_html=True)
        st.markdown(left_text_with_size(f"{corrent_co2} ppm", 30), unsafe_allow_html=True)
        st.markdown(styled_text_with_size_and_color(f"{dif_co2:.2f}",'ppm', 18), unsafe_allow_html=True)
      with cor4:
        st.markdown(left_text_with_size("내부 순간 일사량", 15), unsafe_allow_html=True)
        st.markdown(left_text_with_size(f"{corrent_solar} W", 30), unsafe_allow_html=True)
        st.markdown(styled_text_with_size_and_color(f"{dif_solar:.2f}",'W', 18), unsafe_allow_html=True)
      with cor5:
        st.markdown(left_text_with_size("근권온도", 15), unsafe_allow_html=True)
        st.markdown(left_text_with_size(f"{corrent_root} °C", 30), unsafe_allow_html=True)
        st.markdown(styled_text_with_size_and_color(f"{dif_root:.2f}", '°C', 18), unsafe_allow_html=True)
      
  ### mcol1 구역의 분할을 위한 새로운 컬럼
  scol1, scol2 = st.columns(2)
  with scol1:
    with st.container():
      st.markdown("#### 내부 온도")
      ### 이 아래에 내부 온도를 보여주기 위한 그래프를 넣어주기
      st.line_chart(data=filtered_df, x='check_datetime', y='내부온도', color='#FF69B4', width=0, height=0, use_container_width=True)
    
    with st.container():
      st.markdown("#### 내부 순간 일사량")
      ### 이 아래에 내부 순간 일사량을 보여주기 위한 그래프 넣어주기
      st.line_chart(data=filtered_df, x='check_datetime', y='내부순간일사량', color='#FF7F50', width=0, height=0, use_container_width=True)
  
  with scol2:
    with st.container():
      st.markdown("#### 내부 습도")
      ### 이 아래에 내부 습도를 보여주기 위한 그래프 넣어주기
      st.line_chart(data=filtered_df, x='check_datetime', y='내부습도', color='#00BFFF', width=0, height=0, use_container_width=True)
    with st.container():
      st.markdown("#### 근권온도")
      ### 이 아래에 근권온도를 보여주기 위한 그래프 넣어주기
      st.line_chart(data=filtered_df, x='check_datetime', y='근권온도', color='#CD853F', width=0, height=0, use_container_width=True)
 

### 두번째 컬럼을 기준으로    
with mcol2:
  with st.container():
    st.markdown("#### 오늘의 날씨")
    container = st.container(border=True)
    need = weather_main()

    # prev_weather = {"강수형태": "없음", "하늘상태": "불러오는 중", "기온": "불러오는 중", "강수확률": "불러오는 중"}
    
    with open("/home/ubuntu/drive/dashboard/prev_weather.json", 'r', encoding='utf-8') as json_file:    
      weather = json.load(json_file)
    
    for key in weather.keys():
      if key in need.keys():
        weather[key] = need[key]

    with open("/home/ubuntu/drive/dashboard/prev_weather.json", 'w', encoding='utf-8') as f:
      json.dump(weather, f, ensure_ascii=False, indent=4)
      
    if weather["강수형태"] == '비':
      st.markdown(adjusted_emoji("🌧️", size=40), unsafe_allow_html=True)
    elif weather["강수형태"] == '비/눈':
      st.markdown(adjusted_emoji("🌧️🌨️", size=40), unsafe_allow_html=True)
    elif weather["강수형태"] == '눈':
      st.markdown(adjusted_emoji("🌨️", size=40), unsafe_allow_html=True)
    elif weather["강수형태"] == '소나기':
      st.markdown(adjusted_emoji("🌦️", size=40), unsafe_allow_html=True)
    elif weather["강수형태"] == '빗방울':
      st.markdown(adjusted_emoji("💧", size=40), unsafe_allow_html=True)
    elif weather["강수형태"] == '빗방울/ 눈날림':
      st.markdown(adjusted_emoji("💧❄️", size=40), unsafe_allow_html=True)
    elif weather["강수형태"] == '눈날림':
      st.markdown(adjusted_emoji("❄️", size=40), unsafe_allow_html=True)
    else:
      if weather["하늘상태"] == "맑음":
        st.markdown(adjusted_emoji("☀️", size=40), unsafe_allow_html=True)
      elif weather["하늘상태"] == "구름많음":
        st.markdown(adjusted_emoji("☁️", size=40), unsafe_allow_html=True)
      else:
        st.markdown(adjusted_emoji("🌥️", size=40), unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
      st.markdown(centered_text_with_size("기온", 15), unsafe_allow_html=True)
      st.markdown(centered_text_with_size(f"{weather['기온']} °C", 25), unsafe_allow_html=True)
    with col2:
      st.markdown(centered_text_with_size("강수확률", 15), unsafe_allow_html=True)
      st.markdown(centered_text_with_size(f"{weather['강수확률']} %", 25), unsafe_allow_html=True)

    ### 이 아래에 오늘의 날씨를 보여주기 위한 그래프 넣어주기
  with st.container():
    st.markdown("#### 내부 CO2 농도")
    ### 이 아래에 내부 CO2 농도를 보여주기 위한 그래프 넣어주기
    st.line_chart(data=filtered_df, x='check_datetime', y='내부CO2', color='#BA55D3', width=0, height=0, use_container_width=True)
  
  
  with st.container():
    
    ### session state 설정 - 메모내용 기록
    if "user_input" not in st.session_state:
      user_input = ""
      st.session_state.user_input = user_input
      
    st.markdown("#### 유의사항")
    user_input = st.text_area(label="", value=st.session_state.user_input)
    print(user_input)
    submitted = st.button("저장")
    if submitted:
        st.success("저장되었습니다!")
        st.session_state.user_input = user_input
      
    # st.text_area(label="", help="기억해야 할 유의사항을 기록해주세요.", label_visibility="collapsed")
    