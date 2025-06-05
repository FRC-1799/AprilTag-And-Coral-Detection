import os
imageFolder = "/home/lidar/Downloads/2025 REEFSCAPE.v1i.yolov8/test/images/"
outputFile = "dataset.txt"
validExts = [".jpg"]

imagePaths = [
    os.path.join(imageFolder, fname)
    for fname in os.listdir(imageFolder)
    if os.path.splitext(fname)[1].lower() in validExts
]

with open(outputFile, "w") as f:
    for path in imagePaths:
        f.write(path + "\n")