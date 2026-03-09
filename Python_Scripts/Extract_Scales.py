
import os
import json
import csv

# Directory containing the JSON files
input_directory = 'Canad_Zoo_Training/Canad_Zoo_Test/results/measurements-canad-zoo'  # Update this path to your directory
# Output CSV file
output_file = 'Canad_Zoo_Training/test_specimen_scales.csv'

# List to hold specimen data
specimen_data = []

# Iterate through all files in the directory
for filename in os.listdir(input_directory):
    if filename.endswith('.json'):
        file_path = os.path.join(input_directory, filename)
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            # Extract the reference scale
            reference_data = data.get('reference', {})
            #  Get the first (and typically only) key in reference
            key = next(iter(reference_data), None)
            if key:
                reference_scale = reference_data[key].get('data', {}).get('reference', [None])[0]
            else:
                reference_scale = None
            # Extract specimen name from filename, remove .json extension and everything from _annotations_config onwards
            specimen_name = filename.replace('.json', '').split('_annotations_config')[0]
            # Clean up leading double underscore (e.g., "0__FG_GL_19T_340" -> "FG_GL_19T_340")
            specimen_name = specimen_name.replace('0__', '', 1)
             # Append the specimen data
            specimen_data.append({'specimen': specimen_name, 'scale': reference_scale})

# Write the data to a CSV file
with open(output_file, 'w', newline='') as csv_file:
    fieldnames = ['specimen', 'scale']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for specimen in specimen_data:
        writer.writerow(specimen)

print(f'Data has been written to {output_file}')