# 폴더명 directory는 target
import os
import pandas as pd
import cv2
import numpy as np

## 밝기 조절
def adjust_brightness(path, bright):
    # 각 이미지에 대해 처리하고 결과를 출력 및 저장
    input_image = cv2.imread(path)

    # 이미지의 밝기 계산
    brightness = np.mean(input_image)

    # 이미지의 밝기가 140 이상인 경우
    if brightness >= bright:
        brightened_image = input_image
    # 이미지의 밝기가 140 미만인 경우
    else:
        # 이미지의 밝기를 140으로 맞춰줌
        brightness_factor = bright / brightness
        brightened_image = np.clip(input_image.astype(np.float32) * brightness_factor, 0, 255).astype(np.uint8)

    return brightened_image


## 대비 조절
def adjust_contrast(path, contrast_factor=1.5):
    # 이미지 로드
    input_image = cv2.imread(path)

    # 이미지 조정
    output_image = cv2.convertScaleAbs(input_image, alpha=contrast_factor)

    return output_image

def extract_non_transparent_pixels_cv(img):
    # 이미지의 높이, 너비, 채널 수 구하기
    height, width, _ = img.shape
    
    # 모든 픽셀의 RGB 값을 저장할 리스트
    rgb_pixels = []
    
    # 모든 픽셀에 대해 반복하여 RGB 값을 추출
    for y in range(height):
        for x in range(width):
            # 해당 픽셀의 BGR 값을 추출
            bgr = img[y, x]
            # 투명한 픽셀인지 확인 (알파 값이 0인지)
            if len(bgr) == 3 or (len(bgr) == 4 and bgr[3] != 0):
                # 투명하지 않은 경우 BGR 값을 추출하여 리스트에 추가
                rgb_pixels.append(bgr[:3][::-1])
    
    # 2차원 배열로 변환하여 반환
    return np.array(rgb_pixels)



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
        for idx, value in enumerate(counts[10:-10]):
            num += idx * value
        color_sum.append(num)
    
    # r, g, b 비율 구하기
    total = sum(color_sum)
    print(total)
    result = [value/total for value in color_sum]

    return result

def main():

    result_data = []

    for directory in os.listdir('./'):
        print(f"directory is <{directory}>.")
        directory_path = os.path.join('./', directory)
        if os.path.isdir(directory_path):
            for file_name in os.listdir(directory_path):
                print(f"file name is <{file_name}>.")
                file_path = os.path.join(directory_path, file_name)
                # 이미지 파일인가?
                if os.path.isfile(file_path) and file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                    '''
                        target, file_name, 
                        origin_r, origin_g, origin_b,
                        bright_r, bright_g, bright_b,
                        contrast_r, contrast_g, contrast_b
                    '''
                    print(file_path)
                    row = [directory, file_name]
                    # origin, bright, contrast 각각 이미지 불러와 픽셀별 rgb 값 추출
                    original_rgb = extract_non_transparent_pixels_cv(cv2.imread(file_path, cv2.IMREAD_UNCHANGED))
                    bright_rgb = extract_non_transparent_pixels_cv(adjust_brightness(file_path, 130))
                    contrast_rgb = extract_non_transparent_pixels_cv(adjust_contrast(file_path, 1.5))
                    
                    # 픽셀별 rgb 값 기반으로 rgb 비율 추출
                    original_rgb_ratio = calculate_rgb_ratio(original_rgb)
                    bright_rgb_ratio = calculate_rgb_ratio(bright_rgb)
                    contrast_rgb_ratio = calculate_rgb_ratio(contrast_rgb)
                    
                    # 한 행으로 합치기
                    row.extend(original_rgb_ratio)
                    row.extend(bright_rgb_ratio)
                    row.extend(contrast_rgb_ratio)

                    result_data.append(row)
                
    # dataframe으로 만들기
    result_df = pd.DataFrame(result_data, columns=["target", "file_name", 
                                                "origin_r", "origin_g", "origin_b",
                                                "bright_r", "bright_g", "bright_b",
                                                "contrast_r", "contrast_g", "contrast_b"])

    # csv로 저장
    mask_rgb_info_path = os.path.join(".", "mask_rgb_info3.csv")
    result_df.to_csv(mask_rgb_info_path, index=False)

if __name__ == "__main__":
    main()