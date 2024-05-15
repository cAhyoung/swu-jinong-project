import os

import groundingdino.datasets.transforms as T
import numpy as np
import torch
# from torchvision.ops import box_iou, nms
from groundingdino.models import build_model
from groundingdino.util import box_ops
from groundingdino.util.inference import predict
from groundingdino.util.slconfig import SLConfig
from groundingdino.util.utils import clean_state_dict
from huggingface_hub import hf_hub_download
from segment_anything import sam_model_registry
from segment_anything import SamPredictor
from preprocessing.split_n_concat import *


SAM_MODELS = {
    "vit_h": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth",
    "vit_l": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth",
    "vit_b": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth"
}

CACHE_PATH = os.environ.get("TORCH_HOME", os.path.expanduser("~/.cache/torch/hub/checkpoints"))

# def nms(boxes, scores, iou_threshold):
#     """
#     boxes: Nx4 텐서 (N은 박스의 개수), 각 행은 [x1, y1, x2, y2] 형태의 좌표
#     scores: N 크기의 텐서, 각 박스의 점수
#     iou_threshold: IOU 임계값
#     """
#     # 점수에 따라 박스들을 내림차순으로 정렬
#     sorted_indices = torch.argsort(scores, descending=True)
#     picked_indices = []
    
#     while len(sorted_indices) > 0:
#         # 가장 높은 점수를 가진 박스 선택
#         current_index = sorted_indices[0]
#         # print(current_index)
#         picked_indices.append(current_index)

#         # 선택한 박스와 다른 모든 박스들 간의 IOU 계산
#         current_box = boxes[current_index]
#         # print(current_box)
        
#         other_boxes = boxes[sorted_indices[1:]]
#         iou = calculate_iou(current_box, other_boxes)

#         # IOU가 임계값보다 작은 박스들만 남기기
#         keep_indices = torch.nonzero((iou <= iou_threshold) & (torch.prod(other_boxes - current_box.unsqueeze(0), dim=1) > torch.prod(current_box[2:] - current_box[:2])))
#         sorted_indices = sorted_indices[keep_indices + 1].view(-1)
        
#     return torch.LongTensor(picked_indices)

# def calculate_iou(box, boxes):
#     """
#     box: 1x4 텐서, [x1, y1, x2, y2] 형태의 좌표
#     boxes: Nx4 텐서, 각 행은 [x1, y1, x2, y2] 형태의 좌표
#     """
#     # box의 좌표
#     x1, y1, x2, y2 = box
#     # boxes의 좌표
#     x1s, y1s, x2s, y2s = boxes.t()

#     # 각 박스의 영역 계산
#     areas1 = (x2 - x1) * (y2 - y1)
#     areas2s = (x2s - x1s) * (y2s - y1s)

#     # 교집합 영역 계산
#     inter_x1 = torch.max(x1, x1s)
#     inter_y1 = torch.max(y1, y1s)
#     inter_x2 = torch.min(x2, x2s)
#     inter_y2 = torch.min(y2, y2s)

#     inter_widths = torch.clamp(inter_x2 - inter_x1, min=0)
#     inter_heights = torch.clamp(inter_y2 - inter_y1, min=0)

#     intersections = inter_widths * inter_heights

#     # IOU 계산
#     unions = areas1 + areas2s - intersections
#     iou = intersections / unions

#     return iou



def load_model_hf(repo_id, filename, ckpt_config_filename, device='cpu'):
    cache_config_file = hf_hub_download(repo_id=repo_id, filename=ckpt_config_filename)

    args = SLConfig.fromfile(cache_config_file)
    model = build_model(args)
    args.device = device

    cache_file = hf_hub_download(repo_id=repo_id, filename=filename)
    checkpoint = torch.load(cache_file, map_location='cpu')
    log = model.load_state_dict(clean_state_dict(checkpoint['model']), strict=False)
    print(f"Model loaded from {cache_file} \n => {log}")
    model.eval()
    return model


def transform_image(image) -> torch.Tensor:
    transform = T.Compose([
        T.RandomResize([800], max_size=1333),
        T.ToTensor(),
        T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    image_transformed, _ = transform(image, None)
    return image_transformed


class LangSAM():

    def __init__(self, sam_type="vit_h", ckpt_path=None, return_prompts: bool = False):
        self.sam_type = sam_type
        self.return_prompts = return_prompts
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.build_groundingdino()
        self.build_sam(ckpt_path)

    def build_sam(self, ckpt_path):
        if self.sam_type is None or ckpt_path is None:
            if self.sam_type is None:
                print("No sam type indicated. Using vit_h by default.")
                self.sam_type = "vit_h"
            checkpoint_url = SAM_MODELS[self.sam_type]
            try:
                sam = sam_model_registry[self.sam_type]()
                state_dict = torch.hub.load_state_dict_from_url(checkpoint_url)
                sam.load_state_dict(state_dict, strict=True)
            except:
                raise ValueError(f"Problem loading SAM please make sure you have the right model type: {self.sam_type} \
                    and a working checkpoint: {checkpoint_url}. Recommend deleting the checkpoint and \
                    re-downloading it.")
            sam.to(device=self.device)
            self.sam = SamPredictor(sam)
        else:
            try:
                sam = sam_model_registry[self.sam_type](ckpt_path)
            except:
                raise ValueError(f"Problem loading SAM. Your model type: {self.sam_type} \
                should match your checkpoint path: {ckpt_path}. Recommend calling LangSAM \
                using matching model type AND checkpoint path")
            sam.to(device=self.device)
            self.sam = SamPredictor(sam)

    def build_groundingdino(self):
        ckpt_repo_id = "ShilongLiu/GroundingDINO"
        ckpt_filename = "groundingdino_swinb_cogcoor.pth"
        ckpt_config_filename = "GroundingDINO_SwinB.cfg.py"
        self.groundingdino = load_model_hf(ckpt_repo_id, ckpt_filename, ckpt_config_filename)

    # def predict_dino(self, image_pil, text_prompt, box_threshold, text_threshold):
    #     image_trans = transform_image(image_pil)
    #     boxes, logits, phrases = predict(model=self.groundingdino,
    #                                      image=image_trans,
    #                                      caption=text_prompt,
    #                                      box_threshold=box_threshold,
    #                                      text_threshold=text_threshold,
    #                                      remove_combined=self.return_prompts,
    #                                      device=self.device)
        
    #     print(boxes)
    #     W, H = image_pil.size
    #     boxes = box_ops.box_cxcywh_to_xyxy(boxes) * torch.Tensor([W, H, W, H])
    #     return boxes, logits, phrases
    
    
    def predict_dino(self, image_pil, image_path, text_prompt, box_threshold, text_threshold):
        imgs=ImageProcessor(image_path).img_split()
        all_boxes = []
        all_logits = []
        all_phrases = []

        for img in imgs:
            # 이미지 전처리
            image_trans = transform_image(img)
            boxes, logits, phrases = predict(model=self.groundingdino,
                                            image=image_trans,
                                            caption=text_prompt,
                                            box_threshold=box_threshold,
                                            text_threshold=text_threshold,
                                            remove_combined=self.return_prompts,
                                            device=self.device)
            
            # 예측 결과 저장
            all_boxes.append(boxes)
            all_logits.append(logits)
            all_phrases.append(phrases)
        
        # W, H = image_pil.size
        # boxes = box_ops.box_cxcywh_to_xyxy(all_boxes) * torch.Tensor([W, H, W, H])
        boxes, logits, phrases = ImageProcessor(image_path).img_concat(imgs, all_boxes, all_logits, all_phrases)

        # nms_result = nms(boxes, logits, 1.0)
        # selected_boxes = boxes[nms_result]
        # selected_logits = logits[nms_result]
        # selected_scalar = nms_result.detach().cpu().numpy()
        # selected_phrases = (phrases[scalar] for scalar in selected_scalar)    
        
        # print(boxes)
        return boxes, logits, phrases

    def predict_sam(self, image_pil, boxes):
        image_array = np.asarray(image_pil)
        self.sam.set_image(image_array)
        transformed_boxes = self.sam.transform.apply_boxes_torch(boxes, image_array.shape[:2])
        masks, _, _ = self.sam.predict_torch(
            point_coords=None,
            point_labels=None,
            boxes=transformed_boxes.to(self.sam.device),
            multimask_output=False,
        )
        return masks.cpu()

    def predict(self, image_pil,image_pil2,image_path, text_prompt, box_threshold=0.3, text_threshold=0.25):
        boxes, logits, phrases = self.predict_dino(image_pil,image_path, text_prompt, box_threshold, text_threshold)
        masks = torch.tensor([])
        if len(boxes) > 0:
            masks = self.predict_sam(image_pil2, boxes)
            masks = masks.squeeze(1)
        return masks, boxes, phrases, logits
