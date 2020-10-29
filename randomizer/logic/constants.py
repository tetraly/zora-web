from enum import IntEnum
from typing import List, NewType
import random
from .direction import Direction

PositionNum = NewType("PositionNum", int)
RoomNum = NewType("RoomNum", int)
RoomOrPositionNum = NewType("RoomOrPositionNum", int)


class RoomAction(IntEnum):
  NO_ROOM_ACTION = 0  # 0 000
  KILLING_ENEMIES_OPENS_SHUTTER_DOORS = 1  # 0 001
  MASTER_ENEMY = 2  # 0 010
  KILLING_THE_BEAST_OPENS_SHUTTER_DOORS = 3
  EXPERIMENTAL_6 = 6
  KILLING_ENEMIES_OPENS_SHUTTER_DOORS_AND_DROPS_ITEM = 7
  PUSHABLE_BLOCK_HAS_NO_EFFECT = 8
  PUSHABLE_BLOCK_OPENS_SHUTTER_DOORS = 12
  PUSHABLE_BLOCK_MAKES_STAIRS_APPEAR = 13
  KILLING_ENEMIES_OPENS_SHUTTER_DOORS_DROPS_ITEM_AND_MAKES_BLOCK_PUSHABLE = 15


class SpriteSet(IntEnum):
  NO_SPRITE_SET = 0
  GORIYA_SPRITE_SET = 1
  DARKNUT_SPRITE_SET = 2
  WIZZROBE_SPRITE_SET = 3
  DODONGO_SPRITE_SET = 4
  GLEEOK_SPRITE_SET = 5
  PATRA_SPRITE_SET = 6


class DungeonPalette(IntEnum):
  BLACK_AND_WHITE = 0
  ACCENT_COLOR = 1
  PRIMARY = 2
  WATER = 3


class WallType(IntEnum):
  OPEN_DOOR = 0
  SOLID_WALL = 1
  WALK_THROUGH_WALL = 2
  ENTRANCE = 3  # really WALK_THROUGH_WALL_2
  BOMB_HOLE = 4
  LOCKED_DOOR_1 = 5
  LOCKED_DOOR_2 = 6
  SHUTTER_DOOR = 7

  def ToChar(self, direction: Direction) -> str:
    if self.value == WallType.OPEN_DOOR:
      return ' '
    elif self.value == WallType.SOLID_WALL:
      if direction in [Direction.EAST, Direction.WEST]:
        return '|'
      elif direction == Direction.NORTH:
        return 'ˉ'
      return '_'
    elif self.value == WallType.ENTRANCE:
      if direction == Direction.EAST:
        return '<'
      elif direction == Direction.WEST:
        return '>'
      elif direction == Direction.SOUTH:
        return '^'
      return 'v'
    elif self.value == WallType.BOMB_HOLE:
      return 'O'
    elif self.value == WallType.LOCKED_DOOR_1:
      return 'k'
    elif self.value == WallType.SHUTTER_DOOR:
      return 'x'
    return 'Q'

  @classmethod
  def RandomValue(cls) -> "WallType":
    while True:
      try:
        return cls(random.randrange(0x0, 0x7))
      except ValueError:
        continue


class LevelNumOrCaveType(IntEnum):

  def IsLevelNum(self) -> bool:
    return self.value in Range.VALID_LEVEL_NUMBERS

  def IsCaveType(self) -> bool:
    return self.value in Range.VALID_CAVE_TYPES

  def CastToCaveType(self) -> "CaveType":
    return CaveType(self.value)


class LevelNum(LevelNumOrCaveType):
  NO_LEVEL_NUM = 0x00
  LEVEL_1 = 0x01
  LEVEL_2 = 0x02
  LEVEL_3 = 0x03
  LEVEL_4 = 0x04
  LEVEL_5 = 0x05
  LEVEL_6 = 0x06
  LEVEL_7 = 0x07
  LEVEL_8 = 0x08
  LEVEL_9 = 0x09
  # No caves 0x0A - 0x0F
  # 0x10-0x25 are for overworld caves


class CaveType(LevelNumOrCaveType):
  NO_CAVE_TYPE = 0x00
  # Level numbers are 0x01-0x09
  # No caves 0x0A - 0x0F
  WOOD_SWORD_CAVE = 0x10
  TAKE_ANY_CAVE = 0x11
  WHITE_SWORD_CAVE = 0x12
  MAGICAL_SWORD_CAVE = 0x13
  ANY_ROAD_CAVE = 0x14
  HINT_CAVE_A = 0x15
  MONEY_MAKING_GAME = 0x16
  DOOR_REPAIR_CAVE = 0x17
  LETTER_CAVE = 0x18
  HINT_CAVE_B = 0x19
  POTION_SHOP = 0x1A
  PAY_ME_AND_ILL_TALK_CAVE_A = 0x1B
  PAY_ME_AND_ILL_TALK_CAVE_B = 0x1C
  SHOP_A = 0x1D
  SHOP_B = 0x1E
  SHOP_C = 0x1F
  SHOP_D = 0x20
  MEDIUM_SECRET_CAVE = 0x21
  LARGE_SECRET_CAVE = 0x22
  SMALL_SECRET_CAVE = 0x23
  ARMOS_ITEM_VIRTUAL_CAVE = 0x24
  COAST_ITEM_VIRTUAL_CAVE = 0x25

  def HasItems(self) -> bool:
    return self in [
        self.WOOD_SWORD_CAVE, self.TAKE_ANY_CAVE, self.WHITE_SWORD_CAVE, self.MAGICAL_SWORD_CAVE,
        self.LETTER_CAVE, self.POTION_SHOP, self.SHOP_A, self.SHOP_B, self.SHOP_C, self.SHOP_D,
        self.ARMOS_ITEM_VIRTUAL_CAVE, self.COAST_ITEM_VIRTUAL_CAVE
    ]


class GridId(IntEnum):
  NO_GRID_ID = 0
  GRID_A = 1
  GRID_B = 2

  @classmethod
  def GetGridIdForLevelNum(cls, level_num: LevelNum) -> "GridId":
    return GridId.GRID_B if level_num in [7, 8, 9] else GridId.GRID_A


class Range():
  VALID_LEVEL_NUMBERS = [LevelNum(n) for n in range(1, 10)]  # Levels 1-9 (1-indexed)
  VALID_ROOM_NUMBERS = [RoomNum(n) for n in range(0, 0x80)]
  VALID_ROOM_TABLE_NUMBERS = range(0, 6)  # Six tables (0-indexed)
  CARDINAL_DIRECTIONS = [Direction.NORTH, Direction.WEST, Direction.EAST, Direction.SOUTH]
  VALID_CAVE_TYPES = [CaveType(n) for n in range(0x10, 0x26)]
  VALID_CAVE_POSITION_NUMBERS = [1, 2, 3]  # Three possible positions per cave (1-indexed)
  VALID_LEVEL_NUMS_AND_CAVE_TYPES = ([int(n) for n in VALID_LEVEL_NUMBERS] +
                                     [int(n) for n in VALID_CAVE_TYPES])
  VALID_CAVE_TYPES_WITH_ITEMS = [
      CaveType.SHOP_A, CaveType.SHOP_B, CaveType.SHOP_C, CaveType.SHOP_D, CaveType.WOOD_SWORD_CAVE,
      CaveType.WHITE_SWORD_CAVE, CaveType.MAGICAL_SWORD_CAVE, CaveType.LETTER_CAVE,
      CaveType.ARMOS_ITEM_VIRTUAL_CAVE, CaveType.COAST_ITEM_VIRTUAL_CAVE
  ]
  FOO = ([
      CaveType.SHOP_A,
      CaveType.SHOP_B,
      CaveType.SHOP_C,
      CaveType.SHOP_D,
  ] + [CaveType(n) for n in range(0x10, 0x1C)] + [CaveType(n) for n in range(0x21, 0x26)])
  VALID_LEVEL_NUMS_AND_CAVE_TYPES_WITH_SHOPS_FIRST = ([int(n) for n in FOO] +
                                                      [int(n) for n in VALID_LEVEL_NUMBERS])


class Screen():
  POSSIBLE_FIRST_WEAPON_SCREENS = [
      0x0A, 0x0B, 0x0C, 0x0E, 0x0F, 0x1A, 0x1C, 0x1F, 0x34, 0x37, 0x3C, 0x3D, 0x44, 0x4A, 0x4E,
      0x5E, 0x64, 0x66, 0x6F, 0x70, 0x74, 0x75, 0x77
  ]

  CANDLE_BLOCKED_CAVE_SCREENS = [
      0x28, 0x46, 0x47, 0x48, 0x4B, 0x4D, 0x51, 0x56, 0x5B, 0x62, 0x63, 0x68, 0x6A, 0x6B, 0x6D, 0x78
  ]
  BOMB_BLOCKED_CAVE_SCREENS = [
      0x01, 0x03, 0x05, 0x07, 0x0D, 0x10, 0x12, 0x13, 0x14, 0x16, 0x1E, 0x26, 0x27, 0x2C, 0x2D,
      0x33, 0x67, 0x71, 0x76, 0x7B, 0x7C, 0x7D
  ]
  OPEN_CAVE_SCREENS = [
      0x04, 0x0A, 0x0B, 0x0C, 0x0E, 0x0F, 0x1A, 0x1C, 0x1F, 0x21, 0x22, 0x25, 0x34, 0x37, 0x3C,
      0x3D, 0x44, 0x4A, 0x4E, 0x5E, 0x64, 0x66, 0x6F, 0x70, 0x74, 0x75, 0x77
  ]
  RAFT_BLOCKED_CAVE_SCREENS = [0x2F, 0x45]
  POWER_BRACELET_BLOCKED_CAVE_SCREENS = [0x1D, 0x23, 0x49, 0x79]
  RECORDER_BLOCKED_CAVE_SCREENS = [0x42]

  ALL_SCREENS_WITH_1Q_CAVES = (CANDLE_BLOCKED_CAVE_SCREENS + BOMB_BLOCKED_CAVE_SCREENS +
                               OPEN_CAVE_SCREENS + RAFT_BLOCKED_CAVE_SCREENS +
                               POWER_BRACELET_BLOCKED_CAVE_SCREENS + RECORDER_BLOCKED_CAVE_SCREENS)


class HintType(IntEnum):
  WOOD_SWORD = 0
  WHITE_AND_MASTER_SWORD = 1
  ANY_ROAD = 2
  OW_HINT_1 = 3
  MMG = 4
  DOOR_REPAIR = 5
  LETTER_CAVE = 6
  OW_HINT_2 = 7
  POTION_SHOP = 8
  HINT_SHOP = 9
  OVERWORLD_HINT_1 = 10
  OVERWORLD_HINT_2 = 11
  OVERWORLD_HINT_3 = 12
  OVERWORLD_HINT_4 = 13
  SHOP_1 = 14
  SHOP_2 = 15
  TAKE_ANY = 16
  SECRET = 17
  HUNGRY_ENEMY = 18
  DUNGEON_HINT_A1 = 19
  DUNGEON_HINT_A2 = 20
  DUNGEON_HINT_B1 = 21
  DUNGEON_HINT_B2 = 22
  DUNGEON_HINT_A3 = 23
  DUNGEON_HINT_A4 = 24
  BOMB_UPGRADE = 25
  DUNGEON_HINT_B3 = 26
  MUGGER = 27
  SOMETHING_1 = 28
  SOMETHING_2 = 29
  SOMETHING_3 = 30
  SOMETHING_4 = 31
  SOMETHING_5 = 32
  SOMETHING_6 = 33
  TRIFORCE_CHECK = 34
  LEVEL_9_HINT = 35
  LEVEL_9_HINT_2 = 36
  LEVEL_9_HINT_3 = 37
  LEVEL_9_HINT_4 = 37
  OVERWORLD_HINT_5 = 38
  OVERWORLD_HINT_6 = 39
  ENGLISH_COMMUNITY_HINT = 98
  FRENCH_COMMUNITY_HINT = 99
