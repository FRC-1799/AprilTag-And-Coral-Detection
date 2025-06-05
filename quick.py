# import os

# folder = "C:\\Users\\brenn\\Downloads\\Images For Reef Detection.v1i.yolov8\\train\\images"

# for filename in os.listdir(folder):
#     if filename.endswith(".jpg"):
#         # Get the part before the first underscore
#         new_name = filename.split("_")[0] + ".jpg"

#         # Build full file paths
#         src = os.path.join(folder, filename)
#         dst = os.path.join(folder, new_name)

#         # Rename the file
#         os.rename(src, dst)
#         print(f"Renamed: {filename} -> {new_name}")

import os

folder = "C:\\Users\\brenn\\Downloads\\Images For Reef Detection.v1i.yolov8\\test\\images"

for filename in os.listdir(folder):
    if ".jpg" in filename:
        # Remove all occurrences of '.jpg' (case-insensitive), then add a single one
        name_without_ext = filename.lower().replace("frame_", "")
        #new_name = name_without_ext + ".jpg"

        src = os.path.join(folder, filename)
        #dst = os.path.join(folder, new_name)

        # Only rename if name actually changes
        if src != name_without_ext:
            os.rename(src, name_without_ext)
            print(f"Renamed: {filename} -> {name_without_ext}")
