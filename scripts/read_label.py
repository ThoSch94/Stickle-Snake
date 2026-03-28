
# path (including filename) where th logfile should be created
log_file = r"/mnt/data/label_log.json"

# path where the images are stored
image_dir = r"/mnt/data/raw_images/"

# regex pattern for correct labels
pattern = "[A-Z]{2}[0-9]{2}[A-Z][0-9]{3}"

# should plausible filenames be changed? - not yet functional
force_rename = False

# should the images be renamed?
rename =  False

# should the images be rotated 180° before processing?
flip = False

#should OCR detection be visualized and saved on the image? 
save_ocr_visualization = True
visualization_dir = r"/mnt/data/debug"

#################################################################################################
# For information on risks and side effects of changes beyond this point, 
# read the comments and consult your bioinformatician or software engineer.
#################################################################################################
import cv2
import easyocr
import matplotlib.pyplot as plt
import numpy as np
import rawpy
import os
import re
import json
import argparse
import sys

def main(log_file, image_dir, flip, pattern = "[A-Z]{2}[0-9]{2}[A-Z][0-9]{3}", rename = True, save_ocr_visualization = False, visualization_dir = r"/mnt/data/debug"):
    file_duplications = {}
    unclear_labels = {}
    statistics = {}
    label_name_mismatch = {}
    single_label_detected = {}
    identical_names = {}
    majority_votes = {}
    errors = {}

    # instance text detector
    reader = easyocr.Reader(['en'], gpu=False)
    for id, file in enumerate(os.listdir(image_dir)):
        print(f"processed: {id +1}/{len(os.listdir(image_dir))}")
        
        if file.endswith(('.jpg', '.JPG', ".NEF")):
            image_path = image_dir + "/" + file
            if file.endswith((".NEF")):
                img = convert_nef_to_jpg(image_path)
            else:
                img = cv2.imread(image_path)
            if flip:
                    img = np.flip(img, axis=1)
                    img = np.flip(img, axis=0)
            # detect text on image
            text_ = reader.readtext(np.array(img))

            # visualize step (optional)
            if save_ocr_visualization:
                os.makedirs(visualization_dir, exist_ok=True)
                viz_path = os.path.join(visualization_dir, f"ocr_{file}.jpg")
                visualize_ocr_detections(img, text_, output_path=viz_path)
                print(f"saved OCR visualization to {viz_path}")

            labels = []
            scores = []
            for t_, t in enumerate(text_):
                bbox, text, score = t
                temp = text.replace('.', '')
                number_of_errors, temp = label_error_handeling(temp)
                if re.search(pattern, temp):
                    labels.append(temp)
                    scores.append(score)
            unique,pos = np.unique(labels,return_inverse=True) #Finds all unique elements and their positions
            file_base_name = file.split(".")[0]
            #try:

            if len(labels) >=1:
                counts = np.bincount(pos)                     #Count the number of each unique element
                maxpos = counts.argmax()                      #Finds the positions of the maximum count
                most_frequent_label = unique[maxpos]

            if len(labels) == 0:
                errors[f"error_{file_base_name}"]={"log_type": "error", "status": "error", "old_filename": file, "comment": "No label detected"}

            # catch if file already has the correct name
            elif file_base_name == most_frequent_label:
                identical_names[f"filename_identical_{file_base_name}"]={"log_type": "filename_identical", "status": "skipped", "old_filename": file, "comment": "filename already matches detected label"}

            # catch if file already exists
            elif most_frequent_label +".jpg" in os.listdir(image_dir):
                file_duplications[f"file_duplication_{most_frequent_label}"]={"log_type": "file_duplication", "status": "skipped; user intervention required", "old_filename": file, "detected_label": most_frequent_label, "comment": "another file exists that name matches the detected label"}

            # catch if file already has a different plausible name.
            elif re.search("[A-Z]{2}[0-9]{2}[A-Z][0-9]{3}", file_base_name):
                label_name_mismatch[f"label_name_mismatch_{file_base_name}"]={"log_type": "label_name_mismatch", "status": "skipped; user intervention required", "old_filename": file, "detected_label": most_frequent_label, "comment": "the file already has a plausible name, but it doesn't match the detected label"}
            # check if only one label is detected
            elif len(labels) == 1:
                single_label_detected[f"single_label_detected_{file_base_name}"]={"log_type": "single_label_detected", "status": "renamed", "old_filename": file, "labels": [{"name":most_frequent_label, "score":scores}], "comment": "one plausible label detected, file renamed"}
                if rename:
                    os.rename(image_path,f"{image_dir}/{most_frequent_label}.jpg")
            # majority vote if multiple unique labels are detected
            elif len(labels) > len(unique) & len(unique) > 1:
                assert len(scores) == len(labels)
                scores = np.array(scores)
                labels = np.array(labels)
                labels_and_scores = []
                for i in unique:
                    labels_and_scores.append({"name":i, "score":(scores[labels == i]).tolist()})
                majority_votes[f"majority_vote_{file_base_name}"]={"log_type": "majority_vote", "status": "renamed", "old_filename": file, "new_filename": most_frequent_label, "labels": labels_and_scores, "comment": "label assigned by majority vote"}
                if rename:
                    os.rename(image_path,f"{image_dir}/{most_frequent_label}.jpg")
            # check if multiple labels detected but only one unique
            elif len(labels) > len(unique) & len(unique) == 1:
                scores = np.array(scores)
                labels = np.array(labels)
                labels_and_scores = []
                for i in unique:
                    labels_and_scores.append({"name":i, "score":(scores[labels == i]).tolist()})
                statistics[f"statistics_{file_base_name}"]={"log_type": "statistics", "status": "renamed", "old_filename": file, "new_filename": most_frequent_label, "labels": labels_and_scores, "comment": "File renamed following unanimous label vote"}
                if rename:
                    os.rename(image_path,f"{image_dir}/{most_frequent_label}.jpg")

            else:
                scores = np.array(scores)
                labels = np.array(labels)
                labels_and_scores = []
                for i in unique:
                    labels_and_scores.append({"name":i, "score":(scores[labels == i]).tolist()})
                errors[f"error_{file_base_name}"]={"log_type": "error", "status": "error", "old_filename": file, "labels": labels_and_scores, "comment": "No majoity in label votes. File not renamed."}
            #except Exception as error:
                #print(text_)
                #errors[f"error_{file_base_name}"]={"log_type": "error", "status": "error", "old_filename": file, "comment": "No label detected"}
    logs = [label_name_mismatch, errors, file_duplications, single_label_detected, identical_names, majority_votes, statistics]
    write_logs_to_file(log_path=log_file, logs = logs)

def convert_nef_to_jpg(nef_file_path):
    with rawpy.imread(nef_file_path) as raw:
        rgb_image = raw.postprocess(use_camera_wb=True)
        return rgb_image


def write_logs_to_file(log_path, logs):
    combined = {}
    for i in logs:
         if i != {}:
              combined.update(i)
    with open(log_path, 'w') as outfile:
            json.dump(combined, outfile, indent=4)


def rotate_image(img, angle, output_path = "", save = False):    
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
    rotated_img = cv2.warpAffine(img, M, (w, h))
    if save:
        cv2.imwrite(output_path, rotated_img)
    return rotated_img

def visualize_ocr_detections(image, text_detections, output_path=None):
    """
    Draw bounding boxes and confidence scores on detected text.
    
    Args:
        image (np.array): The original image (as uint8 BGR or RGB)
        text_detections (list): Output from easyocr reader.readtext()
        output_path (str): Optional path to save the visualization
    
    Returns:
        np.array: Image with annotations drawn on it
    """
    img_copy = image.copy()
    
    for bbox, text, score in text_detections:
        # bbox is a list of 4 corner points; convert to int for drawing
        bbox = [[int(x), int(y)] for x, y in bbox]
        
        # draw the bounding box (quadrilateral)
        pts = np.array(bbox, dtype=np.int32)
        cv2.polylines(img_copy, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
        
        # draw the detected text and score near the top-left corner
        x, y = int(bbox[0][0]), int(bbox[0][1])
        label = f"{text} ({score:.2f})"
        cv2.putText(img_copy, label, (x, y - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    
    if output_path:
        cv2.imwrite(output_path, img_copy)
    
    return img_copy

def label_error_handeling(string):
    """
    modifies label if expectations are not met.
    - strips characters at the end if string is longer than expected
    - replaces characters in positions where numbers would be expected with a similar looking number.

    Args:
        string (str): a string that will be processed to remove non plausible parts.

    Returns:
        list: int - number of errors, str - processed string
    """
    errors_handled = 0
    pattern = r"[A-Z]{2}[OoIZzg0-9]{2}[A-Z][ZSgIOo0-9]{3}"
    indices = [2, 3, 5, 6, 7]
    replacements = {
            'Z': '2', 'z': '2',
            'g': '9',
            'O': '0', 'o': '0',
            'I': '1',
            "S": "5"
        }
    # check if string matches structure
    if re.search(pattern, string):
        # remove additional characters
        new_string =  re.search(pattern, string).group()
        if(new_string != string):
            errors_handled += 1
        string = new_string

        # convert string to list and replace characters with similar looking numbers in places where numbers would be expected.
        string_list = list(string)
        errors_handled = 0

        for index in indices:
            if string_list[index] in replacements:
                string_list[index] = replacements[string_list[index]]
                errors_handled += 1
        string = ''.join(string_list)
    return [errors_handled, string]

def str2bool(v):
    # helper function to parse boolean arguments from command line
    if isinstance(v, bool): return v
    if v.lower() in ("yes","true","t","1"): return True
    if v.lower() in ("no","false","f","0"): return False
    raise argparse.ArgumentTypeError("Boolean value expected.")

def validate_paths(log_file, image_dir):
    """Check paths are valid before running the rest of the script."""
    errors = []
    
    # Check input directory exists
    if not os.path.exists(image_dir):
        errors.append(f"Image directory does not exist: {image_dir}")
    
    # Check log file directory exists, create it if not
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir, exist_ok=True)
            print(f"Created log directory: {log_dir}")
        except PermissionError:
            errors.append(f"Cannot create log directory (permission denied): {log_dir}")
    
    # If any errors, report them all at once and exit cleanly
    if errors:
        print("Path validation failed:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Read labels from images using OCR and rename files accordingly.")
    parser.add_argument("--log_file", default=log_file, help="Path to the log file where results will be saved.")
    parser.add_argument("--image_dir", default=image_dir, help="Directory containing the images to process.")
    parser.add_argument("--flip", type=str2bool, nargs='?', const=True, default=False, help="Whether to flip images 180° before processing.")
    parser.add_argument("--rename", type=str2bool, nargs='?', const=True, default=True, help="Whether to rename files based on detected labels.")
    parser.add_argument("--pattern", default=pattern, help="Regex pattern to identify valid labels.")
    parser.add_argument("--save_ocr_visualization", type=str2bool, nargs='?', const=True, default=False, help="Whether to save images with OCR detections visualized.")
    args = parser.parse_args()
    validate_paths(args.log_file, args.image_dir)
    main(log_file = args.log_file, image_dir = args.image_dir, flip = args.flip, pattern = args.pattern, rename =  args.rename, save_ocr_visualization = args.save_ocr_visualization)
    