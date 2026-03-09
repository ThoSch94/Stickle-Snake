import re
import json
import os
import argparse

"""
This script processes TPS files containing landmark coordinates for images.
It crops the coordinates based on bounding box information from JSON files.
"""

def append_to_file(temp, outfile):
    """
    Append the contents of temp list to outfile in reverse order.

    Args:
        temp (list): List of strings to append.
        outfile (str): Path to the output file.
    """
    with open(outfile, "a") as output:
        for i in reversed(temp):
            output.write(i)
            output.write("\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crop TPS coordinates based on bounding boxes.")
    parser.add_argument("tps_file", help="Path to the input TPS file.")
    parser.add_argument("outfile", help="Path to the output TPS file.")
    parser.add_argument("bbox_files", help="Directory containing JSON bounding box files.")
    parser.add_argument("--keep_negative_coords", action="store_true", help="Keep negative coordinates instead of removing them.")
    args = parser.parse_args()

    remove_negative_coords = not args.keep_negative_coords
    processed_output = []
    temp = []
    invalid_images = set()
    counter = 0
    open(args.outfile, "w").close()
    with open(args.tps_file, "r") as tps:
        lines = tps.readlines() 
        for line in reversed(lines):
            line = line.strip()
            if line == "-1.00000 -1.00000":
                invalid_images.add(image)
                valid_landmarks = False
            if re.search(r"LM=", line):
                nr = line.split("=")[1].strip()
                if nr != "13":
                    invalid_images.add(image)
                    valid_landmarks = False
                else:
                    processed_output.append(line)
                    if os.path.exists(json_file) and valid_landmarks:
                        append_to_file(processed_output, args.outfile)
                        processed_output = []
            elif re.search(r"SCALE=", line):
                processed_output = [line]
            elif re.search(r"IMAGE=", line):
                valid_landmarks = True
                image = line.split("=")[1]
                image = image.strip()
                json_file = os.path.join(args.bbox_files, image + ".json")
                if os.path.exists(json_file):
                    with open(json_file, "r") as file:
                        bbox = json.load(file)
                    processed_output.append(line)
                else:
                    bbox = None
            elif re.search(r"[0-9]+.[0-9]+ [0-9]+.[0-9]+", line):
                x, y = line.split(" ")
                x = int(x.split(".")[0])
                y = int(y.split(".")[0])
                if bbox is None:
                    invalid_images.add(image)
                    valid_landmarks = False
                else:
                    x_image_size = int(bbox["image_size"][1])
                    x_max = int(bbox["x_max"])
                    x_min = int(bbox["x_min"])
                    y_image_size = int(bbox["image_size"][0])
                    y_max = int(bbox["y_max"])
                    y_min = int(bbox["y_min"])
                    if remove_negative_coords:
                        if x == -1:
                            x_new = -1
                            valid_landmarks = False
                        else:
                            x_new = x - (x_image_size - x_max)
                            if x_new < 0:
                                print(f"x_new < 0; image:{image} x_new = {x_new}, x_max: {x_max}, x_min:{x_min}, x:{x}, x_size: {x_image_size}") 
                            if x_new >= x_max - x_min:
                                print(f"x_new >= x_max - x_min; image:{image}, x_new= {x_new}, x_max: {x_max}, x_min:{x_min}, x:{x}, x_size: {x_image_size}") 
                        if y == -1:
                            y_new = -1
                            valid_landmarks = False
                        else:
                            y_new = y - y_min
                            if y_new < 0:
                                print(f"y_new < 0; image:{image}, y_new = {y_new}, y_max: {y_max}, y_min:{y_min}, y:{y}, y_size: {y_image_size}") 
                            if y_new >= y_max - y_min:
                                print(f"y_new >= y_max - y_min, image:{image}, y_new = {y_new}, y_max: {y_max}, y_min:{y_min}, y:{y}, y_size: {y_image_size}") 
                    else:
                        x_new = -1
                        y_new = -1

                    processed_output.append(f"{x_new}.00000 {y_new}.00000")
            else:
                processed_output.append(line)
    print(f"invalid images: {invalid_images}")
    print(f"Nr invalid images: {len(invalid_images)}")