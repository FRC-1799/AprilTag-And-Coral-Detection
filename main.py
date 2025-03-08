import time
import ntcore
import cv2
import wpimath
from ConstantsAndUtils.Constants import PhotonLibConstants, CoralAndAlgaeCameraConstants
from Classes.AprilTagCamera import *
from wpimath.geometry import Pose3d, Rotation3d
import keyboard
import Classes.CoralCamera as CoralCamera
from wpilib import DriverStation
from wpimath.units import degreesToRadians
from Classes.Hitbox import hitbox
from ConstantsAndUtils import FieldMirroringUtils
import pyudev

def grab_past_reef(reefSubscribers) -> list[list]:
    """
    Grabs the past value of the reef
    
    Parameters:
    reefSubscribers - Subscribers of the reef

    Returns:
    list[list] - List of a list of boolean values for the reef
    """

    defaultValue = [False for _ in range(12)]
    reef = [[] for _ in range(12)]
    for subscriber in reefSubscribers:
        reefLevelBools = subscriber.get(defaultValue)
        for i, level in enumerate(reef):
            level.append(reefLevelBools[i])
            
    return reef 

def coralCameraIndex() -> int:
    context = pyudev.Context()
    device_file = "/dev/video{}".format(device)
    device = pyudev.Devices.from_device_file(context, device_file)
    info = { item[0] : item[1] for item in device.items()}
    return info["ID_SERIAL_SHORT"]



    
def main():
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
    
    def updateReef(coralPublishers, algaePublishers):
        """
        Updates the reef's values on Network Tables
        """

        for level, publisher in enumerate(coralPublishers):
            coralLevelBoolVals = []
            for coralSection in reef:
                coralLevelBoolVals.append(coralSection[level])
            publisher.set(coralLevelBoolVals) 
            
        for level, publisher in enumerate(algaePublishers):
            algaeLevelBoolVals = []
            for algaeSection in reef:
                algaeLevelBoolVals.append(algaeSection[level])
            publisher.set(algaeLevelBoolVals) 

    def createReefPubSub(visionTable) -> list[list]:
        """
        Creates the publishers and subscribers for the reef, including both the algae and coral
        subscribers and publishers

        Returns:
        list[list] - List of all of the lists for the publishers and subscribers
        """

        reefTable = visionTable.getTable("CoralLocationTable")
        reefL1Topic = reefTable.getBooleanArrayTopic("ReefL1")
        reefL2Topic = reefTable.getBooleanArrayTopic("ReefL2")
        reefL3Topic = reefTable.getBooleanArrayTopic("ReefL3")
        reefL4Topic = reefTable.getBooleanArrayTopic("ReefL4")
        algae1Topic = reefTable.getBooleanArrayTopic("Algae1")
        algae2Topic = reefTable.getBooleanArrayTopic("Algae2")
        coralSubscribers = [reefL1Topic.subscribe(defaultReef), reefL2Topic.subscribe(defaultReef), reefL3Topic.subscribe(defaultReef), reefL4Topic.subscribe(defaultReef)] 
        coralPublishers = [reefL1Topic.publish(), reefL2Topic.publish(), reefL3Topic.publish(), reefL4Topic.publish()]
        algaeSubscribers = [algae1Topic.subscribe(defaultAlgae), algae2Topic.subscribe(defaultAlgae)]
        algaePublishers = [algae1Topic.publish(), algae2Topic.publish()]

        return coralSubscribers, coralPublishers, algaeSubscribers, algaePublishers
    
    # Start NT server
    inst = ntcore.NetworkTableInstance.getDefault()
    inst.setServerTeam(1799)
    if Constants.CoralAndAlgaeCameraConstants.robotReal:
        inst.startClient4("Vision")
    else:
        inst.startServer()


    # Reef Values
    reef = [[False for _ in range(4)] for _ in range(12)]
    algae = [[False for _ in range(2)] for _ in range(12)]
    defaultReef = [False for _ in range(4)] # Used for subscribing
    defaultAlgae = [False for _ in range(2)]
    algaeNotSeenCounterList = [[0 for _ in range(2)] for _ in range(12)]


    # Create an instance of the AprilTag camera
    aprilTagCameraFront = AprilTagCamera(PhotonLibConstants.APRIL_TAG_FRONT_CAMERA_NAME, PhotonLibConstants.ROBOT_TO_CAMERA_FRONT_TRANSFORMATION)
    aprilTagCameraBack = AprilTagCamera(PhotonLibConstants.APRIL_TAG_BACK_CAMERA_NAME, PhotonLibConstants.ROBOT_TO_CAMERA_BACK_TRANSFORMATION)

    # Grabs the Robot's topic and publisher
    visionTable = inst.getTable("Vision")
    robotFrontPoseTopic = visionTable.getStructTopic("FrontRobotPose", Pose3d)
    robotFrontPosePublisher = robotFrontPoseTopic.publish()
    robotBackPoseTopic = visionTable.getStructTopic("BackRobotPose", Pose3d)
    robotBackPosePublisher = robotBackPoseTopic.publish()
    aprilTagCameraConnectionTopic = visionTable.getBooleanTopic("AprilTagCameraConnection")
    aprilTagCameraConnectionPublisher = aprilTagCameraConnectionTopic.publish()
    aprilTagFrontCameraTimestampTopic = visionTable.getDoubleTopic("RobotPoseTimestampFront")
    aprilTagFrontCameraTimestampPublisher = aprilTagFrontCameraTimestampTopic.publish()
    aprilTagBackCameraTimestampTopic = visionTable.getDoubleTopic("RobotPoseTimestampBack")
    aprilTagBackCameraTimestampPublisher = aprilTagBackCameraTimestampTopic.publish()

    robotPosition = None

    # Reef Publishers and Subscribers
    coralSubscribers, coralPublishers, algaeSubscribers, algaePublishers = createReefPubSub(visionTable)

    reefCameraConnectionTopic = inst.getBooleanTopic("ReefCameraConnection") # if the reef camera is connected
    reefCameraConnectionPublisher = reefCameraConnectionTopic.getEntry(True)

    # Reef Pose3D for debugging purposes
    reefPose3dTable = inst.getTable("reefPose3dTable")
    pose3dTableTopic = reefPose3dTable.getStructArrayTopic("pose", Pose3d)
    pose3dPublisher = pose3dTableTopic.publish()
    reefPose3dToPublish = []

    coralCamera = CoralCamera.CoralCamera(cameraIndex=coralCameraIndex())
    reefCameraConnectionPublisher.set(coralCamera.camera.isOpened())
    
    coralHitboxes, pose3dReefValues = hitbox.makeCoralHitboxes()
    algaeHitboxes, pose3dAlgaeValues = hitbox.makeAlgaeHitboxes()
    
    while True:
        if keyboard.is_pressed("q"):
            inst.stopServer()
            cv2.destroyAllWindows()
            break

        if Constants.PhotonLibConstants.shouldTestAprilTags:
        
            if aprilTagCameraFront.isConnected():
                aprilTagCameraConnectionPublisher.set(True)
                aprilTagsFront = aprilTagCameraFront.get_tags()
                if aprilTagsFront:
                    robotPositionFront, timestamp = fetchRobotPosition(aprilTagCameraFront)
                    if robotPositionFront:
                        robotFrontPosePublisher.set(robotPositionFront.estimatedPose)
                        aprilTagFrontCameraTimestampPublisher.set(timestamp)
                        
                    else:
                        robotFrontPosePublisher.set(Pose3d(Translation3d(0, 0, 0), Rotation3d(0, 0, 0)))
                        
            if aprilTagCameraBack.isConnected():
                aprilTagCameraConnectionPublisher.set(True)
                aprilTagsBack = aprilTagCameraBack.get_tags()
                if aprilTagsBack:
                    robotPositionBack, timestamp = fetchRobotPosition(aprilTagCameraBack)
                    if robotPositionBack:
                        robotBackPosePublisher.set(robotPositionBack.estimatedPose)
                        aprilTagBackCameraTimestampPublisher.set(timestamp)
                        
                    else:
                        robotBackPosePublisher.set(Pose3d(Translation3d(0, 0, 0), Rotation3d(0, 0, 0)))
                       

        # Only used for testing just coral
        if not Constants.PhotonLibConstants.shouldTestAprilTags:
            robotPosition = Pose3d(Translation3d(0,0,0), Rotation3d(0,0,0))
            
        if coralCamera.camera.isOpened() and robotPosition and (Constants.CoralAndAlgaeCameraConstants.shouldTestAlgae or Constants.CoralAndAlgaeCameraConstants.shouldTestCoral):
            reefCameraConnectionPublisher.set(True)
            reef = grab_past_reef(coralSubscribers)
            coralCamera.findCoralsAndAlgaesOnReef(reef, algae, coralHitboxes, algaeHitboxes, algaeNotSeenCounterList, robotPosition)
            updateReef(coralPublishers, algaePublishers)
                
            for reefSection in range(len(reef)):
                for index in range(len(reefSection)):
                    if reef[reefSection][index]:
                        reefPose3dToPublish.append(pose3dReefValues[reefSection][index])
                    
            pose3dPublisher.set(reefPose3dToPublish)
                             
    time.sleep(0.01)
            
if __name__ == "__main__":
    main()