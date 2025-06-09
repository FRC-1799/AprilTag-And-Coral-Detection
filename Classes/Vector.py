from wpimath.geometry import Pose3d, Rotation3d, Transform3d, Pose2d
import math
import ConstantsAndUtils.Constants as Constants
class vector:
    def __init__(self, cameraPosition: Pose2d, pitch:float, yaw: float, NumbersInRad=True):
        self.self = self
        cameraX, cameraY, cameraZ = cameraPosition.X(), cameraPosition.Y(), Constants.CoralAndAlgaeCameraConstants.ROBOT_TO_CAMERA_ROTATED_TRANSFORMATION.Z()

        if NumbersInRad:
            self.pose = Pose3d(cameraX, cameraY, cameraZ, Rotation3d(0, pitch, yaw))

        else:
            self.pose = Pose3d(cameraX, cameraY, cameraZ, Rotation3d(0, math.degrees(pitch), (math.degrees(yaw))))

    def getPoseAtStep(self, lenght:float)->Pose3d:
        """
        Returns the pose of this vector when extended to the given length
        """
        return self.pose.transformBy(Transform3d(lenght, 0, 0, Rotation3d()))
    
