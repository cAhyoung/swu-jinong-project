import streamlit as st

st.set_page_config(layout="wide")

### 사이드바 구성
with st.sidebar:
  st.header("사이드바 목록")
  st.page_link("main.py", label="통합 대시보드", icon="📶")
  st.page_link("pages/sensor1.py", label="센서 통합 정보", icon="🦾")
  st.page_link("pages/growth2.py", label="딸기 생육 정보", icon="🍓")
  st.page_link("pages/money3.py", label="도소매가 정보", icon="💰")
  st.page_link("pages/alert4.py", label="알림", icon="⚠️")
  st.page_link("pages/calender5.py", label="달력 메모장", icon="📆")

### 타이틀 구성
st.title("달력 메모장")