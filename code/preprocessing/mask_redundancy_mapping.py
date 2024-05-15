import pandas as pd

# CSV 파일을 데이터프레임으로 읽어오기
df = pd.read_csv('/home/ubuntu/drive/swu-jinong-project/dataset/merged_data/merged_growth_real_final_filtering.csv')

# is_filtering 열이 0이고 input_image_name이 동일한 경우 중복된 mask_id를 처리
for image_name in df[df['is_filtering'] == 0]['input_image_name'].unique():
    # 중복된 mask_id를 가진 행들을 필터링
    duplicate_mask_ids = df[(df['is_filtering'] == 0) & (df['input_image_name'] == image_name)]['mask_id']
    
    # mask_id별로 개수를 세기
    mask_id_counts = duplicate_mask_ids.value_counts()
    
    # 개수가 2개 이상인 mask_id들의 리스트 저장
    mask_ids_to_check = mask_id_counts[mask_id_counts >= 2].index.tolist()
    
    # mask_id들을 돌면서 size 비교하여 is_filtering 값을 변경
    for mask_id in mask_ids_to_check:
        mask_rows = df[(df['is_filtering'] == 0) & (df['input_image_name'] == image_name) & (df['mask_id'] == mask_id)]
        mask_size_counts = mask_rows['size'].value_counts()
        
        # size가 모두 동일한지 확인
        if len(mask_size_counts) == 1:
            # size가 모두 동일하면 가장 첫 번째 행은 그대로 두고 나머지 행은 is_filtering을 1로 변경
            df.loc[mask_rows.index[1:], 'is_filtering'] = 1
        else:
            # size가 다른 경우는 모든 행의 is_filtering을 1로 변경
            mask_size = df[(df['is_filtering'] == 0) & (df['input_image_name'] == image_name) & (df['mask_id'] == mask_id)]['size'].max()
            larger_size_indices = df[(df['is_filtering'] == 0) & (df['input_image_name'] == image_name) & (df['mask_id'] == mask_id) & (df['size'] == mask_size)].index
            df.loc[larger_size_indices, 'is_filtering'] = 1
        

# 변경 사항이 있는지 확인
df.to_csv('merge_growth_real_final_filtering2.csv', encoding="UTF-8", index=False)
