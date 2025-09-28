import time
import ntcore
import cv2
import wpimath
from ConstantsAndUtils.Constants import PhotonLibConstants, BaseConstants
from Classes.AprilTagCamera import *
from Classes.ReefCamera import *
from wpimath.geometry import Pose3d, Rotation3d
# import keyboard
from wpilib import DriverStation, SmartDashboard
from wpimath.units import degreesToRadians
from ConstantsAndUtils import FieldMirroringUtils
from ntcore import StructPublisher, BooleanPublisher, DoublePublisher, StructSubscriber, NetworkTable, PubSubOptions
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
    inst.setServer(BaseConstants.serverName)
    if PhotonLibConstants.robotReal:
        inst.startClient4("ReefAprilTagCamera")
    else:
        inst.startServer()

    # Create an instance of the AprilTag and Reef cameras
    aprilTagCameraFront = AprilTagCamera(PhotonLibConstants.APRIL_TAG_FRONT_CAMERA_NAME, PhotonLibConstants.ROBOT_TO_CAMERA_FRONT_TRANSFORMATION, apriltag.AprilTagField.k2025ReefscapeWelded)
    aprilTagCameraBack = AprilTagCamera(PhotonLibConstants.APRIL_TAG_BACK_CAMERA_NAME, PhotonLibConstants.ROBOT_TO_CAMERA_BACK_TRANSFORMATION, apriltag.AprilTagField.k2025ReefscapeWelded)
    reefCamera = ReefCamera(PhotonLibConstants.REEF_CAMERA_NAME, PhotonLibConstants.ROBOT_TO_CAMERA_REEF_TRANSFORMATION)


    visionTable: NetworkTable = inst.getTable("Vision")

    # Publishers to publish the 2 camera's estimated positions, and the odometry's position
    robotFrontPosePublisher: StructPublisher = visionTable.getStructTopic("FrontRobotPose", Pose3d).publish()
    robotBackPosePublisher: StructPublisher = visionTable.getStructTopic("BackRobotPose", Pose3d).publish()
    odometryRobotPoseSubscriber: StructSubscriber = inst.getStructTopic("RobotPose", Pose3d).subscribe(PhotonLibConstants.DEFAULT_ROBOT_POSE, ntcore.PubSubOptions(keepDuplicates=True))

    # Camera connection statuses and timestamps for debugging
    aprilFrontCameraConnectionPublisher: BooleanPublisher = visionTable.getBooleanTopic("FrontCameraConnection").publish()
    aprilBackCameraConnectionPublisher: BooleanPublisher = visionTable.getBooleanTopic("BackCameraConnection").publish()
    reefCameraConnectionPublisher: BooleanPublisher = visionTable.getBooleanTopic("ReefCameraConnection").publish()
    aprilFrontCameraTimestampPublisher: DoublePublisher = inst.getDoubleTopic("RobotPoseTimestampFront").publish()
    aprilBackCameraTimestampPublisher: DoublePublisher = inst.getDoubleTopic("RobotPoseTimestampBack").publish()

    robotPositionFront = None
    
    # Hitboxes, publishers and subscribers made here
    coralHitboxes, coralHitboxLocations = hitbox.makeCoralHitboxes()
    algaeHitboxes, algaeHitboxLocations = hitbox.makeAlgaeHitboxes()
    coralSubscribers, coralPublishers, algaeSubscribers, algaePublishers = reefCamera.createReefPubSub(visionTable)

    # Debug topics, publishers and subscribers
    vectorPose3dsPublisher = visionTable.getStructArrayTopic("VectorPose3ds", Pose3d).publish()
    coralHitboxLocationsPublisher = visionTable.getStructArrayTopic("CoralHitboxLocations", Pose3d).publish()
    algaeHitboxLocationsPublisher = visionTable.getStructArrayTopic("AlgaeHitboxLocations", Pose3d).publish()
    odometryRobotPosePublisher = inst.getStructTopic("RobotPose", Pose3d).publish()
    coralHitboxLocationsPublisher.set(coralHitboxLocations)
    algaeHitboxLocationsPublisher.set(algaeHitboxLocations)
    odometryRobotPosePublisher.set(PhotonLibConstants.DEFAULT_ROBOT_POSE) 

    while True:
        frontCameraConnection, backCameraConnection, reefCameraConnection = aprilTagCameraFront.isConnected(), aprilTagCameraBack.isConnected(), reefCamera.isConnected()

        aprilFrontCameraConnectionPublisher.set(frontCameraConnection)
        aprilBackCameraConnectionPublisher.set(backCameraConnection)
        reefCameraConnectionPublisher.set(reefCameraConnection)

        
        # Checks if cameras are connected and see April Tags. If they do, publish their estimated positions
        if PhotonLibConstants.shouldTestAprilTags:
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

        
        if PhotonLibConstants.shouldTestReef:
            if reefCameraConnection:
                coralNetworkTables, algaeNetworkTables = ReefCamera.grabPastReef(coralSubscribers, algaeSubscribers)
                robotOdometryPose = odometryRobotPoseSubscriber.get()
                objectsInFrame = reefCamera.getObjects()
                algaeOnFrame, coralOnFrame = reefCamera.findCoralsAndAlgaesOnReef(objectsInFrame, robotOdometryPose, coralHitboxes, algaeHitboxes)

                # Only updates the 2 closest reef sections. This is not done with coral, so change if needed
                algaeToPublish = reefCamera.manageViewedAlgae(algaeNetworkTables, algaeHitboxes, algaeOnFrame, robotOdometryPose)
                coralToPublish = reefCamera.manageViewedCorals(coralNetworkTables, coralOnFrame)
                reefCamera.updateReef(coralPublishers, algaePublishers, coralToPublish, algaeToPublish)

                # Debug stuff here
                vectorPose3dsPublisher.set(reefCamera.allPositions)
                    


        # if keyboard.is_pressed("q"):
        #     aprilFrontCameraConnectionPublisher.set(False)
        #     aprilBackCameraConnectionPublisher.set(False)
        #     inst.disconnect()
        #     cv2.destroyAllWindows()
        #     break

        time.sleep(0.01) # 10 ms

            
if __name__ == "__main__":
    main()