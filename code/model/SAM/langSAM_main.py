# 최종
import warnings
import numpy as np
import matplotlib.pyplot as plt
from lang_sam.lang_sam import LangSAM
from PIL import Image
from PIL import ImageFile

import hashlib
import os
import json
import datetime
import pandas as pd
import re
ImageFile.LOAD_TRUNCATED_IMAGES = True

# 이전 이미지의 mask 정보 리스트
previous_masks_info = []

# 이미지 데이터 폴더 경로와 결과 저장 폴더
data_folder = "/home/ubuntu/drive/dataset/result"
# result_folder = "/home/ubuntu/drive/dataset/SAM_result"
result_folder = "/opt/dlami/nvme/SAM_result"
text_prompt = "strawberry"

# 기존 mask 정보 파일
previous_mask_info_file = os.path.join(result_folder, 'previous_mask_info.json')

# 이전에 저장된 mask 정보 불러오기
if os.path.exists(previous_mask_info_file):
    with open(previous_mask_info_file, 'r') as f:
        previous_masks_info = json.load(f)

# 사진 촬영 날짜 추출 함수
def extract_datetime_from_image_name(image_name):
    parts = image_name.split('-')
    datetime_str = parts[2] + parts[3].split('.')[0]
    shot_datetime = datetime.datetime.strptime(datetime_str, "%Y%m%d%H%M%S")
    return shot_datetime

# 데이터 날짜 순서대로 들어갈 수 있도록 sorting하는 함수
def sort_images_by_datetime(image_paths):
    return sorted(image_paths, key=lambda x: extract_datetime_from_image_name(os.path.basename(x)))


# 데이터 폴더 구조를 순회하며 이미지 파일 경로 반환
def get_image_paths(data_folder):
    image_paths = []
    for farm_code in sorted(os.listdir(data_folder)):
        farm_folder_path = os.path.join(data_folder, farm_code)
        if os.path.isdir(farm_folder_path):
            for area_code in sorted(os.listdir(farm_folder_path)):
                area_folder_path = os.path.join(farm_folder_path, area_code)
                if os.path.isdir(area_folder_path):
                    for file in sort_images_by_datetime(os.listdir(area_folder_path)):
                        if file.endswith(".jpg") or file.endswith(".png"):
                            image_paths.append(os.path.join(area_folder_path, file))
    return image_paths

# 이미지 고유 번호 생성
def generate_image_hash(image_path):
    with open(image_path, "rb") as f:
        image_hash = hashlib.md5(f.read()).hexdigest()
    return image_hash

# 마스크 고유 번호 생성
def generate_mask_hash(mask_np):
    # 마스크 데이터를 이진 형태로 변환하여 이를 해시화
    mask_hash = hashlib.md5(mask_np.cpu().numpy().tobytes()).hexdigest()
    return mask_hash

# 이미지 사이즈 출력 함수
def get_image_size(image_path):
    with Image.open(image_path) as img:
        width, height = img.size
    return width, height

# 이미지 이름 분석
def parse_image_name(image_name):
    parts = image_name.split('-')
    farm_code, area_code = parts[0], parts[1]
    datetime_str = parts[2] + parts[3].split('.')[0]
    shot_datetime = datetime.datetime.strptime(datetime_str, "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
    return farm_code, area_code, shot_datetime

def extract_non_transparent_pixels(image_path):
    # 이미지 열기
    img = Image.open(image_path)
    
    # 이미지의 너비와 높이 구하기
    width, height = img.size
    
    # 모든 픽셀의 RGB 값을 저장할 리스트
    rgb_pixels = []
    
    # 모든 픽셀에 대해 반복하여 RGB 값을 추출
    for y in range(height):
        for x in range(width):
            # 해당 픽셀의 RGBA 값을 추출
            rgba = img.getpixel((x, y))
            # 투명한 픽셀인지 확인 (알파 값이 0인지)
            if rgba[3] != 0:
                # 투명하지 않은 경우 RGB 값을 추출하여 리스트에 추가
                rgb_pixels.append(rgba[:3])
    
    return rgb_pixels

# def calculate_average_rgb(rgb_pixels):
#     # R, G, B 값의 합을 초기화
#     sum_r = sum_g = sum_b = 0

#     # 모든 픽셀에 대해 R, G, B 값을 더함
#     for r, g, b in rgb_pixels:
#         sum_r += r
#         sum_g += g
#         sum_b += b

#     # R, G, B 값의 평균 계산
#     avg_r = sum_r / len(rgb_pixels)
#     avg_g = sum_g / len(rgb_pixels)
#     avg_b = sum_b / len(rgb_pixels)

#     return avg_r, avg_g, avg_b

# 마스크 별 이미지 저장 코드
def save_mask_with_folder(image_path, mask_np, mask_folder, i):
    original_image = Image.open(image_path).convert("RGBA")
    mask_rgba = np.zeros((*mask_np.shape, 4), dtype=np.uint8)
    mask_rgba[..., 3] = (mask_np * 255).astype(np.uint8)  # 마스크의 투명도 채널을 설정합니다.

    # 바운딩 박스를 계산합니다.
    y_nonzero, x_nonzero = np.nonzero(mask_np)
    if len(x_nonzero) == 0 or len(y_nonzero) == 0:  # 마스크가 전혀 없으면 저장하지 않습니다.
        return None
    x_min, x_max = x_nonzero.min(), x_nonzero.max()
    y_min, y_max = y_nonzero.min(), y_nonzero.max()

    # 마스크가 적용된 부분만 크롭합니다.
    cropped_image = original_image.crop((x_min, y_min, x_max + 1, y_max + 1))
    cropped_mask = mask_rgba[y_min:y_max + 1, x_min:x_max + 1]

    # 새로운 투명한 이미지를 생성하고 마스크된 이미지를 적용합니다.
    result_image = Image.new('RGBA', cropped_image.size)
    cropped_mask_image = Image.fromarray(cropped_mask, 'RGBA')
    result_image.paste(cropped_image, (0, 0), mask=cropped_mask_image)

    # 결과 이미지를 저장합니다.
    if not os.path.exists(mask_folder):
        os.makedirs(mask_folder)
    mask_path = os.path.join(mask_folder, f"image_mask_{i + 1}.png")
    result_image.save(mask_path)

    ## 수정해야하는 부분
    rgb_pixels = extract_non_transparent_pixels(mask_path)
    # avg_r, avg_g, avg_b = calculate_average_rgb(rgb_pixels)
    return rgb_pixels

# 바운딩 박스 그려진 이미지 저장 코드
# def save_image_with_boxes(image, boxes, logits, image_name, output_path):
#     fig, ax = plt.subplots()
#     ax.imshow(image)
#     ax.set_title(f"Image: {image_name}")  # 이미지 이름으로 제목 설정
#     ax.axis('off')

#     for box, logit in zip(boxes, logits):
#         x_min, y_min, x_max, y_max = box
#         # confidence_score = round(logit.item(), 2)
#         box_width = x_max - x_min
#         box_height = y_max - y_min

#         rect = plt.Rectangle((x_min, y_min), box_width, box_height, fill=False, edgecolor='red', linewidth=2)
#         ax.add_patch(rect)

#         # ax.text(x_min, y_min, f"Confidence: {confidence_score}", fontsize=8, color='red', verticalalignment='top')

#     plt.savefig(output_path)
#     plt.close()

def save_image_with_boxes(image, boxes, logits, image_name, output_path):
    dpi = 100  # 원하는 DPI 값
    figsize = (2560 / dpi, 1440 / dpi)  # 이미지의 픽셀 크기를 DPI로 나누어 figsize 계산
    
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    ax.imshow(image)
    ax.axis('off')  # 축과 라벨을 끕니다.

    for box, logit in zip(boxes, logits):
        x_min, y_min, x_max, y_max = box
        box_width = x_max - x_min
        box_height = y_max - y_min

        rect = plt.Rectangle((x_min, y_min), box_width, box_height, fill=False, edgecolor='red', linewidth=2)
        ax.add_patch(rect)

    plt.savefig(output_path, bbox_inches='tight', pad_inches=0)
    plt.close()

# 마스크 정보 저장 함수
mapping_point = []

def save_mask_info(mask_folder, image_name, masks, boxes, logits, color):
    masks_info = []

    threshold_x = 10  # 임계값 설정
    threshold_y = 10  # 임계값 설정

    # 동일한 딸기인지 맵핑하는 코드
    if not mapping_point:
        for i, (mask_np, box, logit) in enumerate(zip(masks, boxes, logits)):
            x_min, y_min, x_max, y_max = box
            center_x = (x_min + x_max) / 2
            center_y = (y_min + y_max) / 2
            mask_id = generate_mask_hash(mask_np)
            point = [float(center_x), float(center_y)]

            mask = np.argwhere(mask_np).tolist()
            # print(len(mask[0]))

            masks_info.append({
                "mask_num": f"{image_name}_{i+1}",
                "mask_id": mask_id,
                "size": len(mask[0]),  # 마스크의 픽셀 수 추가
                "box": box.tolist(),
                "point": point,
                "mask": mask,
                "confidence": logit.item(),
                "color": color[i],
                "output_image_path": f"image_mask_{i+1}.png"
            })

            mapping_point.append({'masks_id': mask_id, 'point_x': float(center_x), 'point_y': float(center_y)})
            # print("if-mapping", mapping_point)
    else:
        for i, (mask_np, box, logit) in enumerate(zip(masks, boxes, logits)):
            x_min, y_min, x_max, y_max = box
            center_x = (x_min + x_max) / 2
            center_y = (y_min + y_max) / 2
            mask_id_2 = generate_mask_hash(mask_np)
            point_2 = [float(center_x), float(center_y)]

            mask = np.argwhere(mask_np).tolist()
            # print(len(mask[0]))

            for point in mapping_point:
                # 이전 마스크 포인트와 비교
                if (abs(point['point_x'] - float(center_x)) < threshold_x) and (
                        abs(point['point_y'] - float(center_y)) < threshold_y):
                    mask_id_2 = point['masks_id']
                    point['point_x'] = float(center_x)
                    point['point_y'] = float(center_y)
                    break
                elif mapping_point[-1] == point:
                    mapping_point.append(
                        {'masks_id': mask_id_2, 'point_x': float(center_x), 'point_y': float(center_y)})

            masks_info.append({
                "mask_num": f"{image_name}_{i+1}",
                "mask_id": mask_id_2,
                "size": len(mask[0]),  # 마스크의 픽셀 수 추가
                "box": box.tolist(),
                "point": point_2,
                "mask": np.argwhere(mask_np).tolist(),
                "confidence": logit.item(),
                "color": color[i],
                "output_image_path": f"image_mask_{i+1}.png"
            })
        # print("else-mapping", mapping_point)

    # mask_info.json 파일에 저장
    mask_info_path = os.path.join(mask_folder, 'mask_info.json')
    with open(mask_info_path, 'w') as json_file:
        json.dump(masks_info, json_file, indent=4)

    return masks_info

def save_image_with_boxes_and_masks(image_path, image_name, masks, boxes, logits, result_folder,
                                    previous_image_name=None, previous_image_hash=None):
    farm_code, area_code, shot_datetime = parse_image_name(image_name)
    image_folder = os.path.join(result_folder, farm_code, area_code, image_name)
    bbox_folder = os.path.join(image_folder, "bbox")
    mask_folder = os.path.join(image_folder, "masks")

    os.makedirs(image_folder, exist_ok=True)
    os.makedirs(bbox_folder, exist_ok=True)
    os.makedirs(mask_folder, exist_ok=True)

    # 바운딩 박스 이미지 저장
    bbox_image_path = os.path.join(bbox_folder, f"{image_name}.png")
    image = Image.open(image_path).convert("RGB")
    save_image_with_boxes(image, boxes, logits, image_name, bbox_image_path)

    # mask 정보 저장
    masks_np = [mask.squeeze().cpu().numpy() for mask in masks]
    
    color = []
    # mask 이미지 저장
    for i, mask_np in enumerate(masks_np):
        color.append(save_mask_with_folder(image_path, mask_np, mask_folder, i))

    save_mask_info(mask_folder, image_name, masks, boxes, logits, color)

    json_data = {
        "input_image_name": image_name,
        "input_image_path": image_path,
        "img_id": generate_image_hash(image_path),
        "farm_code": farm_code,
        "area_code": area_code,
        "shot_datetime": shot_datetime,
        "count_masks": len(masks),
        "bbox_image_path": bbox_image_path,
    }

    # 이전 이미지 정보가 있으면 추가
    if previous_image_name and previous_image_hash:
        json_data["before_img_name"] = previous_image_name
        json_data["before_img_id"] = previous_image_hash

    image_info_path = os.path.join(image_folder, 'image_info.json')
    with open(image_info_path, 'w') as json_file:
        json.dump(json_data, json_file, indent=4)

    # mask_info.json 파일 이동
    mask_info_path = os.path.join(mask_folder, 'mask_info.json')
    os.rename(mask_info_path, os.path.join(mask_folder, 'mask_info.json'))

# input이 [(r,g,b), (),,...] 일 때 rgb 값 count 후 비율 추출
def calculate_rgb_ratio(rgb_data):
    """
    parameter: 픽셀별 rgb 값 (2차원)
    return: [r 비율, g 비율, b 비율]
    """

    # 픽셀별 색상 카운트를 저장할 리스트 초기화 (r, g, b)
    color_counts = [[0] * 256, [0] * 256, [0] * 256]

    # 각 픽셀별로 색상 카운트 수행
    for r, g, b in rgb_data:
        # 각 색상별로 카운트 증가
        color_counts[0][r] += 1
        color_counts[1][g] += 1
        color_counts[2][b] += 1
    
    # 색상값 * count 값
    color_sum = []
    for counts in color_counts:
        num = 0
        # 5 ~ 250 사이의 값만 합산
        for idx, value in enumerate(counts[5:-5]):
            num += idx * value
        color_sum.append(num)
    
    # r, g, b 비율 구하기
    total = sum(color_sum)
    result = [value/total for value in color_sum]

    return result

def main():
    warnings.filterwarnings("ignore")
    os.makedirs(result_folder, exist_ok=True)
    image_paths = get_image_paths(data_folder)

    previous_image_name = None
    previous_image_hash = None

    for image_path in image_paths:
        image_path2 = image_path.replace('result', 'plant')
        image_name = os.path.basename(image_path)
        image_name = os.path.splitext(image_name)[0]
        # try:
        image_pil = Image.open(image_path).convert("RGB")
        image_pil2 = Image.open(image_path2).convert("RGB")
        # 이미지 고유 번호 생성
        Image_num = generate_image_hash(image_path)

        # LangSAM 모델을 돌려, 예측한 값
        model = LangSAM()
        masks, boxes, phrases, logits = model.predict(image_pil, image_pil2, image_path, text_prompt)

        # 결과 저장
        save_image_with_boxes_and_masks(image_path2, image_name, masks, boxes, logits, result_folder,
                                        previous_image_name, previous_image_hash)


        # 현재 이미지 정보를 "이전"으로 업데이트(바로 전에 돌아간 사진의 이미지 이름과 고유번호를 저장하기 위함)
        previous_image_name = image_name
        previous_image_hash = generate_image_hash(image_path2)

        # except Exception as e:
        #     missing_bboxes.append(image_name)
        #     print(f"Error processing {image_name}: {e}")

if __name__ == "__main__":
    main()