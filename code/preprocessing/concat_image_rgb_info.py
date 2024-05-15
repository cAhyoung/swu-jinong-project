import os
import pandas as pd

def main(result_dir = './result/'):
    result_df = pd.DataFrame()

    for directory in os.listdir(result_dir): 
        # farm_code (F0016)
        if os.path.isdir(result_dir + directory):
            print(f"directory is <{directory}>.")
            directory_path = os.path.join(result_dir, directory)
            for subdirectory in os.listdir(directory_path):
                # area_code (C101)
                print(f"subdirectory is <{subdirectory}>.")
                subdirectory_path = os.path.join(directory_path, subdirectory)
                imagedirectory_paths = sorted(os.listdir(subdirectory_path))
                for imagedirectory in imagedirectory_paths:
                    # image id (F0016-C101-20220202-084500)
                    print(f"imagedirectory is <{imagedirectory}>.")
                    # masks rgb info 파일 경로
                    file_path = os.path.join(subdirectory_path, imagedirectory, "masks/", "mask_rgb_info.csv")
                    # 파일이 존재한다면
                    if os.path.exists(file_path):
                        info = pd.read_csv(file_path)
                        result_df = pd.concat([result_df, info], ignore_index=True)
                    
                    
        print()

    result_df.to_csv(result_dir + "concat_image_rgb_info.csv", index=False)


                
if __name__ == "__main__":
    main('../dataset/SAM_result/')