from adjust_image import adjust_brightness, adjust_contrast
import numpy as np
import pandas as pd
import cv2


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
        for idx, value in enumerate(counts[1:-1]):
            num += idx * value
        color_sum.append(num)
    
    # r, g, b 비율 구하기
    total = sum(color_sum)
    result = [value/total for value in color_sum]

    return result

import os
import pandas as pd

def main(result_dir = './result/'):
    for directory in os.listdir(result_dir): 
        # farm_code (F0016)
        if directory in ["F0016", "F0017"]:
            print(f"directory is <{directory}>.")
            directory_path = os.path.join(result_dir, directory)
            for subdirectory in os.listdir(directory_path):
                # area_code (C101)
                print(f"subdirectory is <{subdirectory}>.")
                subdirectory_path = os.path.join(directory_path, subdirectory)
                for imagedirectory in sorted(os.listdir(subdirectory_path)):
                    # image id (F0016-C101-20220202-084500)
                    print(f"imagedirectory is <{imagedirectory}>.")
                    # masks 폴더
                    masks_path = os.path.join(subdirectory_path, imagedirectory, "masks/")
                    ## mask info json 파일 불러오기 (나중에)
                    result_data = []
                    for file_name in os.listdir(masks_path):
                        file_path = os.path.join(masks_path, file_name)
                        # 이미지 파일인가?
                        if os.path.isfile(file_path) and file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                            # print(f"file name is <{file_name}>.")
                            '''
                                imagedirectory, file_name, 
                                origin_r, origin_g, origin_b,
                                bright_r, bright_g, bright_b,
                                contrast_r, contrast_g, contrast_b
                            '''
                            
                            row = [imagedirectory, file_name]
                            # origin, bright, contrast 각각 이미지 불러와 픽셀별 rgb 값 추출
                            original_rgb = extract_non_transparent_pixels_cv(cv2.imread(file_path, cv2.IMREAD_UNCHANGED))
                            # bright_rgb = extract_non_transparent_pixels_cv(adjust_brightness(file_path, 130))
                            # contrast_rgb = extract_non_transparent_pixels_cv(adjust_contrast(file_path, 1.5))
                            
                            # 픽셀별 rgb 값 기반으로 rgb 비율 추출
                            original_rgb_ratio = calculate_rgb_ratio(original_rgb)
                            # bright_rgb_ratio = calculate_rgb_ratio(bright_rgb)
                            # contrast_rgb_ratio = calculate_rgb_ratio(contrast_rgb)
                            
                            # 한 행으로 합치기
                            row.extend(original_rgb_ratio)
                            # row.extend(bright_rgb_ratio)
                            # row.extend(contrast_rgb_ratio)

                            result_data.append(row)
                        
                        # dataframe으로 
                        result_df = pd.DataFrame(result_data, columns=["imagedirectory", "file_name", 
                                                        "origin_r", "origin_g", "origin_b"])

                        # result_df = pd.DataFrame(result_data, columns=["imagedirectory", "file_name", 
                        #                                 "origin_r", "origin_g", "origin_b",
                        #                                 "bright_r", "bright_g", "bright_b",
                        #                                 "contrast_r", "contrast_g", "contrast_b"])

                        # csv로 저장
                        mask_rgb_info_path = os.path.join(masks_path, "mask_rgb_info.csv")
                        result_df.to_csv(mask_rgb_info_path, index=False)
                        
            print()

                
if __name__ == "__main__":
    main('../dataset/SAM_result/')