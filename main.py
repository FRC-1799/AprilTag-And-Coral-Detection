import time
import ntcore
import cv2
import wpimath
from ConstantsAndUtils.Constants import PhotonLibConstants
from Classes.AprilTagCamera import *
from Classes.ReefCamera import *
from wpimath.geometry import Pose3d, Rotation3d
import keyboard
from wpilib import DriverStation, SmartDashboard
from wpimath.units import degreesToRadians
from ConstantsAndUtils import FieldMirroringUtils
from ntcore import StructPublisher, BooleanPublisher, DoublePublisher, StructSubscriber
import robotpy_apriltag as apriltag

def fetchRobotPosition(camera) -> tuple[Pose3d, float]:
    """
    Calculates robot position and adds it to the queue

    Returns:
    tuple[Pose3d, float] - the position of the robot as well as the timestamp this position was 
    obtained at
    """
    robotPosition, timestamp = camera.get_estimated_global_pose()
    
    if DriverStation.getAlliance() == DriverStation.Alliance.kRed:
        robotPosition=robotPosition.relativeTo(FieldMirroringUtils.FIELD_WIDTH, FieldMirroringUtils.FIELD_HEIGHT, 0, Rotation3d)
    
    return robotPosition, timestamp 
    
def main():
    
    
    
    # Start NT server
    inst = ntcore.NetworkTableInstance.getDefault()
    inst.setServer(Constants.baseConstants.serverName)
    if Constants.PhotonLibConstants.robotReal:
        inst.startClient4("AprilTag")
    else:
        inst.startServer()

    # Create an instance of the AprilTag and Reef cameras
    aprilTagCameraFront = AprilTagCamera(PhotonLibConstants.APRIL_TAG_FRONT_CAMERA_NAME, PhotonLibConstants.ROBOT_TO_CAMERA_FRONT_TRANSFORMATION, apriltag.AprilTagField.k2025ReefscapeWelded)
    aprilTagCameraBack = AprilTagCamera(PhotonLibConstants.APRIL_TAG_BACK_CAMERA_NAME, PhotonLibConstants.ROBOT_TO_CAMERA_BACK_TRANSFORMATION, apriltag.AprilTagField.k2025ReefscapeWelded)
    reefCamera = ReefCamera(PhotonLibConstants.REEF_CAMERA_NAME, PhotonLibConstants.ROBOT_TO_CAMERA_REEF_TRANSFORMATION)


    visionTable = inst.getTable("Vision")

    # Publishers to publish the 2 camera's estimated positions, and the odometry's position
    robotFrontPosePublisher: StructPublisher = visionTable.getStructTopic("FrontRobotPose", Pose3d).publish()
    robotBackPosePublisher: StructPublisher = visionTable.getStructTopic("BackRobotPose", Pose3d).publish()
    odometryRobotPoseSubscriber: StructSubscriber = inst.getStructTopic("RobotPose", Pose3d).subscribe(Pose3d(), ntcore.PubSubOptions(keepDuplicates=True))

    # Camera connection statuses and timestamps for debugging
    aprilFrontCameraConnectionPublisher: BooleanPublisher = visionTable.getBooleanTopic("FrontCameraConnection").publish()
    aprilBackCameraConnectionPublisher: BooleanPublisher = visionTable.getBooleanTopic("BackCameraConnection").publish()
    reefCameraConnectionPublisher: BooleanPublisher = visionTable.getBooleanTopic("ReefCameraConnection").publish()
    aprilFrontCameraTimestampPublisher: DoublePublisher = inst.getDoubleTopic("RobotPoseTimestampFront").publish()
    aprilBackCameraTimestampPublisher: DoublePublisher = inst.getDoubleTopic("RobotPoseTimestampBack").publish()

    robotPositionFront = None
    
    while True:
        frontCameraConnection, backCameraConnection, reefCameraConnection = aprilTagCameraFront.isConnected(), aprilTagCameraBack.isConnected(), reefCamera.isConnected()

        aprilFrontCameraConnectionPublisher.set(frontCameraConnection)
        aprilBackCameraConnectionPublisher.set(backCameraConnection)
        reefCameraConnectionPublisher.set(reefCameraConnection)

        
        # Checks if cameras are connected and see April Tags. If they do, publish their estimated positions
        if Constants.PhotonLibConstants.shouldTestAprilTags:
            if frontCameraConnection:
                aprilTagsFront = aprilTagCameraFront.get_tags()
                if aprilTagsFront:
                    robotPositionFront, timestampFront = fetchRobotPosition(aprilTagCameraFront)
                    timeOffset = inst.getServerTimeOffset()
                    if timeOffset != None and timestampFront != None:
                        timestampFront += (timeOffset / 1000000)
                    else:
                        timestampFront = 0

                    if robotPositionFront:
                        robotFrontPosePublisher.set(robotPositionFront.estimatedPose)
                        aprilFrontCameraTimestampPublisher.set(timestampFront)
                    else:
                        robotFrontPosePublisher.set(Pose3d(Translation3d(0, 0, 0), Rotation3d(0, 0, 0)))
                        
            if backCameraConnection:
                aprilTagsBack = aprilTagCameraBack.get_tags()
                if aprilTagsBack:
                    robotPositionBack, timestampBack = fetchRobotPosition(aprilTagCameraBack)
                    timeOffset = inst.getServerTimeOffset()
                    if timeOffset != None and timestampBack != None:
                        timestampBack += (timeOffset / 1000000)
                    else: 
                        timestampBack = 0

                    if robotPositionBack:
                        robotBackPosePublisher.set(robotPositionBack.estimatedPose)
                        aprilBackCameraTimestampPublisher.set(timestampBack)
                    else:
                        robotBackPosePublisher.set(Pose3d(Translation3d(0, 0, 0), Rotation3d(0, 0, 0)))

        if PhotonLibConstants.shouldTestCoral:
            if reefCameraConnection:
                reefCamera.getObjects()

        if keyboard.is_pressed("q"):
            aprilFrontCameraConnectionPublisher.set(False)
            aprilBackCameraConnectionPublisher.set(False)
            inst.disconnect()
            cv2.destroyAllWindows()
            break

        time.sleep(0.01) # 10 ms

            
if __name__ == "__main__":
    main()