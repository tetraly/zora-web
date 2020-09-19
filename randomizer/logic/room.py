from typing import List, Optional
import logging
import random
import sys
from .constants import DungeonPalette, Range, RoomAction, RoomNum, WallType
from .direction import Direction
from .enemy import Enemy
from .item import Item
from .room_type import RoomType

log = logging.getLogger(__name__)


def NumBitsToShiftForBitmask(bitmask: int) -> int:
  assert bitmask > 0x0
  assert bitmask < 0x100

  bit_number = 0
  while bitmask % (pow(2, (bit_number + 1))) == 0:
    bit_number += 1

  assert bit_number in range(0, 8)
  return bit_number


class Room():

  def __init__(self, rom_data: Optional[List[int]] = None) -> None:
    if not rom_data:
      rom_data = [0x26, 0x26, 0x00, 0x00, 0x17, 0x00]
    if rom_data[4] & 0x1F == 0x03:
      stuff_not_to_change = rom_data[4] & 0xE0
      rom_data[4] = stuff_not_to_change + 0x0E
    self.rom_data = rom_data

    self.marked_as_visited = False
    # -1 is used as a sentinal value indicating a lack of stairway room
    self.stairs_destination = RoomNum(-1)

  def _ReadRomBits(self, byte_num: int, read_bitmask: int) -> int:
    assert byte_num in range(0, 6)
    data = self.rom_data[byte_num] & read_bitmask
    return data >> NumBitsToShiftForBitmask(read_bitmask)

  def _SetRomBits(self, byte_num: int, write_bitmask: int, value: int) -> None:
    assert byte_num in range(0, 6)

    bits_to_write = value << NumBitsToShiftForBitmask(write_bitmask)
    # Make sure that you don't have too large a value to fit into the write bitmask
    assert bits_to_write == bits_to_write & write_bitmask

    # Save and keep track of bits that should not be overwritten.
    read_bitmask = 0xFF - write_bitmask
    bits_to_save = self.rom_data[byte_num] & read_bitmask

    self.rom_data[byte_num] = bits_to_save + bits_to_write

  def GetRomData(self) -> List[int]:
    if self.GetRoomType() in [
        RoomType.ELDER_PLACEHOLDER_ROOM_TYPE, RoomType.HUNGRY_ENEMY_PLACEHOLDER_ROOM_TYPE,
        RoomType.TRIFORCE_CHECK_PLACEHOLDER_ROOM_TYPE
    ]:
      self.SetRoomType(RoomType.BLACK_ROOM)
    if not self.IsStairwayRoom() and self.GetEnemy() == Enemy.TRIFORCE_CHECKER_PLACEHOLDER_ELDER:
      self.SetEnemy(Enemy.ELDER)
    return self.rom_data

  def IsMarkedAsVisited(self) -> bool:
    return self.marked_as_visited

  def MarkAsVisited(self) -> None:
    self.marked_as_visited = True

  def ClearVisitMark(self) -> None:
    self.marked_as_visited = False

  # Getters/Setters for bytes 0 and 1

  def HasShutterDoor(self) -> bool:
    for direction in Range.CARDINAL_DIRECTIONS:
      if self.GetWallType(direction) == WallType.SHUTTER_DOOR:
        return True
    return False

  def GetWallType(self, direction: Direction) -> WallType:
    assert self.GetRoomType() not in [RoomType.ITEM_STAIRCASE, RoomType.TRANSPORT_STAIRCASE]
    byte_num = 1 if direction in [Direction.EAST, Direction.WEST] else 0
    read_bitmask = 0xE0 if direction in [Direction.NORTH, Direction.WEST] else 0x1C

    return WallType(self._ReadRomBits(byte_num, read_bitmask))

  # According to http://www.bwass.org/romhack/zelda1/zelda1bank6.txt:
  # Bytes in table 0 represent:
  # xxx. ....	Type of Door on Top Wall
  # ...x xx..	Type of Door on Bottom Wall
  # .... ..xx	Code for Palette 0 (Outer Border)
  # Bytes in table 1 represent:
  # xxx. ....	Type of Door on Left Wall
  # ...x xx..	Type of Door on Right Wall
  # .... ..xx	Code for Palette 1 (Inner Section)
  def SetWallType(self, direction: Direction, wall_type: WallType) -> None:
    assert self.GetRoomType() not in [RoomType.ITEM_STAIRCASE, RoomType.TRANSPORT_STAIRCASE]
    assert direction in Range.CARDINAL_DIRECTIONS

    byte_num = 1 if direction in [Direction.EAST, Direction.WEST] else 0
    write_bitmask = 0xE0 if direction in [Direction.NORTH, Direction.WEST] else 0x1C
    self._SetRomBits(byte_num, write_bitmask, wall_type.value)

  def SetOuterPalette(self, palette: DungeonPalette) -> None:
    self._SetRomBits(0, 0x03, palette.value)

  def SetInnerPalette(self, palette: DungeonPalette) -> None:
    self._SetRomBits(1, 0x03, palette.value)

  ### Staircase room methods ###

  def IsStairwayRoom(self) -> bool:
    return self.GetRoomType() in [RoomType.ITEM_STAIRCASE, RoomType.TRANSPORT_STAIRCASE]

  def IsItemStairway(self) -> bool:
    return self.GetStairwayRoomLeftExit() == self.GetStairwayRoomRightExit()

  def IsTransportStairway(self) -> bool:
    return self.IsStairwayRoom() and not self.IsItemStairway()

  def GetStairwayRoomLeftExit(self) -> RoomNum:
    assert self.IsStairwayRoom()
    return RoomNum(self._ReadRomBits(0, 0x7F))

  def GetStairwayRoomRightExit(self) -> RoomNum:
    assert self.IsStairwayRoom()
    return RoomNum(self._ReadRomBits(1, 0x7F))

  def SetStairwayRoomExit(self, room_num: RoomNum, is_right_side: bool) -> None:
    assert self.IsStairwayRoom()
    assert room_num in Range.VALID_ROOM_NUMBERS
    self._SetRomBits(1 if is_right_side else 0, 0x7F, int(room_num))

  def HasStairs(self) -> bool:
    # -1 is used as a sentinal value indicating a lack of stairs room
    return self.stairs_destination != RoomNum(-1)

  def GetStairsDestination(self) -> RoomNum:
    return self.stairs_destination

  def SetStairsDestination(self, stairs_destination: RoomNum) -> None:
    self.stairs_destination = stairs_destination

  def ClearStairsDestination(self) -> None:
    self.stairs_destination = RoomNum(-1)

  def SetReturnPosition(self, return_position: int) -> None:
    assert self.IsStairwayRoom()
    self._SetRomBits(2, 0xFF, return_position)

  # Byte 2
  def GetEnemy(self) -> Enemy:
    assert not self.IsStairwayRoom()
    lower_bits = self._ReadRomBits(byte_num=2, read_bitmask=0x3F)
    upper_bit = self._ReadRomBits(byte_num=3, read_bitmask=0x80)
    return Enemy(lower_bits + 0x40 if upper_bit > 0 else lower_bits)

  def SetEnemy(self, enemy: Enemy) -> None:
    assert not self.IsStairwayRoom()
    enemy_code = enemy.value
    self._SetRomBits(3, 0x80, 1 if enemy_code >= 0x40 else 0)
    self._SetRomBits(2, 0x3F, (enemy_code % 0x40))

  def SetEnemyQuantityCode(self, code: int) -> None:
    assert code in range(0, 4)
    self._SetRomBits(2, 0xC0, code)

  # Byte 3
  def GetRoomType(self) -> RoomType:
    return RoomType(self._ReadRomBits(byte_num=3, read_bitmask=0x3F))

  def SetRoomType(self, room_type: RoomType) -> None:
    self._SetRomBits(3, 0x3F, room_type.value)

  def IsItemStaircase(self) -> bool:
    return self.GetRoomType() == RoomType.ITEM_STAIRCASE

  def IsTransportStaircase(self) -> bool:
    return self.GetRoomType() == RoomType.TRANSPORT_STAIRCASE

  ### Byte 4 -- Item-related methods ###
  def SetItem(self, item_num: Item) -> None:
    self._SetRomBits(byte_num=4, write_bitmask=0x1F, value=item_num.value)

  def GetItem(self) -> Item:
    return Item(self._ReadRomBits(byte_num=4, read_bitmask=0x1F))

  def HasItem(self) -> bool:
    return not self.GetItem() == Item.NOTHING

  def SetDarkRoomBit(self, is_dark_room: bool) -> None:
    self._SetRomBits(4, 0x80, 1 if is_dark_room else 0)

  ### Byte 5
  def SetItemPositionCode(self, code: int) -> None:
    assert code in range(0, 4)
    self._SetRomBits(5, 0x30, code)

  def HasDropBitSet(self) -> bool:
    # Checks for killing_enemies_opens_shutters_and_drops_item condition
    return self._ReadRomBits(byte_num=5, read_bitmask=0x07) == 0x07

  def SetBossRoarSound(self, roar_sound: bool = True) -> None:
    self._SetRomBits(4, 0x20, 0x01 if roar_sound else 0x00)

  # TODO: This could be re-implemented using math on room_action's value more easily
  def SetRoomAction(self, room_action: RoomAction) -> None:
    if room_action == RoomAction.NO_ROOM_ACTION:
      self._SetRomBits(3, 0x40, 0x00)
      self._SetRomBits(5, 0x07, 0x00)
    elif room_action == RoomAction.KILLING_ENEMIES_OPENS_SHUTTER_DOORS:
      self._SetRomBits(3, 0x40, 0x00)
      self._SetRomBits(5, 0x07, 0x01)
    elif room_action == RoomAction.MASTER_ENEMY:
      self._SetRomBits(3, 0x40, 0x00)
      self._SetRomBits(5, 0x07, 0x02)
    elif room_action == RoomAction.KILLING_THE_BEAST_OPENS_SHUTTER_DOORS:
      self._SetRomBits(3, 0x40, 0x00)
      self._SetRomBits(5, 0x07, 0x03)
    elif room_action == RoomAction.PUSHABLE_BLOCK_OPENS_SHUTTER_DOORS:
      self._SetRomBits(3, 0x40, 0x01)
      self._SetRomBits(5, 0x07, 0x04)
    elif room_action == RoomAction.PUSHABLE_BLOCK_MAKES_STAIRS_APPEAR:
      self._SetRomBits(3, 0x40, 0x01)
      self._SetRomBits(5, 0x07, 0x05)
    elif room_action == RoomAction.KILLING_ENEMIES_OPENS_SHUTTER_DOORS_AND_DROPS_ITEM:
      self._SetRomBits(3, 0x40, 0x00)
      self._SetRomBits(5, 0x07, 0x07)
    elif room_action == RoomAction.PUSHABLE_BLOCK_HAS_NO_EFFECT:
      self._SetRomBits(3, 0x40, 0x01)
      self._SetRomBits(5, 0x07, 0x00)
    elif room_action == RoomAction.KILLING_ENEMIES_OPENS_SHUTTER_DOORS_DROPS_ITEM_AND_MAKES_BLOCK_PUSHABLE:
      self._SetRomBits(3, 0x40, 0x01)
      self._SetRomBits(5, 0x07, 0x07)
    else:
      log.error("Found undefined room action code: %d" % int(room_action))
      sys.exit(1)
