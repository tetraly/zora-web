import math
import random
import sys
from typing import Any, Dict, List, Optional, Tuple, Union

from .constants import CaveType, GridId, DungeonPalette, LevelNum, Range
from .constants import RoomAction, RoomNum, Screen, SpriteSet, WallType
from .direction import Direction
from .data_table import DataTable
from .enemy import Enemy
from .grid_generator import GridGenerator
from .item import Item, BorderType
from .location import Location
from .room import Room
from .room_type import RoomType

GRID_B_LEVEL_NUMBERS = [LevelNum.LEVEL_7, LevelNum.LEVEL_8, LevelNum.LEVEL_9]

"""from colorama import Fore, Back, Style

COLORS: Dict[int, "Fore"] = {
    0: Fore.WHITE,
    1: Fore.CYAN,
    2: Fore.BLUE,
    3: Fore.GREEN,
    4: Fore.YELLOW,
    5: Fore.MAGENTA,
    6: Fore.RED,
    7: Fore.WHITE
}
"""

def GetNextRoomNum(room_num: RoomNum, direction: Direction) -> RoomNum:
  assert room_num in Range.VALID_ROOM_NUMBERS
  assert direction in Range.CARDINAL_DIRECTIONS
  return RoomNum(int(room_num) + int(direction))


def PrintListInHex(list: List[RoomNum], text: str = "") -> None:
  if text:
    print("%s: " % text, end='')
  print('[', end='')
  for item in list:
    print('%x, ' % item, end='')
  print(']')


OK_BORDER_TYPES_FOR_TRANSPORT_STAIRCASE = [
    BorderType.BOOMERANG_BLOCK, BorderType.CANDLE_BLOCK, BorderType.BOW_BLOCK,
    BorderType.RECORDER_BLOCK, BorderType.WAND_BLOCK, BorderType.MINI_BOSS
]


class LevelPlanGenerator:

  def __init__(self, data_table: DataTable) -> None:
    self.data_table = data_table

  def _GenerateStairwayItemPool(self) -> List[Item]:
    stairway_item_pool = [
        Item.BOW, Item.MAGICAL_BOOMERANG, Item.RAFT, Item.LADDER, Item.RECORDER, Item.WAND,
        Item.RED_CANDLE, Item.BOOMERANG, Item.BOOK, Item.MAGICAL_KEY, Item.RED_RING,
        Item.SILVER_ARROWS
    ]
    random.shuffle(stairway_item_pool)

    return [
        Item.BOW,
        Item.MAGICAL_BOOMERANG,
        Item.RAFT,
        Item.LADDER,
        Item.RECORDER,
        Item.WAND,
        Item.RED_CANDLE,
        Item.BOOMERANG,
        Item.BOOK,
        Item.MAGICAL_SHIELD,
        #Item.MAGICAL_KEY,
        Item.RED_RING,
        Item.SILVER_ARROWS
    ]

  def _GenerateEnemySpriteSetAssignments(self) -> List[SpriteSet]:
    enemy_sprite_sets = [
        SpriteSet.GORIYA_SPRITE_SET, SpriteSet.DARKNUT_SPRITE_SET, SpriteSet.WIZZROBE_SPRITE_SET
    ]
    enemy_sprite_set_pool: List[SpriteSet] = enemy_sprite_sets.copy()
    enemy_sprite_set_pool.extend(enemy_sprite_sets)
    for unused_counter in range(0, 3):
      enemy_sprite_set_pool.append(random.choice(enemy_sprite_sets))
    random.shuffle(enemy_sprite_set_pool)
    return enemy_sprite_set_pool

  def _GenerateBossSpriteSetAssignments(self) -> List[SpriteSet]:
    boss_sprite_sets = [
        SpriteSet.DODONGO_SPRITE_SET, SpriteSet.GLEEOK_SPRITE_SET, SpriteSet.PATRA_SPRITE_SET
    ]
    boss_sprite_set_pool = boss_sprite_sets.copy()
    boss_sprite_set_pool.extend(boss_sprite_sets)
    for unused_counter in range(0, 3):
      boss_sprite_set_pool.append(
          random.choice([SpriteSet.DODONGO_SPRITE_SET, SpriteSet.GLEEOK_SPRITE_SET]))

    random.shuffle(boss_sprite_set_pool)
    while boss_sprite_set_pool[8] != SpriteSet.PATRA_SPRITE_SET:
      random.shuffle(boss_sprite_set_pool)
    return boss_sprite_set_pool

  def _GeneratePaletteAssignments(self) -> List[Tuple[int, int, int, int]]:
    palettes: List[Tuple[int, int, int, int]] = [(0x0A, 0x0C, 0x1C, 0x02), (0x0F, 0x1C, 0x3B, 0x01),
                                                 (0x03, 0x00, 0x21, 0x02), (0x04, 0x2D, 0x24, 0x16),
                                                 (0x04, 0x24, 0x3D, 0x16), (0x12, 0x1C, 0x29, 0x02),
                                                 (0x09, 0x2A, 0x2C, 0x02), (0x08, 0x18, 0x19, 0x02),
                                                 (0x04, 0x3F, 0x2C, 0x02), (0x03, 0x23, 0x33, 0x02),
                                                 (0x02, 0x14, 0x23, 0x02), (0x0C, 0x1C, 0x23, 0x02),
                                                 (0x0C, 0x26, 0x23, 0x02), (0x0F, 0x05, 0x23, 0x01),
                                                 (0x0F, 0x08, 0x19, 0x01), (0x02, 0x2D, 0x1A, 0x02),
                                                 (0x07, 0x18, 0x38, 0x02)]
    random.shuffle(palettes)
    return palettes[:9]

  def GenerateLevelPlan(
      self, num_rooms_per_level: Dict[LevelNum, int], grid_a_stairway_room_nums: List[RoomNum],
      grid_b_stairway_room_nums: List[RoomNum]) -> Dict[Union[LevelNum, str], Any]:
    # 1) Shuffle and place stairway items
    level_plan: Dict[Union[LevelNum, str], Any] = {}

    stairway_item_pool = self._GenerateStairwayItemPool()
    enemy_sprite_set_assignments = self._GenerateEnemySpriteSetAssignments()
    boss_sprite_set_assignments = self._GenerateBossSpriteSetAssignments()
    palette_assignments = self._GeneratePaletteAssignments()

    for level_num in Range.VALID_LEVEL_NUMBERS:
      self.data_table.SetSpriteSetsForLevel(level_num, enemy_sprite_set_assignments[level_num - 1],
                                            boss_sprite_set_assignments[level_num - 1])
      self.data_table.WriteDungeonPalette(level_num, palette_assignments[level_num - 1])

    for level_num in Range.VALID_LEVEL_NUMBERS:
      level_plan[level_num] = {
          #'stairway_items': [stairway_item_pool.pop(0)],
          'enemy_sprite_set': enemy_sprite_set_assignments.pop(0),
          'boss_sprite_set': boss_sprite_set_assignments.pop(0),
          'palette': palette_assignments.pop(0)
      }

    assert not enemy_sprite_set_assignments
    assert not boss_sprite_set_assignments
    assert not palette_assignments

    # Elder assigments (Hints and Bomb upgrades only -- not muggers or hungry enemies)
    level_group_assignments = ['a', 'a', 'a', 'a', 'b', 'b', 'b', 'b']
    elder_assigments: Dict[int, List[Enemy]] = {}
    elder_group_a: List[Enemy] = [
        Enemy.BOMB_UPGRADER, Enemy.BOMB_UPGRADER, Enemy.ELDER, Enemy.ELDER_2, Enemy.ELDER_3,
        Enemy.ELDER_4, Enemy.ELDER_6, Enemy.ELDER_8
    ]
    elder_group_b: List[Enemy] = [
        Enemy.ELDER, Enemy.ELDER_2, Enemy.ELDER_3, Enemy.ELDER_4, Enemy.RUPEE_BOSS, Enemy.ELDER_6,
        Enemy.ELDER_8, Enemy.RUPEE_BOSS
    ]
    random.shuffle(level_group_assignments)
    random.shuffle(elder_group_a)
    random.shuffle(elder_group_b)

    for level_num in Range.VALID_LEVEL_NUMBERS:
      # Skip ELDER_1 in L9 since that's a triforce check which we place as a border
      if level_num == LevelNum.LEVEL_9:
        level_plan[level_num]['elders'] = [Enemy.ELDER_2, Enemy.ELDER_3, Enemy.ELDER_4]
      else:
        elder_group = (elder_group_a if level_group_assignments[level_num -
                                                                1] == 'a' else elder_group_b)
        level_plan[level_num]['elders'] = [elder_group.pop(0), elder_group.pop(0)]
    assert len(elder_group_a) == 0 and len(elder_group_b) == 0

    found_first_bomb_upgrader = False
    for level_num in Range.VALID_LEVEL_NUMBERS:
      if level_num == LevelNum.LEVEL_9:
        continue
      self.data_table.SetTextGroup(level_num, level_group_assignments[level_num - 1])
      if Enemy.BOMB_UPGRADER in level_plan[level_num]['elders'] and level_group_assignments[
          level_num - 1] == 'a':
        self.data_table.SetBombUpgradeLevel(level_num, found_first_bomb_upgrader)
        found_first_bomb_upgrader = True

    # Staircase room assignments
    stairway_rooms_a = grid_a_stairway_room_nums.copy()
    stairway_rooms_b = grid_b_stairway_room_nums.copy()
    assert len(stairway_rooms_a) == 8 and len(stairway_rooms_b) == 12
    for level_num in [
        LevelNum.LEVEL_1, LevelNum.LEVEL_2, LevelNum.LEVEL_3, LevelNum.LEVEL_4, LevelNum.LEVEL_5,
        LevelNum.LEVEL_6
    ]:
      level_plan[level_num]['transport_stairway_room_nums'] = []
      level_plan[level_num]['item_stairway_room_nums'] = [stairway_rooms_a.pop(0)]
    for level_num in [LevelNum.LEVEL_5, LevelNum.LEVEL_6]:
      level_plan[level_num]['transport_stairway_room_nums'].append(stairway_rooms_a.pop(0))
    for level_num in [LevelNum.LEVEL_7, LevelNum.LEVEL_8, LevelNum.LEVEL_9]:
      level_plan[level_num]['item_stairway_room_nums'] = [
          stairway_rooms_b.pop(0), stairway_rooms_b.pop(0)
      ]
      level_plan[level_num]['transport_stairway_room_nums'] = [stairway_rooms_b.pop(0)]
    for unused_counter in range(3):
      level_plan[LevelNum.LEVEL_9]['transport_stairway_room_nums'].append(stairway_rooms_b.pop(0))
    assert not stairway_rooms_a and not stairway_rooms_b

    # Borders
    minor_border_types = [BorderType.BOMB_HOLE, BorderType.MINI_BOSS]
    blocking_border_type_pool = [
        BorderType.BAIT_BLOCK,  # 
        BorderType.BOOMERANG_BLOCK,
        BorderType.CANDLE_BLOCK,
        BorderType.BOW_BLOCK,
        BorderType.RECORDER_BLOCK,
        BorderType.WAND_BLOCK,
        BorderType.LADDER_BLOCK,
        BorderType.MUGGER,
    ]
    done = False
    while not done:
      random.shuffle(blocking_border_type_pool)
      done = True
      for level_num in Range.VALID_LEVEL_NUMBERS:
        if level_num == LevelNum.LEVEL_9:
          continue
        if (blocking_border_type_pool[level_num - 1] == BorderType.RECORDER_BLOCK and
            level_plan[level_num]['boss_sprite_set'] != SpriteSet.DODONGO_SPRITE_SET):
          done = False
        if (blocking_border_type_pool[level_num -
                                      1] in [BorderType.WAND_BLOCK, BorderType.BOW_BLOCK] and
            level_plan[level_num]['boss_sprite_set'] != SpriteSet.GLEEOK_SPRITE_SET):
          done = False
        if (blocking_border_type_pool[level_num - 1] == BorderType.CANDLE_BLOCK and
            level_plan[level_num]['enemy_sprite_set'] != SpriteSet.GORIYA_SPRITE_SET):
          done = False
    blocking_border_type_pool.append(BorderType.TRIFORCE_CHECK)

    for level_num in Range.VALID_LEVEL_NUMBERS:
      num_areas: int
      border_pool: List[BorderType] = []
      item_pool: List[Item] = []
      stairway_rooms_to_assign = level_plan[level_num]['transport_stairway_room_nums'].copy()

      border_pool.append(random.choice(minor_border_types))
      blocking_border_type = blocking_border_type_pool.pop(0)
      border_pool.append(blocking_border_type)

      if blocking_border_type == BorderType.BAIT_BLOCK:
        self.data_table.AdjustHungryEnemyForSpriteSet(level_plan[level_num]['enemy_sprite_set'])
        #input("HUNGRY ENEMY CHANGE to %s" % level_plan[level_num]['enemy_sprite_set'])

      item_pool.append(stairway_item_pool.pop(0))
      item_pool.append(Item.COMPASS)
      item_pool.append(Item.MAP)

      if level_num not in [LevelNum.LEVEL_1, LevelNum.LEVEL_2, LevelNum.LEVEL_3]:
        border_pool.append(BorderType.LOCKED_DOOR)
        item_pool.append(Item.KEY)
      if level_num in [LevelNum.LEVEL_7, LevelNum.LEVEL_8, LevelNum.LEVEL_9]:
        border_pool.append(BorderType.MINI_BOSS)
        item_pool.append(stairway_item_pool.pop(0))

      while True:
        random.shuffle(border_pool)
        random.shuffle(item_pool)
        if ((BorderType.LOCKED_DOOR in border_pool or Item.KEY in item_pool) and
            border_pool.index(BorderType.LOCKED_DOOR) != item_pool.index(Item.KEY)):
          continue
        if (BorderType.BOMB_HOLE in border_pool and
            border_pool.index(BorderType.BOMB_HOLE) < item_pool.index(Item.MAP)):
          continue
        if (BorderType.TRIFORCE_CHECK in border_pool and
            border_pool.index(BorderType.TRIFORCE_CHECK) != 0):
          continue
        if item_pool[-1] == Item.KEY:
          continue
        break

      num_areas = 5
      if level_num > 3:
        num_areas = 6
      if level_num > 6:
        num_areas = 7
      target_num_rooms = num_rooms_per_level[level_num]

      print()
      print(level_num)
      print("target num rooms: %d" % target_num_rooms)
      num_rooms: List[int] = []
      while True:
        num_rooms = []
        for area_num in range(num_areas):
          if area_num == num_areas - 1:
            num_rooms.append(1)
          else:
            num_rooms.append(random.randrange(3, num_areas + level_num))
        if 1 in num_rooms and sum(num_rooms) == target_num_rooms:
          print("Gotta plan! %s" % num_rooms)
          break
      print()

      level_plan[level_num]['1'] = {
          'border_type': border_pool.pop(0),
          'items': [item_pool.pop(0)],
          #          'min_num_rooms': 4,
          #          'max_num_rooms': 4 + level_num
      }
      level_plan[level_num]['2'] = {
          'border_type': border_pool.pop(0),
          'items': [item_pool.pop(0)],
          #          'min_num_rooms': 3,
          #          'max_num_rooms': 8 + level_num
      }
      n = 0
      if level_num > 3:
        n = 1
        level_plan[level_num]['3'] = {
            'border_type': border_pool.pop(0),
            'items': [item_pool.pop(0)],
            #           'min_num_rooms': 3,
            #            'max_num_rooms': 8 + level_num
        }
      if level_num > 6:
        n = 2
        level_plan[level_num]['4'] = {
            'border_type': border_pool.pop(0),
            'items': [item_pool.pop(0)],
            #          'min_num_rooms': 3,
            #         'max_num_rooms': 10 + level_num
        }
      level_plan[level_num][str(3 + n)] = {
          'border_type': BorderType.LOCKED_DOOR,
          'items': [Item.KEY, item_pool.pop(0)],
          #      'min_num_rooms': 3,
          #     'max_num_rooms': 8 + level_num
      }
      level_plan[level_num][str(4 + n)] = {
          'border_type': BorderType.THE_BEAST if level_num == LevelNum.LEVEL_9 else BorderType.BOSS,
          'items': [Item.NOTHING] if level_num == LevelNum.LEVEL_9 else [Item.HEART_CONTAINER],
          #        'min_num_rooms': 1,
          #        'max_num_rooms': 4
      }
      level_plan[level_num][str(5 + n)] = {
          'border_type':
              BorderType.THE_KIDNAPPED
              if level_num == LevelNum.LEVEL_9 else BorderType.TRIFORCE_ROOM,
          'items': [Item.BLUE_POTION] if level_num == LevelNum.LEVEL_9 else [Item.TRIFORCE],
          #       'min_num_rooms':
          #            1,
          #        'max_num_rooms':
          #            1
      }
      for area_num in range(num_areas):
        if num_rooms[area_num] != 1:
          path_length_max = max(3, num_rooms[area_num] - 2, 3)
          level_plan[level_num][str(area_num + 1)]['path_length'] = random.randrange(
              2, path_length_max)
          level_plan[level_num][str(area_num + 1)]['stairway_border'] = False

  #       level_plan[level_num][str(area_num + 1)]['min_num_rooms'] = num_rooms[area_num]

  #        level_plan[level_num][str(area_num + 1)]['max_num_rooms'] = num_rooms[area_num] + 2
  #       if num_rooms[area_num] == 3:
  #        level_plan[level_num][str(area_num + 1)]['min_num_rooms'] = 3
        else:
          level_plan[level_num][str(area_num + 1)]['path_length'] = 1
          level_plan[level_num][str(area_num + 1)]['min_num_rooms'] = 1
          level_plan[level_num][str(area_num + 1)]['max_num_rooms'] = 1
        if stairway_rooms_to_assign and level_plan[level_num][str(
            area_num + 1)]['border_type'] in OK_BORDER_TYPES_FOR_TRANSPORT_STAIRCASE:
          print("Doing level %d. stairway_rooms_to_assign %s" %
                (level_num, stairway_rooms_to_assign))
          level_plan[level_num][str(area_num + 1)]['stairway_border'] = True
          stairway_rooms_to_assign.pop(0)
          #input()

      level_plan[level_num][str(1)]['path_length'] = 3

      print(level_plan[level_num])
      assert not item_pool
      assert not border_pool

    # TODO: Make this a self thing from the start (and put the initialization in the constructor)
    for a, b in level_plan.items():
      if isinstance(b, dict):
        print(a, ":")
        # Again iterate over the nested dictionary
        for c, d in b.items():
          print(' ', c, ': ', d)
      else:
        print(a, ':', b)
    return level_plan


class DungeonGenerator:

  def __init__(self, data_table: DataTable) -> None:
    #RoomType.PrintStats()
    self.data_table = data_table
    self.grid_generator_a: GridGenerator = GridGenerator(self.data_table)
    self.grid_generator_b: GridGenerator = GridGenerator(self.data_table)
    self.level_plan_generator = LevelPlanGenerator(self.data_table)
    self.level_plan: Dict[Union[LevelNum, str], Any] = {}

    # The following lists have placeholder values for one-indexing
    self.level_start_rooms: List[RoomNum] = [RoomNum(-1)]
    self.level_entrance_directions: List[Direction] = [Direction.NO_DIRECTION]
    for level_num in Range.VALID_LEVEL_NUMBERS:
      self.level_start_rooms.append(RoomNum(-1))
      self.level_entrance_directions.append(Direction.NO_DIRECTION)

    self.level_rooms_a: List[List[RoomNum]] = []
    self.level_rooms_b: List[List[RoomNum]] = []
    self.room_grid_a: List[Room] = []
    self.room_grid_b: List[Room] = []
    self.item_position_dict: Dict[RoomType, int] = {}

  def GenerateItemPositions(self) -> None:
    # For each level, pick four random item drop positions such that at least one will be a valid
    # and accessible tile (i.e. not on top of blocks, water, etc.). They get numbered 0-3.
    # Then, create a dictionary for each level mapping each room type to the position number (0-3)
    # that is valid for the room type.
    positions = [
        0x89,
        RoomType.GetValidPositionForRoomType(RoomType.CIRCLE_BLOCK_WALL_ROOM,
                                             is_item_position=True),
        RoomType.GetValidPositionForRoomType(RoomType.VERTICAL_LINES, is_item_position=True),
        RoomType.GetValidPositionForRoomTypes(RoomType.HORIZONTAL_LINES,
                                              RoomType.SPIRAL_STAIR_ROOM,
                                              is_item_position=True)
    ]
    values = [0, 1, 2, 3]
    for level_num in Range.VALID_LEVEL_NUMBERS:
      self.data_table.SetItemPositionsForLevel(level_num, positions)
    for room_type in range(0x00, 0x2A):
      if room_type == RoomType.TURNSTILE_ROOM:
        continue
      room_type = RoomType(room_type)
      random.shuffle(values)
      for v in values:
        #if room_type in [
        #    RoomType.VERTICAL_CHUTE_ROOM, RoomType.HORIZONTAL_CHUTE_ROOM,
        #    RoomType.HORIZONTAL_MOAT_ROOM, RoomType.DOUBLE_MOAT_ROOM
        #]:
        #  self.level_position_dict[room_type] = 0
        #  break
        #elif room_type in [RoomType.CIRCLE_BLOCK_WALL_ROOM, RoomType.DIAMOND_STAIR_ROOM]:
        #  self.level_position_dict[room_type] = 3
        #  break
        if RoomType.IsValidPositionForRoomType(positions[v], room_type, is_item_position=True):
          self.item_position_dict[room_type] = v
          break
      print(room_type)
      assert room_type in self.item_position_dict
    self.item_position_dict[RoomType(0x31)] = 0
    self.item_position_dict[RoomType(0x32)] = 0
    self.item_position_dict[RoomType(0x33)] = 0
    self.item_position_dict[RoomType(0x3F)] = 0

  ## Helper methods ##
  def _GetLevelNumForRoomNum(self, room_num: RoomNum, grid_id: GridId) -> LevelNum:
    return self._GetGridGenerator(grid_id=grid_id).GetLevelNumForRoomNum(room_num)

  def _GetGridId(self,
                 level_num: Optional[LevelNum] = None,
                 grid_id: Optional[GridId] = None) -> GridId:
    assert level_num and not grid_id or grid_id and not level_num
    if not grid_id:
      assert level_num is not None
      grid_id = GridId.GRID_B if level_num in GRID_B_LEVEL_NUMBERS else GridId.GRID_A
    return grid_id

  def _GetGridGenerator(self,
                        level_num: Optional[LevelNum] = None,
                        grid_id: Optional[GridId] = None) -> GridGenerator:
    grid_id = self._GetGridId(level_num, grid_id)
    return self.grid_generator_a if grid_id == GridId.GRID_A else self.grid_generator_b

  def _GetGrid(self,
               level_num: Optional[LevelNum] = None,
               grid_id: Optional[GridId] = None) -> List[Room]:
    grid_id = self._GetGridId(level_num, grid_id)
    return self.room_grid_b if grid_id == GridId.GRID_B else self.room_grid_a

  def _GetRoomNumsForLevel(self, level_num: LevelNum) -> List[RoomNum]:
    assert level_num in Range.VALID_LEVEL_NUMBERS
    grid_id = self._GetGridId(level_num)
    if grid_id == GridId.GRID_A:
      return self.level_rooms_a[level_num].copy()
    return self.level_rooms_b[level_num].copy()

  def _GetRoom(self,
               room_num: RoomNum,
               level_num: Optional[LevelNum] = None,
               grid_id: Optional[GridId] = None) -> Room:
    assert room_num in Range.VALID_ROOM_NUMBERS
    return self._GetGrid(level_num, grid_id)[room_num]

  def _GetStairwayRoomsForGrid(self, grid_id: GridId) -> List[RoomNum]:
    return self.level_rooms_a[0] if grid_id == GridId.GRID_A else self.level_rooms_b[0]

  def _GetNumberOfRoomsPerLevel(self) -> Dict[LevelNum, int]:
    tbr: Dict[LevelNum, int] = {}
    for level_num in Range.VALID_LEVEL_NUMBERS:
      num_rooms = len(self._GetRoomNumsForLevel(level_num))
      tbr[level_num] = num_rooms
    return tbr

  ## End of Helper Methods ##

  def Generate(self) -> None:
    self.grid_generator_a.GenerateLevelGrid(num_levels=6,
                                            min_level_size=15,
                                            max_level_size=28,
                                            num_stairway_rooms=8)
    self.grid_generator_a.GenerateMapData(is_7_to_9=False)
    self.grid_generator_a.Print()
    self.level_rooms_a = self.grid_generator_a.GetLevelRoomNumbers()

    self.grid_generator_b.GenerateLevelGrid(num_levels=3,
                                            min_level_size=30,
                                            max_level_size=60,
                                            num_stairway_rooms=12)
    self.grid_generator_b.AddSixToLevelNumbers()
    self.grid_generator_b.GenerateMapData(is_7_to_9=True)
    self.grid_generator_b.Print()
    self.level_rooms_b = self.grid_generator_b.GetLevelRoomNumbers()
    self.GenerateItemPositions()
    self.level_plan = self.level_plan_generator.GenerateLevelPlan(
        self._GetNumberOfRoomsPerLevel(), self._GetStairwayRoomsForGrid(GridId.GRID_A),
        self._GetStairwayRoomsForGrid(GridId.GRID_B))

    self.GenerateLevelStartRooms()
    self.CreateLevelRooms()
    self.GenerateLevels()
    self.RandomizeOverworldCaves()
    self.RandomizeShops()
    self.data_table.RandomizeBombUpgrades()

  def CreateLevelRooms(self) -> None:
    for grid_id in [GridId.GRID_A, GridId.GRID_B]:
      room_grid = [Room() for unused_counter in Range.VALID_ROOM_NUMBERS]
      for room_num in Range.VALID_ROOM_NUMBERS:
        level_num = self._GetLevelNumForRoomNum(room_num, grid_id)
        if level_num not in Range.VALID_LEVEL_NUMBERS:
          continue
        for direction in Range.CARDINAL_DIRECTIONS:
          room_grid[room_num].SetWallType(direction, WallType.SOLID_WALL)
      if grid_id == GridId.GRID_A:
        self.room_grid_a = room_grid
      else:
        self.room_grid_b = room_grid

  def GenerateLevelStartRooms(self) -> None:
    for level_num in Range.VALID_LEVEL_NUMBERS:
      self._GenerateLevelStartRoom(level_num)

  def _GenerateLevelStartRoom(self, level_num: LevelNum) -> None:
    (start_room, entrance_direction) = self._PickStartRoomForLevel(level_num)
    self.data_table.SetStartRoomDataForLevel(level_num, start_room, entrance_direction)
    self.level_start_rooms[level_num] = start_room
    self.level_entrance_directions[level_num] = entrance_direction

  def _PickStartRoomForLevel(self, level_num: LevelNum) -> Tuple[RoomNum, Direction]:
    possible_start_rooms: List[Tuple[RoomNum, Direction]] = []
    grid_id = GridId.GetGridIdForLevelNum(level_num)

    for room_num in Range.VALID_ROOM_NUMBERS:
      for entrance_direction in Range.CARDINAL_DIRECTIONS:
        if (room_num == 0x00 and entrance_direction == Direction.WEST or
            room_num == 0x7F and entrance_direction == Direction.EAST):
          continue
        # Coming down into the top row seems to cause wonky graphical glitches.
        if entrance_direction == Direction.NORTH and room_num < 0x10:
          continue
        # Same for coming up from the bottom?
        if entrance_direction == Direction.SOUTH and room_num >= 0x70:
          continue
        if self._GetLevelNumForRoomNum(room_num, grid_id) == level_num:
          potential_gateway = GetNextRoomNum(room_num, entrance_direction)
          if (potential_gateway not in Range.VALID_ROOM_NUMBERS or
              level_num != self._GetLevelNumForRoomNum(potential_gateway, grid_id)):
            possible_start_rooms.append((room_num, entrance_direction))
    return random.choice(possible_start_rooms)

  """def _GetColorForPrinting(self, room_num: RoomNum, level_num: Optional[LevelNum] = None) -> Fore:
    grid_gen = self._GetGridGenerator(level_num)
    level_num_of_room = grid_gen.GetLevelNumForRoomNum(room_num)
    if level_num and level_num != level_num_of_room:
      return Fore.BLACK
    #lock_level = self._GetRoom(room_num, grid_id=GridId.GRID_A).GetLockLevel()
    lock_level = self._GetRoom(room_num, level_num).GetLockLevel()
    return COLORS[lock_level]

  def Print(self, level_num: LevelNum, print_all_grid: bool = False) -> None:
    grid_id = self._GetGridId(level_num=level_num)
    print(level_num)
    print(grid_id)
    (row_min, col_min, row_max, col_max) = (0, 0, 7, 15)
    if not print_all_grid:
      grid_generator = self._GetGridGenerator(level_num=level_num)
      (row_min, col_min, row_max, col_max) = (7, 15, 0, 0)
      for row in range(0, 8):
        for col in range(0, 16):
          if grid_generator.GetLevelNumForRoomNum(RoomNum((16 * row) + col)) == level_num:
            if row < row_min:
              row_min = row
            if col < col_min:
              col_min = col
            if row > row_max:
              row_max = row
            if col > col_max:
              col_max = col
    for row in range(row_min, row_max + 1):
      for col in range(col_min, col_max + 1):
        room = self._GetRoom(RoomNum(16 * row + col), level_num)
        print(self._GetColorForPrinting(RoomNum(16 * row + col), level_num), end='')
        print('|ˉˉˉˉˉ', end='')
        for a in range(0, 2):
          print(room.GetWallType(Direction.NORTH,
                                 return_solid_if_stairway=True).ToChar(Direction.NORTH),
                end='')
        print('ˉˉˉˉˉ|', end='')
      print('')

      for col in range(col_min, col_max + 1):
        room = self._GetRoom(RoomNum(16 * row + col), level_num)
        print(self._GetColorForPrinting(RoomNum(16 * row + col), level_num), end='')
        #        print('| %10s |' % room.GetRoomType().GetShortName(), end='')
        #print('| %10s |' % (room.GetLockingDirection().GetShortName()
        #                    if room.GetLockingDirection().GetShortName() != "No Dir'n" else "  "),
        #      end='')
        print('| %10s |' % room.GetDebugString()[:10], end='')
      print('')
      for col in range(col_min, col_max + 1):
        room = self._GetRoom(RoomNum(16 * row + col), level_num)
        print(self._GetColorForPrinting(RoomNum(16 * row + col), level_num), end='')
        print(
            '%s' %
            room.GetWallType(Direction.WEST, return_solid_if_stairway=True).ToChar(Direction.WEST),
            end='')
        print(' %10s ' % room.GetEnemy().GetShortName(), end='')
        #print(' %10s ' % ('Area ' + str(room.GetLockLevel())), end='')
        print(
            '%s' %
            room.GetWallType(Direction.EAST, return_solid_if_stairway=True).ToChar(Direction.EAST),
            end='')
      print('')
      for col in range(col_min, col_max + 1):
        room = self._GetRoom(RoomNum(16 * row + col), level_num)
        print(self._GetColorForPrinting(RoomNum(16 * row + col), level_num), end='')
        #print('| %10s |' % "", end='')
        #print('| %10s |' % room.GetItem().GetShortName(), end='')
        print('| %10s |' % room.GetRoomAction(), end='')
      print('')
      for col in range(col_min, col_max + 1):
        room = self._GetRoom(RoomNum(16 * row + col), level_num)
        print(self._GetColorForPrinting(RoomNum(16 * row + col), level_num), end='')
        print('|_____', end='')
        for a in range(0, 2):
          print(room.GetWallType(Direction.SOUTH,
                                 return_solid_if_stairway=True).ToChar(Direction.SOUTH),
                end='')
        print('_____|', end='')
      print(Fore.WHITE)
  """

  def GenerateLevels(self) -> None:
    #print(self.level_start_rooms)
    for level_num in Range.VALID_LEVEL_NUMBERS:
      self.CreateRoomTree(level_num)
      #self.PlaceItems(level_num)
      self.LinkUpRooms(level_num)
      self.AddEnemies(level_num)

      self.data_table.ClearStaircaseRoomNumbersForLevel(level_num)
      for stairway_room_num in self.level_plan[level_num]['item_stairway_room_nums']:
        print("Adding item staircase %x for level %d" % (stairway_room_num, level_num))
        self.data_table.AddStaircaseRoomNumberForLevel(level_num, stairway_room_num)
      for stairway_room_num in self.level_plan[level_num]['transport_stairway_room_nums']:
        print("Adding transport staircase %x for level %d" % (stairway_room_num, level_num))
        self.data_table.AddStaircaseRoomNumberForLevel(level_num, stairway_room_num)
      #self.data_table.SetItemPositionsForLevel(level_num, [0x89, 0x69, 0x89, 0x42])
      #self.Print(level_num)
      #input()

    self.data_table.SetLevelGrid(GridId.GRID_A, self.room_grid_a)
    self.data_table.SetLevelGrid(GridId.GRID_B, self.room_grid_b)
    #input("done!")

  def CreateRoomTree(self, level_num: LevelNum) -> None:
    while True:
      self.ResetRooms(level_num)
      self._GenerateLevelStartRoom(level_num)
      if not self.TryCreateRoomTree(level_num):
        continue
      if not self.PlaceItems(level_num):
        continue
      self.PlaceBorders(level_num)
      if not self.PlaceNonBorderElders(level_num):
        continue
      break

  def ResetRooms(self, level_num: LevelNum) -> None:
    for room_num in self._GetRoomNumsForLevel(level_num):
      self._GetRoom(room_num, level_num).ResetRoomState()


#      room = self._GetRoom(room_num, level_num)
#  room.SetEnemy(Enemy.NO_ENEMY)
#  room.SetItem(Item.NOTHING)
#  room.SetRoomType(RoomType.PLAIN_ROOM)
#  room.SetLockLevel(0)
#  room.SetLockingDirection(Direction.NO_DIRECTION)
#  room.child_room_nums = []
#  room.SetDebugString("")
#  for direction in Range.CARDINAL_DIRECTIONS:
#    room.SetWallType(direction, WallType.SOLID_WALL)

  def TryCreateRoomTree(self, level_num: LevelNum) -> bool:
    print("TryCreateRoomTree")
    # Entrance into the level from the OW should always be an open door
    entrance_dir = self.level_entrance_directions[level_num]
    entrance_room_num = self.level_start_rooms[level_num]
    entrance_room = self._GetRoom(entrance_room_num, level_num)
    entrance_room.SetRoomType(RoomType.ENTRANCE_ROOM)
    entrance_room.SetWallType(entrance_dir, WallType.OPEN_DOOR)
    entrance_room.SetLockLevel(1)

    level_room_nums = self._GetRoomNumsForLevel(level_num).copy()
    level_room_nums.remove(entrance_room_num)
    assigned_room_nums = [entrance_room_num]

    actual_num_rooms = {1: 1, 2: 0, 3: 0, 4: 0, 5: 0}
    if level_num > 3:
      actual_num_rooms[6] = 0
    if level_num > 6:
      actual_num_rooms[7] = 0
    #print("Resetting TSRN")
    transport_stairway_room_nums = self.level_plan[level_num]['transport_stairway_room_nums'].copy()

    current_room_num = entrance_room_num
    while True:
      #self.Print(level_num)
      #print("Current room num is %x" % current_room_num)
      #self.Print(level_num)
      #input("---")

      current_room = self._GetRoom(current_room_num, level_num)
      area_id = current_room.GetLockLevel()
      plan = self.level_plan[level_num][str(area_id)]
      PrintListInHex(transport_stairway_room_nums)
      if plan['border_type'] in [BorderType.THE_KIDNAPPED, BorderType.TRIFORCE_ROOM]:
        break

      # Transport stair case
      if (actual_num_rooms[area_id] == self.level_plan[level_num][str(area_id)]['path_length'] and
          self.level_plan[level_num][str(area_id)]['stairway_border'] == True):
        next_room_num = random.choice(level_room_nums)
        next_room = self._GetRoom(next_room_num, level_num)
        level_room_nums.remove(next_room_num)
        assigned_room_nums.append(next_room_num)

        stairway_room_num = transport_stairway_room_nums.pop()
        print("Popped %s. Now: ..." % stairway_room_num)
        PrintListInHex(transport_stairway_room_nums)
        stairway_room = self._GetRoom(stairway_room_num, level_num)
        stairway_room.SetRoomType(RoomType.TRANSPORT_STAIRCASE)
        stairway_room.SetStairwayRoomExit(room_num=current_room_num, is_right_side=False)
        stairway_room.SetStairwayRoomExit(room_num=next_room_num, is_right_side=True)
        stairway_room.SetRoomAction(RoomAction.NO_ROOM_ACTION)
        stairway_room.SetItem(Item.NOTHING)
        print("I'm in level %d. stairway_rooms_transport %x" % (level_num, stairway_room_num))
        print("left: %x, right %x" % (current_room_num, next_room_num))
        #input()

        current_room.SetStairsDestination(stairway_room_num)
        next_room.SetStairsDestination(stairway_room_num)
        current_room_type = RoomType.RandomValueOkayForStairs()
        next_room_type = RoomType.RandomValueOkayForStairs()
        current_room.SetRoomType(current_room_type)
        next_room.SetRoomType(next_room_type)
        current_room.SetRoomAction(current_room_type.GetRoomActionIfHasStairs())
        next_room.SetRoomAction(next_room_type.GetRoomActionIfHasStairs())
        stairway_room.SetReturnPosition(
            RoomType.GetValidPositionForRoomTypes(current_room_type, next_room_type))
        current_room.SetLockingDirection(Direction.STAIRCASE)
        next_room.SetLockLevel(current_room.GetLockLevel() + 1)
        current_room.AddChildRoomNum(next_room_num)
        next_room.SetParentRoomNum(current_room_num)
        actual_num_rooms[current_room.GetLockLevel() + 1] += 1
        current_room.SetDebugString("%x -> %x" % (current_room_num, next_room_num))
        next_room.SetDebugString("%x -> %x" % (next_room_num, current_room_num))
        #self.Print(level_num)
        #input("qqq")
      else:
        #print("path length is %d" % self.level_plan[level_num][str(area_id)]['path_length'] )
        #print("actual length is %d" %  actual_num_rooms[area_id] )

        is_expanding = actual_num_rooms[area_id] == self.level_plan[level_num][str(
            area_id)]['path_length']
        border_type = self.level_plan[level_num][str(area_id)]['border_type']

        maybe_next_dirs = Range.CARDINAL_DIRECTIONS.copy()
        random.shuffle(maybe_next_dirs)
        next_dir = Direction.NO_DIRECTION
        for maybe_next_dir in maybe_next_dirs:

          if is_expanding:
            if border_type in [BorderType.BAIT_BLOCK, BorderType.MUGGER
                              ] and maybe_next_dir != Direction.NORTH:
              continue
            if border_type in [BorderType.TRIFORCE_CHECK, BorderType.BOSS
                              ] and maybe_next_dir == Direction.SOUTH:
              continue
            if border_type == BorderType.THE_BEAST and maybe_next_dir == Direction.SOUTH:
              continue

          maybe_next_room_num = GetNextRoomNum(current_room_num, maybe_next_dir)
          if maybe_next_room_num in level_room_nums:
            next_dir = maybe_next_dir
            break

        # If we don't have a valid next room to move to, give up :(
        if next_dir == Direction.NO_DIRECTION:
          #print( "No valid room to move to :(")
          #input("Hi")
          return False

        #print("Next room num is %x" % GetNextRoomNum(current_room_num, next_dir))
        #input("sd")
        # Claim the next room and connect them.
        next_room_num = GetNextRoomNum(current_room_num, next_dir)
        next_room = self._GetRoom(next_room_num, level_num)
        level_room_nums.remove(next_room_num)
        assigned_room_nums.append(next_room_num)
        current_room.SetWallType(maybe_next_dir, WallType.OPEN_DOOR)
        next_room.SetWallType(maybe_next_dir.Reverse(), WallType.OPEN_DOOR)
        current_room.AddChildRoomNum(next_room_num)
        next_room.SetParentRoomNum(current_room_num)

        if actual_num_rooms[area_id] == self.level_plan[level_num][str(area_id)]['path_length']:
          current_room.SetLockingDirection(next_dir)
          next_room.SetLockLevel(current_room.GetLockLevel() + 1)
        else:
          next_room.SetLockLevel(current_room.GetLockLevel())
      actual_num_rooms[area_id] += 1
      current_room_num = next_room_num

    counter = 0
    while True:
      if len(level_room_nums) == 0:
        print("Success! Counter is %d " % counter)
        #self.Print(level_num)
        break
      counter += 1
      if counter > 1000:
        if level_num > 6:
          #self.Print(level_num)
          #input("timeout")
        return False
      maybe_parent_room_num = random.choice(assigned_room_nums)
      maybe_parent_room = self._GetRoom(maybe_parent_room_num, level_num)
      current_area = maybe_parent_room.GetLockLevel()

      maybe_direction = random.choice(Range.CARDINAL_DIRECTIONS)
      maybe_child_room_num = GetNextRoomNum(maybe_parent_room_num, maybe_direction)

      # Don't expand into a room that's not available for expansion
      if maybe_child_room_num not in level_room_nums:
        continue

      if self.level_plan[level_num][str(maybe_parent_room.GetLockLevel())]['border_type'] in [
          BorderType.THE_KIDNAPPED, BorderType.TRIFORCE_ROOM
      ]:
        continue

      (parent_room_num, child_room_num) = (maybe_parent_room_num, maybe_child_room_num)
      parent_room = maybe_parent_room

      # Move from the "to-do" list to the assigned list.
      level_room_nums.remove(child_room_num)
      assigned_room_nums.append(child_room_num)
      child_room = self._GetRoom(maybe_child_room_num, level_num)
      parent_room.SetWallType(maybe_direction, WallType.OPEN_DOOR)
      child_room.SetWallType(maybe_direction.Reverse(), WallType.OPEN_DOOR)

      parent_room.AddChildRoomNum(maybe_child_room_num)
      child_room.SetParentRoomNum(maybe_parent_room_num)
      child_room_lock_level = parent_room.GetLockLevel()

      #if maybe_create_new_border:
      #    parent_room.SetLockingDirection(maybe_direction)
      #    child_room_lock_level = parent_room.GetLockLevel() + 1

      child_room.SetLockLevel(child_room_lock_level)
      actual_num_rooms[child_room_lock_level] += 1

    return True

  def PlaceItems(self, level_num: LevelNum) -> bool:
    print("PlaceItems")
    item_stairway_room_nums = self.level_plan[level_num]['item_stairway_room_nums'].copy()
    for area_id in self.level_plan[level_num].keys():
      if len(area_id) > 1:
        continue
      good_item_room_nums: List[RoomNum] = []
      backup_item_room_nums: List[RoomNum] = []
      triforce_room_num: RoomNum = RoomNum(-1)

      print("level num %d, area_id %s" % (level_num, area_id))
      for room_num in self._GetRoomNumsForLevel(level_num):

        # Figure out the triforce room by virtue of it being the highest lock level
        if triforce_room_num == RoomNum(-1):
          triforce_room_num = room_num
        elif (self._GetRoom(room_num, level_num).GetLockLevel() > self._GetRoom(
            triforce_room_num, level_num).GetLockLevel()):
          triforce_room_num = room_num

        # Now look for good item rooms
        room = self._GetRoom(room_num, level_num)
        if str(room.GetLockLevel()) != area_id:
          continue

        #print("Considering room %x ..." % room_num)
        if room.GetLockingDirection() != Direction.NO_DIRECTION:
          #print("... nope, has a %s lock dir" % room.GetLockingDirection())
          continue
        if room.HasStairs():
          continue
        #print(room.GetChildRoomNums())

        if len(room.GetChildRoomNums()) == 0:
          #print("... Has no child rooms")
          good_item_room_nums.append(room_num)
        elif room.GetRoomType() != RoomType.ENTRANCE_ROOM:
          #print("Isn't an entrance. %d child rooms" % len(room.GetChildRoomNums()))
          backup_item_room_nums.append(room_num)
      # else:
      #print("Is an entrance")
      random.shuffle(good_item_room_nums)
      random.shuffle(backup_item_room_nums)
      items_to_place = self.level_plan[level_num][area_id]['items']

      for item in [Item.HEART_CONTAINER, Item.TRIFORCE, Item.NOTHING, Item.BLUE_POTION]:
        if item in items_to_place:
          items_to_place.remove(item)

      #print("level num %d, area_id %s" % (level_num, area_id))
      #print("%s %s %d %d" % (good_item_room_nums , backup_item_room_nums ,len(good_item_room_nums), len(backup_item_room_nums)))
      if len(items_to_place) > len(good_item_room_nums) + len(backup_item_room_nums):
        return False
      while len(good_item_room_nums) < len(items_to_place):
        good_item_room_nums.append(backup_item_room_nums.pop())

      for item in items_to_place:
        item_room_num = good_item_room_nums.pop()
        item_room = self._GetRoom(item_room_num, level_num)
        enemy = Enemy.RandomHardEnemyOrMiniBossOkayForSpriteSets(
            self.level_plan[level_num]['boss_sprite_set'],
            self.level_plan[level_num]['enemy_sprite_set'])
        item_room.SetEnemy(enemy)
        item_room.SetEnemyQuantityCode(random.randrange(2, 3))
        if item.IsMajorItem():
          stairway_room_num = item_stairway_room_nums.pop(0)
          print("MAJOR ITEM TO PLACE: %s. Item room %x -> Stairway %x" %
                (item, item_room_num, stairway_room_num))
          stairway_room = self._GetRoom(stairway_room_num, level_num)
          stairway_room.SetRoomType(RoomType.ITEM_STAIRCASE)
          stairway_room.SetStairwayRoomExit(room_num=item_room_num, is_right_side=True)
          stairway_room.SetStairwayRoomExit(room_num=item_room_num, is_right_side=False)
          stairway_room.SetItemPositionCode(0)
          stairway_room.SetItem(item)
          item_room.SetStairsDestination(stairway_room_num)
          item_room.SetInnerPalette(DungeonPalette.WATER)
          room_type = RoomType.RandomValueOkayForStairs()
          item_room.SetRoomAction(room_type.GetRoomActionIfHasStairs())
          item_room.SetRoomType(room_type)
          stairway_room.SetReturnPosition(RoomType.GetValidPositionForRoomType(room_type))
          item_room.SetDebugString("S %s" % item.name)
        else:
          room_type = RoomType.RandomValue(okay_for_enemy=enemy)
          item_room.SetRoomType(room_type)
          item_room.SetItem(item)
          item_room.SetItemPositionCode(self.item_position_dict[room_type])
          item_room.SetDebugString("F %s" % item.name)
          item_room.SetRoomAction(
              random.choice([
                  RoomAction.NO_ROOM_ACTION,
                  RoomAction.KILLING_ENEMIES_OPENS_SHUTTER_DOORS_AND_DROPS_ITEM
              ]))
    return True

  def PlaceBorders(self, level_num: LevelNum) -> None:
    for area_id in self.level_plan[level_num].keys():
      if len(area_id) > 1:
        continue
      border_room_nums = []

      # Find the border room
      for room_num in self._GetRoomNumsForLevel(level_num):
        room = self._GetRoom(room_num, level_num)
        if str(room.GetLockLevel()) != area_id:
          continue

        if room.GetLockingDirection() != Direction.NO_DIRECTION:
          #print("level %d area %s room %x direction %s" %
          #      (level_num, area_id, room_num, room.GetLockingDirection()))
          border_room_nums.append(room_num)
          #print(len(border_room_nums))

        elif self.level_plan[level_num][area_id]['border_type'] in [
            BorderType.TRIFORCE_ROOM, BorderType.THE_KIDNAPPED
        ]:
          border_room_nums.append(room_num)
      #print(border_room_nums)
      assert len(border_room_nums) == 1
      border_room_num = border_room_nums.pop()
      border_type = self.level_plan[level_num][area_id]['border_type']
      border_room = self._GetRoom(border_room_num, level_num)
      border_dir = border_room.GetLockingDirection()

      if border_type == BorderType.BAIT_BLOCK:
        border_room.SetEnemy(Enemy.HUNGRY_ENEMY)
        border_room.SetRoomType(RoomType.BLACK_ROOM)
        border_room.SetInnerPalette(DungeonPalette.BLACK_AND_WHITE)
      elif border_type == BorderType.MUGGER:
        border_room.SetEnemy(Enemy.MUGGER)
        border_room.SetRoomType(RoomType.BLACK_ROOM)
        border_room.SetInnerPalette(DungeonPalette.BLACK_AND_WHITE)
      elif border_type in [BorderType.BOMB_HOLE, BorderType.LOCKED_DOOR]:
        next_room_num = GetNextRoomNum(border_room_num, border_dir)
        next_room = self._GetRoom(next_room_num, level_num)
        wall_type = WallType.BOMB_HOLE if border_type == BorderType.BOMB_HOLE else WallType.LOCKED_DOOR_1
        border_room.SetWallType(border_dir, wall_type)
        next_room.SetWallType(border_dir.Reverse(), wall_type)
        border_room.SetEnemy(
            Enemy.RandomEnemyOkayForSpriteSet(self.level_plan[level_num]['enemy_sprite_set']))
      elif border_type in OK_BORDER_TYPES_FOR_TRANSPORT_STAIRCASE or border_type == BorderType.BOSS:
        okay_enemies = {
            BorderType.BOOMERANG_BLOCK: [Enemy.RED_KEESE, Enemy.DARK_KEESE],
            BorderType.CANDLE_BLOCK: [Enemy.ROPE],
            BorderType.BOW_BLOCK: [Enemy.RED_GOHMA, Enemy.BLUE_GOHMA],
            BorderType.RECORDER_BLOCK: [Enemy.SINGLE_DIGDOGGER, Enemy.TRIPLE_DIGDOGGER],
            BorderType.WAND_BLOCK: [Enemy.MANHANDALA],
            BorderType.BOSS: [
                Enemy.RandomBossFromSpriteSet(self.level_plan[level_num]['boss_sprite_set'])
            ],
            BorderType.MINI_BOSS: [
                Enemy.RandomHardEnemyOrMiniBossOkayForSpriteSets(
                    boss_sprite_set=self.level_plan[level_num]['boss_sprite_set'],
                    enemy_sprite_set=self.level_plan[level_num]['enemy_sprite_set'])
            ]
        }
        enemy = random.choice(okay_enemies[border_type])
        border_room.SetEnemy(enemy)
        border_room.SetEnemyQuantityCode(0)
        if border_room.GetLockingDirection() != Direction.STAIRCASE:
          #pass
          # Not needed I think because the room action is set when creating the staircase
          #border_room.SetRoomAction(RoomAction.PUSHABLE_BLOCK_MAKES_STAIRS_APPEAR)
          #else:
          border_room.SetWallType(border_dir, WallType.SHUTTER_DOOR)
          border_room.SetRoomAction(RoomAction.KILLING_ENEMIES_OPENS_SHUTTER_DOORS)
        if border_type == BorderType.BOSS:
          border_room.SetItem(Item.HEART_CONTAINER)
          room.SetItemPositionCode(2)
          border_room.SetRoomAction(RoomAction.KILLING_ENEMIES_OPENS_SHUTTER_DOORS_AND_DROPS_ITEM)
      elif border_type == BorderType.TRIFORCE_ROOM:
        border_room.SetRoomType(RoomType.TRIFORCE_ROOM)
        border_room.SetItem(Item.TRIFORCE)
        room.SetItemPositionCode(0)
        border_room.SetEnemy(Enemy.NO_ENEMY)
        self.data_table.UpdateCompassPointer(Location(level_num=level_num,
                                                      room_num=border_room_num))
      elif border_type == BorderType.LADDER_BLOCK:
        border_room.SetRoomType(RoomType.CHEVY_ROOM)
      elif border_type == BorderType.THE_KIDNAPPED:
        border_room.SetEnemy(Enemy.THE_KIDNAPPED)
        self.data_table.UpdateCompassPointer(Location(level_num=level_num,
                                                      room_num=border_room_num))
        border_room.SetBossRoarSound(False)
      elif border_type == BorderType.THE_BEAST:
        border_room.SetEnemy(Enemy.THE_BEAST)
        border_room.SetDarkRoomBit(True)
        border_room.SetRoomType(RoomType.BEAST_ROOM)
        border_room.SetRoomAction(RoomAction.KILLING_THE_BEAST_OPENS_SHUTTER_DOORS)
        border_room.SetOuterPalette(DungeonPalette.PRIMARY)
        border_room.SetInnerPalette(DungeonPalette.PRIMARY)
        border_room.SetEnemyQuantityCode(0)

        for direction in Range.CARDINAL_DIRECTIONS:
          if border_room.GetWallType(direction) != WallType.SOLID_WALL:
            border_room.SetWallType(direction, WallType.SHUTTER_DOOR)
          next_room_num = GetNextRoomNum(border_room_num, direction)
          assert border_room.GetWallType(direction) != WallType.OPEN_DOOR
          if next_room_num in self._GetRoomNumsForLevel(level_num):
            next_room = self._GetRoom(next_room_num, level_num)
            if next_room.GetEnemy() != Enemy.THE_KIDNAPPED:
              next_room.SetBossRoarSound(True)

      elif border_type == BorderType.POWER_BRACELET_BLOCK:
        border_room.SetRoomAction(RoomAction.EXPERIMENTAL_6)
        border_room.SetRoomType(RoomType.SINGLE_BLOCK_ROOM)
        border_room.SetInnerPalette(DungeonPalette.ACCENT_COLOR)
      elif border_type in [BorderType.TRIFORCE_CHECK]:
        border_room.SetEnemy(Enemy.ELDER)
        border_room.SetRoomType(RoomType.BLACK_ROOM)
        border_room.SetInnerPalette(DungeonPalette.BLACK_AND_WHITE)
        border_room.SetRoomAction(RoomAction.KILLING_ENEMIES_OPENS_SHUTTER_DOORS)
        for direction in Range.CARDINAL_DIRECTIONS:
          print("Direction in iter %s" % direction)
          print("locking dir %s" % border_room.GetLockingDirection())
          print(" -> reverse %s" % border_room.GetLockingDirection().Reverse())
          if direction != border_room.GetLockingDirection():
            print("skipping")
            continue
          if border_room.GetWallType(direction) != WallType.SOLID_WALL:
            print("setting")
            border_room.SetWallType(direction, WallType.SHUTTER_DOOR)
        #input("")
      else:
        print("Need a handler for border type: %s " % border_type)
        assert (1 == 2)

  def PlaceNonBorderElders(self, level_num: LevelNum) -> bool:
    possible_room_nums: List[RoomNum] = []
    all_room_nums = self._GetRoomNumsForLevel(level_num)
    random.shuffle(all_room_nums)
    for room_num in all_room_nums:
      print("Room %x" % room_num)
      room = self._GetRoom(room_num, level_num)
      if room.GetLockingDirection() != Direction.NO_DIRECTION:
        print("locking")
        continue
      if room.GetWallType(Direction.NORTH) != WallType.SOLID_WALL:
        print("no solid wall")
        continue
      if room.GetItem() != Item.NOTHING:
        print("item %s" % room.GetItem())
        continue
      if room.GetEnemy() != Enemy.NO_ENEMY:
        print("enemy %s" % room.GetEnemy())
        continue
      if room.GetRoomType() == RoomType.ENTRANCE_ROOM:
        print("ENTRANCE ROOM")
        continue
      if room.HasStairs():
        print("STAIRS")
        continue
      if len(room.GetChildRoomNums()) == 0:
        possible_room_nums.insert(0, room_num)
        print("OK 1")
      else:
        possible_room_nums.append(room_num)
        print("OK 2")

    if len(possible_room_nums) < len(self.level_plan[level_num]['elders']):
      return False

    for elder in self.level_plan[level_num]['elders']:
      room_num = possible_room_nums.pop(0)
      room = self._GetRoom(room_num, level_num)
      room.SetInnerPalette(DungeonPalette.BLACK_AND_WHITE)
      room.SetRoomType(RoomType.BLACK_ROOM)
      room.SetEnemy(elder)
    return True

  def AddEnemies(self, level_num: LevelNum) -> None:
    level_room_nums = self._GetRoomNumsForLevel(level_num)
    for room_num in level_room_nums:
      room = self._GetRoom(room_num, level_num)
      if (room.GetEnemy() == Enemy.NO_ENEMY and room.GetRoomType() == RoomType.PLAIN_ROOM and
          room.GetItem() == Item.NOTHING):
        enemy = Enemy.RandomEnemyOkayForSpriteSet(
            sprite_set=self.level_plan[level_num]['enemy_sprite_set'])
        room_type = RoomType.RandomValue(okay_for_enemy=enemy)
        room.SetEnemy(enemy)
        room.SetEnemyQuantityCode(random.randrange(1, 2))
        room.SetRoomType(room_type)
        item = random.choice([Item.BOMBS, Item.FIVE_RUPEES, Item.RUPEE, Item.NOTHING, Item.NOTHING])
        room.SetItem(item)

        if item != Item.NOTHING:
          room.SetRoomAction(
              random.choice([
                  RoomAction.NO_ROOM_ACTION,
                  RoomAction.KILLING_ENEMIES_OPENS_SHUTTER_DOORS_AND_DROPS_ITEM
              ]))

  def LinkUpRooms(self, level_num: LevelNum) -> None:
    level_room_nums = self._GetRoomNumsForLevel(level_num)

    # For east-west room pairs
    for room_num in level_room_nums:
      if room_num + 0x01 not in level_room_nums:
        continue
      left_room = self._GetRoom(room_num, level_num)
      right_room_num = RoomNum(room_num + 0x01)
      right_room = self._GetRoom(right_room_num, level_num)
      if (left_room.GetParentRoomNum() == right_room_num or
          right_room.GetParentRoomNum() == room_num or
          left_room.GetLockLevel() != right_room.GetLockLevel()):
        continue
      if level_num < 4:
        wall_type = WallType.BOMB_HOLE
      elif level_num < 7:
        wall_type = random.choice([WallType.OPEN_DOOR, WallType.BOMB_HOLE])
      else:
        wall_type = random.choice([WallType.OPEN_DOOR, WallType.BOMB_HOLE, WallType.SOLID_WALL])

      self._GetRoom(room_num, level_num).SetWallType(Direction.EAST, wall_type)
      self._GetRoom(right_room_num, level_num).SetWallType(Direction.WEST, wall_type)

    # For north-south room pairs
    for room_num in level_room_nums:
      if room_num + 0x10 not in level_room_nums:
        continue
      top_room = self._GetRoom(room_num, level_num)
      bottom_room_num = RoomNum(room_num + 0x10)
      bottom_room = self._GetRoom(bottom_room_num, level_num)
      if (top_room.GetParentRoomNum() == room_num + 0x10 or
          bottom_room.GetParentRoomNum() == room_num or
          top_room.GetLockLevel() != bottom_room.GetLockLevel()):
        continue
      if bottom_room.GetEnemy() in [
          Enemy.ELDER, Enemy.ELDER_2, Enemy.ELDER_3, Enemy.ELDER_4, Enemy.BOMB_UPGRADER,
          Enemy.ELDER_6, Enemy.ELDER_8
      ]:
        continue
      wall_type = random.choice([WallType.OPEN_DOOR, WallType.BOMB_HOLE])
      wall_type = WallType.BOMB_HOLE
      self._GetRoom(room_num, level_num).SetWallType(Direction.SOUTH, wall_type)
      self._GetRoom(bottom_room_num, level_num).SetWallType(Direction.NORTH, wall_type)

  def RandomizeShops(self) -> None:
    minor_items = [(Item.BOMBS, random.randrange(5, 20)), (Item.BOMBS, random.randrange(20, 35)),
                   (Item.MAGICAL_SHIELD, random.randrange(125, 160)),
                   (Item.SINGLE_HEART, random.randrange(1, 20)),
                   (Item.KEY, random.randrange(230, 255)), (Item.FAIRY, random.randrange(20, 35)),
                   (Item.BLUE_POTION, random.randrange(30, 55)),
                   (Item.RED_POTION, random.randrange(55, 85))]
    major_items = [
        (Item.BLUE_CANDLE, random.randrange(50, 80)),
        (Item.WOOD_ARROWS, random.randrange(60, 100)),
        (Item.BAIT, random.randrange(60, 100)),
        (Item.BLUE_RING, random.randrange(125, 175)),
        (Item.OVERWORLD_NO_ITEM, 0),
    ]

    while True:
      random.shuffle(major_items)
      random.shuffle(minor_items)
      if (minor_items[0][0] == minor_items[1][0] or minor_items[2][0] == minor_items[3][0] or
          minor_items[4][0] == minor_items[5][0] or minor_items[6][0] == minor_items[7][0]):
        continue
      if major_items[3][0] == Item.OVERWORLD_NO_ITEM:
        continue
      break
    shop_item_data = [
        [minor_items[0][0], major_items[0][0], minor_items[1][0]],
        [minor_items[2][0], major_items[1][0], minor_items[3][0]],
        [minor_items[4][0], major_items[2][0], minor_items[5][0]],
        [Item.OVERWORLD_NO_ITEM, major_items[3][0], Item.OVERWORLD_NO_ITEM],
        [minor_items[6][0], major_items[4][0], minor_items[7][0]],
    ]
    shop_price_data = [
        [minor_items[0][1], major_items[0][1], minor_items[1][1]],
        [minor_items[2][1], major_items[1][1], minor_items[3][1]],
        [minor_items[4][1], major_items[2][1], minor_items[5][1]],
        [0, major_items[3][1], 0],
        [minor_items[6][1], major_items[4][1], minor_items[7][1]],
    ]

    for shop_num in range(5):
      for position_num in range(3):
        cave_type = CaveType(0x1D + shop_num) if shop_num != 4 else CaveType.POTION_SHOP
        location = Location(cave_type=cave_type, position_num=position_num + 1)
        self.data_table.SetCaveItem(shop_item_data[shop_num][position_num], location)
        self.data_table.SetCavePrice(shop_price_data[shop_num][position_num], location)

    #location = Location(cave_type=CaveType.POTION_SHOP, position_num=1)
    #self.data_table.SetCavePrice(random.randrange(30, 55), location)
    #location = Location(cave_type=CaveType.POTION_SHOP, position_num=3)
    #self.data_table.SetCavePrice(random.randrange(50, 75), location)
    """# 7 minor items?
# bombs, shield, heart, key, fairy, potion, potion
# + bombs
2 (pot shop)
3
3
3
1
--
12
-4
8
"""

  def OldRandomizeShops(self) -> None:
    minor_items: List[Tuple[Item, int]] = []
    is_done = False
    while not is_done:
      minor_items = [(Item.BOMBS, random.randrange(5, 20)), (Item.BOMBS, random.randrange(20, 35)),
                     (Item.MAGICAL_SHIELD, random.randrange(90, 125)),
                     (Item.MAGICAL_SHIELD, random.randrange(125, 160)),
                     (Item.SINGLE_HEART, random.randrange(1, 20)),
                     (Item.SINGLE_HEART, random.randrange(1, 20)),
                     (Item.KEY, random.randrange(230, 255)), (Item.FAIRY, random.randrange(20, 35))]
      random.shuffle(minor_items)
      if (minor_items[0][0] != minor_items[1][0] and minor_items[2][0] != minor_items[3][0] and
          minor_items[4][0] != minor_items[5][0] and minor_items[6][0] != minor_items[7][0]):
        is_done = True
    shop_item_data = [[minor_items[0][0], Item.BLUE_CANDLE, minor_items[1][0]],
                      [minor_items[2][0], Item.WOOD_ARROWS, minor_items[3][0]],
                      [minor_items[4][0], Item.BLUE_RING, minor_items[5][0]],
                      [minor_items[6][0], Item.BAIT, minor_items[7][0]]]
    shop_price_data = [[minor_items[0][1],
                        random.randrange(50, 80), minor_items[1][1]],
                       [minor_items[2][1],
                        random.randrange(80, 100), minor_items[3][1]],
                       [minor_items[4][1],
                        random.randrange(100, 125), minor_items[5][1]],
                       [minor_items[6][1],
                        random.randrange(125, 150), minor_items[7][1]]]

    for shop_num in range(0, 4):
      for position_num in range(0, 3):
        location = Location(cave_type=CaveType(0x1D + shop_num), position_num=position_num + 1)
        self.data_table.SetCaveItem(shop_item_data[shop_num][position_num], location)
        self.data_table.SetCavePrice(shop_price_data[shop_num][position_num], location)

    location = Location(cave_type=CaveType.POTION_SHOP, position_num=1)
    self.data_table.SetCavePrice(random.randrange(30, 55), location)
    location = Location(cave_type=CaveType.POTION_SHOP, position_num=3)
    self.data_table.SetCavePrice(random.randrange(50, 75), location)

  def RandomizeOverworldCaves(self) -> None:
    destinations: List[Union[LevelNum, CaveType]] = []
    any_road_screen_nums: List[int] = []
    recorder_screen_nums: List[int] = [-1] * 8

    all_screen_nums = Screen.ALL_SCREENS_WITH_1Q_CAVES.copy()
    all_screen_nums.sort()
    for screen_num in all_screen_nums:
      dest = self.data_table.GetCaveDestination(screen_num)
      destinations.append(dest)
    random.shuffle(destinations)

    # Assign Wood Sword cave to an open cave
    wood_sword_cave_screen_num = random.choice(Screen.POSSIBLE_FIRST_WEAPON_SCREENS)
    self.data_table.SetCaveDestination(wood_sword_cave_screen_num, CaveType.WOOD_SWORD_CAVE)
    screen_nums = Screen.ALL_SCREENS_WITH_1Q_CAVES.copy()
    assert len(destinations) == len(screen_nums)
    screen_nums.remove(wood_sword_cave_screen_num)
    destinations.remove(CaveType.WOOD_SWORD_CAVE)
    assert len(destinations) == len(screen_nums)

    while len(any_road_screen_nums) < 4:
      random.shuffle(screen_nums)
      if screen_nums[0] not in [0x03, 0x07, 0x0A, 0x1E, 0x6D]:  # From Sinistral's research
        any_road_screen_nums.append(screen_nums.pop(0))
        destinations.remove(CaveType.ANY_ROAD_CAVE)
    assert len(destinations) == len(screen_nums)

    for screen_num in screen_nums:
      print(destinations[0])
      destination = destinations.pop(0)
      self.data_table.SetCaveDestination(screen_num, destination)
      if destination in range(1, 9):  # Levels 1-8
        recorder_screen_nums[destination - 1] = screen_num - 1
        hint_text: str = ""
        if destination == 7:
          hint_text += "FIND LEVEL SEVEN"
        else:
          hint_text += "LOOK FOR LEVEL %d" % destination
        hint_text += "|IN THE "
        hint_text += "N" if screen_num < 0x40 else "S"
        hint_text += "W" if screen_num % 16 < 8 else "E"
        hint_text += " OF HYRULE|"
        if screen_num in Screen.OPEN_CAVE_SCREENS:
          hint_text += "IN AN OPEN CAVE"
        elif screen_num in Screen.BOMB_BLOCKED_CAVE_SCREENS:
          hint_text += "IN A HIDDEN CAVE"
        elif screen_num in Screen.CANDLE_BLOCKED_CAVE_SCREENS:
          hint_text += "UNDERNEATH A BUSH"
        elif screen_num in Screen.POWER_BRACELET_BLOCKED_CAVE_SCREENS:
          hint_text += "BY MOVING A BLOCK"
        elif screen_num in Screen.RAFT_BLOCKED_CAVE_SCREENS:
          hint_text += "ON A SMALL ISLAND"
        elif screen_num in Screen.RECORDER_BLOCKED_CAVE_SCREENS:
          hint_text += "UNDERNEATH A LAKE"
        self.data_table.hints.append(hint_text)
        #input(hint_text)
    assert -1 not in recorder_screen_nums
    self.data_table.UpdateAnyRoadAndRecorderScreensNums(any_road_screen_nums, recorder_screen_nums)
    