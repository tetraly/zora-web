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


class Validator():
  NUM_HEARTS_FOR_WHITE_SWORD_ITEM = 5
  NUM_HEARTS_FOR_MAGICAL_SWORD_ITEM = 12

  def __init__(self, data_table: DataTable, settings: Settings) -> None:
    self.data_table = data_table
    self.settings = settings
    self.inventory = Inventory()

  def _HasInitialWeapon(self) -> bool:
    for screen_num in Screen.POSSIBLE_FIRST_WEAPON_SCREENS:
      cave_type = self.data_table.GetLevelNumberOrCaveType(screen_num)
      print("Screen %x has cave type %s" % (screen_num, cave_type))
      if not isinstance(cave_type, CaveType):
        continue
      print("Checking %s" % cave_type)
      if cave_type != CaveType.WOOD_SWORD_CAVE:
        continue
      location = Location(cave_type=cave_type, position_num=2)
      print(self.data_table.GetCaveItem(location))
      if self.data_table.GetCaveItem(location).IsSwordOrWand():
        print("screen %x has cave %s with %s" %
              (screen_num, cave_type, self.data_table.GetCaveItem(location)))
        return True
    return False

  def IsSeedValid(self) -> bool:
    print("Starting check of whether the seed is valid or not")
    self.inventory.Reset()
    self.inventory.SetStillMakingProgressBit()
    num_iterations = 0
    self.data_table.ClearAllVisitMarkers()

    # TODO: Only check this if incremental upgrade flag is enabled
    if self._IsAnIncrementalUpgradeItemAvaliableInAShop():
      print("Incremental upgrade item found in shop -- shouldn't happen right?")
      return False

    if not self._HasInitialWeapon():
      print("No initial weapon -- shouldn't happen right?")
      return False

    while self.inventory.StillMakingProgress():
      num_iterations += 1
      print("")
      print("Iteration #%d of checking" % num_iterations)
      self.inventory.ClearMakingProgressBit()
      self.data_table.ClearAllVisitMarkers()
      self._VisitAccessibleOverworldCaves()
      if self.inventory.Has(Item.KIDNAPPED_PLACEHOLDER_ITEM):
        if not (self.inventory.Has(Item.SILVER_ARROWS) and self.inventory.Has(Item.LADDER) and
                self.inventory.Has(Item.BOW) and self.inventory.Has(Item.RAFT) and
                self.inventory.Has(Item.RECORDER) and self.inventory.Has(Item.POWER_BRACELET) and
                self.inventory.GetTriforceCount() == 8):
          print("WARNING: Missing a key item")
        print("Seed appears to be beatable. :)")
        #input()
        return True
      if num_iterations > 10:
        return False
    print("Seed doesn't appear to be beatable. :(")
    return False

  def _IsAnIncrementalUpgradeItemAvaliableInAShop(self) -> bool:
    for cave_type in [CaveType.SHOP_A, CaveType.SHOP_B, CaveType.SHOP_C]:
      for position_num in [1, 2, 3]:
        location = Location(cave_type=cave_type, position_num=position_num)
        if self.data_table.GetCaveItem(location).IsAnIncrementalUpgradeItem():
          print("  Found %s in %s" % (self.data_table.GetCaveItem(location), cave_type))
          return True
    return False

  def _VisitAccessibleOverworldCaves(self) -> None:
    print("Visiting open caves ...")
    self._ConditionallyVisitCavesForScreens(True, Screen.OPEN_CAVE_SCREENS)
    print("Visiting bomb caves if able ...")
    self._ConditionallyVisitCavesForScreens(self.inventory.HasSwordOrWand(),
                                            Screen.BOMB_BLOCKED_CAVE_SCREENS)
    print("Visiting burn bushes if able ...")
    self._ConditionallyVisitCavesForScreens(self.inventory.HasCandle(),
                                            Screen.CANDLE_BLOCKED_CAVE_SCREENS)
    print("Visiting power bracelet-blocked caves if able ...")
    self._ConditionallyVisitCavesForScreens(self.inventory.Has(Item.POWER_BRACELET),
                                            Screen.POWER_BRACELET_BLOCKED_CAVE_SCREENS)
    print("Visiting raft-blocked caves if able ...")
    self._ConditionallyVisitCavesForScreens(self.inventory.Has(Item.RAFT),
                                            Screen.RAFT_BLOCKED_CAVE_SCREENS)
    print("Visiting recorder-blocked caves if able ...")
    self._ConditionallyVisitCavesForScreens(self.inventory.Has(Item.RECORDER),
                                            Screen.RECORDER_BLOCKED_CAVE_SCREENS)
    print("Visiting Armos and coast 'virtual caves'")
    self._VisitCave(CaveType.ARMOS_ITEM_VIRTUAL_CAVE)
    self._VisitCave(CaveType.COAST_ITEM_VIRTUAL_CAVE)

  def _ConditionallyVisitCavesForScreens(self, condition: bool, screen_numbers: List[int]) -> None:
    if not condition:
      return
    for screen_number in screen_numbers:
      level_num_or_cave_type = self.data_table.GetLevelNumberOrCaveType(screen_number)
      if level_num_or_cave_type in Range.VALID_LEVEL_NUMBERS:
        level_num = LevelNum(level_num_or_cave_type)
        print("Entering level %s (at screen %x)" % (level_num, screen_number))
        self._RecursivelyTraverseLevel(level_num,
                                       self.data_table.GetLevelStartRoomNumber(level_num),
                                       self.data_table.GetLevelEntranceDirection(level_num))
        print("Exiting level %s" % level_num)
      elif level_num_or_cave_type in Range.VALID_CAVE_TYPES_WITH_ITEMS:
        cave_type = CaveType(level_num_or_cave_type)
        self._VisitCave(cave_type)
      else:
        pass

  def _VisitCave(self, cave_type: CaveType) -> None:
    if not cave_type.HasItems():
      return
    if (cave_type == CaveType.WHITE_SWORD_CAVE and
        self.inventory.GetHeartCount() < self.NUM_HEARTS_FOR_WHITE_SWORD_ITEM):
      print("Can access %s but not enough hearts" % cave_type)
      return
    if (cave_type == CaveType.MAGICAL_SWORD_CAVE and
        self.inventory.GetHeartCount() < self.NUM_HEARTS_FOR_MAGICAL_SWORD_ITEM):
      print("Can access %s but not enough hearts" % cave_type)
      return
    if cave_type == CaveType.POTION_SHOP and not self.inventory.Has(Item.LETTER):
      print("Can access %s but no paper" % cave_type)
      return
    if cave_type == CaveType.COAST_ITEM_VIRTUAL_CAVE and not self.inventory.Has(Item.LADDER):
      print("Can access %s but no ladder" % cave_type)
      return
    for position_num in Range.VALID_CAVE_POSITION_NUMBERS:
      location = Location(cave_type=cave_type, position_num=position_num)
      item = self.data_table.GetCaveItem(location)
      if item.IsMajorItem():
        print("Found %s in %s" % (item, cave_type))
        self.inventory.AddItem(item, location)
      else:
        pass  #print("    Found minor item %s in %s" % (item, cave_type) )

  def _RecursivelyTraverseLevel(self, level_num: LevelNum, room_num: RoomNum,
                                entry_direction: Direction) -> None:
    #print("  Visiting level %d room %x" % (level_num, room_num))
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

    if room.HasItem():
      if self._CanGetRoomItem(entry_direction, room):
        print("-- Room has item %s. Got it!" % room.GetItem())
        self.inventory.AddItem(room.GetItem(), current_location)
      else:
        print("-- Room has %s but I can't get it. Enemy is %s" % (room.GetItem(), room.GetEnemy()))
    if room.GetEnemy() == Enemy.THE_BEAST and self.inventory.HasBowSilverArrowsAndSword():
      print("Got the triforce of power!")
      #input()
      self.inventory.AddItem(Item.TRIFORCE_OF_POWER_PLACEHOLDER_ITEM, current_location)
    if room.GetEnemy() == Enemy.THE_KIDNAPPED:
      print("Found the kidnapped")
      self.inventory.AddItem(Item.KIDNAPPED_PLACEHOLDER_ITEM, current_location)

    for direction in (Direction.WEST, Direction.NORTH, Direction.EAST, Direction.SOUTH):
      if direction == entry_direction:
        continue
      if not self.inventory.HasReusableWeapon() and room.GetEnemy().HasHardCombatEnemies():
        print("  Found enemy %s but no reusable weapon. Abort!" % room.GetEnemy())
        continue
      if self._CanMove(entry_direction, direction, level_num, room_num, room):
        self._RecursivelyTraverseLevel(level_num, RoomNum(room_num + direction),
                                       direction.Reverse())
    if room.GetRoomType().HasUnobstructedStairs() or (room.HasStairs() and
                                                      self._CanDefeatEnemies(room)):
      if entry_direction != Direction.STAIRCASE:
        print("Taking a staircase in room %s" % room_num)
        self._RecursivelyTraverseLevel(level_num, room.GetStairsDestination(), Direction.STAIRCASE)

    if room.HasStairs() and not self._CanDefeatEnemies(room):
      print("!!! Can't take a staircase. Enemy is %s" % room.GetEnemy())

  def _CanMove(self, entry_direction: Direction, exit_direction: Direction, level_num: LevelNum,
               room_num: RoomNum, room: Room) -> bool:

    # Hungry enemy's room doesn't have a closed shutter door. So need a special check to similate
    # how it's not possible to move up in the room until the goriya has been properly fed.
    if (exit_direction == Direction.NORTH and room.GetEnemy() == Enemy.HUNGRY_ENEMY and
        not self.inventory.Has(Item.BAIT)):
      print("!!!!! Hungry enemy block :(")
      return False

    if not room.GetRoomType().AllowsDoorToDoorMovement(entry_direction, exit_direction,
                                                       self.inventory.Has(Item.LADDER)):
      print("!!!!! Movement block -- maybe ladder block?  Roomtype %s" % room.GetRoomType())
      return False

    wall_type = room.GetWallType(exit_direction)
    if wall_type == WallType.SOLID_WALL:
      return False
    if wall_type == WallType.SHUTTER_DOOR and not self._CanDefeatEnemies(room):
      print("!!!!! Can't proceed through shutter door. Enemy is %s" % room.GetEnemy())
      return False

    if wall_type in [WallType.LOCKED_DOOR_1, WallType.LOCKED_DOOR_2]:
      if self.inventory.HasKey():
        self.inventory.UseKey(level_num, room_num, exit_direction)
      else:
        print("????  Found a locked door but don't have a key. :(")
        return False
    return True

  def _CanGetRoomItem(self, entry_direction: Direction, room: Room) -> bool:
    # Can't pick up a room in any rooms with water/moats without a ladder.
    # TODO: Make a better determination here based on the drop location and the entry direction.
    if room.GetRoomType().HasWater() and not self.inventory.Has(Item.LADDER):
      print("!!!!! Ladder block")
      return False
    if room.HasDropBitSet() and not self._CanDefeatEnemies(room):
      print("!!!!! Can't get drop item %s because of enemy %s" % (room.GetItem(), room.GetEnemy()))
      return False
    if (room.GetRoomType() == RoomType.HORIZONTAL_CHUTE_ROOM and
        entry_direction in [Direction.NORTH, Direction.SOUTH]):
      print("!!!! OH CHUTE")
      return False
    if (room.GetRoomType() == RoomType.VERTICAL_CHUTE_ROOM and
        entry_direction in [Direction.EAST, Direction.WEST]):
      print("!!!! OH CHUTE 2")
      return False
    if room.GetRoomType() in [RoomType.T_ROOM, RoomType.SECOND_QUEST_T_LIKE_ROOM]:
      print("!!!! T WHIZ!")
      return False
    return True

  def _CanDefeatEnemies(self, room: Room) -> bool:
    enemy = room.GetEnemy()
    if enemy == Enemy.NO_ENEMY:
      print("NO ENEMY")
    if enemy.HasNoEnemiesToKill():
      return True
    if enemy == Enemy.NO_ENEMY:
      print("NO ENEMY -- this shouldn't happen")
    if enemy.IsBoomerangOnly() and not self.inventory.HasBoomerang():
      return False
    if enemy.IsFireOnly() and not self.inventory.HasFireSource():
      return False
    if enemy.IsWandOnly() and not self.inventory.Has(Item.WAND):
      return False
    if room.HasPowerBraceletRoomAction() and not self.inventory.Has(Item.POWER_BRACELET):
      return False
    if (room.HasKillingTheBeastOpensShutterDoorsRoomAction() and
        not self.inventory.Has(Item.TRIFORCE_OF_POWER_PLACEHOLDER_ITEM)):
      return False
    if (enemy == Enemy.ELDER and self.inventory.GetTriforceCount() < 8):
      print("triforce check failed -- %d tringles" % self.inventory.GetTriforceCount())
      return False
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
