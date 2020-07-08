import logging
import sys
from typing import List

from .constants import CaveType, LevelNum, Range, RoomNum, Screen, WallType
from .data_table import DataTable
from .direction import Direction
from .enemy import Enemy
from .item import Item
from .inventory import Inventory
from .location import Location
from .room import Room
from .room_type import RoomType
from .settings import Settings
from . import flags

log = logging.getLogger(__name__)


class Validator():
  NUM_HEARTS_FOR_WHITE_SWORD_ITEM = 5
  NUM_HEARTS_FOR_MAGICAL_SWORD_ITEM = 12

  def __init__(self, data_table: DataTable, settings: Settings) -> None:
    self.data_table = data_table
    self.settings = settings
    self.inventory = Inventory()

  def IsSeedValid(self) -> bool:
    log.info("Starting check of whether the seed is valid or not")
    self.inventory.Reset()
    self.inventory.SetStillMakingProgressBit()
    num_iterations = 0
    self.data_table.ClearAllVisitMarkers()

    # TODO: Only check this if incremental upgrade flag is enabled
    if self._IsAnIncrementalUpgradeItemAvaliableInAShop():
      print("Incremental upgrade item found in shop")
      return False
    while self.inventory.StillMakingProgress():
      num_iterations += 1
      log.info("Iteration #%d of checking", num_iterations)
      self.inventory.ClearMakingProgressBit()
      self.data_table.ClearAllVisitMarkers()
      self._VisitAccessibleOverworldCaves()
      if self.inventory.Has(Item.RESCUED_KIDNAPPED_VIRTUAL_ITEM):
        log.info("Seed appears to be beatable. :)")
        return True
      if num_iterations > 10:
        return False
    log.warning("Seed doesn't appear to be beatable. :(")
    return False

  def _IsAnIncrementalUpgradeItemAvaliableInAShop(self) -> bool:
    for cave_type in [CaveType.SHOP_A, CaveType.SHOP_B, CaveType.SHOP_C, CaveType.SHOP_D]:
      for position_num in [1, 2, 3]:
        location = Location(cave_type=cave_type, position_num=position_num)
        if self.data_table.GetCaveItem(location).IsAnIncrementalUpgradeItem():
          print("Found %s in %s pos %d" %
                (self.data_table.GetCaveItem(location), cave_type, position_num))
          #input("...")
          return True
    return False

  def _VisitAccessibleOverworldCaves(self) -> None:
    self._ConditionallyVisitCavesForScreens(True, Screen.OPEN_CAVE_SCREENS)
    self._ConditionallyVisitCavesForScreens(self.inventory.HasSwordOrWand(),
                                            Screen.BOMB_BLOCKED_CAVE_SCREENS)
    self._ConditionallyVisitCavesForScreens(self.inventory.HasCandle(),
                                            Screen.CANDLE_BLOCKED_CAVE_SCREENS)
    self._ConditionallyVisitCavesForScreens(self.inventory.Has(Item.POWER_BRACELET),
                                            Screen.POWER_BRACELET_BLOCKED_CAVE_SCREENS)
    self._ConditionallyVisitCavesForScreens(self.inventory.Has(Item.RAFT),
                                            Screen.RAFT_BLOCKED_CAVE_SCREENS)
    self._ConditionallyVisitCavesForScreens(self.inventory.Has(Item.RECORDER),
                                            Screen.RECORDER_BLOCKED_CAVE_SCREENS)
    self._VisitCave(CaveType.ARMOS_ITEM_VIRTUAL_CAVE)
    self._VisitCave(CaveType.COAST_ITEM_VIRTUAL_CAVE)

  def _ConditionallyVisitCavesForScreens(self, condition: bool, screen_numbers: List[int]) -> None:
    if not condition:
      return
    for screen_number in screen_numbers:
      level_num_or_cave_type = self.data_table.GetLevelNumberOrCaveType(screen_number)
      if level_num_or_cave_type in Range.VALID_LEVEL_NUMBERS:
        level_num = LevelNum(level_num_or_cave_type)
        if level_num == LevelNum.LEVEL_9 and self.inventory.GetTriforceCount() < 8:
          continue
        log.info("Visiting level %s" % level_num)
        self._RecursivelyTraverseLevel(level_num,
                                       self.data_table.GetLevelStartRoomNumber(level_num),
                                       self.data_table.GetLevelEntranceDirection(level_num))
      elif level_num_or_cave_type in Range.VALID_CAVE_TYPES:
        cave_type = CaveType(level_num_or_cave_type)
        self._VisitCave(cave_type)
      else:
        log.error("Encountered unexpected level num or cave type: 0x%x" % level_num_or_cave_type)
        sys.exit()

  def _VisitCave(self, cave_type: CaveType) -> None:
    if not cave_type.HasItems():
      return
    log.info("Visiting cave %s" % cave_type)
    if (cave_type == CaveType.WHITE_SWORD_CAVE and
        self.inventory.GetHeartCount() < self.NUM_HEARTS_FOR_WHITE_SWORD_ITEM):
      return
    if (cave_type == CaveType.MAGICAL_SWORD_CAVE and
        self.inventory.GetHeartCount() < self.NUM_HEARTS_FOR_MAGICAL_SWORD_ITEM):
      return
    if cave_type == CaveType.POTION_SHOP and not self.inventory.Has(Item.LETTER):
      return
    if cave_type == CaveType.COAST_ITEM_VIRTUAL_CAVE and not self.inventory.Has(Item.LADDER):
      return
    for position_num in Range.VALID_CAVE_POSITION_NUMBERS:
      location = Location(cave_type=cave_type, position_num=position_num)
      self.inventory.AddItem(self.data_table.GetCaveItem(location), location)

  def _RecursivelyTraverseLevel(self, level_num: LevelNum, room_num: RoomNum,
                                entry_direction: Direction) -> None:
    log.debug("Visiting level %d room %x" % (level_num, room_num))
    if not room_num in Range.VALID_ROOM_NUMBERS:
      return
    room = self.data_table.GetRoom(level_num, room_num)
    if room.IsMarkedAsVisited():
      return
    room.MarkAsVisited()
    current_location = Location.LevelRoom(level_num, room_num)

    # An item staircase room is a dead-end, so no need to recurse after picking up the item.
    if room.IsItemStaircase():
      self.inventory.AddItem(room.GetItem(), current_location)
      return

    # For a transport staircase, we don't know whether we came in through the left or right.
    # So try to leave both ways; the one that we came from will have already been marked as
    # visited and just return.
    if room.IsTransportStaircase():
      for room_num_to_visit in [room.GetStairwayRoomLeftExit(), room.GetStairwayRoomRightExit()]:
        self._RecursivelyTraverseLevel(level_num, room_num_to_visit, Direction.STAIRCASE)
      return

    if self._CanGetRoomItem(entry_direction, room) and room.HasItem():
      self.inventory.AddItem(room.GetItem(), current_location)
    if room.GetEnemy() == Enemy.THE_BEAST:
      if self.inventory.HasBowSilverArrowsAndSword() and self.inventory.Has(Item.LADDER):
        # TODO: Doesn't address the case where ladder isn't obtained
        log.info("Got the triforce of power!")
        self.inventory.AddItem(Item.TRIFORCE_OF_POWER, current_location)
    if room.GetEnemy() == Enemy.THE_KIDNAPPED:
      log.info("Found the kidnapped")
      if self.inventory.Has(Item.TRIFORCE_OF_POWER):
        log.info("And rescued the kidnapped! :)")
        self.inventory.AddItem(Item.RESCUED_KIDNAPPED_VIRTUAL_ITEM, current_location)

    for direction in (Direction.WEST, Direction.NORTH, Direction.EAST, Direction.SOUTH):
      if direction == entry_direction:
        continue
      if not self.inventory.HasReusableWeapon() and room.GetEnemy().HasHardCombatEnemies():
        continue
      if self._CanMove(entry_direction, direction, level_num, room_num, room):
        self._RecursivelyTraverseLevel(level_num, RoomNum(room_num + direction),
                                       direction.Reverse())
    if room.GetRoomType().HasUnobstructedStairs() or (room.HasStairs() and
                                                      self._CanDefeatEnemies(room)):
      if entry_direction != Direction.STAIRCASE:
        self._RecursivelyTraverseLevel(level_num, room.GetStairsDestination(), Direction.STAIRCASE)

  def _CanMove(self, entry_direction: Direction, exit_direction: Direction, level_num: LevelNum,
               room_num: RoomNum, room: Room) -> bool:
    if not room.GetRoomType().AllowsDoorToDoorMovement(entry_direction, exit_direction,
                                                       self.inventory.Has(Item.LADDER)):
      return False

    # Hungry enemy's room doesn't have a closed shutter door. So need a special check to similate
    # how it's not possible to move up in the room until the goriya has been properly fed.
    if (exit_direction == Direction.NORTH and room.GetEnemy() == Enemy.HUNGRY_ENEMY and
        not self.inventory.Has(Item.BAIT)):
      log.info("Hungry goriya is still hungry :(")
      return False

    wall_type = room.GetWallType(exit_direction)
    if (wall_type == WallType.SOLID_WALL or
        (wall_type == WallType.SHUTTER_DOOR and not self._CanDefeatEnemies(room))):
      return False

    if wall_type in [WallType.LOCKED_DOOR_1, WallType.LOCKED_DOOR_2]:
      if self.inventory.HasKey():
        self.inventory.UseKey(level_num, room_num, exit_direction)
      else:
        return False
    return True

  def _CanGetRoomItem(self, entry_direction: Direction, room: Room) -> bool:
    # Can't pick up a room in any rooms with water/moats without a ladder.
    # TODO: Make a better determination here based on the drop location and the entry direction.
    if room.GetRoomType().HasWater() and not self.inventory.Has(Item.LADDER):
      return False
    if room.HasDropBitSet() and not self._CanDefeatEnemies(room):
      return False
    if (room.GetRoomType() == RoomType.HORIZONTAL_CHUTE_ROOM and
        entry_direction in [Direction.NORTH, Direction.SOUTH]):
      return False
    if (room.GetRoomType() == RoomType.VERTICAL_CHUTE_ROOM and
        entry_direction in [Direction.EAST, Direction.WEST]):
      return False
    if room.GetRoomType() == RoomType.T_ROOM:
      return False
    return True

  def _CanDefeatEnemies(self, room: Room) -> bool:
    enemy = room.GetEnemy()
    if enemy.HasNoEnemiesToKill():
      return True
    if enemy == Enemy.THE_BEAST and not self.inventory.HasBowSilverArrowsAndSword():
      return False
    if enemy.IsDigdogger() and not self.inventory.HasRecorderAndReusableWeapon():
      return False
    if enemy.IsGohma() and not self.inventory.HasBowAndArrows():
      return False
    if enemy.HasWizzrobes() and not self.inventory.HasSword():
      return False
    if enemy.HasSwordOrWandRequiredEnemies() and not self.inventory.HasSwordOrWand():
      return False
    if enemy.HasOnlyZeroHPEnemies() and not self.inventory.HasReusableWeaponOrBoomerang():
      return False
    if enemy == Enemy.HUNGRY_ENEMY and not self.inventory.Has(Item.BAIT):
      return False
    if (enemy.HasPolsVoice() and
        not (self.inventory.HasSwordOrWand() or self.inventory.HasBowAndArrows())):
      return False
    if (self.settings.IsEnabled(flags.AvoidHardCombat) and enemy.HasHardCombatEnemies() and
        not (self.inventory.HasRing() and self.inventory.Has(Item.WHITE_SWORD))):
      return False

    # At this point, assume regular enemies
    return self.inventory.HasReusableWeapon()
