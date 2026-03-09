# the path where your images are located
path = "/mnt/data/"
# output path - will be created if it doesn't exist
out_dir = "/mnt/data/cropped/"
# where is your pipeline config located
pipeline_config_path = "/mnt/support/pipeline.config"
# Label file
label_path = "/mnt/support/label_map.pbtxt"
# where is your checkpoint located
checkpoint_path = "/mnt/support/"
# checkpoint basename
checkpoint = 'ckpt-5'
# should the bounding box coordinates be saved?
save_bbox_coordinates = True 
# should the image be flipped (180° rotation) before detection? (Is the image right side up? = TRUE. If not, set to FALSE)
flip = True
# should the image be displayed with a bounding box?
display_image_with_bbox = False
# should the full image be saved with the bounding box on it?
save_image_with_bbox = False
# should the cropped image be saved?
save_cropped_image = True

#################################################################################################
# For information on risks and side effects of changes beyond this point, 
# read the comments and consult your bioinformatician or software engineer.
#################################################################################################
import os
import tensorflow as tf
from object_detection.utils import label_map_util
from object_detection.builders import model_builder
from object_detection.utils import config_util
from object_detection.utils import visualization_utils as viz_utils
import cv2 
import numpy as np
import rawpy
import matplotlib.pyplot as plt
import json
import matplotlib.image as mpimg

def main(path, out_dir, pipeline_config_path, checkpoint_path, label_path, checkpoint, flip = True, save_bbox_coordinates = False, display_image_with_bbox = False, save_image_with_bbox = False, save_cropped_image = True):

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    configs = config_util.get_configs_from_pipeline_file(pipeline_config_path)
    detection_model = model_builder.build(model_config=configs['model'], is_training=False)

    ckpt = tf.compat.v2.train.Checkpoint(model=detection_model)
    ckpt.restore(os.path.join(checkpoint_path, checkpoint)).expect_partial()
    category_index = label_map_util.create_category_index_from_labelmap(label_path)

    @tf.function
    def detect_fn(image):
        image, shapes = detection_model.preprocess(image)
        prediction_dict = detection_model.predict(image, shapes)
        detections = detection_model.postprocess(prediction_dict, shapes)
        return detections

    for id, file in enumerate(os.listdir(path)):
        print(f"processed {id +1}/{len(os.listdir(path))}")
        if file.endswith(('.jpg', '.JPG', ".NEF")):
            img_path = path + file
            if file.endswith((".NEF")):
                image_np = convert_nef_to_jpg(img_path)
            else:
                image_np = plt.imread(img_path)

            if flip:
                image_np = np.flip(image_np, axis=1)
                image_np = np.flip(image_np, axis=0)

            detections = run_detection(image_np, detect_fn)

            # this displays the image with the bbox if you want to look at it.
            if display_image_with_bbox:
                image_np_with_detections = draw_bounding_box(image_np, detections, category_index)
                cv2.imshow('Detected Object', image_np_with_detections)
                cv2.waitKey(0)
                cv2.destroyAllWindows()

            base_name = os.path.basename(img_path)
            output_file_path = os.path.join(out_dir, base_name.replace('.nef', '.jpg').replace('.NEF', '.jpg'))

            # save image with bounding box
            if save_image_with_bbox:
                image_np_with_detections = draw_bounding_box(image_np, detections, category_index)
                cv2.imwrite(output_file_path, image_np_with_detections)
            
            # uncomment this to save cropped image
            if save_cropped_image:
                if detections:
                    detected_object = crop_image_to_bounding_box_max_score(image_np, detections, out_path = out_dir, save_bbox_file = save_bbox_coordinates, image_name = file)
                else:
                    detected_object = image_np
                detected_object = np.flip(detected_object, axis=1)
                detected_object = np.flip(detected_object, axis=0)
                if np.any(detected_object.shape) == 0:
                    print(f"{file}: no detection")
                else:
                    mpimg.imsave(output_file_path, detected_object)

def convert_nef_to_jpg(nef_file_path):
    with rawpy.imread(nef_file_path) as raw:
        rgb_image = raw.postprocess(use_camera_wb=True)
        return rgb_image


def run_detection(image_np, detect_fn):
    """
    Runs object detection on a given image using a detection model.

    Args:
        image_np (numpy.ndarray): Input image in numpy array format.
        detect_fn (function): A pre-trained object detection model, 
                              that takes in an image tensor and returns detection results.

    Returns:
        dict: A dictionary containing the detection results, including:
              - 'num_detections' (int): The number of detected objects.
              - 'detection_boxes' (numpy.ndarray): Array of bounding box coordinates for detected objects.
              - 'detection_scores' (numpy.ndarray): Array of confidence scores for each detection.
              - 'detection_classes' (numpy.ndarray): Array of class IDs for detected objects, converted to integers.
    """
    
    input_tensor = tf.convert_to_tensor(np.expand_dims(image_np, 0), dtype=tf.float32)
    detections = detect_fn(input_tensor)
    num_detections = int(detections.pop('num_detections'))
    detections = {key: value[0, :num_detections].numpy()
                for key, value in detections.items()}
    detections['num_detections'] = num_detections
    detections['detection_classes'] = detections['detection_classes'].astype(np.int64)
    return detections

def draw_bounding_box(image_np, detections, category_index):
    """
    Draws bounding boxes on the input image based on detection results.

    Args:
        image_np (numpy.ndarray): The input image in numpy array format.
        detections (dict): A dictionary containing detection results, including:
                           - 'detection_boxes' (numpy.ndarray): Array of bounding box coordinates.
                           - 'detection_classes' (numpy.ndarray): Array of class IDs for detected objects.
                           - 'detection_scores' (numpy.ndarray): Array of confidence scores for each detection.

    Returns:
        numpy.ndarray: The image with bounding boxes drawn around detected objects.
    """
    label_id_offset = 1
    image_np_with_detections = image_np.copy()
    viz_utils.visualize_boxes_and_labels_on_image_array(
                image_np_with_detections,
                detections['detection_boxes'],
                detections['detection_classes']+label_id_offset,
                detections['detection_scores'],
                category_index,
                use_normalized_coordinates=True,
                max_boxes_to_draw=5,
                min_score_thresh=.8,
                agnostic_mode=False)
    return image_np_with_detections

def crop_image_to_bounding_box_max_score(image_np, detections, out_path = "", save_bbox_file = False, image_name = ""):
    """
    Crops the input image to the bounding box of the detected object with the highest score.

    Args:
        image_np (numpy.ndarray): The input image in numpy array format.
        detections (dict): A dictionary containing detection results, including:
                           - 'detection_boxes' (numpy.ndarray): Array of bounding box coordinates.
                           - 'detection_scores' (numpy.ndarray): Array of confidence scores for each detection.

    Returns:
        numpy.ndarray: The cropped region of the image containing the detected object with the highest score.
    """
    max_score_index = np.argmax(detections['detection_scores'])
    ymin, xmin, ymax, xmax = detections['detection_boxes'][max_score_index]
    
    # Convert the normalized coordinates to pixel values
    (left, right, top, bottom) = (int(xmin * image_np.shape[1]), int(xmax * image_np.shape[1]),
                                  int(ymin * image_np.shape[0]), int(ymax * image_np.shape[0]))
    if save_bbox_file:
        # bad implementation of writing bboxes to files. but I am lazy 
        os.makedirs(out_path, exist_ok=True)
        data = {
            "image_name": image_name,
            "x_min": left-100,
            "x_max": right+100,
            "y_min": top-100,
            "y_max": bottom+100,
            "image_size": image_np.shape
        }
        with open(out_path + "/" + image_name + ".json" , "w") as file:
            json.dump(data, file)
    # Crop the image to the bounding box with a 20-pixel margin
    detected_object = image_np[top-100:bottom+100, left-100:right+100]

    return detected_object


if __name__ == "__main__":
    main(path, out_dir, pipeline_config_path, checkpoint_path, label_path, checkpoint, flip, save_bbox_coordinates = save_bbox_coordinates, display_image_with_bbox = display_image_with_bbox, save_image_with_bbox = save_image_with_bbox, save_cropped_image = save_cropped_image)
