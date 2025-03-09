from typing import Self
from wpimath.geometry import Pose3d, Rotation3d, Translation2d, Rotation2d, Translation3d, Transform3d
from wpimath.units import degreesToRadians
from ConstantsAndUtils import FieldMirroringUtils
from ConstantsAndUtils.Constants import CoralAndAlgaeCameraConstants
import math

def addTranslation2ds(translation1: Translation2d, translation2: Translation2d):
    return Translation2d(translation1.X() + translation2.X(), translation1.Y() + translation2.Y())

class hitbox:

    def __init__(self, x: float, y:float, z:float, r:float, roll=0, pitch=0, yaw=0):
        self.x, self.y, self.z, self.r, self.roll, self.pitch, self.yaw = x, y, z, r, roll, pitch, yaw

    @staticmethod
    def hitboxFromPose3d(pose:Pose3d, r: float)->Self:
        return hitbox(pose.X(), pose.Y(), pose.Z(), r, roll=pose.rotation().X(), pitch=pose.rotation().Y(), yaw=pose.rotation().Z())
    

    def colideXYZ(self, pointOnRay: tuple[float, float, float])->bool:
        pointX, pointY, pointZ = pointOnRay
        return (pointX-self.x)**2 + (pointY-self.y)**2 + (pointZ-self.z)**2 <= self.r**2
    
    def colidePose3d(self, pose:Pose3d)->bool:
        pointLocation = (pose.X(), pose.Y(), pose.Z())
        return self.colideXYZ(pointLocation)
    
    def getPose(self)->Pose3d:
        return Pose3d(Translation3d(self.x, self.y, self.z), Rotation3d(self.roll, self.pitch, self.yaw))
    
    @staticmethod
    def makeCoralHitboxes()->list[list[Pose3d]]:
        

        blueHitboxes = [[None, None, None, None] for _ in range(12)]
        

        # Translation2d of the reef's position on the field based on the origin
        blueStarts = [
            Pose3d(x=4, y=4.189, z=0, rotation=Rotation3d.fromDegrees(0, 0, 0)),    #A
            Pose3d(x=4, y=3.862, z=0, rotation=Rotation3d.fromDegrees(0, 0, 0)), #B
            Pose3d(x=4.101, y=3.69, z=0, rotation=Rotation3d.fromDegrees(0, 0, 60)), #C
            Pose3d(x=4.389, y=3.519, z=0, rotation=Rotation3d.fromDegrees(0, 0, 60)), #D
            Pose3d(x=4.590, y=3.528, z=0, rotation=Rotation3d.fromDegrees(0, 0, 120)), #E
            Pose3d(x=4.888, y=3.69, z=0, rotation=Rotation3d.fromDegrees(0, 0, 120)), #F
            Pose3d(x=4.990, y=3.859, z=0, rotation=Rotation3d.fromDegrees(0, 0, 180)), #G
            Pose3d(x=4.990, y=4.192, z=0, rotation=Rotation3d.fromDegrees(0, 0, 180)), #H
            Pose3d(x=4.881, y=4.381, z=0, rotation=Rotation3d.fromDegrees(0, 0, 240)), #I
            Pose3d(x=4.589, y=4.533, z=0, rotation=Rotation3d.fromDegrees(0, 0, 240)), #J
            Pose3d(x=4.373, y=4.553, z=0, rotation=Rotation3d.fromDegrees(0, 0, 300)), #K
            Pose3d(x=4.095, y=4.378, z=0, rotation=Rotation3d.fromDegrees(0, 0, 300))  #L
        ]

        editTran=[
            Transform3d(Translation3d(-0.15, 0, 0.5), Rotation3d.fromDegrees(0, 0, 90)),
            Transform3d(Translation3d(-0.2, 0, 0.78), Rotation3d.fromDegrees(0, 35, 0)),
            Transform3d(Translation3d(-0.2, 0, 1.18), Rotation3d.fromDegrees(0, 35, 0)),
            Transform3d(Translation3d(-0.3, 0, 1.78), Rotation3d.fromDegrees(0, 90, 0))
        ]

        pose3dList = [[None for _ in range(4)] for _ in range(12)] # for testing where it thinks coral is
        for i in range(12):
            for j in range(4):
                transformedPose = blueStarts[i].transformBy(editTran[j])
                blueHitboxes[i][j] = hitbox.hitboxFromPose3d(transformedPose, CoralAndAlgaeCameraConstants.radius)
                pose3dList[i][j] = transformedPose
            
        return blueHitboxes, pose3dList
    
    @staticmethod
    def makeAlgaeHitboxes():

        blueHitboxes = [[None, None] for _ in range(6)]
        blueStarts = [
            Pose3d(x=3.801, y=4.025, z=0, rotation=Rotation3d.fromDegrees(0, 0, 0)),    #A
            Pose3d(x=4.192, y=3.439, z=0, rotation=Rotation3d.fromDegrees(0, 0, 0)), #B
            Pose3d(x=4.838, y=3.409, z=0, rotation=Rotation3d.fromDegrees(0, 0, 0)), #C
            Pose3d(x=5.209, y=4.025, z=0, rotation=Rotation3d.fromDegrees(0, 0, 0)), #D
            Pose3d(x=4.823, y=4.611, z=0, rotation=Rotation3d.fromDegrees(0, 0, 0)), #E
            Pose3d(x=4.132, y=4.626, z=0, rotation=Rotation3d.fromDegrees(0, 0, 0)), #F

        ]

        editTran=[
            Transform3d(Translation3d(-0, 0, 0.9), Rotation3d.fromDegrees(0, 0, 0)),
            Transform3d(Translation3d(0, 0, 1.3), Rotation3d.fromDegrees(0, 0, 0))
        ]

        pose3dList = [[None for _ in range(4)] for _ in range(12)] # for testing where it thinks algae is

        for i in range(6):
            for j in range(2):
                transformedPose = blueStarts[i].transformBy(editTran[j])
                blueHitboxes[i][j] = hitbox.hitboxFromPose3d(transformedPose, CoralAndAlgaeCameraConstants.radius)
                pose3dList[i][j] = transformedPose
            
        return blueHitboxes, pose3dList 