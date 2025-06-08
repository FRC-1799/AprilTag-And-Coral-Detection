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
1. Install the Ai's from [here](https://drive.google.com/drive/folders/1cxrA04-azHyn-g9JzCtohw8g3ot95fH8) which I found in the Photonvision Discord. Go to the ```actuallyWorking``` folder and download ```algaeAndCoralv8-640-640-yolov8s.rknn```, as well as the associated labels file. 
   - You can also go into the ```Models``` folder located in this repo and download those, they are the same as the files in the Drive folder.
2. Start Photonvision on a computer that supports RKNN Ai models
   - Your computer needs a RK3588 CPU in order to run Ai models on Photonvision (more info [here](https://docs.photonvision.org/en/latest/docs/objectDetection/about-object-detection.html))
3. Go to Settings, then find the ```Object Detection``` panel. Once there, click ```Import New Model``` and upload the files downloaded in step 1.
4. Go to Dashboard and change the Type to Object Detection. Go to the Object Detection slide below the camera view; select the imported model and edit any other settings to make it optimized to your specific system.

**_NOTE:_**  I'm writing this now so I don't forget the steps later. The flow of this readme is good right now.


