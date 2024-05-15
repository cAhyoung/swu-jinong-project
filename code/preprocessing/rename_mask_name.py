import os
import re

# 정규식 패턴 설정
pattern = re.compile(r'(\d+)(?=\.\w+$)')

# 이미지 파일이 있는 폴더 경로
folder_path = "/home/ubuntu/drive/dataset/test"

# 폴더 내의 모든 파일 및 폴더 목록 얻기
contents = os.listdir(folder_path)

# output_image_path 전처리
for content in contents:
    # 해당 경로가 디렉토리인지 확인
    if os.path.isdir(os.path.join(folder_path, content)):
        # 'masks' 폴더인 경우
        if content == 'masks':
            masks_folder_path = os.path.join(folder_path, content)
            # masks 폴더 내의 파일 목록 얻기
            mask_files = os.listdir(masks_folder_path)
            for mask_file in mask_files:
                # 숫자를 추출하여 1을 더하기
                match = re.search(pattern, mask_file)
                if match:
                    number = int(match.group()) + 1
                    # 새로운 파일 이름 생성
                    new_file_name = re.sub(pattern, str(number), mask_file)
                    # 파일 이름 변경
                    os.rename(os.path.join(masks_folder_path, mask_file), os.path.join(masks_folder_path, new_file_name))
        # 'image' 폴더인 경우
        elif content == 'image':
            image_folder_path = os.path.join(folder_path, content)
            # image 폴더 내의 파일 목록 얻기
            image_files = os.listdir(image_folder_path)
            for image_file in image_files:
                # 숫자를 추출하여 1을 더하기
                match = re.search(pattern, image_file)
                if match:
                    number = int(match.group()) + 1
                    # 새로운 파일 이름 생성
                    new_file_name = re.sub(pattern, str(number), image_file)
                    # 파일 이름 변경
                    os.rename(os.path.join(image_folder_path, image_file), os.path.join(image_folder_path, new_file_name))
