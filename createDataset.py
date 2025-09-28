import os

def replace_spaces_in_filenames(directory):
    # Loop through all files in the given directory
    for filename in os.listdir(directory):
        # Construct full file path
        old_path = os.path.join(directory, filename)
        
        # Check if it's a file (not a directory)
        if os.path.isfile(old_path):
            # Replace spaces with underscores in the filename
            new_filename = filename.replace(' ', '_')
            new_path = os.path.join(directory, new_filename)
            
            # Rename the file
            os.rename(old_path, new_path)
            print(f'Renamed: "{filename}" to "{new_filename}"')

# Example usage
folder_path = '/home/lidar/Downloads/'  # Replace this with your folder path
replace_spaces_in_filenames(folder_path)



import os

folders = ['/home/lidar/Downloads/FRC_2025_Algae_and_Coral.v1i.coco/train', '/home/lidar/Downloads/FRC_2025_Algae_and_Coral.v1i.coco/valid']  # Only use train and valid
with open('dataset.txt', 'w') as f:
    for folder in folders:
        for filename in os.listdir(folder):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                path = os.path.join(folder, filename)
                f.write(path + '\n')
