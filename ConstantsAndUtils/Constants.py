from wpimath.geometry import Transform3d, Rotation3d, Translation2d, Rotation2d, Pose3d, Transform2d, Translation3d

class BaseConstants:
    serverName = "127.0.0.1"

class PhotonLibConstants:
    # Debug values and camera names
    shouldTestAprilTags = False
    shouldTestReef = True
    robotReal = True
    APRIL_TAG_FRONT_CAMERA_NAME = "AprilTag0"
    APRIL_TAG_BACK_CAMERA_NAME = "AprilTag1"
    REEF_CAMERA_NAME = "Reef2"
    
    
    # Camera Transformation    
    ROBOT_TO_CAMERA_FRONT_TRANSFORMATION = Transform3d(0.08, 0.255, 0.552, Rotation3d(0, 0, 0)) # Front camera below the other one. This one is not tilted and for april tags. ID 0
    ROBOT_TO_CAMERA_BACK_TRANSFORMATION = Transform3d(-0.293, 0.297, 0.627, Rotation3d.fromDegrees(0, 0, 180)) # Back camera. This one is for april tags. ID 1
    ROBOT_TO_CAMERA_REEF_TRANSFORMATION = Transform3d(0.118, 0.266, 1.001, Rotation3d.fromDegrees(0, 10, 0)) # Front camera above the other one. This one is tilted and for coral. ID 2
    ROBOT_TO_CAMERA_REEF_TRANSFORMATION2D = Transform2d(-0.118, -0.266, Rotation2d.fromDegrees(10)) # Front camera above the other one. This one is tilted and for coral. ID 2

    # Detection Info
    OBJECT_IDS = {0: "Algae", 1: "Coral"}
    RED_APRIL_TAG_REEF_LOCATIONS = {6: (0, 1), 7: (2, 3), 8: (4, 5), 9: (6, 7), 10: (8, 9), 11: (10, 11)}
    BLUE_APRIL_TAG_REEF_LOCATIONS = {17: (0, 1), 18: (2, 3), 19: (4, 5), 20: (6, 7), 21: (8, 9), 22: (10, 11)}
    vectorLengthToExtend = 50 # meters
    POSE_AMBIGUITY_TOLERANCE = 0.20
    REEF_WIDTH = 0.25 
    REEF_HEIGHT = 0.25
    REEF_X_TOLERANCE = 0.5
    REEF_Y_TOLERANCE = 1
    ALGAE_VIEWED_TOLERANCE = 100 # frames

    CORAL_RADIUS = 0.3 # meters
    ALGAE_RADIUS = 0.203 # meters

    DEFAULT_ROBOT_POSE = Pose3d(Translation3d(2, 4, 0), Rotation3d(0, 0, 0))

# Algae and Coral Shapes for debugging
algae = [
    [False, False, False, False, False, False], # L2 algae
    [False, False, False, False, False, False]  # L3 algae
]

coral = [
    [False, False, False, False, False, False, False, False, False, False, False, False], # L1
    [False, False, False, False, False, False, False, False, False, False, False, False], # L2
    [False, False, False, False, False, False, False, False, False, False, False, False], # L3
    [False, False, False, False, False, False, False, False, False, False, False, False]  # L4
]