rule: read_label #Rule to read the label using a trained OCR model and save the output
    input:
        config=workflow.source_path("resources/configs/Step_1.yaml"), #We need to supply the config
        images_dir="data/raw_images" #input folder path
    output:
        "results/labelled_images" #output folder path
    container:
        "containers/ocr_model.sif" #We need to specify the container that contains the trained OCR model and the necessary dependencies to run the script
    shell:
        "python3 scripts/read_label.py"
    log:
        notebook="logs/read_label.ipynb" #log file path stored as notebook
