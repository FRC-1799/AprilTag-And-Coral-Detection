from typing import Optional, Callable
import math
from wpimath.geometry import Translation2d, Rotation2d, Translation3d, Pose2d
from wpilib import DriverStation

FIELD_WIDTH = 16.54
FIELD_HEIGHT = 8.21

SPEAKER_POSE_BLUE = Translation3d(0.1, 5.55, 2.2)

def flipRotation2d(rotation: Rotation2d):
    return rotation.rotateBy(Rotation2d(math.radians(math.pi)))

def flipTranslation2d(translation: Translation2d) -> Translation2d:
    return Translation2d(FIELD_WIDTH - translation.X(), FIELD_HEIGHT - translation.Y())

def to_current_alliance_rotation(rotation_at_blue_side: Rotation2d) -> Rotation2d:
    y_axis = Rotation2d.from_degrees(90)
    difference_from_y_axis_at_blue_side = rotation_at_blue_side.minus(y_axis)
    difference_from_y_axis_new = difference_from_y_axis_at_blue_side.times(-1 if is_side_presented_as_red() else 1)
    return y_axis.rotate_by(difference_from_y_axis_new)

def to_current_alliance_translation(translation_at_blue_side: Translation2d) -> Translation2d:
    if is_side_presented_as_red():
        return Translation2d(FIELD_WIDTH - translation_at_blue_side.get_x(), translation_at_blue_side.get_y())
    return translation_at_blue_side

def to_current_alliance_translation_3d(translation3d_at_blue_side: Translation3d) -> Translation3d:
    translation_2d_at_current_alliance = to_current_alliance_translation(translation3d_at_blue_side.to_translation2d())
    if is_side_presented_as_red():
        return Translation3d(translation_2d_at_current_alliance.get_x(), translation_2d_at_current_alliance.get_y(), translation3d_at_blue_side.get_z())
    return translation3d_at_blue_side

def to_current_alliance_pose(pose_at_blue_side: Pose2d) -> Pose2d:
    return Pose2d(to_current_alliance_translation(pose_at_blue_side.get_translation()), to_current_alliance_rotation(pose_at_blue_side.get_rotation()))


def is_side_presented_as_red() -> bool:
    alliance = DriverStation.get_alliance()
    return alliance is not None and alliance == DriverStation.Alliance.Red

def get_current_alliance_driver_station_facing() -> Rotation2d:
    alliance = DriverStation.get_alliance() or DriverStation.Alliance.Red
    return Rotation2d(math.pi) if alliance == DriverStation.Alliance.Red else Rotation2d(0)

SPEAKER_POSITION_SUPPLIER: Callable[[], Translation2d] = lambda: to_current_alliance_translation(SPEAKER_POSE_BLUE.to_translation2d())
