from wpimath.geometry import Pose3d, Rotation3d, Transform3d, Pose2d
import math
import ConstantsAndUtils.Constants as Constants
class vector:
    def __init__(self, cameraPosition: Pose2d, pitch:float, yaw: float, NumbersInRad=True):
        """
        Vector class that handles creation of vectors pointing toward a gamepiece.
        cameraPosition: Position of the camera in a 2d space (ignoring height)
        pitch: Rotation of the object (coral or algae) from top to bottom
        yaw: Rotation of the object (coral or algae) from left to right
        """

        self.self = self
        cameraX, cameraY, cameraZ = cameraPosition.X(), cameraPosition.Y(), Constants.PhotonLibConstants.ROBOT_TO_CAMERA_REEF_TRANSFORMATION.Z()

        if NumbersInRad:
            self.pose = Pose3d(cameraX, cameraY, cameraZ, Rotation3d(0, pitch, yaw))

        else:
            self.pose = Pose3d(cameraX, cameraY, cameraZ, Rotation3d(0, math.degrees(pitch), (math.degrees(yaw))))

    def getPoseAtStep(self, lenght:float)->Pose3d:
        """
        Returns the pose of this vector when extended to the given length
        """
        return self.pose.transformBy(Transform3d(lenght, 0, 0, Rotation3d()))
    
