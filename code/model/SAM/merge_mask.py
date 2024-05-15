# import csv
# import json
# import os

# def read_csv(csv_file):
#     """
#     CSV 파일을 읽고, 이미지 이름을 키로 사용하여 각 이미지에 대한 정보를 리스트로 반환합니다.
#     """
#     image_data = {}
#     with open(csv_file, 'r', newline='') as csvfile:
#         csv_reader = csv.DictReader(csvfile)
#         for row in csv_reader:
#             image_data.setdefault(row['input_image_name'], []).append(row)
#     return image_data

# def extract_mask_info(json_folder):
#     """
#     JSON 폴더에서 mask_info.json 파일을 읽어서 필요한 정보를 추출합니다.
#     각 디렉토리를 순회하며 mask_info.json 파일을 찾고, 각 이미지 이름에 따라 마스크 정보를 저장합니다.
#     """
#     mask_info_data = {}
#     for root, dirs, files in os.walk(json_folder):
#         for dir in dirs:
#             image_folder = os.path.join(root, dir)
#             masks_folder = os.path.join(image_folder, "masks")
#             if os.path.exists(masks_folder):
#                 mask_info_file = os.path.join(masks_folder, "mask_info.json")
#                 if os.path.exists(mask_info_file):
#                     with open(mask_info_file, 'r') as json_file:
#                         masks = json.load(json_file)
#                         for mask_info in masks:
#                             base_image_name = mask_info['mask_num'].rsplit('_', 1)[0]
#                             if isinstance(mask_info['point'], list):
#                                 point_x, point_y = mask_info['point']
#                             else:
#                                 point_x, point_y = mask_info['point']
#                             mask_info_data.setdefault(base_image_name, []).append({
#                                 'mask_num': mask_info['mask_num'],
#                                 'mask_id': mask_info['mask_id'],
#                                 'size': mask_info['size'],
#                                 'color': mask_info.get('color'),  # Not all entries have color
#                                 'output_image_path': mask_info['output_image_path'],
#                                 'point_x': point_x,
#                                 'point_y': point_y
#                             })
#     return mask_info_data


# def merge_data(csv_file, json_folder, output_file):
#     """
#     CSV 파일과 JSON 폴더에서 데이터를 읽어와서 병합하여 새로운 CSV 파일을 생성합니다.
#     """
#     image_data = read_csv(csv_file)
#     mask_info_data = extract_mask_info(json_folder)
    
#     with open(output_file, 'w', newline='') as csvfile:
#         base_fieldnames = list(image_data.values())[0][0].keys()
#         additional_fieldnames = ['mask_num', 'mask_id', 'point_x', 'point_y', 'size', 'color', 'output_image_path']
#         fieldnames = list(base_fieldnames) + additional_fieldnames
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#         writer.writeheader()

#         # 원본 데이터 처리
#         for image_name, original_rows in image_data.items():
#             # 일치하는 마스크 정보가 있으면 추가 행을 생성
#             if image_name in mask_info_data:
#                 for mask_info in mask_info_data[image_name]:
#                     for original_row in original_rows:
#                         merged_data = original_row.copy()
#                         merged_data.update(mask_info)
#                         writer.writerow(merged_data)
#             else:
#                 continue

#     print(f"데이터가 {output_file}에 성공적으로 병합되었습니다.")

# # 사용 예
# merge_data("result_f0017.csv", "/home/ubuntu/drive/dataset/SAM_result/F0017", "merged_f0017.csv")

import csv
import json
import os

def read_csv(csv_file):
    """
    CSV 파일을 읽고, 이미지 이름을 키로 사용하여 각 이미지에 대한 정보를 리스트로 반환합니다.
    """
    image_data = {}
    with open(csv_file, 'r', newline='') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            image_name = row['input_image_name']
            image_data.setdefault(image_name, []).append(row)
    return image_data

# def extract_mask_info(json_folder):
#     """
#     JSON 폴더에서 mask_info.json 파일을 읽어서 필요한 정보를 추출합니다.
#     각 디렉토리를 순회하며 mask_info.json 파일을 찾고, 각 이미지 이름에 따라 마스크 정보를 저장합니다.
#     """
#     mask_info_data = {}
#     for root, dirs, files in os.walk(json_folder):
#         for dir in dirs:
#             image_folder = os.path.join(root, dir)
#             masks_folder = os.path.join(image_folder, "masks")
#             if os.path.exists(masks_folder):
#                 mask_info_file = os.path.join(masks_folder, "mask_info.json")
#                 if os.path.exists(mask_info_file):
#                     with open(mask_info_file, 'r') as json_file:
#                         masks = json.load(json_file)
#                         for mask_info in masks:
#                             base_image_name = mask_info['mask_num'].rsplit('_', 1)[0]
#                             if isinstance(mask_info['point'], list):
#                                 point_x, point_y = mask_info['point']
#                             else:
#                                 point_x, point_y = mask_info['point']
#                             mask_info_data.setdefault(base_image_name, []).append({
#                                 'mask_num': mask_info['mask_num'],
#                                 'mask_id': mask_info['mask_id'],
#                                 'size': mask_info['size'],
#                                 'color': mask_info.get('color'),  # Not all entries have color
#                                 'output_image_path': mask_info['output_image_path'],
#                                 'point_x': point_x,
#                                 'point_y': point_y
#                             })
#     return mask_info_data


# def extract_mask_info(json_folder):
#     """
#     JSON 폴더에서 mask_info.json 파일을 읽어서 필요한 정보를 추출합니다.
#     각 디렉토리를 순회하며 mask_info.json 파일을 찾고, 각 이미지 이름에 따라 마스크 정보를 저장합니다.
#     """
#     mask_info_data = {}
#     for directory in os.listdir(json_folder):
#         # C101, C102
#         if os.path.isdir(json_folder + directory):
#             print(f"directory is <{directory}>.")
#             directory_path = os.path.join(json_folder, directory)
#             for subdirectory in os.listdir(directory_path):
#                 # 각 이미지별 폴더 F0017-C101-어쩌구 ....
#                 if os.path.isdir(json_folder + directory):
#                     print(f"subdirectory is <{subdirectory}>.")
#                     mask_info_file = os.path.join(directory_path, subdirectory, "masks", "mask_info.json")
#                     if os.path.exists(mask_info_file):
#                         with open(mask_info_file, 'r') as json_file:
#                             masks = json.load(json_file)
#                             for mask_info in masks:
#                                 base_image_name = mask_info['mask_num'].rsplit('_', 1)[0]
#                                 if isinstance(mask_info['point'], list):
#                                     point_x, point_y = mask_info['point']
#                                 else:
#                                     point_x, point_y = mask_info['point']
#                                 mask_info_data.setdefault(base_image_name, []).append({
#                                     'mask_num': mask_info['mask_num'],
#                                     'mask_id': mask_info['mask_id'],
#                                     'size': mask_info['size'],
#                                     'color': mask_info.get('color'),  # Not all entries have color
#                                     'output_image_path': mask_info['output_image_path'],
#                                     'point_x': point_x,
#                                     'point_y': point_y
#                                 })
#     return mask_info_data
def extract_mask_info(json_folder):
    """
    JSON 폴더에서 mask_info.json 파일을 읽어서 필요한 정보를 추출합니다.
    각 디렉토리를 순회하며 mask_info.json 파일을 찾고, 각 이미지 이름에 따라 마스크 정보를 저장합니다.
    """
    mask_info_data = {}
    for directory in os.listdir(json_folder):
        if os.path.isdir(os.path.join(json_folder, directory)):
            directory_path = os.path.join(json_folder, directory)
            for subdirectory in os.listdir(directory_path):
                subdirectory_path = os.path.join(directory_path, subdirectory)
                masks_folder = os.path.join(subdirectory_path, "masks")
                mask_info_file = os.path.join(masks_folder, "mask_info.json")
                if os.path.exists(mask_info_file):
                    with open(mask_info_file, 'r') as json_file:
                        masks = json.load(json_file)
                        for mask_info in masks:
                            base_image_name = mask_info['mask_num'].rsplit('_', 1)[0]
                            if isinstance(mask_info['point'], list):
                                point_x, point_y = mask_info['point']
                            else:
                                point_x, point_y = mask_info['point']
                            mask_info_data.setdefault(base_image_name, []).append({
                                'mask_num': mask_info['mask_num'],
                                'mask_id': mask_info['mask_id'],
                                'size': mask_info['size'],
                                'color': mask_info.get('color'),  # Not all entries have color
                                'output_image_path': mask_info['output_image_path'],
                                'point_x': point_x,
                                'point_y': point_y
                            })
    return mask_info_data


def merge_data(csv_file, json_folder, output_file):
    """
    CSV 파일과 JSON 폴더에서 데이터를 읽어와서 병합하여 새로운 CSV 파일을 생성합니다.
    """
    image_data = read_csv(csv_file)
    mask_info_data = extract_mask_info(json_folder)
    
    with open(output_file, 'w', newline='') as csvfile:
        base_fieldnames = list(image_data.values())[0][0].keys()
        additional_fieldnames = ['mask_num', 'mask_id', 'point_x', 'point_y', 'size', 'color', 'output_image_path']
        fieldnames = list(base_fieldnames) + additional_fieldnames
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # 이미지 데이터 처리
        for image_name, original_rows in image_data.items():
            # 해당 이미지에 대한 마스크 정보가 있는 경우
            if image_name in mask_info_data:
                mask_infos = mask_info_data[image_name]
                for original_row in original_rows:
                    for mask_info in mask_infos:
                        merged_data = original_row.copy()
                        merged_data.update(mask_info)
                        writer.writerow(merged_data)
            # 해당 이미지에 대한 마스크 정보가 없는 경우
            else:
                # 마스크 정보가 없는 경우에도 원본 데이터 유지
                for original_row in original_rows:
                    writer.writerow(original_row)

    print(f"데이터가 {output_file}에 성공적으로 병합되었습니다.")

# 사용 예
merge_data("final_f0017.csv", "/home/ubuntu/drive/dataset/SAM_result2/F0017/", "final_merged_f0017.csv")
