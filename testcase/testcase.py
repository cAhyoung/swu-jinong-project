import sys
import torch
import torchvision
import transformers
import matplotlib.pyplot as plt
import numpy as np
from transformers import SamModel, SamProcessor, pipeline
from PIL import Image
import requests

### Transformers 다운받기 : 
### pip install -q git+https://github.com/huggingface/transformers

def check_version():
  ### check python version
  print("Python version : ", sys.version)
  print("-"*30)
  
  ### check cuda version and name
  print("PyTorch version : ", torch.__version__)
  print("-"*30)
  print("Torchvision version : ", torchvision.__version__)
  print("-"*30)
  print("CUDA is available : ", torch.cuda.is_available())
  print("CUDA version: {}".format(torch.version.cuda))
  print("cudnn version:{}".format(torch.backends.cudnn.version()))
  print("-"*30)
  
  ### check transformers version 
  print("Transformers version : ", transformers.__version__)
  print("-"*30)
  
def set_cuda():
  device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
  model = SamModel.from_pretrained("facebook/sam-vit-base").to(device)
  processor = SamProcessor.from_pretrained("facebook/sam-vit-base")   
  return device, model, processor

def show_mask(mask, ax, random_color=False):
    if random_color:
        color = np.concatenate([np.random.random(3), np.array([0.6])], axis=0)
    else:
        color = np.array([30 / 255, 144 / 255, 255 / 255, 0.6])
    h, w = mask.shape[-2:]
    mask_image = mask.reshape(h, w, 1) * color.reshape(1, 1, -1)
    ax.imshow(mask_image)
    
def show_masks_on_image(raw_image, masks, scores):
    if len(masks.shape) == 4:
      masks = masks.squeeze()
    if scores.shape[0] == 1:
      scores = scores.squeeze()

    nb_predictions = scores.shape[-1]
    fig, axes = plt.subplots(1, nb_predictions, figsize=(15, 15))

    for i, (mask, score) in enumerate(zip(masks, scores)):
      mask = mask.cpu().detach()
      axes[i].imshow(np.array(raw_image))
      show_mask(mask, axes[i])
      axes[i].title.set_text(f"Mask {i+1}, Score: {score.item():.3f}")
      axes[i].axis("off")
    plt.show()

def running_sam():
  ### setting cuda
  device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
  model = SamModel.from_pretrained("facebook/sam-vit-base").to(device)
  processor = SamProcessor.from_pretrained("facebook/sam-vit-base")  

  ### load image
  img_url = "https://huggingface.co/ybelkada/segment-anything/resolve/main/assets/car.png"
  raw_image = Image.open(requests.get(img_url, stream=True).raw).convert("RGB")

  plt.imshow(raw_image)
  
  ### image embeddings
  inputs = processor(raw_image, return_tensors="pt").to(device)
  image_embeddings = model.get_image_embeddings(inputs["pixel_values"])
  
  ### point
  input_points = [[[450, 600]]]
  
  ### masking
  inputs = processor(raw_image, input_points=input_points, return_tensors="pt").to(device)
  ###### pop the pixel_values as they are not neded
  inputs.pop("pixel_values", None)
  inputs.update({"image_embeddings": image_embeddings})

  with torch.no_grad():
      outputs = model(**inputs)

  masks = processor.image_processor.post_process_masks(outputs.pred_masks.cpu(), inputs["original_sizes"].cpu(), inputs["reshaped_input_sizes"].cpu())
  scores = outputs.iou_scores

  ### showing mask
  show_masks_on_image(raw_image, masks[0], scores)

if __name__ == "__main__":
  check_version()
  running_sam()