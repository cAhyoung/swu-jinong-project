import json
from datetime import datetime, timedelta
from pytz import timezone
import numpy as np
import requests

### 기본 파라미터 설정 및 시간 불러오기
key = "jFSNebMPutZ8sA7Fhiy22HBs4D9JK531VAZ/fvTVK83yZODW7PXMqaKJxtzlE7Tv0tpsv4zxaYWUBmuAhjl29w=="

##### 초단기실황 url
sht_real_url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"

##### 단기예보 url
pred_url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"

##### 예보를 위한 기준시간 리스트
now_day = datetime.now(timezone('Asia/Seoul')).strftime("%Y%m%d")
base_time_list = ["0200", "0500", "0800", "1100", "1400", "1700", "2000", "2300"]



def find_similar_time(base_time, base_time_list):
  base_time_arr = np.fromiter((int(i[:2]) for i in base_time_list), dtype="int64")
  base_time_int = int(base_time[:2])
  closest_value = min(base_time_arr, key=lambda x: (abs(x-base_time_int), x))
  return closest_value

def time_change(base_time):
  change_time = int(base_time[:2])
  change_time += 1
  if change_time == 24:
    change_time = 0
  if len(str(change_time)) == 2:
    after_time = str(change_time) + "00"
  else:
    after_time = "0" + str(change_time) + "00"
  
  return after_time

def date_change():
  return (datetime.now(timezone('Asia/Seoul')) + timedelta(days=1)).strftime("%Y%m%d")

def filter_real_data(res, need):
  for dic_list in res['response']['body']['items']['item']:
    for i in ["T1H", "RN1", "REH", "PTY"]:
        if dic_list["category"] == i:
          need[i] = dic_list["obsrValue"]
          
  return need
          
def filter_pred_data(res, base_time, need):
  for dic_list in res['response']['body']['items']['item']:
    for i in ["POP", "SKY", "TMN", "TMX"]:
      if dic_list["category"] == i:
        if (dic_list["fcstTime"] == time_change(base_time)) | (dic_list["fcstTime"] == base_time):
          if (dic_list["fcstTime"] == "0000") & (dic_list["fcstDate"] == date_change()):
            need[f"{i}_예보"] = dic_list["fcstValue"]
          elif dic_list["fcstDate"] == now_day:
            need[f"{i}_예보"] = dic_list["fcstValue"]

  return need
      
def code_mapping(need):
  ### code
  replace_need = {}
  code = {"PTY" : "강수형태", "REH" : "습도", "T1H" : "기온", "RN1" : "1시간강수량", 
              "POP_예보" : "강수확률", "SKY_예보" : "하늘상태", "TMS" : "일최저기온", "TMX" : "일최고기온"}
  sky = {"1" : "맑음", "3" : "구름 많음", "4" : "흐림"}
  pty = {"0" : "없음", "1" : "비", "2" : "비/눈", "3" : "눈", "4" : "소나기", "5" : "빗방울", "6" : "빗방울/눈날림", "7" : "눈날림"}
  
  ### mapping
  for key, value in need.items():
    if key in code:
      if key == "SKY_예보":
        value = sky[value]
      elif (key == "PTY") | (key == "PTY_예보"):
        value = pty[value]
        
      replace_need[code[key]] = value
      
  return replace_need

def return_params(base_time):
  ### 논산시 지역코드
  nonsan_coor = {"전체" : ["62", "97"] , "강경읍" : ["61", "96"], 
              "연무읍" : ["62",	"95"], "성동면" : ["61",	"97"], 
              "광석면" : ["62",	"98"], "노성면" : ["63",	"99"], "상월면" : ["63", "99"], 
              "부적면" : ["63",	"97"], "연산면" : ["64",	"97"], 
              "벌곡면" : ["65",	"97"], "양촌면" :["65",	"96"], "가야곡면" : ["63",	"96"], 
              "은진면" : ["62",	"96"], "채운면" : ["62",	"96"], 
              "취암동" : ["62",	"97"], "부창동" : ["62",	"97"]}
  params ={"serviceKey" : key, "pageNo" : "1", "numOfRows" : "1000", "dataType" : "JSON", "base_date" : now_day, "base_time" : base_time, "nx" : nonsan_coor["전체"][0], "ny" : nonsan_coor["전체"][1] }
  return params

def weather_main():
  ### 저장할 딕셔너리
  need = {}
  
  ### 현재 시간 불러오기
  base_time = datetime.now(timezone('Asia/Seoul')).strftime("%H00")

  ### 데이터 추출하여 need에 저장
  ##### 시간 조정
  if base_time not in base_time_list:
    similar_value = str(find_similar_time(base_time, base_time_list))
  
    if len(similar_value) == 2:
      base_time = similar_value + "00"
    else:
      base_time = "0" + similar_value + "00"
  
  ##### 파라미터 설정
  params = return_params(base_time)
      
  ##### 예보값
  pred_res = requests.get(pred_url, params=params)
  pred = json.loads(pred_res.content)
  if pred["response"]["header"]["resultMsg"] != "NO_DATA":
    need = filter_pred_data(pred, base_time, need)
  
  ##### 실황값
  base_time = datetime.now(timezone('Asia/Seoul')).strftime("%H00")
  params = return_params(base_time)
  real_res = requests.get(sht_real_url, params=params)
  real = json.loads(real_res.content)
  if real["response"]["header"]["resultMsg"] != "NO_DATA":
    need = filter_real_data(real, need)
  
  need = code_mapping(need)
  print(need)
  return need