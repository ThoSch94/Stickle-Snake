# the path where your images are located
path = "/data/Fish_photos/Fish_photos_2021_unsorted/"

# output path - will be created if it doesn't exist
out_dir = "/data/Fish_photos/Fish_photos_2021_unsorted/aligned/"

# where is your pipeline config located
pipeline_config_path = "../Stickleback_detection_model/pipeline.config"

# Label file
label_path = "../Stickleback_detection_model/label_map.pbtxt"

# where is your checkpoint located
checkpoint_path = "../Stickleback_detection_model/"

# checkpoint basename
checkpoint = 'ckpt-5'

# rotation angle for first step - big and small angles will increase computation time
initial_rotation_angle = 4

# should the images be rotated 180° before processing?
flip = False

# should the image be cropped at the end?
crop = False

# generate a debug gif?
debug = False 

# save aligned image?
save = True 

# should the bounding box coordinates be saved to a file?
save_bbox = False

# should the Lanczos-Interpolation algorithm be used? This might be the most accurate version. 
# However, it can also lead to artifacts like rings around edges. In that case, turn it off - cubic interpolation will be used instead.
use_INTER_LANCZOS4 = True

# should existing files be overwritten?
overwrite = True

#################################################################################################
# For information on risks and side effects of changes beyond this point, 
# read the comments and consult your bioinformatician or software engineer.
#################################################################################################
import os
import cv2 
import json
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from object_detection.utils import config_util
from object_detection.utils import label_map_util
from object_detection.builders import model_builder

def main(pipeline_config_path, checkpoint_path, label_path, path, out_dir, initial_rotation_angle, use_INTER_LANCZOS4 = True, debug = False, save = False, save_bbox = False, flip = False, crop = False, overwrite = False):
    os.makedirs(out_dir, exist_ok=True)
    detection_model = load_model(pipeline_config_path, checkpoint_path)
    category_index = load_category_index(label_path)
    for id, file in enumerate(os.listdir(path)):
        total_files = len(os.listdir(path))
        print(f"image {id +1}/{total_files}")
        if (file not in os.listdir(out_dir)) or overwrite:
            if file.endswith(('.jpg', '.JPG')):
                if debug:
                    debug_gif = []
                img_path = path + file
                original_img = cv2.imread(img_path)
                original_img = np.array(original_img)
                if flip:
                    original_img = np.flip(original_img, axis=1)
                    original_img = np.flip(original_img, axis=0)
                rot_angle = initial_rotation_angle


                input_tensor = tf.convert_to_tensor(np.expand_dims(original_img, 0), dtype=tf.float32)
                detections = detect_fn(input_tensor, detection_model)

                cropped_image = crop_to_detection(detections, original_img)
                
                last_aspect_ratio = calculate_aspect_ratio(cropped_image, file)

                if use_INTER_LANCZOS4:
                    interpolation_method = cv2.INTER_LANCZOS4
                else:
                    interpolation_method = cv2.INTER_CUBIC
                total_angle = 0
                while np.abs(rot_angle) >= 0.4:
                    total_angle += rot_angle
                    rotated_image = rotate_image(original_img, total_angle,interpolation_method = interpolation_method, output_path = "", save = False)
                    
                    input_tensor = tf.convert_to_tensor(np.expand_dims(rotated_image, 0), dtype=tf.float32)
                    detections = detect_fn(input_tensor, detection_model)
                    cropped_rotated_image = crop_to_detection(detections, rotated_image)
                    if debug:
                        debug_gif.append(rotated_image, cropped_rotated_image)

                    aspect_ratio = calculate_aspect_ratio(cropped_rotated_image, file)
                    if last_aspect_ratio < aspect_ratio:
                        last_aspect_ratio = aspect_ratio

                    else:
                        # divide by 2.1 to prevent getting the same angle twice in one go. (results from cropping are very reproducable. so this makes sure one wrongly cropped image can't influence the entire run - unless in the last run)
                        rot_angle = -rot_angle/2.1
                        # set last_aspect_ratio to 0 works better as it removes values from beneficial cropped images
                        last_aspect_ratio = 0
                if debug:
                    frame_one = debug_gif[0]
                    frame_one.save(f"{file}.gif", format="GIF", append_images=debug_gif, save_all=True, duration=100, loop=0)
                rotated_image = rotate_image(original_img, total_angle-rot_angle,interpolation_method = interpolation_method, output_path = out_dir+file, save = False)
                input_tensor = tf.convert_to_tensor(np.expand_dims(rotated_image, 0), dtype=tf.float32)
                detections = detect_fn(input_tensor, detection_model)
                if crop:
                    rotated_image = crop_to_detection(detections, rotated_image, image_name = file, out_path = out_dir, save_bbox_file = save_bbox)
                rotated_image = np.flip(rotated_image, axis=1)
                rotated_image = np.flip(rotated_image, axis=0)

                if save:
                    cv2.imwrite(out_dir+file, rotated_image)
                    f = open(f"{out_dir}/{file}.txt", "w")
                    (h, w) = original_img.shape[:2]
                    center = (w // 2, h // 2)
                    f.write(str(total_angle-rot_angle))
                    f.write("\n")
                    f.write(str(center))
                    f.close()
            
def rotate_image(img, angle, interpolation_method = cv2.INTER_LANCZOS4, output_path = "", save = False):    
    """
    Rotates an image and saves the output.

    Args:
        img (np array):  numpy array containing the pixel values of the image
        output_path (str): The path to save the rotated image.
        angle (float): The angle by which to rotate the image.
        save (bool): states if rotated image should be saved before being returned. default: False
    Returns:
        np.array: np array containing the image data
    """
    (h, w) = img.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated_img = cv2.warpAffine(img, M, (w, h), flags=interpolation_method)
    if save:
        cv2.imwrite(output_path, rotated_img)
    return rotated_img
    
def calculate_aspect_ratio(img, file):
    height, width = img.shape[:2]
    try:
        aspect_ratio = width / height
    except:
        print(f"file: {file}, width: {width}, height: {height}")
        aspect_ratio = 999999999999
    return aspect_ratio

def display_image(image):
    cv2.imshow('Detected Object', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
def load_model(pipeline_config_path, checkpoint_path):
    # Load pipeline config and build a detection model
    configs = config_util.get_configs_from_pipeline_file(pipeline_config_path)
    detection_model = model_builder.build(model_config=configs['model'], is_training=False)

    # Restore checkpoint
    ckpt = tf.compat.v2.train.Checkpoint(model=detection_model)
    ckpt.restore(os.path.join(checkpoint_path, 'ckpt-5')).expect_partial()

    return detection_model

@tf.function
def detect_fn(image, detection_model):
    image, shapes = detection_model.preprocess(image)
    prediction_dict = detection_model.predict(image, shapes)
    detections = detection_model.postprocess(prediction_dict, shapes)
    return detections

def load_category_index(label_path):
    # Load label file
    return label_map_util.create_category_index_from_labelmap(label_path)

def crop_to_detection(detections, original_img, image_name = "", out_path = "", save_bbox_file = False):
    num_detections = int(detections.pop('num_detections'))
    detections = {key: value[0, :num_detections].numpy() for key, value in detections.items()}
    y_min, x_min, y_max, x_max = detections['detection_boxes'][0]

    # Convert normalized coordinates to pixel values
    left = int(x_min * original_img.shape[1]-100)
    right = int(x_max * original_img.shape[1]+100)
    top = int(y_min * original_img.shape[0]-100)
    bottom = int(y_max * original_img.shape[0]+100)
    if save_bbox_file:
        # bad implementation of writing bboxes to files. but I am lazy right now
        os.makedirs(out_path + "/" + "bboxes", exist_ok=True)
        data = {
            "image_name": image_name,
            "x_min": left-100,
            "x_max": right+100,
            "y_min": top-100,
            "y_max": bottom+100#,
            #"image_size": image_np.shape
        }
        with open(out_path + "/" + "bboxes" + "/" + image_name + ".json" , "w") as file:
            json.dump(data, file)
    return original_img[top:bottom, left:right]

if __name__ == "__main__":
    main(pipeline_config_path, checkpoint_path, label_path, path, out_dir, initial_rotation_angle, use_INTER_LANCZOS4, debug, save, save_bbox, flip, crop, overwrite)
