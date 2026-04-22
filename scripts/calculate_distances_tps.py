import math
import os.path
import argparse

def parse_tps_file(file_path):
    """
    Parse a .tps file to extract landmarks and associated metadata.
    
    Args:
        file_path (str): Path to the .tps file.
        
    Returns:
        dict: Keys are image names, values are dicts with 'id' and 'landmarks'.
              Landmarks is a list of (x, y) tuples.
    """
    results = {}
    with open(file_path, 'r') as f:
        lines = f.readlines()

    current_entry = {}
    for line in lines:
        line = line.strip()
        if line.startswith("LM="):
            curve = False
            if 'image' in current_entry:
                results[current_entry['image']] = current_entry
            current_entry = {'landmarks': []}
        elif line.startswith("IMAGE="):
            # Extract the image filename from the full path
            full_path = line.split("=")[1].strip()
            current_entry['image'] = os.path.basename(full_path)
        elif line.startswith("ID="):
            current_entry['id'] = int(line.split("=")[1].strip())
        elif line.startswith("CURVES="):
            # Skip lines starting with CURVES= or other non-landmark entries
            curve = True
        elif line and not any(line.startswith(prefix) for prefix in ["LM=", "IMAGE=", "ID=", "CURVES="]):
            if not curve:
                try:
                    x, y = map(float, line.split())
                    current_entry['landmarks'].append((x, y))
                except ValueError:
                    print(f"Skipping invalid line: {line}")

    if 'image' in current_entry:
        results[current_entry['image']] = current_entry

    return results

def calculate_distances(file_a, file_b):
    """
    Calculate the distances between corresponding landmarks in two .tps files.

    Args:
        file_a (str): Path to the first .tps file (subset).
        file_b (str): Path to the second .tps file (full dataset).

    Returns:
        list of dict: Each entry contains 'image', 'id', and 'distances'.
                      Distances is a list of floats.
    """
    data_a = parse_tps_file(file_a)
    data_b = parse_tps_file(file_b)

    results = []
    for image, entry_a in data_a.items():
        if image not in data_b:
            print(f"Warning: Image {image} in File A not found in File B. Skipping.")
            continue

        entry_b = data_b[image]
        if len(entry_a['landmarks']) != len(entry_b['landmarks']):
            raise ValueError(f"Mismatch in number of landmarks for image {image}.")

        distances = [
            math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            for (x1, y1), (x2, y2) in zip(entry_a['landmarks'], entry_b['landmarks'])
        ]
        results.append({
            'image': image,
            'id': entry_a['id'],
            'distances': distances
        })

    return results


def save_distances_to_csv(results, output_file):
    """
    Save calculated distances to a CSV file.

    Args:
        results (list of dict): Distances calculated for each image and landmark.
        output_file (str): Path to save the CSV file.
    """
    with open(output_file, 'w') as f:
        f.write("Image,ID,Landmark,Distance\n")
        for result in results:
            for i, distance in enumerate(result['distances']):
                f.write(f"{result['image']},{result['id']},{i + 1},{distance}\n")


def main(file_a, file_b, output_file):
    distances = calculate_distances(file_a, file_b)
    save_distances_to_csv(distances, output_file)
    print(f"Distances saved to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate distances between landmarks in two .tps files.")
    parser.add_argument("--file_a", type=str, required=True, help="Path to the first .tps file.")
    parser.add_argument("--file_b", type=str, required=True, help="Path to the second .tps file.")
    parser.add_argument("--output_file", type=str, required=True, default="landmark_distances.csv", help="Path to save the output CSV file.")
    args = parser.parse_args()  

    main(args.file_a, args.file_b, args.output_file)

