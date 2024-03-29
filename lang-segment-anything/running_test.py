# '''
#     This is just adapted from the example in the readme,
#     The main usage is for the built image to have the weights cached.
# '''

# from PIL import Image
# from lang_sam import LangSAM

# model = LangSAM()
# image_pil = Image.open("/home/sunghoon/sj/sam/lang-segment-anything/1.jpg").convert("RGB")
# text_prompt = "strawberry"
# masks, boxes, phrases, logits = model.predict(image_pil, text_prompt)

# print('all ok')

# # 바운딩 박스 그리는 버전
# from PIL import Image, ImageDraw
# from lang_sam import LangSAM

# # 모델 초기화
# model = LangSAM()

# # 이미지 열기
# image_pil = Image.open("/home/sunghoon/sj/sam/lang-segment-anything/6.jpg").convert("RGB")

# # 텍스트 프롬프트 정의
# text_prompt = "strawberry"

# # 모델로 이미지 분석 수행
# masks, boxes, phrases, logits = model.predict(image_pil, text_prompt)

# # 이미지에 결과를 그리기 위해 복사
# draw = ImageDraw.Draw(image_pil)

# # 결과를 이미지에 그리기
# for mask, box, phrase, logit in zip(masks, boxes, phrases, logits):
#     draw.rectangle(box.tolist(), outline="red")
#     draw.text((box[0], box[1]), f"{phrase} ({logit:.2f})", fill="red")

# # 결과가 적용된 이미지 저장
# image_pil.save("/home/sunghoon/sj/sam/lang-segment-anything/result_image6.jpg")

# print('all ok')

# from PIL import Image, ImageDraw
# import numpy as np
# import torch
# from lang_sam import LangSAM

# # 모델 초기화
# model = LangSAM()

# # 이미지 열기
# image_pil = Image.open("/home/sunghoon/sj/sam/lang-segment-anything/6.jpg").convert("RGB")

# # 텍스트 프롬프트 정의
# text_prompt = "strawberry"

# # 모델로 이미지 분석 수행
# masks, boxes, phrases, logits = model.predict(image_pil, text_prompt)

# # 결과를 표시할 색상 선택
# colors = ["red", "green", "blue", "yellow", "orange", "purple", "pink", "cyan", "magenta"]

# # 이미지에 결과를 그리기 위해 복사
# draw = ImageDraw.Draw(image_pil)

# # 마스크를 사용하여 이미지에 결과를 그리기
# for mask, phrase, logit, color in zip(masks, phrases, logits, colors):
#     # 마스크를 numpy 배열로 변환
#     mask_np = mask.cpu().numpy()
#     # 마스크를 PIL 이미지로 변환
#     mask_pil = Image.fromarray((mask_np * 255).astype(np.uint8)).convert("L")
#     # 마스크를 사용하여 원본 이미지를 색상으로 채우기
#     image_pil.paste(color, (0, 0), mask_pil)
#     # 텍스트 및 확률 표시
#     draw.text((0, 0), f"{phrase} ({logit:.2f})", fill=color)

# # 결과가 적용된 이미지 저장
# image_pil.save("/home/sunghoon/sj/sam/lang-segment-anything/result_image_mask6.jpg")

# print('all ok')

from PIL import Image, ImageDraw
import numpy as np
from lang_sam import LangSAM

# 모델 초기화
model = LangSAM()

# 이미지 열기
image_pil = Image.open("/home/sunghoon/sj/sam/lang-segment-anything/7_aa.jpg").convert("RGB")

# 텍스트 프롬프트 정의
text_prompt = "strawberry"

# 모델로 이미지 분석 수행
masks, boxes, phrases, logits = model.predict(image_pil, text_prompt)

# 딸기 색상 정의
strawberry_color = (255, 192, 203)  # 연한 핑크색 (RGB)

# 이미지에 딸기 영역을 연한 핑크색으로 채우기
draw = ImageDraw.Draw(image_pil)
for mask, phrase, logit in zip(masks, phrases, logits):
    if "strawberry" in phrase.lower():
        # 마스크를 numpy 배열로 변환
        mask_np = mask.cpu().numpy()
        # 마스크를 PIL 이미지로 변환
        mask_pil = Image.fromarray((mask_np * 255).astype(np.uint8)).convert("L")
        # 딸기 영역에 대해 연한 핑크색으로 채우기
        image_pil.paste(strawberry_color, (0, 0), mask_pil)

# 결과가 적용된 이미지 저장
image_pil.save("/home/sunghoon/sj/sam/lang-segment-anything/result_image_mask7_aa.jpg")

print('all ok')
