import json

# File paths
file1_path = "quiz_data_og.json"
file2_path = "quiz_data_og_2.json"
output_file_path = "combined_quiz_data.json"


# Load JSON files
def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


# Merge dictionaries
def merge_json(dict1, dict2):
    merged_dict = dict1.copy()
    for key, value in dict2.items():
        if key in merged_dict:
            merged_dict[key].extend(value)  # Append questions if experiment exists
        else:
            merged_dict[key] = value  # Add new experiment
    return merged_dict


# Load data
quiz_data_1 = load_json(file1_path)
quiz_data_2 = load_json(file2_path)

# Merge data
combined_data = merge_json(quiz_data_1, quiz_data_2)

# Sort dictionary by experiment headers
sorted_combined_data = dict(sorted(combined_data.items()))

# Save merged and sorted data
with open(output_file_path, "w", encoding="utf-8") as output_file:
    json.dump(sorted_combined_data, output_file, indent=4, ensure_ascii=False)

print(f"Sorted combined file saved as {output_file_path}")
