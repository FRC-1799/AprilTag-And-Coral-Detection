from ConstantsAndUtils.Constants import CoralAndAlgaeCameraConstants
import cv2
from ultralytics import YOLO
import math
from Classes import Vector
import os

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

    def findCoralsAndAlgaesOnReef(self, reef: list[list[bool]], algae: list[list[bool]], reefHitboxes: list, algaeHitboxes: list, algaeNotSeenCounter: list, robotPosition):
        readSuccess, frame = self.camera.read()

        self.allPositions = []
        if readSuccess:
            frame = cv2.resize(frame, (self.screenWidth, self.screenHeight)) 
            results = self.model(frame)
            vectorAlreadyCollided = False
            x1, y1, x2, y2 = False, False, False, False
            print(algaeNotSeenCounter)
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
                                # self.allPositions.append(positionLocation)
                                if vectorAlreadyCollided:
                                    break
                                
                                for hitboxSection in range(len(reefHitboxes)):
                                    for hitbox in range(len(reefHitboxes[0])):

                                        # If the Pose3d is colliding with the hitbox, we know which level it is on, so we set that level to true
                                        if reefHitboxes[hitboxSection][hitbox].colidePose3d(positionLocation):
                                            reef[hitboxSection][hitbox] = True
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
                            vectorPoseIntersects = [[False for _ in range(len(algaeHitboxes[0]))] for _ in range(len(algaeHitboxes))] # list of booleans that indicate if a vector has collided with an algae

                            for length in range(1, CoralAndAlgaeCameraConstants.vectorLengthToExtend):
                                length = length * 0.05
                                positionLocation = vectorOfAlgae.getPoseAtStep(length)
                                
                                if vectorAlreadyCollided:
                                    break
                                self.allPositions.append(positionLocation)
                                for hitboxSection in algaeHitboxes:
                                    for hitbox in hitboxSection:

                                        hitboxSectionIndex = algaeHitboxes.index(hitboxSection)
                                        hitboxIndex = hitboxSection.index(hitbox)
                                        algaeSeen = hitbox.colidePose3d(positionLocation)

                                        vectorPoseIntersects[hitboxSectionIndex][hitboxIndex] = algaeSeen
                                        

                                        # If we haven't seen the algae for more than the tolerance frames, it is not seen right now, and it is marked as true, then assume it isn't there anymore
                                        if algaeNotSeenCounter[hitboxSectionIndex][hitboxIndex] > CoralAndAlgaeCameraConstants.algaeViewedTolerance and not algaeSeen and algae[hitboxSectionIndex][hitboxIndex]:
                                            algae[hitboxSectionIndex][hitboxIndex] = False
                                        
                                        # If we do see the algae and it is false, mark it as true
                                        if algaeSeen and not algae[hitboxSectionIndex][hitboxIndex]:
                                            algae[hitboxSectionIndex][hitboxIndex] = True
                                            vectorAlreadyCollided = True
                                            break


                                    if vectorAlreadyCollided:
                                        break
                            
                            # Getting each point on the reef to compare which ones are closest to the robot
                            distancesFromSections = []
                            xyPosesForSections = [(algaeHitboxes[i][0].getPose().X(), algaeHitboxes[i][0].getPose().Y()) for i in range(len(algaeHitboxes))]
                            
                            for poses in xyPosesForSections:
                                changeInXY = (poses[0] - robotPosition.X(), poses[1] - robotPosition.Y())
                                hypotenuseDistance = changeInXY[0] **2 + changeInXY[1] **2
                                distancesFromSections.append(hypotenuseDistance)
                            if distancesFromSections:
                                distancesFromSections.sort()
                                closestDistances = distancesFromSections[-2:]
                                closestSections = []
                                for distance in closestDistances:
                                    distanceIndex = distancesFromSections.index(distance)
                                    distanceSectionIndex = xyPosesForSections.index(xyPosesForSections[distanceIndex])
                                    closestSections.append(algaeHitboxes[distanceSectionIndex])
                                    
                                    
                            
                            
                            # If the algae is marked as true but is not seen, increase it's not seen counter by 1
                            for hitboxSection in algaeHitboxes:
                                for section in closestSections:
                                    if hitboxSection == section:
                                        for hitbox in hitboxSection:
                                            hitboxSectionIndex = algaeHitboxes.index(hitboxSection)
                                            hitboxIndex = hitboxSection.index(hitbox)
                                            if algae[hitboxSectionIndex][hitboxIndex] and not vectorPoseIntersects[hitboxSectionIndex][hitboxIndex]:
                                                algaeNotSeenCounter[hitboxSectionIndex][hitboxIndex] += 1
                                    
                            
                            
                            # When the loop is exited, reset this variable in order to be able to search again
                            vectorAlreadyCollided = False if vectorAlreadyCollided else True

                            # If there is no algae seen but have the algae 
                            

                    # Labeling of the detections
                    if [x1, y1, x2, y2] != [False for _ in range(4)]:
                        label = f"{self.model.names[cls]}"
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            cv2.imshow('heheh', frame)
            cv2.waitKey(1)


