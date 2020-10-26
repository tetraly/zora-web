from typing import DefaultDict, List, Tuple, Iterable
from collections import defaultdict

from .constants import CaveType, LevelNum, Range, RoomNum, WallType
from .data_table import DataTable
from .direction import Direction
from .enemy import Enemy
from . import flags
from .item import Item
from .location import Location
from .settings import Settings
import random


class NotAllItemsWereShuffledAndIDontKnowWhyException(Exception):
  pass


class ItemRandomizer():

  def __init__(self, data_table: DataTable, settings: Settings) -> None:
    self.data_table = data_table
    self.settings = settings
    self.item_shuffler = ItemShuffler(settings)
    self.hints: List[str] = []
    self.letter_cave_text: str = ""

  WOOD_SWORD_LOCATION = Location.CavePosition(CaveType.WOOD_SWORD_CAVE, 2)
  WHITE_SWORD_LOCATION = Location.CavePosition(CaveType.WHITE_SWORD_CAVE, 2)
  MAGICAL_SWORD_LOCATION = Location.CavePosition(CaveType.MAGICAL_SWORD_CAVE, 2)
  LETTER_LOCATION = Location.CavePosition(CaveType.LETTER_CAVE, 2)
  WOODEN_ARROWS_LOCATION = Location.CavePosition(CaveType.SHOP_A, 2)
  BLUE_CANDLE_LOCATION = Location.CavePosition(CaveType.SHOP_B, 2)
  BAIT_LOCATION = Location.CavePosition(CaveType.SHOP_C, 2)
  BLUE_RING_LOCATION = Location.CavePosition(CaveType.SHOP_D, 2)
  POTION_SHOP_MIDDLE_LOCATION = Location.CavePosition(CaveType.POTION_SHOP, 2)
  ARMOS_ITEM_LOCATION = Location.CavePosition(CaveType.ARMOS_ITEM_VIRTUAL_CAVE, 2)
  COAST_ITEM_LOCATION = Location.CavePosition(CaveType.COAST_ITEM_VIRTUAL_CAVE, 2)

  def ResetState(self) -> None:
    self.item_shuffler.ResetState()
    self.data_table.ClearAllVisitMarkers()

  def Randomize(self) -> None:
    print("A")
    found_bad_thing = False
    found_good_thing = False
    self.ResetState()
    self.ReadItemsAndLocationsFromTable()
    self.ShuffleItems()
    self.WriteItemsAndLocationsToTable()

  def ReadItemsAndLocationsFromTable(self) -> None:
    for level_num in Range.VALID_LEVEL_NUMBERS:
      print("level %d" % level_num)
      self._ReadItemsAndLocationsForUndergroundLevel(level_num)
    for location in self._GetOverworldItemLocationsToShuffle():
      print("OW")
      item_num = self.data_table.GetCaveItem(location)
      self.item_shuffler.AddLocationAndItem(location, item_num)

  def _GetOverworldItemLocationsToShuffle(self) -> List[Location]:
    items: List[Location] = []
    items.append(self.WOOD_SWORD_LOCATION)
    items.append(self.WHITE_SWORD_LOCATION)
    items.append(self.MAGICAL_SWORD_LOCATION)
    items.append(self.COAST_ITEM_LOCATION)
    items.append(self.ARMOS_ITEM_LOCATION)
    items.append(self.LETTER_LOCATION)
    for shop in [CaveType.SHOP_A, CaveType.SHOP_B, CaveType.SHOP_C, CaveType.SHOP_D]:
      for pos in [1, 2, 3]:
        loc = Location.CavePosition(shop, pos)
    if self.settings.IsEnabled(flags.ShuffleShopItems):
      for shop_location in [
          self.WOODEN_ARROWS_LOCATION, self.BLUE_CANDLE_LOCATION, self.BLUE_RING_LOCATION,
          self.BAIT_LOCATION, self.POTION_SHOP_MIDDLE_LOCATION
      ]:
        if self.data_table.GetCaveItem(shop_location) != Item.OVERWORLD_NO_ITEM:
          items.append(shop_location)
    return items

  def _ReadItemsAndLocationsForUndergroundLevel(self, level_num: LevelNum) -> None:
    level_start_room_num = self.data_table.GetLevelStartRoomNumber(level_num)
    level_entrance_direction = self.data_table.GetLevelEntranceDirection(level_num)
    print("Traversing level %d.  Start room is %x. Dir is %s " %
          (level_num, level_start_room_num, level_entrance_direction))
    self._ReadItemsAndLocationsRecursively(level_num, level_start_room_num,
                                           level_entrance_direction)

  def _ReadItemsAndLocationsRecursively(self, level_num: LevelNum, room_num: RoomNum,
                                        entrance_direction: Direction) -> None:
    if room_num not in Range.VALID_ROOM_NUMBERS:
      print("Invalid room num")
      return  # No escaping back into the overworld! :)
    room = self.data_table.GetRoom(level_num, room_num)
    if room.IsMarkedAsVisited():
      return
    room.MarkAsVisited()

    item = room.GetItem()
    if item.IsMajorItem() or item == Item.TRIFORCE:
      print("---------------------------------- Found %s --------------------------" % item)
      self.item_shuffler.AddLocationAndItem(Location.LevelRoom(level_num, room_num), item)

    # Stair cases (bad pun intended)
    if room.IsItemStaircase():
      return  # Dead end, no need to traverse further.
    if room.IsTransportStairway():
      for upstairs_room in [room.GetStairwayRoomLeftExit(), room.GetStairwayRoomRightExit()]:
        self._ReadItemsAndLocationsRecursively(level_num, upstairs_room, Direction.STAIRCASE)
      return
    # Regular (non-staircase) room case.  Check all four cardinal directions, plus "down".
    for direction in (Direction.WEST, Direction.NORTH, Direction.EAST, Direction.SOUTH):
      if direction == entrance_direction:
        continue
      elif room.GetWallType(direction) != WallType.SOLID_WALL:
        self._ReadItemsAndLocationsRecursively(level_num, RoomNum(room_num + direction),
                                               direction.Reverse())
        continue
      else:
        pass
    if room.HasStairs():
      self._ReadItemsAndLocationsRecursively(level_num, room.GetStairsDestination(),
                                             Direction.STAIRCASE)

  def ShuffleItems(self) -> None:
    self.item_shuffler.ShuffleItems()

  def WriteItemsAndLocationsToTable(self) -> None:
    self.data_table.item_hints = []
    for (location, item) in self.item_shuffler.GetAllLocationAndItemData():
      if location.IsLevelRoom():
        print(item)
        self.data_table.SetRoomItem(item, location)

        if item not in [Item.TRIFORCE, Item.HEART_CONTAINER]:
          self.GenerateHint(location, item)
      elif location.IsCavePosition():
        self.data_table.SetCaveItem(item, location)
        print("Putting in %s, %s" % (location.GetCaveType(), item))
        if item not in [Item.TRIFORCE, Item.HEART_CONTAINER]:
          self.GenerateHint(location, item)
        if location.GetCaveType() == CaveType.LETTER_CAVE:
          self.data_table.letter_cave_text = item.GetLetterCaveText()

  def GenerateHint(self, location: Location, item: Item) -> None:
    tbr = ""
    if location.IsLevelRoom():
      level_num = location.GetLevelNum()
      if level_num == LevelNum.LEVEL_7:
        tbr += "IN LEVEL SEVEN"
      else:
        tbr += random.choice(["OFF", "DOWN", "DEEP"])
        tbr += "IN LEVEL %d" % level_num.value
    else:
      tbr += "IN THE OVERWORLD"
    tbr += '|'
    if location.IsLevelRoom():
      room = self.data_table.GetRoom(location.GetLevelNum(), location.GetRoomNum())
      if room.IsItemStaircase():
        tbr += "AN ITEM STAIRWAY HAS A"
      elif room.GetEnemy() == Enemy.NO_ENEMY:
        tbr += "A COMPASS DIRECTS TO A"
      else:
        tbr += "A MAJOR BOSS DEFENDS A"
    else:
      if location.GetCaveType() in [CaveType.SHOP_A, CaveType.SHOP_B, CaveType.SHOP_C]:
        tbr += "A VENDOR IS SELLING A"
      elif location.GetCaveType() == CaveType.SHOP_D:
        tbr += "a specialty shop has a"
      elif location.GetCaveType() == CaveType.POTION_SHOP:
        tbr += "see a pharmacist for a"
      elif location.GetCaveType() == CaveType.LETTER_CAVE:
        tbr += "A letter writer has a"
      elif location.GetCaveType() == CaveType.WHITE_SWORD_CAVE:
        tbr += "a combat guru gives a"
      elif location.GetCaveType() == CaveType.MAGICAL_SWORD_CAVE:
        tbr += "you can master using a"
      elif location.GetCaveType() == CaveType.ARMOS_ITEM_VIRTUAL_CAVE:
        tbr += "AN ARMOS STANDS UPON A"
      elif location.GetCaveType() == CaveType.COAST_ITEM_VIRTUAL_CAVE:
        tbr += "A BLUE OCEAN HARBORS A"
      else:
        tbr += "AN ELDER HAS FOR YOU A"
    tbr += '|'
    tbr += item.GetHintText()
    print(tbr)
    self.data_table.item_hints.append(tbr)


class ItemShuffler():

  def __init__(self, settings: Settings) -> None:
    self.settings = settings
    self.item_num_list: List[Item] = []
    self.per_level_item_location_lists: DefaultDict[int, List[Location]] = defaultdict(list)
    self.per_level_item_lists: DefaultDict[int, List[Item]] = defaultdict(list)

    # for debugging
    self.item_counter = 0
    self.loc_counter = 0

  def ResetState(self) -> None:
    self.item_num_list.clear()
    self.per_level_item_location_lists.clear()
    self.per_level_item_lists.clear()

    # for debugging
    self.item_counter = 0
    self.loc_counter = 0

  def AddLocationAndItem(self, location: Location, item: Item) -> None:
    if item in [
        Item.MAP, Item.COMPASS, Item.KEY, Item.BOMBS, Item.FIVE_RUPEES, Item.FAIRY, Item.NOTHING
    ]:
      return
    level_or_cave_num = location.GetLevelOrCaveNum()
    self.per_level_item_location_lists[level_or_cave_num].append(location)
    self.loc_counter += 1
    #TODO: This would be more elgant with a dict lookup
    if self.settings.IsEnabled(flags.ProgressiveItems):
      if item == Item.RED_CANDLE:
        item = Item.BLUE_CANDLE
      elif item == Item.RED_RING:
        item = Item.BLUE_RING
      elif item == Item.SILVER_ARROWS:
        item = Item.WOOD_ARROWS
      elif item == Item.WHITE_SWORD:
        item = Item.WOOD_SWORD
      elif item == Item.MAGICAL_SWORD:
        item = Item.WOOD_SWORD
      elif item == Item.MAGICAL_BOOMERANG:
        item = Item.BOOMERANG
    if item == Item.TRIFORCE:
      pass
      print("Not adding Triforce")
    else:
      print("Adding item %s" % item)
      self.item_num_list.append(item)
      self.item_counter += 1
    num_locations = 0
    print("Num items/locations: %d/%d" % (self.item_counter, self.loc_counter))

  def ShuffleItems(self) -> None:
    print("Shuffling items")
    print(self.item_num_list)
    print(len(self.item_num_list))
    random.shuffle(self.item_num_list)

    for level_or_cave_num in Range.VALID_LEVEL_NUMS_AND_CAVE_TYPES_WITH_SHOPS_FIRST:
      if level_or_cave_num in Range.VALID_LEVEL_NUMBERS:
        print(LevelNum(level_or_cave_num))
      else:
        print(CaveType(level_or_cave_num))
      print(len(self.item_num_list))
      print()
      # Levels 1-8 shuffle a triforce, heart container, and 1-2 stairway items.
      # Level 9 shuffles only its 2 stairway items
      if level_or_cave_num in Range.VALID_LEVEL_NUMBERS:
        if LevelNum(level_or_cave_num) != LevelNum.LEVEL_9:
          self.per_level_item_lists[level_or_cave_num].append(Item.TRIFORCE)

      num_locations_needing_an_item = len(
          self.per_level_item_location_lists[level_or_cave_num]) - len(
              self.per_level_item_lists[level_or_cave_num])
      try:
        while (CaveType(level_or_cave_num) in [CaveType.SHOP_A, CaveType.SHOP_B, CaveType.SHOP_C]
               and self.item_num_list[0] in [
                   Item.WOOD_ARROWS, Item.WOOD_SWORD, Item.BOOMERANG, Item.BLUE_CANDLE
               ]):
          print("Shufflin!")
          random.shuffle(self.item_num_list)
        while (CaveType(level_or_cave_num) == CaveType.WOOD_SWORD_CAVE and
               self.item_num_list[0] not in [Item.WOOD_SWORD, Item.WAND]):
          print("Shufflin!")
          random.shuffle(self.item_num_list)
      except ValueError:
        pass

      while num_locations_needing_an_item > 0:
        self.per_level_item_lists[level_or_cave_num].append(self.item_num_list.pop(0))
        num_locations_needing_an_item = num_locations_needing_an_item - 1

      if level_or_cave_num in Range.VALID_LEVEL_NUMBERS:  # Technically this could be for OW and caves too
        random.shuffle(self.per_level_item_lists[level_or_cave_num])

    if self.item_num_list:
      raise NotAllItemsWereShuffledAndIDontKnowWhyException()

  def GetAllLocationAndItemData(self) -> Iterable[Tuple[Location, Item]]:
    for level_num_or_cave_type in Range.VALID_LEVEL_NUMS_AND_CAVE_TYPES:
      for location, item_num in zip(self.per_level_item_location_lists[level_num_or_cave_type],
                                    self.per_level_item_lists[level_num_or_cave_type]):
        yield (location, item_num)
