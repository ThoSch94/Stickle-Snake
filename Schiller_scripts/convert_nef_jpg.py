import rawpy
import os
import cv2 

input_folder = "/data/Fish_photos/Fish_photos_2019/Finger(FG)/FG_CC/"
output_folder = '/data/Fish_photos/Fish_photos_2019/Finger(FG)/FG_CC/jpg'

os.makedirs(output_folder, exist_ok=True)

def convert_nef_to_jpg(nef_file_path, output_folder):
    with rawpy.imread(nef_file_path) as raw:
        rgb_image = raw.postprocess(use_camera_wb=True)
        base_name = os.path.basename(nef_file_path)
        output_file_path = os.path.join(output_folder, base_name.replace('.nef', '.jpg').replace('.NEF', '.jpg'))
        cv2.imwrite(output_file_path, cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR))

for id, filename in enumerate(os.listdir(input_folder)):
    print(f"processed {id + 1}/{len(os.listdir(input_folder))}")
    if filename.lower().endswith('.nef'):
        convert_nef_to_jpg(os.path.join(input_folder, filename), output_folder)
