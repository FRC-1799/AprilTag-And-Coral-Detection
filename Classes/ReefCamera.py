import robotpy_apriltag as apriltag
from ConstantsAndUtils import Constants
import math

from typing import Optional
from photonlibpy.estimatedRobotPose import EstimatedRobotPose
from photonlibpy.photonCamera import PhotonCamera
from photonlibpy.photonPoseEstimator import PhotonPoseEstimator, PoseStrategy
from wpimath.geometry import Transform3d, Pose2d, Pose3d, Translation3d
from photonlibpy.targeting.photonTrackedTarget import PhotonTrackedTarget

class ReefCamera:
    def __init__(self, cameraName: str, cameraTransformation: Transform3d):
        """
        When initialized, a PhotonCamera will be created. This will be used to detect coral and algae

        Parameters:
        cameraName  (str): Name of a camera in String format. Used to find which camera is being used in Photon Vision.
        cameraType (str): Optional Parameter that is what the camera will be doing. If it is detecting April Tags, pass Pose in for it, and leave the parameter blank if it is detecting objects.
        """

        self.cameraName = cameraName
        self.camera = PhotonCamera(self.cameraName)
        self.cameraTransformation = cameraTransformation
    
    def isConnected(self):
        return self.camera.isConnected()

    def getObjects(self) -> list[PhotonTrackedTarget]:
        """
        Gets Coral and Algae found in the camera and returns them in a list.

        Returns:
        Dictionary[integer, Transform3d]: The integer is the ID for the April Tag and the Transform3d is the position of the tag
        """

        photonResult = self.camera.getLatestResult()
        resultTargets: list[PhotonTrackedTarget] = photonResult.getTargets()
        return resultTargets
