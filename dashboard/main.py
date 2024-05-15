import streamlit as st
import pandas as pd
import numpy as np
import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from weather_api import weather_main
import json
import plotly.express as px
from collections import Counter
import matplotlib.pyplot as plt
from datetime import datetime 

st.set_page_config(layout="wide")

### session state 설정
if "farm_code" not in st.session_state:
    st.session_state.farm_code = "F0016"

# farm_code = st.session_state.selected_option
# print(st.session_state.farm_code)
### 사이드바 구성
with st.sidebar:
  st.header("사이드바 목록")
  st.page_link("main.py", label="통합 실시간 대시보드", icon="📶")
  st.page_link("pages/sensor1.py", label="센서 통합 정보", icon="🦾")
  st.page_link("pages/growth2.py", label="딸기 생육 정보", icon="🍓")
  st.page_link("pages/money3.py", label="도소매가 정보", icon="💰")
  st.page_link("pages/alert4.py", label="알림", icon="⚠️", disabled=True)
  st.page_link("pages/calender5.py", label="달력 메모장", icon="📆", disabled=True)

def adjusted_emoji(emoji, size=60):
    return f"<div style='text-align: center; margin-top: -20px; margin-left: -10px; font-size: {size}px;'>{emoji}</div>"

def centered_text_with_size(text, font_size=30):
    return f"<div style='text-align: center; font-size: {font_size}px;'>{text}</div>"

### 메인 페이지 구성
# st.title("통합 대시보드")
colt1, colt2 = st.columns([0.7, 0.3])
with colt1:
  # st.markdown("<h1 /style='margin-top: -70px;'>통합 대시보드</h1>", unsafe_allow_html=True)
  st.title("통합 대시보드")
  st.markdown(
    """
    <style>
    h1 {
      margin-top: -70px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
  )
with colt2:
  selected_option = st.selectbox("농가", ("F0016", "F0017"))
  st.session_state.farm_code = selected_option
  st.markdown(
    """
    <style>
    .stSelectbox { margin-top: -70px; }
    </style>
    """,
    unsafe_allow_html=True
  )

##### 세 부분으로 나누기
col1, col2, col3 = st.columns(3)


with col1:
  with st.container():
    st.markdown("### 농가 기본 정보")
    col4, col5, col6, col7 = st.columns(4, gap="small")
    if selected_option == 'F0016':
      with col4:
        st.caption("농장명")
        st.markdown("**KCY**")
      with col5:
        st.caption("품종")
        st.markdown("**비타베리**")
      with col6:
        st.caption("재배방식")
        st.markdown("**촉성재배**")
      with col7:
        st.caption("정식일자")
        st.markdown("**2023-09-01**")
    else:
      with col4:
        st.caption("농장명")
        st.markdown("**lyh**")
      with col5:
        st.caption("품종")
        st.markdown("**설향**")
      with col6:
        st.caption("재배방식")
        st.markdown("**촉성재배**")
      with col7:
        st.caption("정식일자")
        st.markdown("**2023-09-05**")  
  with st.container():
    st.markdown("### 생육상태")

    def load_mask_info():
        mask_info = pd.read_csv('/home/ubuntu/drive/EDA/merged_growth_real_real_final_dashboard.csv')
        return mask_info
    mask_info = load_mask_info()

    # selected_farm = st.selectbox('농가', mask_info['farm_code'].unique())
    selected_farm_data = mask_info[mask_info['farm_code'] == st.session_state.farm_code]   
    # print(selected_farm_data)

    #농가별로 shot_datetime, mask_id, pred_growth 테이블로 정의해 재저장
    mask_info_pivot_table = selected_farm_data.groupby(['shot_datetime','측정일자', 'mask_id'])['pred_growth'].first().reset_index()
    mask_info_pivot_table['shot_datetime'] = pd.to_datetime(mask_info_pivot_table['shot_datetime'])
    selected_date = '2024-03-26'

    # Convert selected_date to datetime format if it's not already
    selected_date = pd.to_datetime(selected_date)

    # Convert '측정일자' column to datetime format
    mask_info_pivot_table['측정일자'] = pd.to_datetime(mask_info_pivot_table['측정일자'])
    current_date = mask_info_pivot_table[mask_info_pivot_table['측정일자'] == selected_date]

    current_date = current_date.sort_values(by='shot_datetime', ascending=False).iloc[0]['shot_datetime']
    current_date = pd.to_datetime(current_date)
    # print(current_date)

    # Convert current_date to string format for comparison
    current_date_mask_info = mask_info_pivot_table[mask_info_pivot_table['shot_datetime'] == current_date]
        # 클래스 비율 계산
    class_percentage = current_date_mask_info['pred_growth'].value_counts(normalize=True) * 100
    # Plotly의 pie chart 그리기
    graph = px.pie(values=class_percentage.values, names=class_percentage.index, hole=0.6)
    graph.update_traces(marker=dict(colors=['#FF0000', '#FFA500', '#32CD32']))
    graph.update_layout(
        width=500,
        height=400,
        legend=dict(
            title='',
            orientation='v',  # 수직 방향으로 배치
            x=0,  # 왼쪽에 배치
            y=0.5  # 중앙에 배치
        )
    )

    # Streamlit에 표시
    st.plotly_chart(graph)

with col3:
  with st.container():
    st.markdown("### 실시간 오늘의 날씨")
    container = st.container(border=True)
    try:
      need = weather_main()
    except json.decoder.JSONDecodeError:
      need = dict()
      
    # prev_weather = {"강수형태": "없음", "하늘상태": "불러오는 중", "기온": "불러오는 중", "강수확률": "불러오는 중"}
    
    # 날씨 백업 데이터 가져오기
    with open("/home/ubuntu/drive/dashboard/prev_weather.json", 'r', encoding='utf-8') as json_file:    
      weather = json.load(json_file)
    
    for key in weather.keys():
      if key in need.keys():
        weather[key] = need[key]

    # 날씨 json으로 백업
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

    col1in, col2in = st.columns(2)
    with col1in:
      st.markdown(centered_text_with_size("기온", 15), unsafe_allow_html=True)
      st.markdown(centered_text_with_size(f"{weather['기온']} °C", 25), unsafe_allow_html=True)
    with col2in:
      st.markdown(centered_text_with_size("강수확률", 15), unsafe_allow_html=True)
      st.markdown(centered_text_with_size(f"{weather['강수확률']} %", 25), unsafe_allow_html=True)
    

  with st.container():
    st.markdown("")
    st.markdown("### 농가 내부 환경")
    # option = st.selectbox('보고 싶은 농가 환경은?', ["내부 온도", "내부 습도", "내부 순간 일사량", "내부 CO2", "근권온도"], key='selectbox')
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
                    (df['farm_code'] == 'F0016') & 
                    (df['측정일자'] >= default_date) & 
                    (df['측정일자'] <= end_date)]
    st.markdown("#### ...")
    option = st.selectbox('환경을 선택해주세요?', ["내부 온도", "내부 습도", "내부 순간 일사량", "내부 CO2", "근권온도"], key='selectbox')

    if option == "내부 온도":
      st.line_chart(data=filtered_df, x='check_datetime', y='내부온도', color='#FF69B4', width=0, height=0, use_container_width=True)
    elif option == "내부 습도":
      st.line_chart(data=filtered_df, x='check_datetime', y='내부습도', color='#00BFFF', width=0, height=0, use_container_width=True)
    elif option == "내부 순간 일사량":
      st.line_chart(data=filtered_df, x='check_datetime', y='내부순간일사량', color='#FF7F50', width=0, height=0, use_container_width=True)
    elif option == "내부 CO2":
      st.line_chart(data=filtered_df, x='check_datetime', y='내부CO2', color='#BA55D3', width=0, height=0, use_container_width=True)
    else:
      st.line_chart(data=filtered_df, x='check_datetime', y='근권온도', color='#CD853F', width=0, height=0, use_container_width=True)
    
with col2:
  with st.container():
    st.markdown("### 총 수확 가능 딸기")
    # print(current_date_mask_info)
    count = current_date_mask_info[current_date_mask_info['pred_growth'] == 'ripe']
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown(f"<h1 style='text-align: center; font-size: 26px;'>{len(count)} 개</h1>", unsafe_allow_html=True)

  with st.container():
    st.markdown("### 수확 적기 제안")
    mask_id = current_date_mask_info['mask_id'].unique()

    filtered_data = pd.DataFrame()

    semi_measurements = []
    unripe_measurements = []

    for mask_id in mask_id:
    # mask_id와 pred_growth 조건을 만족하는 행을 필터링하여 임시 데이터프레임에 저장합니다.
        temp_data = selected_farm_data[(selected_farm_data['mask_id'] == mask_id) & (selected_farm_data['pred_growth'] != 'ripe')]

        # 'pred_growth'가 'semi_ripe'인 행들만 추출
        semi_ripe_data = temp_data[temp_data['pred_growth'] == 'semi-ripe']
        unripe_data = temp_data[temp_data['pred_growth'] == 'unripe']
        # print(semi_ripe_data)
        # print(unripe_data)
            
        # 'semi_ripe'인 행이 존재하는 경우
        if not semi_ripe_data.empty:
            # 측정일자가 가장 빠른 행을 선택하여 earliest_measurements 리스트에 추가
            semi_measurement = semi_ripe_data.loc[semi_ripe_data['check_datetime'].idxmin(), '측정일자']
            semi_measurement = pd.to_datetime(semi_measurement)
            semi_measurements.append(semi_measurement + timedelta(days=5))
        elif not unripe_data.empty:
            unripe_measurement = unripe_data.loc[unripe_data['check_datetime'].idxmin(), '측정일자']
            unripe_measurement = pd.to_datetime(unripe_measurement)
            unripe_measurements.append(unripe_measurement + timedelta(days=5))
        else:
            pass

    # 'semi_measurements'와 'unripe_measurements' 두 리스트를 합침
    all_measurements = semi_measurements + unripe_measurements

    # 각 날짜별 개수를 세기
    measurement_counts = Counter(all_measurements)

    # 개수를 기준으로 내림차순 정렬하여 상위 3개를 출력
    top_3_measurements = measurement_counts.most_common(3)

    formatted_dates = [(top_3_measurements.strftime('%Y-%m-%d'), value) for top_3_measurements, value in top_3_measurements]
    df = pd.DataFrame(formatted_dates, columns=['날짜', '값'])

    # 인덱스를 날짜로 설정
    df.set_index('날짜', inplace=True)

    # 바 그래프 그리기
    st.bar_chart(data=df, height=230)

  with st.container():
    st.markdown("### 성장속도")
    selected_farm = st.session_state.farm_code
    def period(start_date, end_date):
        start_date = datetime.strptime(start_date,'%Y-%m-%d %H:%M:%S')
        end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
        return (start_date, end_date)
    
    if selected_farm == 'F0016':
    # 작기 기간 설정
        period_21_22 = period('2021-09-10 07:59:03', '2022-04-30 16:30:00')
        period_22_23 = period('2022-08-25 16:44:07', '2023-04-30 16:32:53')
        period_23_24 = period('2023-08-29 08:40:22', '2024-03-27 00:00:00')
    else:
        period_21_22 = period('2021-09-10 07:59:03', '2022-05-01 00:00:00')
        period_22_23 = period('2022-08-25 16:44:07', '2022-05-01 00:00:00')
        period_23_24 = period('2023-08-29 08:40:22', '2024-03-27 00:00:00')    
        
    # 작기 기간에 따라 데이터 필터링
    mask_info_period = mask_info_pivot_table[(mask_info_pivot_table['shot_datetime'] >= period_23_24[0]) & (mask_info_pivot_table['shot_datetime'] <= period_23_24[1])]

    #측정 날짜 기준으로 내림차순 정렬
    mask_info_period = mask_info_period.sort_values(by='shot_datetime', ascending=False)

    mask_cal = selected_farm_data.groupby(['unripe_to_semi-ripe','semi-ripe_to_ripe'])['mask_id'].first().reset_index()

    # mask_cal 데이터프레임에서 unripe_to_semi-ripe 칼럼의 통계량 계산
    min_value_semi = round(mask_cal['unripe_to_semi-ripe'].min())
    max_value_semi = round(mask_cal['unripe_to_semi-ripe'].max())
    mode_value_semi = round(mask_cal['unripe_to_semi-ripe'].mode()[0])  # 최빈값은 mode() 함수로 계산됩니다. 여러 최빈값이 있는 경우 첫 번째 값을 선택합니다.
    mean_value_semi = round(mask_cal['unripe_to_semi-ripe'].mean())

    min_value_ripe = round(mask_cal['semi-ripe_to_ripe'].min())
    max_value_ripe = round(mask_cal['semi-ripe_to_ripe'].max())
    mode_value_ripe = round(mask_cal['semi-ripe_to_ripe'].mode()[0])  # 최빈값은 mode() 함수로 계산됩니다. 여러 최빈값이 있는 경우 첫 번째 값을 선택합니다.
    mean_value_ripe = round(mask_cal['semi-ripe_to_ripe'].mean())

    # Selectbox에서 선택할 옵션 설정
    grow_option = st.radio('성장 단계 선택',('성장기 -> 착색기','착색기 -> 수확기'))
    
    #선택된 옵션에 따라 시각화 데이터 선택
    if grow_option == '성장기 -> 착색기':
        kol1, kol2, kol3, kol4 = st.columns([0.1, 0.1, 0.1, 0.1])
        with kol1:
          st.markdown(centered_text_with_size("최소", 15), unsafe_allow_html=True)
          st.markdown(centered_text_with_size(f"{min_value_semi} 일", 25), unsafe_allow_html=True)
        with kol2:
          st.markdown(centered_text_with_size("평균", 15), unsafe_allow_html=True)
          st.markdown(centered_text_with_size(f"{mean_value_semi} 일", 25), unsafe_allow_html=True)
        with kol3:
          st.markdown(centered_text_with_size("최빈", 15), unsafe_allow_html=True)
          st.markdown(centered_text_with_size(f"{mode_value_semi} 일", 25), unsafe_allow_html=True)
        with kol4:
          st.markdown(centered_text_with_size("최대", 15), unsafe_allow_html=True)
          st.markdown(centered_text_with_size(f"{max_value_semi} 일", 25), unsafe_allow_html=True)
    elif grow_option == '착색기 -> 수확기':
        kol1, kol2, kol3, kol4 = st.columns([0.1, 0.1, 0.1, 0.1])
        with kol1:
          st.markdown(centered_text_with_size("최소", 15), unsafe_allow_html=True)
          st.markdown(centered_text_with_size(f"{min_value_ripe} 일", 25), unsafe_allow_html=True)
        with kol2:
          st.markdown(centered_text_with_size("평균", 15), unsafe_allow_html=True)
          st.markdown(centered_text_with_size(f"{mean_value_ripe} 일", 25), unsafe_allow_html=True)
        with kol3:
          st.markdown(centered_text_with_size("최빈", 15), unsafe_allow_html=True)
          st.markdown(centered_text_with_size(f"{mode_value_ripe} 일", 25), unsafe_allow_html=True)
        with kol4:
          st.markdown(centered_text_with_size("최대", 15), unsafe_allow_html=True)
          st.markdown(centered_text_with_size(f"{max_value_ripe} 일", 25), unsafe_allow_html=True)