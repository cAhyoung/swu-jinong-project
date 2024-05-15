import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import json
from pathlib import Path
import os
from datetime import datetime 
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np
import altair as alt
import warnings

# 모든 경고 메시지 숨기기
warnings.filterwarnings("ignore")

st.set_page_config(layout="wide")

### session state 설정
if "farm_code" not in st.session_state:
    st.session_state.farm_code = "F0016"

farm_code = st.session_state.farm_code

def centered_text_with_size(text, font_size=30):
    return f"<div style='text-align: center; font-size: {font_size}px;'>{text}</div>"

### 사이드바 구성
with st.sidebar:
  st.header("대시보드 목록")
  st.page_link("main.py", label="통합 대시보드", icon="📶")
  st.page_link("pages/sensor1.py", label="센서 통합 정보", icon="🦾")
  st.page_link("pages/growth2.py", label="딸기 생육 정보", icon="🍓")
  st.page_link("pages/money3.py", label="도소매가 정보", icon="💰")
  st.page_link("pages/alert4.py", label="알림", icon="⚠️", disabled=True)
  st.page_link("pages/calender5.py", label="달력 메모장", icon="📆", disabled=True)

### 타이틀 구성
# st.title("딸기 생육 정보")
st.markdown("<h1 style='margin-top: -70px;'>딸기 생육 정보</h1>", unsafe_allow_html=True)


### 내부 구성
col1, col2 = st.columns([0.5, 0.45])

with col1:
   with st.container():
      st.markdown("""
      <style>
      .st-ae.st-af.st-ag.st-ah.st-ai.st-aj.st-ak.st-al.st-am {
                     width: 150px;
      }
      .element-container.st-emotion-cache-1ngp9wj.e1f1d6gn4 {
                     width: 300px;
      }
      .row-widget stSelectbox {
                     display: inline-block;
                     width: 150px;
      }           
      </style>
      """, unsafe_allow_html=True) 
   base_folder = '/home/ubuntu/drive/dataset/result'
   st.markdown("##### 농가 및 카메라 선택")

   #result하위 폴더로 농가 선택 selectbox 생성
   # sub_folders = os.listdir(base_folder)
   # farm_code = st.selectbox("농가 선택", sub_folders)
   #farm_code 하위 폴더로 카메라 위치 선택 selectbox 생성
   camera_folders = os.listdir(os.path.join(base_folder, farm_code))
   do1, do2 = st.columns([0.2, 0.7])
   with do1:
      camera_position = st.selectbox("카메라 선택", camera_folders, index=camera_folders.index('C101'))
      image_files = os.listdir(os.path.join(base_folder, farm_code, camera_position))
   with do2:
      #이미지 파일명에서 날짜 추출
      image_date = [file[11:19] for file in image_files]
      filtered_image_date = [date for date in image_date if date <= '20240326']

      #날짜를 년-월-일 형태로 변환
      formatted_dates = [datetime.strptime(date, "%Y%m%d").date() for date in filtered_image_date]
      unique_dates = sorted(set(formatted_dates), reverse=True)
      #촬영일시 선택
      selected_date = st.selectbox("날짜 선택", unique_dates)

   #선택하는 날짜에 해당하는 이미지 파일 표시
   selected_images = [file for file in image_files if selected_date.strftime("%Y%m%d") in file]
   index = 0
   #좌우 이동 버튼 생성
   image_row, buttons_row = st.columns([3, 1])
   with buttons_row:
      left_button = st.button("→", key="left_button")
      right_button = st.button("←", key="right_button")
   #이미지 슬라이더
   with image_row:
      if selected_images:
         if left_button and index > 0:
            index -= 1
         if right_button and index < len(selected_images) - 1:
            index += 1

         image_file = selected_images[index]
         image_path = os.path.join(base_folder, farm_code, camera_position, image_file)
         st.image(image_path, use_column_width=True)
      else:
         st.write("선택한 날짜에 해당하는 이미지가 없습니다.")
 
# 성장 속도 컨테이너 생성
# 마스킹된 객체들 상태 변화 
   with st.container():                                  
      st.markdown("##### 성장 속도")
      ### 이 아래에 시각화 할 수 있도록 구현하기
      @st.cache_data
      def load_mask_info():
         mask_info = pd.read_csv('/home/ubuntu/drive/EDA/merged_growth_real_real_final_dashboard.csv')
         return mask_info
      mask_info = load_mask_info()

      # selected_farm = st.selectbox('농가', mask_info['farm_code'].unique())
      selected_farm = farm_code
      selected_farm_data = mask_info[mask_info['farm_code'] == selected_farm]     

      #농가별로 shot_datetime, mask_id, pred_growth 테이블로 정의해 재저장
      mask_info_pivot_table = selected_farm_data.groupby(['shot_datetime','측정일자', 'mask_id'])['pred_growth'].first().reset_index()
      mask_info_pivot_table['shot_datetime'] = pd.to_datetime(mask_info_pivot_table['shot_datetime'])

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

      #최근 60일 이내 날짜만 가져오기
      # recent_data = mask_info_period[mask_info_period['shot_datetime'] >= mask_info_period['shot_datetime'].max() - pd.Timedelta(days=90)]
      # first_unripe_date = recent_data[recent_data['pred_growth'] == 'unripe'].groupby('mask_id')['shot_datetime'].min()
      # first_semiripe_date = recent_data[recent_data['pred_growth'] == 'semi-ripe'].groupby('mask_id')['shot_datetime'].min()
      # first_ripe_date = recent_data[recent_data['pred_growth'] == 'ripe'].groupby('mask_id')['shot_datetime'].min()
      # print(first_ripe_date)
      
      # #un_to_semi df 생성
      # un_to_semi = pd.DataFrame({ 
      #    'mask_id': first_unripe_date.index,
      #    'first_semiripe_date': first_semiripe_date.reindex(first_unripe_date.index),
      #    'first_unripe_date': first_unripe_date.values
      # })
      # un_to_semi['semi_growth_days'] = (un_to_semi['first_semiripe_date'] - un_to_semi['first_unripe_date']).dt.days
      
      # # semi_to_ripe df 생성
      # semiripe_to_ripe = pd.DataFrame({
      #    'mask_id': first_ripe_date.index,
      #    'first_ripe_date': first_ripe_date.values,
      #    'first_semiripe_date': first_semiripe_date.reindex(first_ripe_date.index),
      # })
      # semiripe_to_ripe['ripe_growth_days'] = (semiripe_to_ripe['first_ripe_date'] - semiripe_to_ripe['first_semiripe_date']).dt.days

      # un_to_semi['absolute_semi_growth_day'] = un_to_semi['semi_growth_days'].abs()
      # # st.write(un_to_semi.describe())


      #area_chart그리기  
      # st.area_chart(data, use_container_width=False, width=600, height=200)


with col2:
   with st.container():
      st.markdown("##### {} 성장 현황".format(selected_date))
      ### 이 아래에 시각화 할 수 있도록 구현하기
      #plotly pie차트로 각 성장 단계마다 집계하여 donut차트로 나타내기      
      # 현재 날짜를 기준으로 mask_info 필터링
      #current_date = mask_info_pivot_table.sort_values(by='shot_datetime', ascending=False).iloc[0]['shot_datetime'] 
      if selected_date is None:
         selected_date = '2024-03-26'

      # Convert selected_date to datetime format if it's not already
      selected_date = pd.to_datetime(selected_date)

      # Convert '측정일자' column to datetime format
      mask_info_pivot_table['측정일자'] = pd.to_datetime(mask_info_pivot_table['측정일자'])
      current_date = mask_info_pivot_table[mask_info_pivot_table['측정일자'] == selected_date]

      current_date = current_date.sort_values(by='shot_datetime', ascending=False).iloc[0]['shot_datetime']
      current_date = pd.to_datetime(current_date)

      # Convert current_date to string format for comparison
      current_date_mask_info = mask_info_pivot_table[mask_info_pivot_table['shot_datetime'] == current_date]
      # 클래스 비율 계산
      class_percentage = current_date_mask_info['pred_growth'].value_counts(normalize=True) * 100
      # Plotly의 pie chart 그리기
      graph = px.pie(values=class_percentage.values, names=class_percentage.index, hole=0.6)
      graph.update_traces(marker=dict(colors=['#FF0000', '#FFA500', '#32CD32']))
      graph.update_layout(width=500, height=400)
      # Streamlit에 표시
      st.plotly_chart(graph)
  
  
  
   with st.container():
      st.markdown("##### 수확기 진입 이후")
      ### 이 아래에 시각화 할 수 있도록 구현하기
      current_date = mask_info_pivot_table[mask_info_pivot_table['측정일자'] == selected_date]

      current_date = current_date.sort_values(by='shot_datetime', ascending=False).iloc[0]['shot_datetime']
      current_date = pd.to_datetime(current_date)
      print(current_date)

      current_date_mask_info = mask_info_pivot_table[mask_info_pivot_table['shot_datetime'] == current_date]

      mask_id = current_date_mask_info['mask_id'].unique()

      ripe_measurements = []

      for mask_id in mask_id:
      # mask_id와 pred_growth 조건을 만족하는 행을 필터링하여 임시 데이터프레임에 저장합니다.
         temp_data = selected_farm_data[(selected_farm_data['mask_id'] == mask_id)]
         
         temp_data['check_datetime'] = pd.to_datetime(temp_data['check_datetime'])
         
         temp_data = temp_data[temp_data['check_datetime'] < current_date]

         # 'pred_growth'가 'semi_ripe'인 행들만 추출
         ripe_data = temp_data[temp_data['pred_growth'] == 'ripe']
         # print(ripe_data)
         if not ripe_data.empty:
            ripe_measurement = ripe_data.loc[ripe_data['check_datetime'].idxmin(), '측정일자']
            ripe_measurement = pd.to_datetime(ripe_measurement)
            ripe_measurements.append(current_date - ripe_measurement)
            print('current_date:', current_date, 'ripe_measurement:', ripe_measurement)
         else:
            pass

      days_only = [str(delta).split(' ')[0] for delta in ripe_measurements]

      # 각 일자별로 개수를 세기 위해 Counter를 사용하여 딕셔너리로 변환
      count_by_day = dict(Counter(days_only))

      # 각 일자별 개수를 센 결과를 기반으로 키와 값을 추출합니다.
      dates = list(count_by_day.keys())
      counts = list(count_by_day.values())

      # 개수의 합으로 나누어 비율을 계산합니다.
      total = sum(counts)
      ratios = [count / total for count in counts]

      data = pd.DataFrame({'dates': dates, 'ratios': ratios})

      # 날짜 별로 다른 색상을 부여하기 위한 범위와 도메인 설정
      color_scale = alt.Scale(domain=dates, range=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])

      # 각 날짜별로 막대를 하나의 가로 막대 그래프로 표현
      bar_chart = alt.Chart(data).mark_bar().encode(
         x=alt.X('sum(ratios):Q', stack='zero', axis=alt.Axis(format='%'), title='Cumulative Ratio'),
         color=alt.Color('dates:N', scale=color_scale, legend=alt.Legend(title="Dates")),
         tooltip=['dates', 'sum(ratios)']
      ).properties(
         width=600,
         height=200
      )

      # text = bar_chart.mark_text(
      #    align='left',
      #    baseline='middle',
      #    dx=-100,  # 텍스트를 막대 오른쪽에 위치하도록 조정
      # ).encode(
      #    text=alt.Text('sum(ratios):Q', format='.0%'),
      #    color=alt.value('black')  # 텍스트 색상을 검정으로 지정  # 텍스트 포맷 설정
      # )

      st.altair_chart(bar_chart, use_container_width=False)
      
      # data = pd.DataFrame({"ratios": ratios}, index=dates)
      # data = data.T
      # color = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
      # st.bar_chart(x=None, y=data["ratios"], color=color[:len(data["ratios"])])
      

      # # # 바 그래프 그리기
      # st.bar_chart(data)

      # mask_info_pivot_table columns: shot_datetime, mask_id, pred_growth
      # mask_info_pivot_table.sort_values(by="shot_datetime")
      # ripe_data = mask_info_pivot_table[mask_info_pivot_table['shot_datetime'] == selected_date]
      # ripe_data = ripe_data[ripe_data['pred_growth'] == 'ripe'] # <- 이 데이터에 대해서 

      # # ripe_data에서 idx, mask_id를 가져오고, 그 mask_id에 대한 값들을 모두 가져오고 정렬시켜서 맨 처음 등장하는 ripe가 있는 행의 날짜를 가져와 diff 구하기
      # def get_cumulative_time(row):
      #    mask_id = row["mask_id"]
      #    first = mask_info_pivot_table[mask_info_pivot_table["mask_id"] == mask_id][mask_info_pivot_table["pred_growth"] == "ripe"]["shot_datetime"].values[0]
      #    return (row["shot_datetime"] - first).days
         
      # ripe_data["cumulative_time"] = ripe_data.apply(get_cumulative_time, axis=1)
      # plt.figure(figsize=(12, 6))
      # colors = ['blue']  # 파란색으로 설정
      # ax = plt.bar(dates, ratios, color=colors)
      # plt.title('Cumulative Time for Ripe Predicted Growth')
      # plt.xlabel('Date')
      # plt.ylabel('Ratio of Cumulative Time')
      # plt.xticks(rotation=45)
      # plt.grid(axis='y')
      # plt.show()

   with st.container():
      st.markdown("")
    ### 디테일한 디자인 구현하기
    ### 이 아래에 이상치 분석과 관련된 내용 구현하기