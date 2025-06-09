import robotpy_apriltag as apriltag
import math
from typing import Optional
from photonlibpy.estimatedRobotPose import EstimatedRobotPose
from photonlibpy.photonCamera import PhotonCamera
from photonlibpy.photonPoseEstimator import PhotonPoseEstimator, PoseStrategy
from wpimath.geometry import Transform3d, Pose2d, Pose3d, Translation3d
#from photonlibpy.photonTrackedTarget import TargetCorner


class AprilTagCamera:

    def __init__(self, cameraName: str, cameraTransformation: Transform3d, aprilTagField: apriltag.AprilTagFieldLayout):
        """
        When initialized, a PhotonCamera will be created, along with a PhotonPoseEstimator if the camera being passed is supposed to detect April Tags.

        Parameters:
        cameraName  (str): Name of a camera in String format. Used to find which camera is being used in Photon Vision.
        cameraType (str): Optional Parameter that is what the camera will be doing. If it is detecting April Tags, pass Pose in for it, and leave the parameter blank if it is detecting objects.
        """

        self.cameraName = cameraName
        self.camera = PhotonCamera(self.cameraName)
        self.estimator = PhotonPoseEstimator(
            apriltag.AprilTagFieldLayout.loadField(aprilTagField),
            PoseStrategy.MULTI_TAG_PNP_ON_COPROCESSOR,
            self.camera,
            cameraTransformation,
        )

        self.estimator.multiTagFallbackStrategy = PoseStrategy.LOWEST_AMBIGUITY

    def isConnected(self):
        return self.camera.isConnected()


    def get_estimated_global_pose(self) -> Optional[EstimatedRobotPose]:
        result = self.estimator.update()
        if result:
            return result, result.timestampSeconds
        else:
            return None, None

    def get_estimated_global_pose_2d(self) -> Optional[Pose2d]:
        result = self.estimator.update()
        if result:
            return result.estimatedPose.toPose2d(), result.timestampSeconds


    def get_tags(self) -> dict[int, Transform3d]:
        """
        Gets April Tags found in the camera and returns them with their id number and estimated location.

        Returns:
        Dictionary[integer, Transform3d]: The integer is the ID for the April Tag and the Transform3d is the position of the tag
        """

        photon_result = self.camera.getLatestResult()
        resultTargets = photon_result.getTargets()
        tags = {}
        for target in resultTargets:
            # Skip target if its pose is too ambiguous
            if target.poseAmbiguity > 0.2:
                continue

            tags[target.fiducialId] = target.bestCameraToTarget

        return tags

    def fetch_robot_position(self):
        position = self.get_estimated_global_pose()  # Get robot position
        return position
