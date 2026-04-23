configfile: "resources/configs/model_params.yaml" #We need to specify the config file that contains the parameters for the script

#rule all:
#    input:
#        "data/cropped_images/{landmark_name}.tps" #indicating that the landmarks have been cropped from the tps files (or otherwise provided)

rule crop_lands: 
    input: 
        lands =config["input_tps"], #We need to specify the input tps file that contains the landmark coordinates
        directory = "data/cropped_images/", #We need to specify the directory that contains the cropped images, which will be used to match the landmark coordinates with the corresponding images
    output: 
        "data/landmarks/cropped_input.tps"
    log: 
        notebook="logs/crop_lands.log"
    benchmark:
        "benchmarks/bench_crop_lands.txt"
    shell: 
        "python3 scripts/crop_tps_coordinates.py "
        "{input.lands} " 
        "{output} "
        "{input.directory}"
        "> {log.notebook} 2>&1"

rule preprocess_landmark_model: 
    input: 
        directory = "data/cropped_images/",
        lands = "data/landmarks/cropped_input.tps"
    output: 
        "data/train.xml",
        "data/test.xml",
    conda: 
        "envs/ml_morph.yaml" #We need to specify the conda environment
    log: 
        notebook="logs/preprocess_landmark_model.log" #log file path
    benchmark:
        "benchmarks/bench_preprocess_landmark_model.txt"
    shell:
        "python3 scripts/ml-morph_scripts/preprocessing.py "
        "-i {input.directory} "
        "-t {input.lands} "
        "> {log.notebook} 2>&1"

rule train_landmark_model: 
    input: 
        train = "data/train.xml",
        test = "data/test.xml",
    output: 
        "models/landmark_model.dat"
    conda: 
        "envs/ml_morph.yaml" #We need to specify the conda environment
    log:
        notebook="logs/train_landmark_model.log" #log file path
    benchmark:
        "benchmarks/bench_train_landmark_model.txt"
    shell:
        "python3 scripts/ml-morph_scripts/shape_trainer.py "
        "-d {input.train} "
        "-t {input.test} "
        "-th {config[threads]} "
        "-dp {config[tree_depth]} "
        "-c {config[cascade_depth]} "
        "-nu {config[nu_reg_param]} "
        "-os {config[oversampling]} "
        "-f {config[feature_size]} "
        "-n {config[num_trees]} "
        "-s {config[test_splits]} "
        "-o {output} "
        "> {log.notebook} 2>&1"

rule predict_landmarks:
    input:
        directory= "data/cropped_images/",
        model = "models/landmark_model.dat",
    output:
        "data/output/predicted_landmarks.tps"
    conda: 
        "envs/ml_morph.yaml" #We need to specify the conda env
    log:
        notebook="logs/predict_landmarks.log" #log file path
    benchmark:
        "benchmarks/bench_predict_landmarks.txt"
    shell:
        "python3 scripts/ml-morph_scripts/prediction.py "
        "-i {input.directory} "
        "-p {input.model} "
        "-o {output} "
        "> {log.notebook} 2>&1"

rule apply_scales_to_landmarks:
    input:
        predicted = "data/output/predicted_landmarks.tps",
        scales = "data/measurements/specimen_scales.csv"
    output:
        "data/output/predicted_landmarks_scaled.tps"
    conda: 
        "envs/ml_morph.yaml" #We need to specify the conda env
    log:
        notebook="logs/apply_scales_to_landmarks.log" #log file path
    benchmark:
        "benchmarks/bench_apply_scales_to_landmarks.txt"
    shell:
        "python3 scripts/Apply_Scale_To_TPS.py "
        "--tps {input.predicted} "
        "--csv {input.scales} "
        "--out {output} "
        "--invert-scale "
        "> {log.notebook} 2>&1"


rule evaluate_landmark_predictions:
    input:
        predicted = "data/output/predicted_landmarks.tps",
        true = "data/landmarks/cropped_input.tps"
    output:
        "data/output/landmark_distances.csv"
    conda: 
        "envs/ml_morph.yaml" #We need to specify the conda env
    log:
        notebook="logs/evaluate_landmark_predictions.log" #log file path
    benchmark:
        "benchmarks/bench_evaluate_landmark_predictions.txt"
    shell:
        "python3 scripts/calculate_distances_tps.py "
        "--file_a {input.predicted} "
        "--file_b {input.true} "
        "--output_file {output} "
        "> {log.notebook} 2>&1"

rule visualize_landmark_predictions:
    input:
        land_data = "data/output/landmark_distances.csv",
    output:
        "data/output/results_table.tex"
    conda: 
        "envs/ml_morph.yaml" #We need to specify the conda env
    log:
        notebook="logs/visualize_landmark_predictions.log" #log file path
    benchmark:
        "benchmarks/bench_visualize_landmark_predictions.txt"
    shell:
        "python3 scripts/analyze_distances.py "
        "--input_csv {input.land_data} "
        "--all_visualizations "
        "> {log.notebook} 2>&1"