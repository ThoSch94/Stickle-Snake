configfile: "resources/configs/Step_1.yaml" #We need to specify the config file that contains the parameters for the script

rule all:
    input:
        "data/raw_images/label_log.json" #This is the final output of the pipeline, which is the folder containing the labelled images after processing.


rule read_label: #Rule to read the label using a trained OCR model and save the output 
    input:
        images_dir="data/raw_images" #input folder path
    output:
        "data/raw_images/label_log.json" #log file (robust in case files are renamed, as the log file will be saved in the same directory as the images)
    container:
        config["container"] #We need to specify the container that contains the trained OCR model and the necessary dependencies to run the script
    log:
        notebook="logs/read_label.log" #log file path
    shell:
        "python3 scripts/read_label.py "
        "--log_file {config[log_file]} "
        "--image_dir {input.images_dir} "
        "--flip {config[flip]} "
        "--pattern {config[pattern]} "
        "--rename {config[rename]} "
        "--save_ocr_visualization {config[save_ocr_visualization]}"
