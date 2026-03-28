configfile: "resources/configs/StickleSnake.yaml" #We need to specify the config file that contains the parameters for the script

#rule all:
#    input:
#        "data/cropped_images/{landmark_name}.tps" #indicating that the landmarks have been cropped from the tps files (or otherwise provided)

rule crop_lands: 
    input: 
        "data/raw_images/{landmark_name}.tps"
    output: 
        "data/cropped_images/{landmark_name}.tps"
    shell: 
        "python3 scripts/crop_tps_coordinates.py"
        "--input_tps {input}" 
        "--outfile {output}"
        "--bbox_files data/cropped_images"

        