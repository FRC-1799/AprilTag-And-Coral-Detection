import ntcore
import cv2
import wpimath
from ConstantsAndUtils.Constants import PhotonLibConstants
from Classes.AprilTagCamera import *
from wpimath.geometry import Pose3d, Rotation3d
import keyboard
from wpilib import DriverStation, SmartDashboard
from wpimath.units import degreesToRadians
from ConstantsAndUtils import FieldMirroringUtils

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
    inst.setServer("10.17.99.1")
    if Constants.PhotonLibConstants.robotReal:
        inst.startClient4("AprilTag")
    else:
        inst.startServer()

    # Create an instance of the AprilTag camera
    aprilTagCameraFront = AprilTagCamera(PhotonLibConstants.APRIL_TAG_FRONT_CAMERA_NAME, PhotonLibConstants.ROBOT_TO_CAMERA_FRONT_TRANSFORMATION)

    aprilTagCameraBack = AprilTagCamera(PhotonLibConstants.APRIL_TAG_BACK_CAMERA_NAME, PhotonLibConstants.ROBOT_TO_CAMERA_BACK_TRANSFORMATION)

    # Grabs the Robot's topic and publisher
    visionTable = inst.getTable("Vision")
    robotFrontPoseTopic = visionTable.getStructTopic("FrontRobotPose", Pose3d)
    robotFrontPosePublisher = robotFrontPoseTopic.publish()
    robotBackPoseTopic = visionTable.getStructTopic("BackRobotPose", Pose3d)
    robotBackPosePublisher = robotBackPoseTopic.publish()
    odometryRobotPoseTopic = inst.getStructTopic("RobotPose", Pose3d)
    odometryRobotPoseSubscriber = odometryRobotPoseTopic.subscribe(Pose3d(), ntcore.PubSubOptions(keepDuplicates=True))
    aprilTagFrontCameraConnectionTopic = visionTable.getBooleanTopic("FrontCameraConnection")
    aprilTagFrontCameraConnectionPublisher = aprilTagFrontCameraConnectionTopic.publish()
    aprilTagBackCameraConnectionTopic = visionTable.getBooleanTopic("BackCameraConnection")
    aprilTagBackCameraConnectionPublisher = aprilTagBackCameraConnectionTopic.publish()
    aprilTagFrontCameraTimestampTopic = inst.getDoubleTopic("RobotPoseTimestampFront")
    aprilTagFrontCameraTimestampPublisher = aprilTagFrontCameraTimestampTopic.publish()
    aprilTagBackCameraTimestampTopic = inst.getDoubleTopic("RobotPoseTimestampBack")
    aprilTagBackCameraTimestampPublisher = aprilTagBackCameraTimestampTopic.publish()

    robotPositionFront = None
    
    while True:
        if keyboard.is_pressed("q"):
            aprilTagFrontCameraConnectionPublisher.set(False)
            aprilTagBackCameraConnectionPublisher.set(False)
            inst.disconnect()
            cv2.destroyAllWindows()
            
            break

        if Constants.PhotonLibConstants.shouldTestAprilTags:
        
            if aprilTagCameraFront.isConnected():
                aprilTagFrontCameraConnectionPublisher.set(True)
                aprilTagsFront = aprilTagCameraFront.get_tags()
                if aprilTagsFront:
                    robotPositionFront, timestamp = fetchRobotPosition(aprilTagCameraFront)
                    timeOffset = inst.getServerTimeOffset()
                    if timeOffset != None and timestamp != None:
                        timestamp += (timeOffset / 1000000)
                    else:
                        timestamp = 0

                    if robotPositionFront:
                        robotFrontPosePublisher.set(robotPositionFront.estimatedPose)
                        aprilTagFrontCameraTimestampPublisher.set(timestamp)
                    else:
                        robotFrontPosePublisher.set(Pose3d(Translation3d(0, 0, 0), Rotation3d(0, 0, 0)))
                        
            if aprilTagCameraBack.isConnected():
                aprilTagBackCameraConnectionPublisher.set(True)
                aprilTagsBack = aprilTagCameraBack.get_tags()
                if aprilTagsBack:
                    robotPositionBack, timestamp = fetchRobotPosition(aprilTagCameraBack)
                    timeOffset = inst.getServerTimeOffset()
                    if timeOffset != None and timestamp != None:
                        timestamp += (timeOffset / 1000000)
                    if robotPositionBack:
                        robotBackPosePublisher.set(robotPositionBack.estimatedPose)
                        aprilTagBackCameraTimestampPublisher.set(timestamp)
                        
                    else:
                        robotBackPosePublisher.set(Pose3d(Translation3d(0, 0, 0), Rotation3d(0, 0, 0)))

            
if __name__ == "__main__":
    main()