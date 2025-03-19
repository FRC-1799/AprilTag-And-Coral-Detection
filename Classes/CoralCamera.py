from ConstantsAndUtils.Constants import CoralAndAlgaeCameraConstants
import cv2
from ultralytics import YOLO
import math
from Classes import Vector, Hitbox
import os
from wpimath.geometry import Pose3d
import sys
import contextlib

class CoralCamera:
    """
    Detects coral and makes a ray to said coral to see which level it is on. This data gets published to NetworkTables
    """

    def __init__(self, cameraIndex, modelPath: str = "Models/runs/detect/train/weights/BestModel.pt"):
        self.self = self
        self.cameraIndex = cameraIndex
        
        self.model = YOLO(modelPath)
        self.screenWidth = CoralAndAlgaeCameraConstants.horizontalPixels
        self.screenHeight = CoralAndAlgaeCameraConstants.verticalPixels
        self.camera = cv2.VideoCapture(self.cameraIndex)
        self.coralEverSeen = [[False for _ in range(12)] for _ in range(4)]
        self.algaeNotSeenCounterList = [[0 for _ in range(6)] for _ in range(2)]
        self.vectorPoseIntersects = [[False for _ in range(6)] for _ in range(2)] # list of booleans that indicate if a vector has collided with an algae

    def get2ClosestAlgaeSections(self, algaeHitboxes: list[Hitbox.hitbox], robotPosition: Pose3d) -> tuple[int, int]:
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

    def findCoralsAndAlgaesOnReef(self, coral: list[list[bool]], reefHitboxes: list, algaeHitboxes: list, robotPosition):
        readSuccess, frame = self.camera.read()


        self.allPositions = []
        if readSuccess:
            frame = cv2.resize(frame, (self.screenWidth, self.screenHeight)) 
            results = self.model.predict(frame, verbose=False)
            vectorAlreadyCollided = False
            x1, y1, x2, y2 = False, False, False, False
            algaeOnFrame = [[False for _ in range(6)] for _ in range(2)]
            coralOnFrame = [[False for _ in range(12)] for _ in range(4)]
            #print(self.algaeNotSeenCounterList)
            for result in results:
                for box in result.boxes:
                    
                    conf = box.conf[0].item()
                    cls = int(box.cls[0].item())
                    if self.model.names[cls].lower() == "coral" and CoralAndAlgaeCameraConstants.shouldTestCoral:
                        if conf > CoralAndAlgaeCameraConstants.coralConfidenceTolerance:


                            # Top left X, top left Y, bottom right X, bottom right Y
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            

                            centerOfCoral = ((x2 - x1) / 2 + x1, (y2 - y1) / 2 + y1) 
                            coralYaw = CoralAndAlgaeCameraConstants.reefCameraHorizontalAnglePerPixel * centerOfCoral[0]
                            coralPitch = CoralAndAlgaeCameraConstants.reefCameraVerticalAnglePerPixel * centerOfCoral[1]

                            centerYaw = CoralAndAlgaeCameraConstants.reefCameraHorizontalAnglePerPixel * (self.screenWidth / 2)
                            centerPitch = CoralAndAlgaeCameraConstants.reefCameraVerticalAnglePerPixel * (self.screenHeight / 2) + math.radians(10)

                            # Adjusts the pitch and yaw so that its center (0, 0) is in the middle of the camera lens
                            coralYaw = -(coralYaw - centerYaw)
                            coralPitch = (coralPitch - centerPitch)

                            vectorOfCoral = Vector.vector(robotPosition.transformBy(CoralAndAlgaeCameraConstants.ROBOT_TO_CAMERA_ROTATED_TRANSFORMATION), coralPitch, coralYaw)

                            # Loops again for a certain increment across the line, and the increment acts as the x value for the equation
                            for length in range(1, CoralAndAlgaeCameraConstants.vectorLengthToExtend):
                                length = length * 0.05
                                positionLocation = vectorOfCoral.getPoseAtStep(length)
                                #self.allPositions.append(positionLocation)
                                if vectorAlreadyCollided:
                                    break
                                
                                for hitboxSection in range(len(reefHitboxes)):
                                    for hitbox in range(len(reefHitboxes[0])):

                                        # If the Pose3d is colliding with the hitbox, we know which level it is on, so we set that level to true
                                        if reefHitboxes[hitboxSection][hitbox].colidePose3d(positionLocation):
                                            self.coralEverSeen[hitboxSection][hitbox] = True
                                            vectorAlreadyCollided = True
                                            break
                                    if vectorAlreadyCollided:
                                        break
                            
                            # When the loop is exited, reset this variable in order to be able to search again
                            vectorAlreadyCollided = False 
                                                

                            
                    
                    elif self.model.names[cls].lower() == "algae" and CoralAndAlgaeCameraConstants.shouldTestAlgae:
                        if conf > CoralAndAlgaeCameraConstants.coralConfidenceTolerance:
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                        
                            centerOfAlgae = ((x2 - x1) / 2 + x1, (y2 - y1) / 2 + y1) 
                            algaeYaw = CoralAndAlgaeCameraConstants.reefCameraHorizontalAnglePerPixel * centerOfAlgae[0]
                            algaePitch = CoralAndAlgaeCameraConstants.reefCameraVerticalAnglePerPixel * centerOfAlgae[1]

                            centerYaw = CoralAndAlgaeCameraConstants.reefCameraHorizontalAnglePerPixel * (self.screenWidth / 2)
                            centerPitch = CoralAndAlgaeCameraConstants.reefCameraVerticalAnglePerPixel * (self.screenHeight / 2)

                            # Adjusts the pitch and yaw so that its center (0, 0) is in the middle of the camera lens
                            algaeYaw = -(algaeYaw - centerYaw)
                            algaePitch = (algaePitch - centerPitch)

                            vectorOfAlgae = Vector.vector(robotPosition.transformBy(CoralAndAlgaeCameraConstants.ROBOT_TO_CAMERA_ROTATED_TRANSFORMATION), algaePitch, algaeYaw)
                            allIntersectValues = []

                            for length in range(1, CoralAndAlgaeCameraConstants.vectorLengthToExtend):
                                length = length * 0.05
                                positionLocation = vectorOfAlgae.getPoseAtStep(length)
                                self.allPositions.append(positionLocation) # debug purposes with vector line
                                
                                
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

                    else:
                        algaeOnFrame = [[False for _ in range(6)] for _ in range(2)]
                                

                                    #     # If we haven't seen the algae for more than the tolerance frames, it is not seen right now, and it is marked as true, then assume it isn't there anymore
                                    #     if algaeNotSeenCounter[hitboxSectionIndex][hitboxIndex] > CoralAndAlgaeCameraConstants.algaeViewedTolerance and not algaeSeen and algae[hitboxSectionIndex][hitboxIndex]:
                                    #         algae[hitboxSectionIndex][hitboxIndex] = False
                                        
                                    #     # If we do see the algae and it is false, mark it as true
                                    #     if algaeSeen and not algae[hitboxSectionIndex][hitboxIndex]:
                                    #         algae[hitboxSectionIndex][hitboxIndex] = True
                                    #         algaeNotSeenCounter[hitboxSectionIndex][hitboxIndex] = 0 # resets counter to 0 once seen again
                                    #         vectorAlreadyCollided = True
                                    #         break


                                    # if vectorAlreadyCollided:
                                    #     break
                            
                           
                            





                            # closestSections = []
                            # closestHitboxSectionIndex = (distancesFromSectionsUnsorted.index(closestDistances[0]), distancesFromSectionsUnsorted.index(closestDistances[1]))





                            # for distance in closestDistances:
                            #     distanceIndex = distancesFromSections.index(distance)
                            #     distanceSectionIndex = xyPosesForSections.index(xyPosesForSections[distanceIndex])
                            #     closestSections.append(algaeHitboxes[distanceSectionIndex])
                                    
                                    
                            
                            
                            # # If the algae is marked as true but is not seen, increase it's not seen counter by 1
                            # for hitboxSection in algaeHitboxes:
                            #     for section in closestSections:
                            #         if hitboxSection == section:
                            #             for hitbox in hitboxSection:
                            #                 hitboxSectionIndex = algaeHitboxes.index(hitboxSection)
                            #                 hitboxIndex = hitboxSection.index(hitbox)
                            #                 if algae[hitboxSectionIndex][hitboxIndex] and not vectorPoseIntersects[hitboxSectionIndex][hitboxIndex]:
                            #                     algaeNotSeenCounter[hitboxSectionIndex][hitboxIndex] += 1

                            # If there is no algae seen but have the algae 
                            

                    # Labeling of the detections
                    if [x1, y1, x2, y2] != [False for _ in range(4)]:
                        label = f"{self.model.names[cls]}"
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            cv2.imshow('heheh', frame)
            cv2.waitKey(1)
        else:
            algaeOnFrame = [[False for _ in range(6)] for _ in range(2)] 
            
        return coralOnFrame, algaeOnFrame

    def updateAlgaePositions(self, algaeNetworkTables: list[list[bool]], algaeHitboxes: list[list[Hitbox.hitbox]], algaeOnFrame: list[list[bool]], robotPosition: Pose3d):
        # Getting each point on the reef to compare which ones are closest to the robot
        closestSectionIndexes = self.get2ClosestAlgaeSections(algaeHitboxes, robotPosition)
        algaeLevelsToSection = [[algaeNetworkTables[0][i], algaeNetworkTables[1][i]] for i in range(6)] # converts to section so distance will be easier
        algaeFrameLevelsToSection = [[algaeOnFrame[0][i], algaeOnFrame[1][i]] for i in range(6)]

        algaeBoolSections = (algaeFrameLevelsToSection[closestSectionIndexes[0]], algaeFrameLevelsToSection[closestSectionIndexes[1]])
        for section in algaeBoolSections:
            sectionIndex = algaeBoolSections.index(section)
            for level in section:
                levelIndex = section.index(level)
                

                algaeCurrentlySeen = algaeFrameLevelsToSection[sectionIndex][levelIndex] # if an algae the level is seen currently
                
                # Handling of all cases of algae
                if section[levelIndex] and not algaeCurrentlySeen:
                    self.algaeNotSeenCounterList[levelIndex][sectionIndex] += 1
                elif algaeCurrentlySeen:
                    algaeLevelsToSection[levelIndex][sectionIndex] = True
                    self.algaeNotSeenCounterList[levelIndex][sectionIndex] = 0

                shouldMarkAsFalse = section[levelIndex] and self.algaeNotSeenCounterList[sectionIndex][levelIndex] > CoralAndAlgaeCameraConstants.algaeViewedTolerance and not algaeCurrentlySeen
                if shouldMarkAsFalse:
                    algaeLevelsToSection[levelIndex][sectionIndex] = False
                    self.algaeNotSeenCounterList[levelIndex][sectionIndex] = 0
        
        # Update the grid at the specified indices
        for row in range(2):  # We only have 2 rows to update
            for col in range(2):  # Each row gets 2 updated values
                algaeNetworkTables[row][closestSectionIndexes[col]] = algaeLevelsToSection[row][col]

        return algaeNetworkTables
    
    def updateCoralPositions(self):
        coralToPublish = [[False for _ in range(12)] for _ in range(4)]
        for level in self.coralEverSeen:
            levelIndex = self.coralEverSeen.index(level)
            for coral in level:
                coralIndex = level.index(coral)
                if coral:
                    coralToPublish[levelIndex][coralIndex] = True
        
        return self.coralEverSeen

