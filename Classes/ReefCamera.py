import robotpy_apriltag as apriltag
from ConstantsAndUtils.Constants import PhotonLibConstants, BaseConstants
import math
from typing import Optional
from photonlibpy.estimatedRobotPose import EstimatedRobotPose
from photonlibpy.photonCamera import PhotonCamera
from photonlibpy.photonPoseEstimator import PhotonPoseEstimator, PoseStrategy
from wpimath.geometry import Transform3d, Pose2d, Pose3d, Translation3d
from photonlibpy.targeting.photonTrackedTarget import PhotonTrackedTarget
from Vector import vector
from Hitbox import hitbox

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
        self.coralEverSeen = [[False for _ in range(12)] for _ in range(4)] # if a coral has ever been seen before
    
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
    
    def get2ClosestAlgaeSections(self, algaeHitboxes: list[hitbox], robotPosition: Pose3d) -> tuple[int, int]:
        """
        Returns the indices of each of the closest algae sections to the robot by finding
        their hypotenuses and sorting the list to find the 2 closest sections.

        Params:
        algaeHitboxes - list of each of the hitboxes of the algae
        robotPosition - the current robot position in a Pose3d
        """

        distancesFromSections = []
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
    
    def findCoralsAndAlgaesOnReef(self, reefObjectsInView: list[PhotonTrackedTarget], robotOdometryPosition: Pose3d, coralHitboxes: list[hitbox], algaeHitboxes: list[hitbox]):
        for object in reefObjectsInView:
            objectType = PhotonLibConstants.OBJECT_IDS[object.objDetectId] # Algae or Coral
            if objectType == 'Coral':
                coralYaw = object.getYaw()
                coralPitch = object.getPitch()

                vectorOfCoral = vector(robotOdometryPosition.transformBy(PhotonLibConstants.ROBOT_TO_CAMERA_REEF_TRANSFORMATION), coralPitch, coralYaw)
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
                                self.coralEverSeen[hitboxSection][hitbox] = True
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
                allIntersectValues = []

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
                            #allIntersectValues.append(algaeSeen)

                            if algaeSeen:
                                vectorAlreadyCollided = True
                                algaeOnFrame[hitboxSectionIndex][hitboxIndex] = True
                                break

                        if vectorAlreadyCollided:
                            break 
                if vectorAlreadyCollided:
                    # These values can be used as they are the last ones that existed before the line intercected with a hitbox
                    
                    vectorAlreadyCollided = False

    def updateAlgaePositions(self, algaeNetworkTables: list[list[bool]], algaeHitboxes: list[list[hitbox]], algaeOnFrame: list[list[bool]], robotPosition: Pose3d):
        # Getting each point on the reef to compare which ones are closest to the robot
        closestSectionIndexes = self.get2ClosestAlgaeSections(algaeHitboxes, robotPosition)

        for level in range(len(algaeOnFrame)): # either 0 or 1
            for algaeSection in range(len(algaeOnFrame)):
                isSpecificAlgaeOnFrame = algaeOnFrame[level][closestSectionIndexes[algaeSection]] # level 0 or 1 and the section closest to the robot
                if isSpecificAlgaeOnFrame:
                    algaeNetworkTables[level][closestSectionIndexes[algaeSection]] = True
                    self.algaeNotSeenCounterList[level][closestSectionIndexes[algaeSection]] = 0  
                elif algaeNetworkTables[level][closestSectionIndexes[algaeSection]]: # algae isn't on frame but value is marked as true
                    self.algaeNotSeenCounterList[level][closestSectionIndexes[level]] += 1
                else:
                    algaeNetworkTables[level][closestSectionIndexes[level]] = False

                if not isSpecificAlgaeOnFrame and self.algaeNotSeenCounterList[level][closestSectionIndexes[level]] > CoralAndAlgaeCameraConstants.algaeViewedTolerance and algaeNetworkTables[level][closestSectionIndexes[level]]:
                    algaeNetworkTables[level][closestSectionIndexes[level]] = False
                    self.algaeNotSeenCounterList[level][closestSectionIndexes[level]] = 0  


                    
        return algaeNetworkTables
            
    