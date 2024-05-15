from PIL import Image
import os
import torch
from groundingdino.util import box_ops

class ImageProcessor:
  def __init__(self, image_path):
    self.image_path = image_path
    # self.img_path = image_pil
    # self.output_path = output_path

  def img_split(self):
    """
      parameter : 
          1) img_path : 이미지가 속해있는 경로
          2) out_path : 분할 후 이미지를 저장할 경로
    """
    split_image = []
    # 이미지 열기
    # image = Image.open(self.img_path)
    image = Image.open(self.image_path)
      
      # 이미지 크기 확인
    width, height = image.size
      
      # 8분할된 이미지 크기 계산
    split_width = width // 4
    split_height = height // 2
      
    #   # 결과를 저장할 폴더 생성
    # if not os.path.exists(self.output_path):
    #     os.makedirs(self.output_path)
      
      # 이미지를 8등분하여 개별적으로 저장
    for i in range(2):
        for j in range(4):
              # 각 부분의 영역 계산
            left = j * split_width
            top = i * split_height
            right = (j + 1) * split_width
            bottom = (i + 1) * split_height
              
              # 부분 이미지 추출
            split_image.append(image.crop((left, top, right, bottom)))
              
            ## 저장할 파일명 생성
            # output_path = os.path.join(self.output_path, f"{i*4+j}.jpg")
              
            #   # 부분 이미지 저장
            # split_image.save(output_path)
            # print(f"{i*4+j}번째 이미지가 저장되었습니다.")
    return split_image

  def img_concat(self, split_image, all_boxes, all_logits,all_phrases):

    adjusted_boxes=[]
    # 이미지를 열어서 리스트에 저장
    # images = [Image.open(path) for path in split_image]
    images = split_image

    # 이미지 크기 확인
    image_width, image_height = images[0].size

    # # 결과 이미지 크기 계산 (가로 * 세로)
    # result_width = image_width * 4
    # result_height = image_height * 2

    # 새로운 이미지 생성
    # result_image = Image.new("RGB", (result_width, result_height))

    # 이미지를 2x4 그리드에 합치기
   # 새로운 바운딩 박스 목록을 저장할 리스트
    new_boxes = []

    # 이미지는 4x2 그리드로 정렬되어 있다.
    for idx, boxes in enumerate(all_boxes):
        
        W, H = split_image[0].size
        boxes = box_ops.box_cxcywh_to_xyxy(boxes) * torch.Tensor([W, H, W, H])
        # 이미지의 행과 열을 계산
        row = idx // 4
        col = idx % 4
        
        # 해당 이미지의 x, y 오프셋을 계산
        x_offset = col * image_width
        y_offset = row * image_height
        
        # 현재 이미지의 모든 박스를 조정
        for box in boxes:
            # 각 박스의 좌표를 조정
            adjusted_box = [
                box[0] + x_offset,  # x1
                box[1] + y_offset,  # y1
                box[2] + x_offset,  # x2
                box[3] + y_offset   # y2
            ]
            # 조정된 박스를 새 리스트에 추가
            new_boxes.append(adjusted_box)          

    # 조정된 박스들을 2차원 배열로 추가
    new_boxes = torch.tensor(new_boxes)

    result_logits = torch.empty((new_boxes.size()[:1]))
    result_phrases = []
    for logits, phrases in zip(all_logits, all_phrases):
        torch.cat((result_logits, logits), dim=0)
        # result_logits.extend(logits)
        result_phrases.extend(phrases)
    # 결과 이미지 저장
    # result_image.save(os.path.join(self.output_path, "파일명 넣을 것"))
    # print("저장이 완료되었습니다.")
    return new_boxes, result_logits, result_phrases