import time
import ntcore
import cv2
import wpimath
from ConstantsAndUtils.Constants import PhotonLibConstants, CoralAndAlgaeCameraConstants
from Classes.AprilTagCamera import *
from wpimath.geometry import Pose3d, Rotation3d
import keyboard
import Classes.CoralCamera as CoralCamera
from wpilib import DriverStation, SmartDashboard
from wpimath.units import degreesToRadians
from Classes.Hitbox import hitbox
from ConstantsAndUtils import FieldMirroringUtils
import pyudev
import os

def grab_past_reef(reefSubscribers, algaeSubscribers) -> list[list]:
    """
    Grabs the past value of the reef
    
    Parameters:
    reefSubscribers - Subscribers of the reef

    Returns:
    list[list] - List of a list of boolean values for the reef
    """

    defaultValue = [False for _ in range(12)]
    reefCoral = [[] for _ in range(12)]
    for subscriber in reefSubscribers:
        reefLevelBools = subscriber.get(defaultValue)
        for i, level in enumerate(reefCoral):
            level.append(reefLevelBools[i])
            
    defaultAlgaeValue = [False for _ in range(6)]
    reefAlgae = [[] for _ in range(6)]
    for subscriber in algaeSubscribers:
        reefLevelBools = subscriber.get(defaultAlgaeValue)
        for i, level in enumerate(reefAlgae):
            level.append(reefLevelBools[i])

            
    return reefCoral, reefAlgae 

def coralCameraIndex(device) -> None | int:
    
    context = pyudev.Context()
    device_file = "/dev/video{}".format(device)
    deviceClass = pyudev.Devices.from_device_file(context, device_file)
    info = { item[0] : item[1] for item in deviceClass.items()}
    print(info["ID_MODEL"])
    if info["ID_MODEL"] == Constants.CoralAndAlgaeCameraConstants.CORAL_CAMERA_NAME:
        return device
    else:
        return None


    
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
    
    def updateReef(coralPublishers, algaePublishers, coralValuesSeenPublisher, algaeValuesSeenPublisher):
        """
        Updates the reef's values on Network Tables
        """

        coralPose3dSeen = []
        for level, publisher in enumerate(coralPublishers):
            coralLevelBoolVals = []
            
            for coralSection in reef:
                coralLevelBoolVals.append(coralSection[level])
                if coralSection[level] and pose3dCoralValues[reef.index(coralSection)][level] != None:
                    coralPose3dSeen.append(pose3dCoralValues[reef.index(coralSection)][level])
            publisher.set(coralLevelBoolVals) 
        
        coralValuesSeenPublisher.set(coralPose3dSeen)
        
        algaePose3dSeen = []
        for level, publisher in enumerate(algaePublishers):
            algaeLevelBoolVals = []
            
            for algaeSection in reef:
                algaeLevelBoolVals.append(algaeSection[level])
                if algaeSection[level] and pose3dAlgaeValues[reef.index(algaeSection)][level] != None:
                    algaePose3dSeen.append(pose3dAlgaeValues[reef.index(algaeSection)][level])
                    
            publisher.set(algaeLevelBoolVals) 
            
        algaeValuesSeenPublisher.set(algaePose3dSeen)

    def createReefPubSub(visionTable) -> list[list]:
        """
        Creates the publishers and subscribers for the reef, including both the algae and coral
        subscribers and publishers

        Returns:
        list[list] - List of all of the lists for the publishers and subscribers
        """

        coralTable = visionTable.getSubTable("CoralPositions")
        algaeTable = visionTable.getSubTable("ReefPositions")
        
        defaultReef = [False for _ in range(12)]
        defaultAlgae = [False for _ in range(6)]

        reefL1Topic = coralTable.getBooleanArrayTopic("ReefL1")
        reefL2Topic = coralTable.getBooleanArrayTopic("ReefL2")
        reefL3Topic = coralTable.getBooleanArrayTopic("ReefL3")
        reefL4Topic = coralTable.getBooleanArrayTopic("ReefL4")
        algae1Topic = algaeTable.getBooleanArrayTopic("Algae1")
        algae2Topic = algaeTable.getBooleanArrayTopic("Algae2")
        coralSubscribers = [reefL1Topic.subscribe(defaultReef), reefL2Topic.subscribe(defaultReef), reefL3Topic.subscribe(defaultReef), reefL4Topic.subscribe(defaultReef)] 
        coralPublishers = [reefL1Topic.publish(), reefL2Topic.publish(), reefL3Topic.publish(), reefL4Topic.publish()]
        algaeSubscribers = [algae1Topic.subscribe(defaultAlgae), algae2Topic.subscribe(defaultAlgae)]
        algaePublishers = [algae1Topic.publish(), algae2Topic.publish()]
        coralValuesSeenTopic = coralTable.getStructArrayTopic("CoralSeen",Pose3d)
        coralValuesSeenPublisher = coralValuesSeenTopic.publish()
        algaeValuesSeenTopic = algaeTable.getStructArrayTopic("AlgaeSeen", Pose3d)
        algaeValuesSeenPublisher = algaeValuesSeenTopic.publish()


        return coralSubscribers, coralPublishers, algaeSubscribers, algaePublishers, coralValuesSeenPublisher, algaeValuesSeenPublisher
    print("test2")
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
    algaeNotSeenCounterList = [[0 for _ in range(2)] for _ in range(12)]

    print("test1")
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
    aprilTagCameraConnectionTopic = visionTable.getBooleanTopic("AprilTagCameraConnection")
    aprilTagCameraConnectionPublisher = aprilTagCameraConnectionTopic.publish()
    aprilTagFrontCameraTimestampTopic = visionTable.getDoubleTopic("RobotPoseTimestampFront")
    aprilTagFrontCameraTimestampPublisher = aprilTagFrontCameraTimestampTopic.publish()
    aprilTagBackCameraTimestampTopic = visionTable.getDoubleTopic("RobotPoseTimestampBack")
    aprilTagBackCameraTimestampPublisher = aprilTagBackCameraTimestampTopic.publish()

    robotPositionFront = None

    # Reef Publishers and Subscribers
    coralSubscribers, coralPublishers, algaeSubscribers, algaePublishers, coralValuesSeenPublisher, algaeValuesSeenPublisher = createReefPubSub(visionTable)
    pitchYawTopic = inst.getStructArrayTopic("Pitch Yaw Line", Pose3d)
    pitchYawPublisher = pitchYawTopic.publish()

    reefCameraConnectionTopic = inst.getBooleanTopic("ReefCameraConnection") # if the reef camera is connected
    reefCameraConnectionPublisher = reefCameraConnectionTopic.getEntry(True)

    # Reef Pose3D for debugging purposes
    reefPose3dTable = inst.getTable("reefPose3dTable")
    pose3dTableTopic = reefPose3dTable.getStructArrayTopic("pose", Pose3d)
    pose3dPublisher = pose3dTableTopic.publish()
    reefPose3dToPublish = []

    print("test")

    deviceNumber = 0
    for deviceIndex in range(1,4):
        deviceNumber = coralCameraIndex(deviceIndex)
        if deviceNumber != None:
            break

    print(deviceNumber)
    coralCamera = CoralCamera.CoralCamera(deviceNumber)
    reefCameraConnectionPublisher.set(coralCamera.camera.isOpened())
    SmartDashboard.putBoolean("wasConnected", coralCamera.camera.isOpened())
    
    coralHitboxes, pose3dCoralValues = hitbox.makeCoralHitboxes()
    algaeHitboxes, pose3dAlgaeValues = hitbox.makeAlgaeHitboxes()
    
    while True:
        if keyboard.is_pressed("q"):
            inst.stopServer()
            cv2.destroyAllWindows()
            break
        
        reefCameraConnectionPublisher.set(coralCamera.camera.isOpened())
        # if not coralCamera.camera.isOpened():
        #     coralCamera = None
        #     time.sleep(10)
        #     coralCamera = CoralCamera.CoralCamera(deviceNumber)


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
            robotPosition = Pose3d(Translation3d(2.55, 4.03, 0), Rotation3d(0,0,0))
        if robotPositionFront and (Constants.CoralAndAlgaeCameraConstants.shouldTestAlgae or Constants.CoralAndAlgaeCameraConstants.shouldTestCoral):
            reef, algae = grab_past_reef(coralSubscribers, algaeSubscribers)
            coralCamera.findCoralsAndAlgaesOnReef(reef, algae, coralHitboxes, algaeHitboxes, algaeNotSeenCounterList, robotPositionFront.estimatedPose)
            updateReef(coralPublishers, algaePublishers, coralValuesSeenPublisher, algaeValuesSeenPublisher)

            pitchYawPublisher.set(coralCamera.allPositions)
                
            for reefSection in range(len(reef)):
                for index in range(len(reef[0])):
                    if reef[reefSection][index]:
                        reefPose3dToPublish.append(pose3dCoralValues[reefSection][index])
                    
            pose3dPublisher.set(reefPose3dToPublish)
                             
    time.sleep(0.01)
            
if __name__ == "__main__":
    main()