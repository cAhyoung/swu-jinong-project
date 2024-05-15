#from google.colab.patches import cv2_imshow
import cv2
import numpy as np
import os

from PIL import Image
import datetime

def adjust_brightness(image):
    brightness = np.mean(image)
    print(brightness)

    if brightness >= 130:
        brightened_image = image
        brightness_status = "원본 이미지 유지"
    else:
        brightness_factor = 130 / brightness
        brightened_image = np.clip(image.astype(np.float32) * brightness_factor, 0, 255).astype(np.uint8)
        brightness_status = "밝기 조정"

    return brightened_image, brightness_status, brightness

# def bright_up(image_path, filename, output_dir):
#     image = cv2.imread(image_path)

#     # 이미지 밝기 조정
#     brightened_image, brightness_status, brightness_value = adjust_brightness(image)

#     # 결과 출력
#     print(f"이미지 파일: {filename}")
#     print(f"원본 이미지의 밝기: {brightness_value:.2f}")
#     print(f"밝기 조정 여부: {brightness_status}\n\n")

#     # 원본 이미지와 조정된 이미지를 양옆으로 출력
#     # combined_image = np.concatenate((image, brightened_image), axis=1)
#     #cv2_imshow(combined_image)
    
#     os.makedirs(output_dir, exist_ok=True)
#     # 밝기가 조정된 이미지 저장
#     output_filename = os.path.splitext(filename)[0] + ".jpg"
#     output_path = os.path.join(output_dir, output_filename)
#     cv2.imwrite(output_path, brightened_image)
#     print(f"밝기가 조정된 이미지 저장 완료: {output_path}\n\n")

def bright_up(image_path, filename, output_dir):
    image = cv2.imread(image_path)

    # 이미지 밝기 조정
    brightened_image, brightness_status, brightness_value = adjust_brightness(image)

    # 결과 출력
    print(f"이미지 파일: {filename}")
    print(f"원본 이미지의 밝기: {brightness_value:.2f}")
    print(f"밝기 조정 여부: {brightness_status}\n\n")

    os.makedirs(output_dir, exist_ok=True)
    # 밝기가 조정된 이미지 저장
    output_filename = os.path.splitext(filename)[0] + ".jpg"
    output_path = os.path.join(output_dir, output_filename)
    cv2.imwrite(output_path, brightened_image)
    print(f"밝기가 조정된 이미지 저장 완료: {output_path}\n\n")

from collections import defaultdict
import shutil

# hour unique하게 뽑는 함수
"""
순회하면서 저장한 파일 중 바로 직전 파일이 같은 시간이면 (이름 슬라이싱해서 비교) continue하면 되는 것 아닌가?
순회하면서 이전 파일명과 같은 시간이면 continue
아니면 복사해 저장
"""
def drop_duplicate(input_dir="./plant/", output_dir="./unique_plant/"):
    for directory in os.listdir(input_dir):
        print(f"directory is <{directory}>.")
        directory_path = os.path.join(input_dir, directory)

        for subdirectory in os.listdir(directory_path) :
            print(f"subdirectory is <{subdirectory}>.")
            subdirectory_path = os.path.join(directory_path, subdirectory)
            
            if os.path.isdir(subdirectory_path):
                # 파일명 정렬
                file_names = sorted(os.listdir(subdirectory_path))
                # 이전 파일 저장
                prev_file_name = file_names[0]

                farm_code = directory
                area_code = subdirectory
                
                image_dir = input_dir + farm_code + "/" + area_code + "/"
                save_dir = output_dir + farm_code + "/" + area_code + "/"
                
                # 첫 번째 파일 저장
                image_path = os.path.join(subdirectory_path, prev_file_name)
                if os.path.isfile(image_path) and prev_file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                    shutil.copyfile(image_dir + prev_file_name, save_dir + prev_file_name)

                for file_name in file_names[1:]:
                    image_path = os.path.join(subdirectory_path, file_name)
                    print(f"file name is <{file_name}>.")

                    if os.path.isfile(image_path) and file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                        # 중복되는 파일이 아니면 파일 복사
                        # (두 파일의 농가 코드, 카메라 코드, 일자, 시간이 같은지)
                        if prev_file_name[:-8] != file_name[:-8]:
                            # 복사해 저장
                            shutil.copyfile(image_dir + file_name, save_dir + file_name)
                        else:
                            print(f"duplicate {prev_file_name} / {file_name}")
                        prev_file_name = file_name

# file_name에서 시간대만 추출
def get_hour(file_name):
	return file_name[-10:-8]
def parse_image_name(image_name):
    parts = image_name.split('-')
    farm_code, area_code = parts[0], parts[1]
    datetime_str = parts[2] 
    return farm_code, area_code, datetime_str

def main(input_dir="./plant/", output_dir="./result/"):
    saved_images = defaultdict(list)  # 이미지를 저장하는 딕셔너리

    save_case = ["08", "12", "16"]
    prev_case = {"07":"08", "11":"12", "15":"16"}
    next_case = {"09":"08", "13":"12", "17":"16"}
    
    os.makedirs(output_dir, exist_ok=True)
    # 입력 폴더 안에 있는 모든 이미지 파일에 대해 처리
    for directory in os.listdir(input_dir): 
        print(f"directory is <{directory}>.")
        directory_path = os.path.join(input_dir, directory)
        os.makedirs(directory_path, exist_ok=True)
        for subdirectory in os.listdir(directory_path):
            print(f"subdirectory is <{subdirectory}>.")
            subdirectory_path = os.path.join(directory_path, subdirectory)
            if os.path.isdir(subdirectory_path):
                file_names = sorted(os.listdir(subdirectory_path))
                os.makedirs(directory_path, exist_ok=True)
                for idx, file_name in enumerate(file_names):
                    print()
                    print(f"file name is <{file_name}>.")

                    image_path = os.path.join(subdirectory_path, file_name)
                    farm_code = directory
                    area_code = subdirectory

                    hour = get_hour(file_name)
                    image_path = input_dir + farm_code + "/" + area_code + "/" + file_name
                    save_dir = output_dir + farm_code + "/" + area_code + "/"
                    print(image_path)
                    print(save_dir)
                    # 이미지 파일인지 확인
                    if os.path.isfile(image_path) and file_name.endswith(('.png', '.jpg', '.jpeg')):
                        print("is file", hour)
                        # 저장해야하는 경우
                        if hour in save_case:
                            farm_code, area_code, datetime_str = parse_image_name(file_name)
                            if hour in saved_images[f"{farm_code}-{area_code}-{datetime_str}"]:
                                continue
                            else:
                                bright_up(image_path, file_name, save_dir)
                                saved_images[f"{farm_code}-{area_code}-{datetime_str}"].append(hour)  # 이미지 저장 기록 업데이트

                        # prev인 경우, 대체해야하는 시간대가 없는 경우
                        elif hour in prev_case \
                            and get_hour(file_names[idx+1]) != prev_case[hour]:

                            farm_code, area_code, datetime_str = parse_image_name(file_name)
                            if prev_case[hour] in saved_images[f"{farm_code}-{area_code}-{datetime_str}"]:
                                continue
                            else:
                                bright_up(image_path, file_name, save_dir)
                                saved_images[f"{farm_code}-{area_code}-{datetime_str}"].append(prev_case[hour]) # 이미지 저장 기록 업데이트
                                
                        # next인 경우, 대체해야하는 시간대와 그 전 시간대(대체 시간대)가 없는 경우
                        elif hour in next_case \
                            and get_hour(file_names[idx-1]) not in next_case[hour] \
                            and get_hour(file_names[idx-2]) not in next_case[hour]:

                            farm_code, area_code, datetime_str = parse_image_name(file_name)
                            if next_case[hour] in saved_images[f"{farm_code}-{area_code}-{datetime_str}"]:
                                continue
                            else:
                                bright_up(image_path, file_name, save_dir)
                                saved_images[f"{farm_code}-{area_code}-{datetime_str}"].append(next_case[hour])  # 이미지 저장 기록 업데이트
                    else:
                        print(file_name)
                        print(hour)

# drop_duplicate()
main()
