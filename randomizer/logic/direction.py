from enum import IntEnum
import random


class Direction(IntEnum):
  NO_DIRECTION = -0x1000
  NORTH = -0x10
  SOUTH = 0x10
  STAIRCASE = 0x00
  WEST = -0x1
  EAST = 0x1

  @classmethod
  def FromRomValue(cls, rom_value: int) -> "Direction":
    assert rom_value in range(1, 5)
    if rom_value == 1:
      return Direction.NORTH
    if rom_value == 2:
      return Direction.SOUTH
    if rom_value == 3:
      return Direction.WEST
    # rom_value == 4
    return Direction.EAST

  def GetRomValue(self) -> int:
    value: int
    if self == Direction.NORTH:
      value = 0x01
    if self == Direction.SOUTH:
      value = 0x02
    if self == Direction.WEST:
      value = 0x03
    if self == Direction.EAST:
      value = 0x04
    assert value in range(1, 5)
    return value

  def Reverse(self) -> "Direction":
    if self == Direction.NORTH:
      return Direction.SOUTH
    if self == Direction.SOUTH:
      return Direction.NORTH
    if self == Direction.EAST:
      return Direction.WEST
    if self == Direction.WEST:
      return Direction.EAST
    if self == Direction.STAIRCASE:
      return Direction.STAIRCASE
    return Direction.NO_DIRECTION

  def IsCardinalDirection(self) -> bool:
    return self in [Direction.NORTH, Direction.WEST, Direction.EAST, Direction.SOUTH]

  @classmethod
  def RandomCardinalDirection(cls) -> "Direction":
    return random.choice([Direction.NORTH, Direction.WEST, Direction.EAST, Direction.SOUTH])
