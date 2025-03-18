import time
import ntcore
import cv2
import wpimath
from ConstantsAndUtils.Constants import CoralAndAlgaeCameraConstants
from wpimath.geometry import Pose3d, Rotation3d, Translation3d
import keyboard
import Classes.CoralCamera as CoralCamera
import ConstantsAndUtils.Constants as Constants
from wpilib import DriverStation, SmartDashboard
from wpimath.units import degreesToRadians
from Classes.Hitbox import hitbox
from ConstantsAndUtils import FieldMirroringUtils
#import pyudev
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
    reefCoral = [[] for _ in range(4)]
    for level, subscriber in enumerate(reefSubscribers):
        reefCoral[level] = subscriber.get(defaultValue)
            
    defaultAlgaeValue = [False for _ in range(6)]
    reefAlgae = [[] for _ in range(2)]
    for level, subscriber in enumerate(algaeSubscribers):
        reefAlgae[level] = subscriber.get(defaultAlgaeValue)

            
    return reefCoral, reefAlgae 

def coralCameraIndex(device) -> None | int:
    return 0
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
    # def fetchRobotPosition(camera) -> tuple[Pose3d, float]:
    #     """
    #     Calculates robot position and adds it to the queue

    #     Returns:
    #     tuple[Pose3d, float] - the position of the robot as well as the timestamp this position was 
    #     obtained at
    #     """
    #     robotPosition, timestamp = camera.get_estimated_global_pose()
        
    #     if DriverStation.getAlliance() == DriverStation.Alliance.kRed:
    #         robotPosition=robotPosition.relativeTo(FieldMirroringUtils.FIELD_WIDTH, FieldMirroringUtils.FIELD_HEIGHT, 0, Rotation3d)
        
    #     return robotPosition, timestamp
    
    def updateReef(coralPublishers, algaePublishers, coralValuesSeenPublisher, algaeValuesSeenPublisher, coralTotalList, algaeTotalList, ):
        """
        Updates the reef's values on Network Tables
        """

        coralPose3dSeen = []
        for publisher in coralPublishers:
            
            for coralLevel in coralTotalList:
                publisher.set(coralLevel)
                for coral in coralLevel:
                    if coral:
                        coralPose3dSeen.append(pose3dCoralValues[coralTotalList.index(coralLevel)][coralLevel.index(coral)])
            
        
        coralValuesSeenPublisher.set(coralPose3dSeen)
        
        algaePose3dSeen = []
        for algaeLevel, publisher in zip(algaeTotalList, algaePublishers):
            publisher.set(algaeLevel)
            
            for algaeLevel in algaeTotalList:
                for algae in algaeLevel:
                    if algae:
                        algaePose3dSeen.append(pose3dAlgaeValues[algaeTotalList.index(algaeLevel)][algaeLevel.index(algae)])
            
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


        for publisher in coralPublishers:
            publisher.set([False for _ in range(12)]) 
        
        for publisher in algaePublishers:
            publisher.set([False for _ in range(6)]) 

        return coralSubscribers, coralPublishers, algaeSubscribers, algaePublishers, coralValuesSeenPublisher, algaeValuesSeenPublisher
    
    
    # Start NT server
    inst = ntcore.NetworkTableInstance.getDefault()
    inst.setServerTeam(1799)
    if Constants.CoralAndAlgaeCameraConstants.robotReal:
        inst.startClient4("ReefIndexer")
    else:
        inst.startServer()


    # Reef Values
    coral = [[False for _ in range(12)] for _ in range(4)]
    algae = [[False for _ in range(6)] for _ in range(2)]
    

    # Create an instance of the AprilTag camera
    # aprilTagCameraFront = AprilTagCamera(PhotonLibConstants.APRIL_TAG_FRONT_CAMERA_NAME, PhotonLibConstants.ROBOT_TO_CAMERA_FRONT_TRANSFORMATION)
    # aprilTagCameraBack = AprilTagCamera(PhotonLibConstants.APRIL_TAG_BACK_CAMERA_NAME, PhotonLibConstants.ROBOT_TO_CAMERA_BACK_TRANSFORMATION)

    # Grabs the Robot's topic and publisher
    visionTable = inst.getTable("Vision")
    # robotFrontPoseTopic = visionTable.getStructTopic("FrontRobotPose", Pose3d)
    # robotFrontPosePublisher = robotFrontPoseTopic.publish()
    # robotBackPoseTopic = visionTable.getStructTopic("BackRobotPose", Pose3d)
    # robotBackPosePublisher = robotBackPoseTopic.publish()
    odometryRobotPoseTopic = inst.getStructTopic("RobotPose", Pose3d)
    odometryRobotPoseSubscriber = odometryRobotPoseTopic.subscribe(Pose3d(), ntcore.PubSubOptions(keepDuplicates=True))
    # aprilTagCameraConnectionTopic = visionTable.getBooleanTopic("AprilTagCameraConnection")
    # aprilTagCameraConnectionPublisher = aprilTagCameraConnectionTopic.publish()
    # aprilTagFrontCameraTimestampTopic = visionTable.getDoubleTopic("RobotPoseTimestampFront")
    # aprilTagFrontCameraTimestampPublisher = aprilTagFrontCameraTimestampTopic.publish()
    # aprilTagBackCameraTimestampTopic = visionTable.getDoubleTopic("RobotPoseTimestampBack")
    # aprilTagBackCameraTimestampPublisher = aprilTagBackCameraTimestampTopic.publish()

    robotPosition = None

    # Reef Publishers and Subscribers
    coralSubscribers, coralPublishers, algaeSubscribers, algaePublishers, coralValuesSeenPublisher, algaeValuesSeenPublisher = createReefPubSub(visionTable)
    pitchYawTopic = inst.getStructArrayTopic("Pitch Yaw Line", Pose3d)
    pitchYawPublisher = pitchYawTopic.publish()

    reefCameraConnectionTopic = inst.getBooleanTopic("ReefCameraConnection") # if the reef camera is connected
    reefCameraConnectionPublisher = reefCameraConnectionTopic.getEntry(True)

    # Reef Pose3D for debugging purposes
    reefPose3dTable = inst.getTable("reefPose3dTable")
    l1TestTableTopic = reefPose3dTable.getStructArrayTopic("poseL1", Pose3d)
    l2TestTableTopic = reefPose3dTable.getStructArrayTopic("poseL2", Pose3d)
    l3TestTableTopic = reefPose3dTable.getStructArrayTopic("poseL3", Pose3d)
    l4TestTableTopic = reefPose3dTable.getStructArrayTopic("poseL4", Pose3d)

    # reefPose3dToPublish = []
    
    deviceNumber = 0
    for deviceIndex in range(4):
        deviceNumber = coralCameraIndex(deviceIndex)
        if deviceNumber != None:
            break

    print(deviceNumber)
    coralCamera = CoralCamera.CoralCamera(deviceNumber)
    reefCameraConnectionPublisher.set(coralCamera.camera.isOpened())
    SmartDashboard.putBoolean("wasConnected", coralCamera.camera.isOpened())

    
    coralHitboxes, pose3dCoralValues = hitbox.makeCoralHitboxes()
    algaeHitboxes, pose3dAlgaeValues = hitbox.makeAlgaeHitboxes()

    # print(pose3dCoralValues)

    L1Publisher = l1TestTableTopic.publish()
    L2Publisher = l2TestTableTopic.publish()
    L3Publisher = l3TestTableTopic.publish()
    L4Publisher = l4TestTableTopic.publish()

    # print(pose3dCoralValues[1])
    # print(pose3dCoralValues[2])
    # print(pose3dCoralValues[3])
    L1Publisher.set(pose3dCoralValues[0])
    L2Publisher.set(pose3dCoralValues[1])
    L3Publisher.set(pose3dCoralValues[2])
    L4Publisher.set(pose3dCoralValues[3])

    
    while True:
        if keyboard.is_pressed("q"):
            inst.stopServer()
            cv2.destroyAllWindows()
            break
        
        # if not coralCamera.camera.isOpened():
        #     coralCamera = None
        #     time.sleep(10)
        #     coralCamera = CoralCamera.CoralCamera(deviceNumber)


        # if Constants.PhotonLibConstants.shouldTestAprilTags:
        
        #     if aprilTagCameraFront.isConnected():
        #         aprilTagCameraConnectionPublisher.set(True)
        #         aprilTagsFront = aprilTagCameraFront.get_tags()
        #         if aprilTagsFront:
        #             robotPositionFront, timestamp = fetchRobotPosition(aprilTagCameraFront)
        #             if robotPositionFront:
        #                 robotFrontPosePublisher.set(robotPositionFront.estimatedPose)
        #                 aprilTagFrontCameraTimestampPublisher.set(timestamp)
                        
        #             else:
        #                 robotFrontPosePublisher.set(Pose3d(Translation3d(0, 0, 0), Rotation3d(0, 0, 0)))
                        
        #     if aprilTagCameraBack.isConnected():
        #         aprilTagCameraConnectionPublisher.set(True)
        #         aprilTagsBack = aprilTagCameraBack.get_tags()
        #         if aprilTagsBack:
        #             robotPositionBack, timestamp = fetchRobotPosition(aprilTagCameraBack)
        #             if robotPositionBack:
        #                 robotBackPosePublisher.set(robotPositionBack.estimatedPose)
        #                 aprilTagBackCameraTimestampPublisher.set(timestamp)
                        
        #             else:
        #                 robotBackPosePublisher.set(Pose3d(Translation3d(0, 0, 0), Rotation3d(0, 0, 0)))
                       
        reefCameraConnectionPublisher.set(coralCamera.camera.isOpened())


        # Only used for testing just coral
        if not Constants.CoralAndAlgaeCameraConstants.shouldTestAprilTags:
            robotPosition = Pose3d(Translation3d(2.55, 4, 0), Rotation3d(0,0,0))
        else:
            robotPosition = odometryRobotPoseSubscriber.get().estimatedPose

        if robotPosition and (Constants.CoralAndAlgaeCameraConstants.shouldTestAlgae or Constants.CoralAndAlgaeCameraConstants.shouldTestCoral):
            coral, algaeNetworkTables = grab_past_reef(coralSubscribers, algaeSubscribers)
            coral, algaeOnFrame = coralCamera.findCoralsAndAlgaesOnReef(coral, coralHitboxes, algaeHitboxes, robotPosition)
            algaeToPublish = coralCamera.updateAlgaePositions(algaeNetworkTables, algaeHitboxes, algaeOnFrame, robotPosition)
            updateReef(coralPublishers, algaePublishers, coralValuesSeenPublisher, algaeValuesSeenPublisher, coral, algaeToPublish)

            pitchYawPublisher.set(coralCamera.allPositions)
                
            # for reefSection in range(len(reef)):
            #     for index in range(len(reef[0])):
            #         if reef[reefSection][index]:
            #             reefPose3dToPublish.append(pose3dCoralValues[reefSection][index])
                    
            # pose3dPublisher.set(reefPose3dToPublish)
                             
    time.sleep(0.005)
            
if __name__ == "__main__":
    main()