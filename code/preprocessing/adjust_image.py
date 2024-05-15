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