from typing import DefaultDict, List, Tuple, Iterable
from collections import defaultdict
from random import shuffle

from .constants import CaveType, LevelNum, LevelNumOrCaveType, Range, RoomNum, WallType
from .data_table import DataTable
from .direction import Direction
from . import flags
from .item import Item
from .location import Location
from .settings import Settings


class ItemRandomizer():

  def __init__(self, data_table: DataTable, settings: Settings) -> None:
    self.data_table = data_table
    self.settings = settings
    self.item_shuffler = ItemShuffler(settings)

  WOOD_SWORD_LOCATION = Location.CavePosition(CaveType.WOOD_SWORD_CAVE, 2)
  WHITE_SWORD_LOCATION = Location.CavePosition(CaveType.WHITE_SWORD_CAVE, 2)
  MAGICAL_SWORD_LOCATION = Location.CavePosition(CaveType.MAGICAL_SWORD_CAVE, 2)
  LETTER_LOCATION = Location.CavePosition(CaveType.LETTER_CAVE, 2)
  WOODEN_ARROWS_LOCATION = Location.CavePosition(CaveType.SHOP_A, 2)
  BLUE_CANDLE_LOCATION = Location.CavePosition(CaveType.SHOP_B, 2)
  BAIT_LOCATION = Location.CavePosition(CaveType.SHOP_C, 2)
  BLUE_RING_LOCATION = Location.CavePosition(CaveType.SHOP_D, 2)
  ARMOS_ITEM_LOCATION = Location.CavePosition(CaveType.ARMOS_ITEM_VIRTUAL_CAVE, 2)
  COAST_ITEM_LOCATION = Location.CavePosition(CaveType.COAST_ITEM_VIRTUAL_CAVE, 2)

  def ResetState(self) -> None:
    self.item_shuffler.ResetState()
    self.data_table.ClearAllVisitMarkers()

  def Randomize(self) -> None:
    self.ResetState()
    self.ReadItemsAndLocationsFromTable()
    self.ShuffleItems()
    self.WriteItemsAndLocationsToTable()

  def ReadItemsAndLocationsFromTable(self) -> None:
    for level_num in Range.VALID_LEVEL_NUMBERS:
      self._ReadItemsAndLocationsForUndergroundLevel(level_num)
    for location in self._GetOverworldItemLocationsToShuffle():
      item_num = self.data_table.GetCaveItem(location)
      self.item_shuffler.AddLocationAndItem(location, item_num)

  def _GetOverworldItemLocationsToShuffle(self) -> List[Location]:
    items: List[Location] = []
    items.append(self.WHITE_SWORD_LOCATION)
    items.append(self.MAGICAL_SWORD_LOCATION)
    items.append(self.COAST_ITEM_LOCATION)
    items.append(self.ARMOS_ITEM_LOCATION)
    items.append(self.LETTER_LOCATION)
    print("Current Shop contents:")
    for shop in [CaveType.SHOP_A, CaveType.SHOP_B, CaveType.SHOP_C, CaveType.SHOP_D]:
      for pos in [1, 2, 3]:
        print("Shop %s pos %d" % (shop, pos))
        loc = Location.CavePosition(shop, pos)
        print(self.data_table.GetCaveItem(loc))
    if self.settings.IsEnabled(flags.ShuffleShopItems):
      items.extend([
          self.WOODEN_ARROWS_LOCATION, self.BLUE_CANDLE_LOCATION, self.BLUE_RING_LOCATION,
          self.BAIT_LOCATION
      ])
    return items

  def _ReadItemsAndLocationsForUndergroundLevel(self, level_num: LevelNum) -> None:
    #logging.debug("Reading staircase room data for level %d " % level_num)
    #for staircase_room_num in self.data_table.GetLevelStaircaseRoomNumberList(level_num):
    print("level %d" % level_num)
    level_start_room_num = self.data_table.GetLevelStartRoomNumber(level_num)
    level_entrance_direction = self.data_table.GetLevelEntranceDirection(level_num)
    print("Traversing level %d.  Start room is %x. Dir is %s " %
          (level_num, level_start_room_num, level_entrance_direction))
    self._ReadItemsAndLocationsRecursively(level_num, level_start_room_num,
                                           level_entrance_direction)

  def _ReadItemsAndLocationsRecursively(self, level_num: LevelNum, room_num: RoomNum,
                                        entrance_direction: Direction) -> None:
    #print("Reading room %x" % room_num)
    if room_num not in Range.VALID_ROOM_NUMBERS:
      #print("Invalid room num")
      return  # No escaping back into the overworld! :)
    room = self.data_table.GetRoom(level_num, room_num)
    if room.IsMarkedAsVisited():
      #print("Already Marked as visited")
      return
    room.MarkAsVisited()

    item = room.GetItem()
    if item.IsMajorItem() or item == Item.TRIFORCE:
      self.item_shuffler.AddLocationAndItem(Location.LevelRoom(level_num, room_num), item)

    # Stair cases (bad pun intended)
    if room.IsItemStaircase():
      #print("Item staircase -- dead end")
      return  # Dead end, no need to traverse further.
    if room.IsTransportStairway():
      #print("transport stair")
      for upstairs_room in [room.GetStairwayRoomLeftExit(), room.GetStairwayRoomRightExit()]:
        self._ReadItemsAndLocationsRecursively(level_num, upstairs_room, Direction.STAIRCASE)
      return
    # Regular (non-staircase) room case.  Check all four cardinal directions, plus "down".
    for direction in (Direction.WEST, Direction.NORTH, Direction.EAST, Direction.SOUTH):
      #print("Trying to walk %s to another room" % direction)
      if direction == entrance_direction:
        #print("Nope, that's where I came from")
        continue
      elif room.GetWallType(direction) != WallType.SOLID_WALL:
        #print("Oooh, not a solid wall!")
        self._ReadItemsAndLocationsRecursively(level_num, RoomNum(room_num + direction),
                                               direction.Reverse())
        continue
      else:
        pass  #print("Bumped up against a solid wall.")
    if room.HasStairs():
      #print("I have a stairway. I'm going in!")
      self._ReadItemsAndLocationsRecursively(level_num, room.GetStairsDestination(),
                                             Direction.STAIRCASE)

  def ShuffleItems(self) -> None:
    self.item_shuffler.ShuffleItems()

  def WriteItemsAndLocationsToTable(self) -> None:
    for (location, item_num) in self.item_shuffler.GetAllLocationAndItemData():
      if location.IsLevelRoom():
        self.data_table.SetRoomItem(item_num, location)
        #if item_num == Item.TRIFORCE:
        #  self.data_table.UpdateTriforceLocation(location)
      elif location.IsCavePosition():
        self.data_table.SetCaveItem(item_num, location)


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
    if item in [Item.MAP, Item.COMPASS, Item.KEY, Item.BOMBS, Item.FIVE_RUPEES, Item.NOTHING]:
      return
    level_or_cave_num = location.GetLevelOrCaveNum()
    self.per_level_item_location_lists[level_or_cave_num].append(location)
    self.loc_counter += 1
    #TODO: This would be more elgant with a dict lookup
    if self.settings.IsEnabled(flags.ProgressiveItems):
      if item == Item.RED_CANDLE:
        item = Item.BLUE_CANDLE
      # elif item == Item.RED_RING:
      #   item = Item.BLUE_RING
      elif item == Item.SILVER_ARROWS:
        item = Item.WOOD_ARROWS
      elif item == Item.WHITE_SWORD:
        item = Item.WOOD_SWORD
      elif item == Item.MAGICAL_SWORD:
        item = Item.WOOD_SWORD
      elif item == Item.MAGICAL_BOOMERANG:
        item = Item.BOOMERANG
    if item == Item.TRIFORCE:
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
    shuffle(self.item_num_list)
    print()
    print(self.item_num_list)
    #input("...")
    for level_or_cave_num in Range.VALID_LEVEL_NUMS_AND_CAVE_TYPES:
      # Levels 1-8 shuffle a triforce, heart container, and 1-2 stairway items.
      # Level 9 shuffles only its 2 stairway items
      if level_or_cave_num in Range.VALID_LEVEL_NUMBERS:
        if LevelNum(level_or_cave_num) != LevelNum.LEVEL_9:
          self.per_level_item_lists[level_or_cave_num].append(Item.TRIFORCE)

      num_locations_needing_an_item = len(
          self.per_level_item_location_lists[level_or_cave_num]) - len(
              self.per_level_item_lists[level_or_cave_num])

      while num_locations_needing_an_item > 0:
        self.per_level_item_lists[level_or_cave_num].append(self.item_num_list.pop())
        num_locations_needing_an_item = num_locations_needing_an_item - 1

      if level_or_cave_num in Range.VALID_LEVEL_NUMBERS:  # Technically this could be for OW and caves too
        shuffle(self.per_level_item_lists[level_or_cave_num])
    print()
    print(self.item_num_list)
    assert not self.item_num_list

  def GetAllLocationAndItemData(self) -> Iterable[Tuple[Location, Item]]:
    for level_num_or_cave_type in Range.VALID_LEVEL_NUMS_AND_CAVE_TYPES:
      for location, item_num in zip(self.per_level_item_location_lists[level_num_or_cave_type],
                                    self.per_level_item_lists[level_num_or_cave_type]):
        yield (location, item_num)
