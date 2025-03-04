from wpimath.geometry import Transform3d, Rotation3d, Translation2d, Rotation2d, Pose3d
import math

class PhotonLibConstants:
    shouldTestAprilTags = True
    APRIL_TAG_FRONT_CAMERA_NAME = "AprilTag0"
    APRIL_TAG_BACK_CAMERA_NAME = "AprilTag1"
    POSE_AMBIGUITY_TOLERANCE = 0.20
    REEF_WIDTH = 0.25
    REEF_HEIGHT = 0.25
    REEF_X_TOLERANCE = 0.5
    REEF_Y_TOLERANCE = 1
    
    # Camera Transformation    
    ROBOT_TO_CAMERA_FRONT_TRANSFORMATION = Transform3d(0.165, -0.249, 0.5245, Rotation3d(0, 0, 0)) # Front camera below the other one. This one is not tilted and for april tags. ID 0
    ROBOT_TO_CAMERA_BACK_TRANSFORMATION = Transform3d(-0.339, -0.204, 0.4745, Rotation3d(0, 0, 0)) # Back camera. This one is for april tags. ID 1

    POSE3D_REEF_LOCATIONS = [
        [Pose3d(4.75, 3.25, 0.45, Rotation3d()), Pose3d(4.75, 3.25, 0.8, Rotation3d()), Pose3d(4.75, 3.25, 1.2, Rotation3d()), Pose3d(4.75, 3.25, 1.825498, Rotation3d())],
        [Pose3d(5, 3.4, 0.45, Rotation3d()), Pose3d(5, 3.4, 0.8, Rotation3d()), Pose3d(5, 3.4, 1.2, Rotation3d()), Pose3d(4, 3.4, 1.825498, Rotation3d())],
        [Pose3d(5.3, 3.8, 0.45, Rotation3d()), Pose3d(5.3, 3.8, 0.8, Rotation3d()), Pose3d(5.3, 3.8, 1.2, Rotation3d()), Pose3d(5.3, 3.8, 1.825498, Rotation3d())],
        [Pose3d(5.3, 4.1, 0.45, Rotation3d()), Pose3d(5.3, 4.1, 0.8, Rotation3d()), Pose3d(5.3, 4.1, 1.2, Rotation3d()), Pose3d(5.3, 4.1, 1.825498, Rotation3d())],
        [Pose3d(5, 4.6, 0.45, Rotation3d()), Pose3d(5, 4.6, 0.8, Rotation3d()), Pose3d(5, 4.6, 1.2, Rotation3d()), Pose3d(4, 4.6, 1.825498, Rotation3d())],
        [Pose3d(4.75, 4.8, 0.45, Rotation3d()), Pose3d(4.75, 4.8, 0.8, Rotation3d()), Pose3d(4.75, 4.8, 1.2, Rotation3d()), Pose3d(4.75, 4.8, 1.825498, Rotation3d())],
        [Pose3d(4.2, 4.8, 0.45, Rotation3d()), Pose3d(4.2, 4.8, 0.8, Rotation3d()), Pose3d(4.2, 4.8, 1.2, Rotation3d()), Pose3d(4.2, 4.8, 1.825498, Rotation3d())],
        [Pose3d(4, 4.6, 0.45, Rotation3d()), Pose3d(4, 4.6, 0.8, Rotation3d()), Pose3d(4, 4.6, 1.2, Rotation3d()), Pose3d(4, 4.6, 1.825498, Rotation3d())],
        [Pose3d(3.6, 4.1, 0.45, Rotation3d()), Pose3d(3.6, 4.1, 0.8, Rotation3d()), Pose3d(3.6, 4.1, 1.2, Rotation3d()), Pose3d(3.6, 4.1, 1.825498, Rotation3d())],
        [Pose3d(3.6, 3.8, 0.45, Rotation3d()), Pose3d(3.6, 3.8, 0.8, Rotation3d()), Pose3d(3.6, 3.8, 1.2, Rotation3d()), Pose3d(3.6, 3.8, 1.825498, Rotation3d())],
        [Pose3d(4, 3.4, 0.45, Rotation3d()), Pose3d(4, 3.4, 0.8, Rotation3d()), Pose3d(4, 3.4, 1.2, Rotation3d()), Pose3d(4, 3.4, 1.825498, Rotation3d())],
        [Pose3d(4.2, 3.25, 0.45, Rotation3d()), Pose3d(4.2, 3.25, 0.8, Rotation3d()), Pose3d(4.2, 3.25, 1.2, Rotation3d()), Pose3d(4.2, 3.25, 1.825498, Rotation3d())],
    ]

    reef = [
        [False, False, False, False],
        [False, False, False, False],
        [False, False, False, False],
        [False, False, False, False],      
        [False, False, False, False],
        [False, False, False, False],
        [False, False, False, False],
        [False, False, False, False],      
        [False, False, False, False],
        [False, False, False, False]
    ]

    RED_APRIL_TAG_REEF_LOCATIONS = {6: (0, 1), 7: (2, 3), 8: (4, 5), 9: (6, 7), 10: (8, 9), 11: (10, 11)}
    BLUE_APRIL_TAG_REEF_LOCATIONS = {17: (0, 1), 18: (2, 3), 19: (4, 5), 20: (6, 7), 21: (8, 9), 22: (10, 11)}

class CoralAndAlgaeCameraConstants:
    shouldTestCoral = False
    shouldTestAlgae = False
    robotReal = False
    coralCameraHorizontalAngleRad = math.radians(54.06)
    coralCameraVerticalAngleRad = math.radians(41.91)
    horizontalPixels = 640
    verticalPixels = 384
    reefCameraHorizontalAnglePerPixel = coralCameraHorizontalAngleRad / horizontalPixels
    reefCameraVerticalAnglePerPixel = coralCameraVerticalAngleRad / verticalPixels
    ROBOT_TO_CAMERA_ROTATED_TRANSFORMATION = Transform3d(0.174, -0.249, 0.9305, Rotation3d(0, 0, 0)) # Front camera above the other one. This one is tilted and for coral. ID 2
    CORAL_CAMERA_NAME = "ArducamCoral"
    cameraPosition = (2.513, 3.997, 0.72)
    vectorLengthToExtend = 30 # m?
    radius = 0.1524
    confidenceTolerance = 0.60
    algaeViewedTolerance = 100 # Times we can not see the algae before we mark it as false

