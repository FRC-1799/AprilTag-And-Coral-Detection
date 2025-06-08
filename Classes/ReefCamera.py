import robotpy_apriltag as apriltag
from ConstantsAndUtils import Constants
import math

from typing import Optional
from photonlibpy.estimatedRobotPose import EstimatedRobotPose
from photonlibpy.photonCamera import PhotonCamera
from photonlibpy.photonPoseEstimator import PhotonPoseEstimator, PoseStrategy
from wpimath.geometry import Transform3d, Pose2d, Pose3d, Translation3d

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
