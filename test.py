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
from Classes.Vector import vector

coralHitboxes, coralPose3ds = hitbox.makeCoralHitboxes()

robotPosition = Pose3d(Translation3d(2.55, 4.03, 0), Rotation3d(0, 0, 0))
inst = ntcore.NetworkTableInstance.getDefault()
inst.startClient4("RPP")
inst.setServer("127.0.0.1")
robotPositionTopic = inst.getStructTopic("Robot Position", Pose3d)
robotPositionPublisher = robotPositionTopic.publish()
cameraPositionTopic = inst.getStructTopic("Camera Position", Pose3d)
cameraPositionPublisher = cameraPositionTopic.publish()
pitchYawTopic = inst.getStructTopic("Pitch Yaw Line", Pose3d)
pitchYawPublisher = pitchYawTopic.publish()

correctCoralTopic = inst.getStructTopic("Correct Coral Position", Pose3d)
correctCoralPublisher = correctCoralTopic.publish()

vectorTable = inst.getStructArrayTopic("Vector Table", Pose3d)
vectorPublisher = vectorTable.publish() # for _ in range(Constants.CoralAndAlgaeCameraConstants.vectorLengthToExtend)]

cameraPosition = robotPosition.transformBy(Constants.CoralAndAlgaeCameraConstants.ROBOT_TO_CAMERA_ROTATED_TRANSFORMATION)
pitchYawTest = cameraPosition.transformBy(Transform3d(0, 0, 0, Rotation3d(0, -50.9, 0.1)))


vectorOfCoral = vector(cameraPosition, pitchYawTest.rotation().Y(), pitchYawTest.rotation().Z())
posesOfCoral = []
correctCoral = None
for length in range(0, Constants.CoralAndAlgaeCameraConstants.vectorLengthToExtend):
    length = length * 0.05
    poseOfCoral = vectorOfCoral.getPoseAtStep(length)
    posesOfCoral.append(poseOfCoral)
    for hitboxSection in coralHitboxes:
        for coralHitbox in hitboxSection:
            if coralHitbox.colidePose3d(poseOfCoral):
                correctCoral = coralPose3ds[coralHitboxes.index(hitboxSection)][hitboxSection.index(coralHitbox)]

if correctCoral:    
    correctCoralPublisher.set(correctCoral)
else: 
    correctCoralPublisher.set(Pose3d(Translation3d(), Rotation3d()))
vectorPublisher.set(posesOfCoral)

robotPositionPublisher.set(robotPosition)
cameraPositionPublisher.set(cameraPosition)
pitchYawPublisher.set(pitchYawTest)
