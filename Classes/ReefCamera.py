from ConstantsAndUtils.Constants import PhotonLibConstants
from photonlibpy.photonCamera import PhotonCamera
from wpimath.geometry import Transform3d, Pose3d
from photonlibpy.targeting.photonTrackedTarget import PhotonTrackedTarget # Remove ".targeting" from the import path if not on orange pi
from ntcore import BooleanArrayPublisher, BooleanPublisher, NetworkTable, BooleanArraySubscriber
from Classes.Vector import vector
from Classes.Hitbox import hitbox

class ReefCamera:
    def __init__(self, cameraName: str, cameraTransformation: Transform3d):
        """
        When initialized, a PhotonCamera will be created. This will be used to detect coral and algae

        Parameters:
        cameraName  (str): Name of a camera in String format. Used to find which camera is being used in Photon Vision.
        cameraType (str): Optional Parameter that is what the camera will be doing. If it is detecting April Tags, pass Pose in for it, and leave the parameter blank if it is detecting objects.
        """

        self.cameraName = cameraName
        self.camera = PhotonCamera(self.cameraName)
        self.cameraTransformation = cameraTransformation
        self.algaeNotSeenCounterList = [[0 for _ in range(12)] for _ in range(2)] # if an algae has not been seen for a certain amount of frames, it will be set to false
    
    def isConnected(self):
        return self.camera.isConnected()

    def getObjects(self) -> list[PhotonTrackedTarget]:
        """
        Gets Coral and Algae found in the camera and returns them in a list.

        Returns:
        Dictionary[integer, Transform3d]: The integer is the ID for the April Tag and the Transform3d is the position of the tag
        """

        photonResult = self.camera.getLatestResult()
        resultTargets: list[PhotonTrackedTarget] = photonResult.getTargets()
        return resultTargets
    
    def __get2ClosestAlgaeSections(self, algaeHitboxes: list[list[hitbox]], robotPosition: Pose3d) -> tuple[int, int]:
        """
        Returns the indices of each of the closest algae sections to the robot by finding
        their hypotenuses and sorting the list to find the 2 closest sections.

        Params:
        algaeHitboxes - list of each of the hitboxes of the algae
        robotPosition - the current robot position in a Pose3d
        """

        distancesFromSections = []
        print(algaeHitboxes[0][0])
        xyPosesForSections = [(algaeHitboxes[0][i].getPose().X(), algaeHitboxes[1][i].getPose().Y()) for i in range(len(algaeHitboxes[0]))]
        
        for poses in xyPosesForSections:
            changeInXY = (poses[0] - robotPosition.X(), poses[1] - robotPosition.Y())
            hypotenuseDistance = changeInXY[0] **2 + changeInXY[1] **2
            distancesFromSections.append(hypotenuseDistance)
        
        unsortedDistances = distancesFromSections.copy()
        distancesFromSections.sort()
        closestDistances = distancesFromSections[:2]

        # Will give us the correct index for each of the closest sections, corresponding to the indexes of algaeHitboxes
        closestHitboxIndexes = (unsortedDistances.index(closestDistances[0]), unsortedDistances.index(closestDistances[1]))
        return closestHitboxIndexes
    
    @staticmethod
    def publishReefValues(coralTotalList: list[list[bool]], algaeTotalList: list[list[bool]], coralPublishers: list[BooleanPublisher], algaePublishers: list[BooleanPublisher]):
        """
        Updates the reef's values on Network Tables
        """

        for coralLevel, publisher in zip(coralTotalList, coralPublishers):
            publisher.set(coralLevel)

        for algaeLevel, publisher in zip(algaeTotalList, algaePublishers):
            publisher.set(algaeLevel)
        
        #coralPose3dSeen = []

        # for coralLevel in coralTotalList:
        #     for coral in coralLevel:
        #         if coral:
        #             coralPose3dSeen.append(pose3dCoralValues[coralTotalList.index(coralLevel)][coralLevel.index(coral)])
            
        
        #coralValuesSeenPublisher.set(coralPose3dSeen)
        
        #algaePose3dSeen = []
        
        # for algaeLevel in algaeTotalList:
        #     for algae in algaeLevel:
        #         if algae:
        #             algaePose3dSeen.append(pose3dAlgaeValues[algaeTotalList.index(algaeLevel)][algaeLevel.index(algae)])
            
        #algaeValuesSeenPublisher.set(algaePose3dSeen)

    @staticmethod
    def grabPastReef(coralSubscribers: list[BooleanArraySubscriber], algaeSubscribers: list[BooleanArraySubscriber]) -> tuple[list[list[bool]], list[list[bool]]]:
        """
        Grabs the past value of the reef
        
        Parameters:
        reefSubscribers - Subscribers of the reef
        algaeSubscribers - Subscribers of the algae

        Returns:
        tuple[list[list[bool]], list[list[bool]]] - Returns the current state of the reef coral and algae
        """

        # Sets the reef coral values to the current state of the reef
        reefCoral = [[] for _ in range(4)]
        for level, subscriber in enumerate(coralSubscribers):
            reefCoral[level] = subscriber.get()
        
        # Same thing with algae
        reefAlgae = [[] for _ in range(2)]
        for level, subscriber in enumerate(algaeSubscribers):
            reefAlgae[level] = subscriber.get()

        return reefCoral, reefAlgae


    @staticmethod
    def createReefPubSub(visionTable: NetworkTable) -> tuple[list[BooleanArraySubscriber], list[BooleanArrayPublisher], list[BooleanArraySubscriber], list[BooleanArrayPublisher]]:
        """
        Creates the publishers and subscribers for the reef, including both the algae and coral
        subscribers and publishers

        Returns:
        list[list] - List of all of the lists for the publishers and subscribers
        """
        # Getting subtables from the vision table and defining the default values for the coral and algae
        coralTable = visionTable.getSubTable("CoralPositions")
        algaeTable = visionTable.getSubTable("AlgaePositions")
        defaultReef = [False for _ in range(12)] # used for 1 level of coral
        defaultAlgae = [False for _ in range(6)] # used for 1 level of algae

        # Topic creation for the coral and algae
        reefL1Topic = coralTable.getBooleanArrayTopic("ReefL1")
        reefL2Topic = coralTable.getBooleanArrayTopic("ReefL2")
        reefL3Topic = coralTable.getBooleanArrayTopic("ReefL3")
        reefL4Topic = coralTable.getBooleanArrayTopic("ReefL4")
        algae1Topic = algaeTable.getBooleanArrayTopic("Algae1")
        algae2Topic = algaeTable.getBooleanArrayTopic("Algae2")

        # Coral subscribers and publishers
        coralSubscribers: list[BooleanArraySubscriber] = [reefL1Topic.subscribe(defaultReef), reefL2Topic.subscribe(defaultReef), reefL3Topic.subscribe(defaultReef), reefL4Topic.subscribe(defaultReef)] 
        coralPublishers: list[BooleanArrayPublisher] = [reefL1Topic.publish(), reefL2Topic.publish(), reefL3Topic.publish(), reefL4Topic.publish()]

        # Algae subscribers and publishers
        algaeSubscribers: list[BooleanArraySubscriber] = [algae1Topic.subscribe(defaultAlgae), algae2Topic.subscribe(defaultAlgae)]
        algaePublishers: list[BooleanArrayPublisher] = [algae1Topic.publish(), algae2Topic.publish()]

        # Debug stuff
        # coralValuesSeenTopic = coralTable.getStructArrayTopic("CoralSeen",Pose3d)
        # coralValuesSeenPublisher = coralValuesSeenTopic.publish()
        # algaeValuesSeenTopic = algaeTable.getStructArrayTopic("AlgaeSeen", Pose3d)
        # algaeValuesSeenPublisher = algaeValuesSeenTopic.publish()


        for publisher in coralPublishers:
            publisher.set([False for _ in range(12)]) 
        
        for publisher in algaePublishers:
            publisher.set([False for _ in range(6)])

        return coralSubscribers, coralPublishers, algaeSubscribers, algaePublishers # coralValuesSeenPublisher, algaeValuesSeenPublisher
    

    
    def findCoralsAndAlgaesOnReef(self, reefObjectsInView: list[PhotonTrackedTarget], robotOdometryPosition: Pose3d, coralHitboxes: list[list[hitbox]], algaeHitboxes: list[list[hitbox]]) -> tuple[list[list[bool]], list[list[bool]]]:
        coralEverSeen = [[False for _ in range(12)] for _ in range(4)] # if a coral has ever been seen before
        algaeOnFrame = [[False for _ in range(6)] for _ in range(2)] # if an algae is on frame
        for object in reefObjectsInView:
            objectType = PhotonLibConstants.OBJECT_IDS[object.objDetectId] # Algae or Coral
            if objectType == 'Coral':
                coralYaw = object.getYaw()
                coralPitch = object.getPitch()

                vectorOfCoral = vector(robotOdometryPosition.transformBy(PhotonLibConstants.ROBOT_TO_CAMERA_REEF_TRANSFORMATION), coralPitch, coralYaw)
                vectorAlreadyCollided = False
                # Loops again for a certain increment across the line, and the increment acts as the x value for the equation
                for length in range(1, PhotonLibConstants.vectorLengthToExtend):
                    length = length * 0.05
                    positionLocation = vectorOfCoral.getPoseAtStep(length)
                    #self.allPositions.append(positionLocation)
                    if vectorAlreadyCollided:
                        break
                    
                    for hitboxSection in range(len(coralHitboxes)):
                        for hitbox in range(len(coralHitboxes[0])):

                            # If the Pose3d is colliding with the hitbox, we know which level it is on, so we set that level to true
                            if coralHitboxes[hitboxSection][hitbox].colidePose3d(positionLocation):
                                coralEverSeen[hitboxSection][hitbox] = True
                                vectorAlreadyCollided = True
                                break
                        if vectorAlreadyCollided:
                            break
                
                # When the loop is exited, reset this variable in order to be able to search again
                vectorAlreadyCollided = False 

            if objectType == "Algae":
                algaePitch = object.getPitch()
                algaeYaw = object.getYaw()
                vectorOfAlgae = vector(robotOdometryPosition.transformBy(PhotonLibConstants.ROBOT_TO_CAMERA_REEF_TRANSFORMATION), algaePitch, algaeYaw)
                vectorAlreadyCollided = False

                for length in range(1, PhotonLibConstants.vectorLengthToExtend):
                    length = length * 0.05
                    positionLocation = vectorOfAlgae.getPoseAtStep(length)
                    #self.allPositions.append(positionLocation) # debug purposes with vector line
                    if vectorAlreadyCollided:
                        break
                    
                    for hitboxSection in algaeHitboxes:
                        for hitbox in hitboxSection:

                            hitboxSectionIndex = algaeHitboxes.index(hitboxSection)
                            hitboxIndex = hitboxSection.index(hitbox)
                            algaeSeen = hitbox.colidePose3d(positionLocation)
                            #allIntersectValues.append(algaeSeen) debug thing

                            if algaeSeen:
                                vectorAlreadyCollided = True
                                algaeOnFrame[hitboxSectionIndex][hitboxIndex] = True
                                break

                        if vectorAlreadyCollided:
                            break 
                if vectorAlreadyCollided:
                    # These values can be used as they are the last ones that existed before the line intercected with a hitbox
                    vectorAlreadyCollided = False

        return coralEverSeen, algaeOnFrame

    def manageViewedAlgae(self, algaeNetworkTables: list[list[bool]], algaeHitboxes: list[list[hitbox]], algaeOnFrame: list[list[bool]], robotPosition: Pose3d):
        # Getting each point on the reef to compare which ones are closest to the robot
        closestSectionIndexes = self.__get2ClosestAlgaeSections(algaeHitboxes, robotPosition)

        for level in range(len(algaeOnFrame)): # either 0 or 1, corrisponding to L2 and L3 algae
            for algaeSection in closestSectionIndexes:
                isSpecificAlgaeOnFrame = algaeOnFrame[level][algaeSection] # level 0 or 1 and the section closest to the robot
                if isSpecificAlgaeOnFrame:
                    algaeNetworkTables[level][algaeSection] = True
                    self.algaeNotSeenCounterList[level][algaeSection] = 0  
                elif algaeNetworkTables[level][algaeSection]: # algae isn't on frame but value is marked as true
                    self.algaeNotSeenCounterList[level][algaeSection] += 1
                
                # If the algae is not on frame, has not been seen for a certain amount of frames, and the network table's value for it is still true, set it to false
                if not isSpecificAlgaeOnFrame and self.algaeNotSeenCounterList[level][algaeSection] > PhotonLibConstants.ALGAE_VIEWED_TOLERANCE and algaeNetworkTables[level][algaeSection]:
                    algaeNetworkTables[level][algaeSection] = False
                    self.algaeNotSeenCounterList[level][algaeSection] = 0

        return algaeNetworkTables
    
    def manageViewedCorals(self, coralNetworkTables: list[list[bool]], coralOnFrame: list[list[bool]]):
        """
        Manages the coral that has been seen on the reef, and updates the coralNetworkTables accordingly.

        Parameters:
        coralNetworkTables - The current state of the coral on the reef
        coralOnFrame - The corals that are currently on frame
        """

        for level in range(len(coralOnFrame)):
            for coralSection in range(len(coralOnFrame[level])):
                isSpecificCoralOnFrame = coralOnFrame[level][coralSection]
                isCoralTrueNetworkTable = coralNetworkTables[level][coralSection]
                if isSpecificCoralOnFrame and not isCoralTrueNetworkTable:
                    coralNetworkTables[level][coralSection] = True

        return coralNetworkTables

    def updateReef(coralPublishers: list[BooleanArrayPublisher], algaePublishers: list[BooleanArrayPublisher], coralToPublish: list[list[bool]], algaeToPublish: list[list[bool]]):
        """
        Updates the reef's values on Network Tables
        """

        for coralLevel, publisher in zip(coralToPublish, coralPublishers):
            publisher.set(coralLevel)

        for algaeLevel, publisher in zip(algaeToPublish, algaePublishers):
            publisher.set(algaeLevel)


        ### Debugging stuff ###
        # coralPose3dSeen = []
        

        # for coralLevel in coralToPublish:
        #     for coral in coralLevel:
        #         if coral:
        #             coralPose3dSeen.append(pose3dCoralValues[coralToPublish.index(coralLevel)][coralLevel.index(coral)])

        # coralValuesSeenPublisher.set(coralPose3dSeen)

        # algaePose3dSeen = []
        

        # for algaeLevel in algaeToPublish:
        #     for algae in algaeLevel:
        #         if algae:
        #             algaePose3dSeen.append(pose3dAlgaeValues[algaeToPublish.index(algaeLevel)][algaeLevel.index(algae)])

        # algaeValuesSeenPublisher.set(algaePose3dSeen)
