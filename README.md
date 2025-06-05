# Photon Vision's Note Detection, April Tag Detection, and Robot Position Estimator 
This code is indended to be used alongside Photon Vision. Photon Vision will take frames from a connected camera, check whether certain objects are in the frame, and send the information about these objects to Network Tables. By pulling this information down using PhotonLibPy, we can run PhotonPoseEstimator to figure out the location of objects and the robot.
## Steps to start Photon Vision
1. Install a Jar file from [this release page](https://github.com/PhotonVision/photonvision/releases). A Jar file is not included in this repo as it is too large to push from Github Desktop.
   - I recommend version [2025.3.1]([https://github.com/PhotonVision/photonvision/releases/tag/v2025.3.1) as it is not a beta and works the best.
2. Install [PhotonLibPy](https://pypi.org/project/photonlibpy/) using ```pip install PhotonLibPy``` or ```pip3 install PhotonLibPy```.
3. Run the Jar file by navigating to the directory of the file in your Terminal and run ```java -jar C:\path\to\photonvision\NAME OF JAR FILE GOES HERE.jar```.
   - For example, if you ran my recommended version of PhotonLib, the command would be  ```java -jar photonvision-v2024.3.1-linuxx64.jar```.
4. Once the Jar file is running (meaning the backend of the UI is running), navigate to ```localhost:5800``` in order to view the UI.

**_NOTE:_**  If you are using an operating system that is not Windows, these steps may vary, so navigate to [Software Installation](https://docs.photonvision.org/en/latest/docs/advanced-installation/sw_install/index.html) to see all other ways of installation

## Using AI with Photonvision
1. Train the AI. I did so by downloading a dataset (e.g. [2025 REEFSCAPE Computer Vision Project](https://universe.roboflow.com/main-ciqhn/2025-reefscape-tzh2r)) and training it using Ultralytics and Python. In the data set folder, you should find a data.yaml file. By using the same template in ```Models/trainModel.py```, you can train the model off of the provided data set.
2. Convert AI format to RKNN. Follow the Training step onward from Team 5990 Trigon's [documentation on Kaggle](https://www.kaggle.com/code/lavirz/yolov8-to-rknn), it was very helpful. Also, installing RKNN Toolkit 2 is easier using pip: ```pip install rknn-toolkit2```.
3. Load newly converted model into Photonvision via the Settings panel.

**_NOTE:_**  I'm writing this now so I don't forget the steps later. The flow of this readme is good right now.


