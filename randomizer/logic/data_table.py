import math
import random
import sys
from typing import Dict, List, Tuple, Union
from absl import logging
from .cave import Cave
from .constants import CaveType, GridId, LevelNum, LevelNumOrCaveType, Range, RoomNum, SpriteSet
from .direction import Direction
from .item import Item
from .location import Location
from .patch import Patch
from .room import Room


class DataTable():
  NES_FILE_OFFSET = 0x10
  OVERWORLD_DATA_START_ADDRESS = 0x18400 + NES_FILE_OFFSET
  LEVEL_1_TO_6_DATA_START_ADDRESS = 0x18700 + NES_FILE_OFFSET
  LEVEL_7_TO_9_DATA_START_ADDRESS = 0x18A00 + NES_FILE_OFFSET
  LEVEL_TABLE_SIZE = 0x80
  NUM_BYTES_OF_DATA_PER_ROOM = 6
  ARMOS_ITEM_ADDRESS = 0x10CF5 + NES_FILE_OFFSET
  COAST_ITEM_ADDRESS = 0x1788A + NES_FILE_OFFSET
  CAVE_TYPE_CAVE_NUM_OFFSET = 0x10
  BOMB_UPGRADE_PRICE_ADDRESS = 0x4B72 + NES_FILE_OFFSET
  BOMB_UPGRADE_QUANTITY_ADDRESS = 0x4B8B + NES_FILE_OFFSET
  BOMB_UPGRADE_DISPLAY_PRICE_ADDRESS = 0x1A2A2 + NES_FILE_OFFSET
  HUNGRY_ENEMY_SPRITE_CODE_ADDRESS = 0x6F2E + NES_FILE_OFFSET
  TEXT_ASSIGNMENT_ADDRESS = 0x4A07 + NES_FILE_OFFSET
  ANY_ROAD_SCREEN_NUMS_ADDRESS = 0x19334 + NES_FILE_OFFSET
  RECORDER_SCREEN_NUMS_ADDRESS = 0x6010 + NES_FILE_OFFSET
  RECORDER_Y_COORDS_ADDRESS = 0x6119 + NES_FILE_OFFSET
  WHITE_SWORD_REQUIRED_HEARTS_ADDRESS = 0x48FD + NES_FILE_OFFSET
  MAGICAL_SWORD_REQUIRED_HEARTS_ADDRESS = 0x4906 + NES_FILE_OFFSET
  FIRST_BOMB_UPGRADE_LEVEL_ADDRESS = 0x4AE0 + NES_FILE_OFFSET
  SECOND_BOMB_UPGRADE_LEVEL_ADDRESS = 0x4AE4 + NES_FILE_OFFSET

  LEVEL_METADATA_ADDRESS = 0x19300 + NES_FILE_OFFSET
  LEVEL_METADATA_OFFSET = 0xFC
  GATEWAY_OFFSET = 0x23
  ENEMY_QUANTITIES_OFFSET = 0x24
  ITEM_POSITIONS_OFFSET = 0x29
  OFFSET_OFFSET = 0x2D
  START_ROOM_OFFSET = 0x2F
  TRIFORCE_LOCATION_OFFSET = 0x30
  STAIRCASE_LIST_OFFSET = 0x34
  ENTRANCE_DIRECTION_OFFSET = 0x3D
  MAP_BYTES_OFFSET = 0x3F
  MAP_THINGIES_OFFSET = 0x4F

  DARK_PALETTE_COLOR_OFFSETS = [
      0x0C, 0x20, 0x7D, 0x85, 0x86, 0x8A, 0x8E, 0x8F, 0x92, 0x93, 0xBD, 0xC5, 0xC6, 0xCA, 0xCE,
      0xCF, 0xD2, 0xD3, 0xD7
  ]
  MEDIUM_PALETTE_COLOR_OFFSETS = [0x0D, 0x11, 0x21, 0x7E, 0x82, 0x87, 0x8B, 0xBE, 0xC2, 0xC7, 0xCB]
  LIGHT_PALETTE_COLOR_OFFSETS = [0x0E, 0x12, 0x22, 0x7F, 0x83, 0xBF, 0xC3]
  WATER_PALETTE_COLOR_OFFSETS = [0x10, 0x81, 0x89, 0xC1, 0xC9]

  SPRITE_SET_ADDRESS = 0xC010
  BOSS_SPRITE_SET_ADDRESS = 0xC024

  SPRITE_SET_VALUE_LOOKUP: Dict[SpriteSet, List[int]] = {
      SpriteSet.GORIYA_SPRITE_SET: [0xBB, 0x9D],
      SpriteSet.DARKNUT_SPRITE_SET: [0x7B, 0x98],
      SpriteSet.WIZZROBE_SPRITE_SET: [0x9B, 0x9A],
      SpriteSet.DODONGO_SPRITE_SET: [0xDB, 0x9F],
      SpriteSet.GLEEOK_SPRITE_SET: [0xDB, 0xA3],
      SpriteSet.PATRA_SPRITE_SET: [0xDB, 0xA7]
  }

  def __init__(self) -> None:
    self.overworld_raw_data = list(open("randomizer/data/overworld-data.bin", 'rb').read(0x300))
    self.level_1_to_6_raw_data = list(open("randomizer/data/level-1-6-data.bin", 'rb').read(0x300))
    self.level_7_to_9_raw_data = list(open("randomizer/data/level-7-9-data.bin", 'rb').read(0x300))
    self.level_metadata = list(open("randomizer/data/level-metadata.bin", 'rb').read(0x9D8))
    self.overworld_caves: List[Cave] = []
    self.level_1_to_6_rooms: List[Room] = []
    self.level_7_to_9_rooms: List[Room] = []
    self.sprite_set_patch = Patch()
    self.misc_data_patch = Patch()

  def GetCaveDestination(self, screen_num: int) -> Union[LevelNum, CaveType]:
    foo = self.overworld_raw_data[0x80 + screen_num]
    bar = foo >> 2
    #bar -= 0x10
    try: 
      return LevelNum(bar)
    except ValueError:
      return CaveType(bar)

  def SetCaveDestination(self, screen_num: int, level_num_or_cave_type: Union[LevelNum, CaveType]) -> None:
    foo = self.overworld_raw_data[0x80 + screen_num]
    bits_to_keep = foo & 0x03

    #foo = level_num_or_cave_type + 0x10
    #bits_to_write = foo << 2

    bits_to_write = level_num_or_cave_type.value << 2
    self.overworld_raw_data[0x80 + screen_num] = bits_to_keep + bits_to_write

  def SetLevelGrid(self, grid_id: GridId, level_grid: List[Room]) -> None:
    if grid_id == GridId.GRID_A:
      self.level_1_to_6_rooms = level_grid
    else:
      self.level_7_to_9_rooms = level_grid

  def ResetToVanilla(self) -> None:
    self._ReadOverworldData()
    self.level_1_to_6_rooms = self._ReadDataForLevelGrid(self.level_1_to_6_raw_data)
    self.level_7_to_9_rooms = self._ReadDataForLevelGrid(self.level_7_to_9_raw_data)
    self.level_metadata = list(open("randomizer/data/level-metadata.bin", 'rb').read(0x9D8))
    self.sprite_set_patch = Patch()

  def _ReadDataForLevelGrid(self, level_data: List[int]) -> List[Room]:
    rooms: List[Room] = []
    for room_num in Range.VALID_ROOM_NUMBERS:
      room_data: List[int] = []
      for byte_num in range(0, self.NUM_BYTES_OF_DATA_PER_ROOM):
        room_data.append(level_data[byte_num * self.LEVEL_TABLE_SIZE + room_num])
      rooms.append(Room(room_data))
    return rooms

  def GetLevelNumberOrCaveType(self, screen_num: int) -> Union[LevelNum, CaveType]:
    level_num_or_cave_type = (self.overworld_raw_data[0x80 + screen_num] & 0xFC) >> 2
    try:
      return LevelNum(level_num_or_cave_type)
    except ValueError:
      return CaveType(level_num_or_cave_type)
       

  def _GetOverworldCaveDataIndex(self, cave_type: CaveType, position_num: int,
                                 is_second_byte: bool) -> int:
    cave_index = int(cave_type - 0x10)
    assert cave_index in range(0, 0x16)
    second_byte_index = 0x3C if is_second_byte else 0x00
    return 0x200 + second_byte_index + 3 * cave_index + position_num

  def _ReadOverworldData(self) -> None:
    self.overworld_caves = []
    for cave_type in Range.VALID_CAVE_TYPES:
      cave_num = cave_type - 0x10
      if cave_type == CaveType.ARMOS_ITEM_VIRTUAL_CAVE:
        self.overworld_caves.append(Cave([0x3F, Item.POWER_BRACELET, 0x7F, 0x00, 0x00, 0x00]))
      elif cave_type == CaveType.COAST_ITEM_VIRTUAL_CAVE:
        self.overworld_caves.append(Cave([0x3F, Item.HEART_CONTAINER, 0x7F, 0x00, 0x00, 0x00]))
      else:
        assert cave_type in Range.VALID_CAVE_TYPES  # Not needed?
        cave_data: List[int] = []
        for position_num in range(0, 3):
          cave_data.append(self.overworld_raw_data[self._GetOverworldCaveDataIndex(
              cave_type, position_num, is_second_byte=False)])
        for position_num in range(0, 3):
          cave_data.append(self.overworld_raw_data[self._GetOverworldCaveDataIndex(
              cave_type, position_num, is_second_byte=True)])
        self.overworld_caves.append(Cave(cave_data))
    assert len(self.overworld_caves) == 22  # 0-19 are actual caves, 20-21 are for the armos/coast

  def GetRoom(self, level_num: LevelNum, room_num: RoomNum) -> Room:
    assert level_num in Range.VALID_LEVEL_NUMBERS
    assert room_num in Range.VALID_ROOM_NUMBERS

    if level_num in [7, 8, 9]:
      return self.level_7_to_9_rooms[room_num]
    return self.level_1_to_6_rooms[room_num]

  def GetRoomItem(self, location: Location) -> Item:
    assert location.IsLevelRoom()
    if location.GetLevelNum() in [7, 8, 9]:
      return self.level_7_to_9_rooms[location.GetRoomNum()].GetItem()
    return self.level_1_to_6_rooms[location.GetRoomNum()].GetItem()

  def SetRoomItem(self, item: Item, location: Location) -> None:
    assert location.IsLevelRoom()
    if location.GetLevelNum() in [7, 8, 9]:
      self.level_7_to_9_rooms[location.GetRoomNum()].SetItem(item)
    else:
      self.level_1_to_6_rooms[location.GetRoomNum()].SetItem(item)

  def GetCaveItem(self, location: Location) -> Item:
    assert location.IsCavePosition()
    return self.overworld_caves[location.GetCaveNum()].GetItemAtPosition(location.GetPositionNum())

  def SetCaveItem(self, item: Item, location: Location) -> None:
    assert location.IsCavePosition()
    self.overworld_caves[location.GetCaveNum()].SetItemAtPosition(item, location.GetPositionNum())

  def SetCavePrice(self, price: int, location: Location) -> None:
    assert location.IsCavePosition()
    self.overworld_caves[location.GetCaveNum()].SetPriceAtPosition(price, location.GetPositionNum())

  def AdjustHungryEnemyForSpriteSet(self, sprite_set: SpriteSet) -> None:
    sprite_code = 0xB2 # Wizzrobe
    #if sprite_set == SpriteSet.WIZZROBE_SPRITE_SET:
    #  code = 0xB4
    if sprite_set == SpriteSet.DARKNUT_SPRITE_SET:
      sprite_code = random.choice([0xAA, 0xB0]) # Gibdo, Darknut
    elif sprite_set == SpriteSet.GORIYA_SPRITE_SET:
      sprite_code = random.choice([0xAA, 0xAC, 0xAE, 0xB0]) # Rope, Stalfos, Wallmaster, Goriya
    self.misc_data_patch.AddData(self.HUNGRY_ENEMY_SPRITE_CODE_ADDRESS, [sprite_code])

  def RandomizeBombUpgrades(self) -> None:
    done = False
    while not done:
      price = random.randrange(75, 125)
      if price == 100:
        continue
      quantity = random.randrange(2, 6)
      if price not in range(110, 126) or quantity not in [2, 3]:
        done = True
    self.misc_data_patch.AddData(self.BOMB_UPGRADE_PRICE_ADDRESS, [price])
    self.misc_data_patch.AddData(self.BOMB_UPGRADE_QUANTITY_ADDRESS, [quantity])
    
    #ones_digit = price % 10
    #tens_digit = math.floor((price % 100) / 10))
    print(price)
    bomb_upgrade_price_text: List[int] = [
      0x01 if price >= 100 else 0x24,
       math.floor((price % 100) / 10),
       price % 10
    ]
    print (bomb_upgrade_price_text)
    input("BOMB!")
    
    # Change white and magical sword heart container requirements.
    # Note that it's stored in the upper 4 bits, not the lower 4 bits, of that byte
    self.misc_data_patch.AddData(self.WHITE_SWORD_REQUIRED_HEARTS_ADDRESS,
                                 [random.randrange(4, 6) * 0x10])
    self.misc_data_patch.AddData(self.MAGICAL_SWORD_REQUIRED_HEARTS_ADDRESS,
                                 [random.randrange(8, 12) * 0x10])

  def SetBombUpgradeLevel(self, level_num: int, first_upgrader: bool) -> None:
    address = self.FIRST_BOMB_UPGRADE_LEVEL_ADDRESS if first_upgrader else self.SECOND_BOMB_UPGRADE_LEVEL_ADDRESS
    self.misc_data_patch.AddData(address, [level_num])

  def SetTextGroup(self, level_num: int, group_id: str) -> None:
    assert level_num in range(1, 10)
    assert group_id in ["a", "b"]
    self.misc_data_patch.AddData(self.TEXT_ASSIGNMENT_ADDRESS + 2 * level_num,
                                 [0x23, 0x8A] if group_id == "a" else [0x69, 0x8A])

  def UpdateAnyRoadAndRecorderScreensNums(self, any_road_screen_nums: List[int],
                                          recorder_screen_nums: List[int]) -> None:
    assert len(any_road_screen_nums) == 4
    assert len(recorder_screen_nums) == 8
    self.misc_data_patch.AddData(self.ANY_ROAD_SCREEN_NUMS_ADDRESS, any_road_screen_nums)
    self.misc_data_patch.AddData(self.RECORDER_SCREEN_NUMS_ADDRESS, recorder_screen_nums)
    
    recorder_y_coords = [0x8D, 0x8D, 0x8D, 0x8D, 0x8D, 0x8D, 0x8D, 0x8D]
    screens_needing_custom_recorder_y_coords = {
      0x05 - 1: 0xAD, # Vanilla 9
      0x0A - 1: 0x5D, # Vanilla WS
      0x21 - 1: 0x9D, # Vanilla Mags
      0x23 - 1: 0xAD, # Grave any road
      0x2C - 1: 0xAD, # Monocle rock
      0x42 - 1: 0xAD, # Vanilla 7
      0x6D - 1: 0x5D, # Vanilla 8
      0x79 - 1: 0xAD, # Near start any road
    }
    for i in range(8):
      if recorder_screen_nums[i] in screens_needing_custom_recorder_y_coords:
        recorder_y_coords[i] = screens_needing_custom_recorder_y_coords[recorder_screen_nums[i]]
    self.misc_data_patch.AddData(self.RECORDER_Y_COORDS_ADDRESS, recorder_y_coords)  
    
    # Set the stair position code to 3 for any roads.
    for screen_num in any_road_screen_nums:
      foo = self.overworld_raw_data[0x280 + screen_num]
      bits_to_keep = foo & 0xCF
      bits_to_write = 0x03 * 0x10
      self.overworld_raw_data[0x280 + screen_num] = bits_to_keep + bits_to_write
      
  def ClearAllVisitMarkers(self) -> None:
    logging.debug("Clearing Visit markers")
    for room in self.level_1_to_6_rooms:
      room.ClearVisitMark()
    for room in self.level_7_to_9_rooms:
      room.ClearVisitMark()

  def ClearStaircaseRoomNumbersForLevel(self, level_num: LevelNum) -> None:
    print("CLEAR!  level %s" % level_num)
    assert level_num in Range.VALID_LEVEL_NUMBERS
    offset = level_num * self.LEVEL_METADATA_OFFSET + self.STAIRCASE_LIST_OFFSET
    for counter in range(0, 9):
      self.level_metadata[offset + counter] = 0xFF

  def AddStaircaseRoomNumberForLevel(self, level_num: LevelNum, room_num: RoomNum) -> None:
    print("ADD!  level %s" % level_num)
    assert level_num in Range.VALID_LEVEL_NUMBERS
    offset = level_num * self.LEVEL_METADATA_OFFSET + self.STAIRCASE_LIST_OFFSET
    assert room_num in range(0, 0x80)
    for counter in range(0, 9):
      if self.level_metadata[offset + counter] == 0xFF:
        print("Found a FF")
        self.level_metadata[offset + counter] = room_num
        return
    print("This should never happen! (AddStaircaseRoomNumberForLevel)")
    assert (1 == 2)

  def UpdateCompassPointer(self, location: Location) -> None:
    assert location.IsLevelRoom()
    (level_num, room_num) = (location.GetLevelNum(), location.GetRoomNum())
    assert room_num in range(0, 0x100)
    self.level_metadata[level_num * self.LEVEL_METADATA_OFFSET +
                        self.TRIFORCE_LOCATION_OFFSET] = room_num

  def WriteDungeonPalette(self, level_num: LevelNum, palette: Tuple[int, int, int, int]) -> None:
    (dark, medium, light, water) = palette
    assert dark in range(0, 0x100)
    assert medium in range(0, 0x100)
    assert light in range(0, 0x100)
    assert water in range(0, 0x100)

    for offset in self.DARK_PALETTE_COLOR_OFFSETS:
      self.level_metadata[level_num * self.LEVEL_METADATA_OFFSET + offset] = dark
    for offset in self.MEDIUM_PALETTE_COLOR_OFFSETS:
      self.level_metadata[level_num * self.LEVEL_METADATA_OFFSET + offset] = medium
    for offset in self.LIGHT_PALETTE_COLOR_OFFSETS:
      self.level_metadata[level_num * self.LEVEL_METADATA_OFFSET + offset] = light
    for offset in self.WATER_PALETTE_COLOR_OFFSETS:
      self.level_metadata[level_num * self.LEVEL_METADATA_OFFSET + offset] = water

  # Gets a list of staircase rooms for a level.
  #
  # Note that this will include not just passage staircases between two
  # dungeon rooms but also item rooms with only one passage two and
  # from a dungeon room.
  def GetLevelStaircaseRoomNumberList(self, level_num: LevelNum) -> List[RoomNum]:
    assert level_num in Range.VALID_LEVEL_NUMBERS
    offset = level_num * self.LEVEL_METADATA_OFFSET + self.STAIRCASE_LIST_OFFSET
    tbr: List[RoomNum] = []
    for offset in range(0, 9):
      tbr.append(RoomNum(self.level_metadata[offset]))
    return tbr

  def SetMapData(self, level_num: LevelNum, map_bytes: List[int], thingies: List[int],
                 offset: int) -> None:
    assert level_num in Range.VALID_LEVEL_NUMBERS
    level_offset = level_num * self.LEVEL_METADATA_OFFSET
    for num in range(0, 0x10):
      self.level_metadata[level_offset + self.MAP_BYTES_OFFSET + num] = map_bytes[num]
    for num in range(0, 44):
      self.level_metadata[level_offset + self.MAP_THINGIES_OFFSET + num] = thingies[num]
    self.level_metadata[level_offset + self.OFFSET_OFFSET] = (4 - offset) % 16
    self.level_metadata[level_offset + self.OFFSET_OFFSET + 1] = ((32 - offset) % 32) * 8

  def SetStartRoomDataForLevel(self, level_num: LevelNum, start_room: RoomNum,
                               entrance_direction: Direction) -> None:
    level_offset = level_num * self.LEVEL_METADATA_OFFSET
    if start_room:
      self.level_metadata[level_offset + self.START_ROOM_OFFSET] = start_room
    if entrance_direction:
      self.level_metadata[level_offset +
                          self.ENTRANCE_DIRECTION_OFFSET] = entrance_direction.GetRomValue()
    if start_room and entrance_direction:
      formatted_gateway = (start_room + int(entrance_direction) + 0x80) % 0x100
      self.level_metadata[level_offset + self.GATEWAY_OFFSET] = formatted_gateway

  # Gets the Room number of the start screen for a level.
  def GetLevelStartRoomNumber(self, level_num: LevelNum) -> RoomNum:
    assert level_num in Range.VALID_LEVEL_NUMBERS
    return RoomNum(self.level_metadata[level_num * self.LEVEL_METADATA_OFFSET +
                                       self.START_ROOM_OFFSET])

  def GetLevelEntranceDirection(self, level_num: LevelNum) -> Direction:
    assert level_num in Range.VALID_LEVEL_NUMBERS
    offset = level_num * self.LEVEL_METADATA_OFFSET + self.ENTRANCE_DIRECTION_OFFSET
    return Direction.FromRomValue(self.level_metadata[offset])

  def SetSpriteSetsForLevel(self, level_num: LevelNum, sprite_set: SpriteSet,
                            boss_sprite_set: SpriteSet) -> None:
    self.sprite_set_patch.AddData(self.SPRITE_SET_ADDRESS + 2 * level_num,
                                  self.SPRITE_SET_VALUE_LOOKUP[sprite_set])
    self.sprite_set_patch.AddData(self.BOSS_SPRITE_SET_ADDRESS + 2 * level_num,
                                  self.SPRITE_SET_VALUE_LOOKUP[boss_sprite_set])

  def SetItemPositionsForLevel(self, level_num: LevelNum, item_positions: List[int]) -> None:
    enemy_quantities = []
    enemy_quantities.append(random.randrange(0, 2))
    enemy_quantities.append(random.randrange(2, 5))
    enemy_quantities.append(random.randrange(4, 7))
    enemy_quantities.append(random.randrange(5, 8))
    enemy_quantities.sort()

    assert item_positions[0] == 0x89

    for counter in range(0, 4):
      offset = level_num * self.LEVEL_METADATA_OFFSET + counter
      assert item_positions[counter] in range(0, 0x100)
      assert enemy_quantities[counter] in range(0, 0x100)
      self.level_metadata[offset + self.ITEM_POSITIONS_OFFSET] = item_positions[counter]
      self.level_metadata[offset + self.ENEMY_QUANTITIES_OFFSET] = enemy_quantities[counter]

  def GetPatch(self) -> Patch:
    patch = Patch()
    patch += self._GetPatchForLevelGrid(self.LEVEL_1_TO_6_DATA_START_ADDRESS,
                                        self.level_1_to_6_rooms)
    patch += self._GetPatchForLevelGrid(self.LEVEL_7_TO_9_DATA_START_ADDRESS,
                                        self.level_7_to_9_rooms)
    patch += self._GetPatchForLevelMetadata()
    patch += self._GetPatchForOverworldCaveData()
    patch += self._GetPatchForOverworldData()
    patch += self.sprite_set_patch
    patch += self.misc_data_patch
    return patch

  def _GetPatchForLevelGrid(self, start_address: int, rooms: List[Room]) -> Patch:
    patch = Patch()
    for room_num in Range.VALID_ROOM_NUMBERS:
      room_data = rooms[room_num].GetRomData()
      assert len(room_data) == self.NUM_BYTES_OF_DATA_PER_ROOM

      for table_num in range(0, self.NUM_BYTES_OF_DATA_PER_ROOM):
        patch.AddData(start_address + table_num * self.LEVEL_TABLE_SIZE + room_num,
                      [room_data[table_num]])
    return patch

  def _GetPatchForLevelMetadata(self) -> Patch:
    patch = Patch()
    patch.AddData(self.LEVEL_METADATA_ADDRESS, self.level_metadata)
    return patch

  def _GetPatchForOverworldData(self) -> Patch:
    patch = Patch()
    for screen_num in Range.VALID_ROOM_NUMBERS:
      addr = 0x80 + int(screen_num)
      patch.AddData(0x18410 + addr, [self.overworld_raw_data[addr]])
    return patch

  def _GetPatchForOverworldCaveData(self) -> Patch:
    patch = Patch()
    for cave_type in Range.VALID_CAVE_TYPES:
      cave_num = int(cave_type) - self.CAVE_TYPE_CAVE_NUM_OFFSET
      if cave_type == CaveType.ARMOS_ITEM_VIRTUAL_CAVE:
        patch.AddData(self.ARMOS_ITEM_ADDRESS,
                      [self.overworld_caves[cave_num].GetItemAtPosition(2)])
        continue
      if cave_type == CaveType.COAST_ITEM_VIRTUAL_CAVE:
        patch.AddData(self.COAST_ITEM_ADDRESS,
                      [self.overworld_caves[cave_num].GetItemAtPosition(2)])
        continue

      # Note that the Cave class is responsible for protecting bits 6 and 7 in its item data
      patch.AddData(
          self.OVERWORLD_DATA_START_ADDRESS +
          self._GetOverworldCaveDataIndex(cave_type, 0, is_second_byte=False),
          self.overworld_caves[cave_num].GetItemData())
      patch.AddData(
          self.OVERWORLD_DATA_START_ADDRESS +
          self._GetOverworldCaveDataIndex(cave_type, 0, is_second_byte=True),
          self.overworld_caves[cave_num].GetPriceData())
    return patch
