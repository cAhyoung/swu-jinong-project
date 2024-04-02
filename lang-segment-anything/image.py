from PIL import Image

# 이미지 열기
image_pil = Image.open("7.jpg")

# 이미지의 크기 변경 (새로운 너비, 새로운 높이)
new_width = 3 * image_pil.width
new_height = 3 * image_pil.height
resized_image = image_pil.resize((new_width, new_height), Image.BICUBIC)

# 결과 이미지 저장
resized_image.save("7_aa.jpg")
