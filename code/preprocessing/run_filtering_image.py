## 필터링 

from PIL import Image
import pandas as pd

'''
df를 가져와서 각 행의 이미지 전처리하기
F0016_filtering 이런 식으로 폴더 구조 그대로 가져와서 필터링 조건에 걸리는 이미지는 이동시키기

'''

## 가로가 긴 경우 True, 아닌 경우 False
def is_wide_image(img):
    width, height = img.size
    aspect_ratio = width / height
    if aspect_ratio >= 2:  # 2:1 이상의 비율을 가지는 이미지만 처리
        return True
    return False

# 임계값 N
N = 0.49

## 투명하지 않은 픽셀 개수 카운트 후 비율 반환
def count_not_transparent_pixel_ratio(img):
    # # 이미지 로드
    # img = Image.open(image_path)
    
    # RGBA 이미지로 변환 (필요한 경우)
    img = img.convert("RGBA")
    # 전체 픽셀 수
    w, h = img.size
    size = w * h
    
    # 픽셀 데이터 가져오기
    pixel_data = img.load()

    # 픽셀 수 초기화
    non_transparent_pixels = 0

    # 이미지 픽셀 순회하며 투명 여부 확인
    for x in range(w):
        for y in range(h):
            # 픽셀의 알파 값 가져오기 (0은 완전 투명, 255는 완전 불투명)
            alpha = pixel_data[x, y][3]
            if alpha != 0:
                non_transparent_pixels += 1

    return non_transparent_pixels / size

## 필터링 대상일 경우 True, 아닌 경우 False
def is_stem_image(img):
    return True if count_not_transparent_pixel_ratio(img) <= N else False

import os
import shutil

# ## 입력 df에 대해 필터링 진행, 필터링된 이미지는 경로 이동
# def run_filtering_image(data_path, img_folder="/home/ubuntu/drive/dataset/SAM_result/"):
#     # df 경로를 입력받아 실행
#     '''
#     farm_code -> F0016
#     input_image_name -> F0016-C101-20210902-165906
#     output_image_path -> image_mask_5.png
#     위 정보를 활용해서 mask png 파일에 바로 접근해 open하고 판별해서 필터링 대상이면 바로 옮기기
    
#     F0016_filtering/C101 정도까지만 폴더 만들되 만약 필터링된 경우만 폴더 생성하도록 하기

#     기존 path: /home/ubuntu/drive/dataset/SAM_result/F0016/C101/F0016-C101-20210910-125907/masks/
#     이동 path: /home/ubuntu/drive/dataset/SAM_result/F0016_filtering/C101/F0016-C101-20210910-125907/masks/
#     '''
#     # farm_code 별 필터링 결과 저장 디렉토리 경로
#     filtering_folder = {"F0016": os.path.join(img_folder, "F0016_filtering", "C101"),
#                         "F0017": os.path.join(img_folder, "F0017_filtering", "C101")}
    
#     # (존재하지 않는 경우만) 필터링된 데이터를 옮길 농가별, C101 폴더 생성
#     if not os.path.exists(filtering_folder["F0016"]):
#         os.mkdir(os.path.join(img_folder, "F0016_filtering"))
#         os.mkdir(os.path.join(img_folder, "F0017_filtering"))

#         os.mkdir(filtering_folder["F0016"])
#         os.mkdir(filtering_folder["F0017"])

#     # 데이터 불러오기
#     data = pd.read_csv(data_path)
    
#     for _, row in data.iterrows():
#         # 이미지 경로
#         img_path = os.path.join(img_folder, row["farm_code"], "C101", row["input_image_name"], "masks", row["output_image_path"])
#         print(f"input image path : {img_path}")

#         # 이미지 불러오기
#         try:
#             img = Image.open(img_path)
#         except FileNotFoundError:
#             continue

#         # 필터링 조건에 걸리면 파일 옮기기
#         if is_stem_image(img) or is_wide_image(img):
#             move_folder = os.path.join(filtering_folder[row["farm_code"]], row["input_image_name"])
#             # 폴더가 존재하지 않으면 폴더 만들기 (masks까지)
#             if not os.path.exists(move_folder):
#                 os.mkdir(move_folder)
#                 os.mkdir(os.path.join(move_folder, "masks"))

#             # 파일 옮기기
#             shutil.move(img_path, os.path.join(move_folder, "masks", row["output_image_path"]))


## 입력 df에 대해 필터링 진행, 필터링된 이미지는 1로 설정, 컬럼 추가 후 data 저장
def run_filtering_image(data_path, img_folder="/home/ubuntu/drive/dataset/SAM_result/"):
    # df 경로를 입력받아 실행
    '''
    farm_code -> F0016
    input_image_name -> F0016-C101-20210902-165906
    output_image_path -> image_mask_5.png
    위 정보를 활용해서 mask png 파일에 바로 접근해 open하고 판별해서 필터링 대상이면 1로 표기하기
    '''
    # 데이터 불러오기
    data = pd.read_csv(data_path)
    is_filtering = []
    
    for _, row in data.iterrows():
        if pd.isna(row['output_image_path']):
            is_filtering.append(None)
            continue

        # 이미지 경로
        img_path = os.path.join(img_folder, row["farm_code"], "C101", row["input_image_name"], "masks", row["output_image_path"])
        print(f"input image path : {img_path}")
        
        # 이미지 불러오기
        img = Image.open(img_path)

        # 필터링 조건에 걸리면 파일 옮기기
        if is_stem_image(img) or is_wide_image(img):
            is_filtering.append(1)
        else:
            is_filtering.append(0)
    
    data["is_filtering"] = is_filtering


    data.to_csv(data_path[:-4] + "_filtering.csv")


def back():
    # filtering 결과 되돌리기.. ㅋ
    base_folder = ["/home/ubuntu/drive/dataset/SAM_result/F0016_filtering", "/home/ubuntu/drive/dataset/SAM_result/F0017_filtering"]

    for directory in base_folder: 
        # farm_code (/home/ubuntu/drive/dataset/SAM_result/F0016_filtering)
        if os.path.isdir(directory):
            print(f"directory path is <{directory}>.")
            # area_code (C101)
            subdirectory_path = os.path.join(directory, "C101")
            for imagedirectory in os.listdir(subdirectory_path):
                print(f"imagedirectory is <{imagedirectory}>.")
                masks_path = os.path.join(subdirectory_path, imagedirectory, "masks")
                for file_name in os.listdir(masks_path):
                    file_path = os.path.join(masks_path, file_name)
                    dest_path = file_path.replace("_filtering", "")
                    # print(file_path, dest_path)
                    shutil.move(file_path, dest_path)

def remove_empty_dir():
    # filtering 결과 되돌리기.. ㅋ
    base_folder = ["/home/ubuntu/drive/dataset/SAM_result/F0016_filtering", "/home/ubuntu/drive/dataset/SAM_result/F0017_filtering"]

    for directory in base_folder: 
        # farm_code (/home/ubuntu/drive/dataset/SAM_result/F0016_filtering)
        if os.path.isdir(directory):
            print(f"directory path is <{directory}>.")
            # area_code (C101)
            subdirectory_path = os.path.join(directory, "C101")
            for imagedirectory in os.listdir(subdirectory_path):
                print(f"imagedirectory is <{imagedirectory}>.")
                masks_path = os.path.join(subdirectory_path, imagedirectory, "masks")
                for file_name in os.listdir(masks_path):
                    file_path = os.path.join(masks_path, file_name)
                    dest_path = file_path.replace("_filtering", "")
                    # print(file_path, dest_path)
                    shutil.move(file_path, dest_path)

import os

def remove_empty_folders(path):
    # 현재 경로의 하위 항목들을 리스트로 가져오기
    with os.scandir(path) as entries:
        # 하위 항목들에 대해 반복
        for entry in entries:
            # 만약 entry가 디렉터리이면
            if entry.is_dir():
                # 재귀적으로 함수를 호출하여 해당 디렉터리 안의 비어있는 폴더를 삭제
                remove_empty_folders(entry.path)
    
    # 현재 경로의 모든 하위 항목들을 리스트로 가져오기
    with os.scandir(path) as entries:
        # 만약 현재 폴더에 항목이 없다면 삭제
        if not any(entries):
            os.rmdir(path)
            print(f"폴더 '{path}'가 비어 있어 삭제되었습니다.")




if __name__ == "__main__":
    df_path = "/home/ubuntu/drive/EDA/merged_growth_real_final.csv"
    run_filtering_image(df_path)
    # back()

    # 시작 경로를 지정
    # base_folder = ["/home/ubuntu/drive/dataset/SAM_result/F0016_filtering", "/home/ubuntu/drive/dataset/SAM_result/F0017_filtering"]

    # for start_path in base_folder:
    #     # 재귀적으로 비어있는 폴더 삭제
    #     remove_empty_folders(start_path)