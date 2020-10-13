from absl import logging
from typing import Optional

from .constants import CaveType, LevelNum, LevelNumOrCaveType, PositionNum, Range, RoomNum, RoomOrPositionNum


class Location():

  def __init__(self,
               level_num: LevelNum = LevelNum.NO_LEVEL_NUM,
               cave_type: CaveType = CaveType.NO_CAVE_TYPE,
               room_num: Optional[RoomNum] = None,
               position_num: Optional[int] = None):
    self.level_num_or_cave_type: LevelNumOrCaveType
    self.sub_id: RoomOrPositionNum

    if level_num != LevelNum.NO_LEVEL_NUM:
      assert level_num in Range.VALID_LEVEL_NUMBERS
      assert room_num in Range.VALID_ROOM_NUMBERS
      assert cave_type is CaveType.NO_CAVE_TYPE
      assert position_num is None
      self.level_num_or_cave_type = level_num
      self.sub_id = RoomOrPositionNum(room_num)

    elif cave_type is not None:
      assert cave_type in Range.VALID_CAVE_TYPES
      assert position_num in Range.VALID_CAVE_POSITION_NUMBERS
      assert level_num is LevelNum.NO_LEVEL_NUM
      assert room_num is None
      self.level_num_or_cave_type = cave_type
      self.sub_id = RoomOrPositionNum(position_num)

    else:
      logging.fatal("Location: level or cave number must be specified")

  @classmethod
  def LevelRoom(cls, level_num: LevelNum, room_num: RoomNum) -> "Location":
    return cls(level_num=level_num, room_num=room_num)

  @classmethod
  def CavePosition(cls, cave_type: CaveType, position_num: int) -> "Location":
    return cls(cave_type=cave_type, position_num=position_num)

  def IsLevelRoom(self) -> bool:
    return self.level_num_or_cave_type in Range.VALID_LEVEL_NUMBERS

  def IsCavePosition(self) -> bool:
    return self.level_num_or_cave_type in Range.VALID_CAVE_TYPES

  def GetUniqueIdentifier(self) -> int:
    return 1000 * self.level_num_or_cave_type + self.sub_id

  def GetLevelNum(self) -> LevelNum:
    assert self.IsLevelRoom()
    return LevelNum(self.level_num_or_cave_type)

  def GetLevelOrCaveNum(self) -> LevelNumOrCaveType:
    return self.level_num_or_cave_type

  def GetRoomNum(self) -> RoomNum:
    assert self.IsLevelRoom()
    return RoomNum(self.sub_id)

  def GetCaveType(self) -> CaveType:
    assert self.IsCavePosition()
    return CaveType(self.level_num_or_cave_type)

  def GetCaveNum(self) -> int:
    assert self.IsCavePosition()
    return int(self.level_num_or_cave_type) - 0x10

  def GetPositionNum(self) -> PositionNum:
    assert self.IsCavePosition()
    return PositionNum(self.sub_id)
