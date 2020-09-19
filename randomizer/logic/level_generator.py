import math
import random
import sys
from typing import Dict, List, Optional, Tuple

from .constants import CaveType, GridId, DungeonPalette, LevelNum, Range
from .constants import RoomAction, RoomNum, Screen, SpriteSet, WallType
from .direction import Direction
from .data_table import DataTable
from .enemy import Enemy
from .item import Item
from .location import Location
from .room import Room
from .room_type import RoomType


def GetNextRoomNum(room_num: RoomNum, direction: Direction) -> RoomNum:
  assert room_num in Range.VALID_ROOM_NUMBERS
  assert direction in Range.CARDINAL_DIRECTIONS
  return RoomNum(int(room_num) + int(direction))


def PrintListInHex(list: List[RoomNum]) -> None:
  print('[', end='')
  for item in list:
    print('%x, ' % item, end='')
  print(']')


# 0x05, 0x08, 0x7A # EW rocks.  (1, 6)
# 0x0B, 0x3B # L2/5                (2)
# 0x39, 0x42, 0x43. # Fairies/L7.  (3,4)
# 0x4F, 0x5F # coast docks. (5)
# 0x7C, 0x7D # south caves  (7)

OW_SCREENS_THAT_MUST_BE_IN_SAME_AREA = [()]


class GridGenerator:

  def __init__(self, data_table: DataTable) -> None:
    self.data_table = data_table
    self.Initialize()
    self.foo: bool

  def Initialize(self) -> None:
    self.grid: List[LevelNum] = [LevelNum.NO_LEVEL_NUM] * 128
    self.level_room_numbers: List[List[RoomNum]] = [[], [], [], [], [], [], [], [], [], []]

  def AddSixToLevelNumbers(self) -> None:
    for a in range(0, 128):
      if int(self.grid[a]) in range(1, 7):
        self.grid[a] = LevelNum(self.grid[a] + 6)
    for b in range(1, 7):
      self.level_room_numbers.insert(1, [])

  def Print(self) -> None:
    for row in range(0, 0x8):
      for col in range(0, 0x10):
        level_num = int(self.grid[0x10 * row + col])
        print(str(level_num), end="")
      print("")

  def GetLevelNumForRoomNum(self, room_num: RoomNum) -> LevelNum:
    assert room_num in Range.VALID_ROOM_NUMBERS
    return self.grid[room_num]

  def GetLevelRoomNumbers(self) -> List[List[RoomNum]]:
    return self.level_room_numbers

  def GenerateLevelGrid(self,
                        num_levels: int,
                        min_level_size: int,
                        max_level_size: int,
                        num_stairway_rooms: int = 6) -> None:
    self.foo = True if num_levels == 3 else False
    while True:
      level_sizes: List[int] = []
      while not sum(level_sizes[1:]) == 0x80 - num_stairway_rooms:
        level_sizes.clear()
        # "Level 0" used to reference item/transport stairways
        level_sizes = [num_stairway_rooms]
        for unused_counter in range(0, num_levels):
          level_sizes.append(random.randint(min_level_size, max_level_size))
      level_sizes.sort()

      self.Initialize()
      if self._AttemptGeneratingLevelGrid(num_levels=num_levels, level_sizes=level_sizes):
        for room_num in Range.VALID_ROOM_NUMBERS:
          if self.grid[room_num] == 0:
            #print("Stairway room %d" % room_num)
            self.level_room_numbers[0].append(room_num)
        return
    print("This should never happen (GenerateLevelGrid)!")

  def _AttemptGeneratingLevelGrid(self, num_levels: int, level_sizes: List[int]) -> bool:
    counter = 0
    for level_num in [LevelNum(n) for n in range(num_levels, 0, -1)]:
      while len(self.level_room_numbers[level_num]) < level_sizes[level_num]:
        expand_result = self._ExpandLevel(level_num)
        if not expand_result:
          counter += 1
        if counter > 900:
          return False
    return True

  def _ExpandLevel(self, level_num: LevelNum) -> bool:
    if not self.level_room_numbers[level_num]:
      return self._ClaimRoomForLevel(level_num, random.choice(Range.VALID_ROOM_NUMBERS))

    random_room_in_level = random.choice(self.level_room_numbers[level_num])
    last_room_added = self.level_room_numbers[level_num][-1]
    original_room_num = random.choice([random_room_in_level, random_room_in_level, last_room_added])

    new_direction_pool = [
        Direction.NORTH,
        Direction.SOUTH,
        Direction.WEST,
        Direction.EAST,
    ]

    if self.foo:
      new_direction_pool.extend([
          #  Direction.EAST, Direction.WEST, Direction.WEST, Direction.EAST, Direction.WEST,
          #Direction.EAST
          random.choice([Direction.EAST, Direction.WEST])
      ])
    else:
      new_direction_pool.extend([
          #Direction.EAST,
          #Direction.SOUTH,
          random.choice([Direction.EAST, Direction.WEST])
      ])

    new_direction = random.choice(new_direction_pool)
    new_room_num = GetNextRoomNum(original_room_num, new_direction)

    if original_room_num % 16 == 15 and new_room_num % 16 == 0:
      return False
    if new_room_num % 16 == 15 and original_room_num % 16 == 0:
      return False

    if new_room_num % 16 in [0, 15] or new_room_num / 16 in [0, 7]:
      if random.choice([False, True, True, True]):
        return False

    # Make sure levels aren't more than 8 rooms wide
    for a in self.level_room_numbers[level_num]:
      if abs(a % 16 - new_room_num % 16) >= 8:
        return False
    return self._ClaimRoomForLevel(level_num, new_room_num)

  def _ClaimRoomForLevel(self, level_num: LevelNum, room_num: RoomNum) -> bool:
    if room_num not in Range.VALID_ROOM_NUMBERS:
      return False
    if self.grid[room_num] > 0:
      return False
    self.grid[room_num] = level_num
    self.level_room_numbers[level_num].append(room_num)
    return True

  def GenerateMapData(self, is_7_to_9: bool) -> None:
    int_level_nums = [7, 8, 9] if is_7_to_9 else [1, 2, 3, 4, 5, 6]
    level_nums = [LevelNum(n) for n in int_level_nums]
    for level_num in level_nums:
      self._GenerateMapDataForLevel(level_num)

  def _GenerateMapDataForLevel(self, level_num: LevelNum) -> None:
    map_bytes: List[int] = [0] * 16
    #    print("Level %d" % level_num)
    for column in range(0, 16):
      for row in range(0, 8):
        if self.grid[16 * row + column] == level_num:
          # print("Found room: row %d, col %d, num %x" % (row, column, (16 * row + column)))
          map_bytes[column] += 2**(7 - row)
    counter_r = 0
    while map_bytes[-1] == 0:
      map_bytes.pop(-1)
      counter_r += 1
    counter_l = 0
    while map_bytes[0] == 0:
      map_bytes.pop(0)
      counter_l += 1

    counter_b = 0
    added_to_left = 0
    while len(map_bytes) < 8:
      if counter_b % 2 == 0:
        map_bytes.append(0)
      else:
        map_bytes.insert(0, 0)
        added_to_left += 1
      counter_b += 1
    offset = counter_l - added_to_left

    for unused_counter in range(0, 4):
      map_bytes.insert(0, 0)
      map_bytes.append(0)

    thingies: List[int] = []
    ppu_command_lookup = {
        0: [0x20, 0x62, 0x08],
        2: [0x20, 0x82, 0x08],
        4: [0x20, 0xA2, 0x08],
        6: [0x20, 0xC2, 0x08]
    }
    ppu_code_lookup = {0: 0x24, 1: 0xFB, 2: 0x67, 3: 0xFF}
    for row in [0, 2, 4, 6]:
      thingies.extend(ppu_command_lookup[row])
      for column in range(4, 12):
        foo = map_bytes[column]
        bar = (foo >> (6 - row)) & 0x03
        assert bar >= 0
        assert bar <= 3
        baz = ppu_code_lookup[bar]
        thingies.append(baz)
    self.data_table.SetMapData(level_num, map_bytes, thingies, offset)


class TimeoutException(Exception):
  pass


class CheckResult(object):

  def __init__(self, message: str) -> None:
    self.message = message


class LevelGenerator:

  def __init__(self, data_table: DataTable) -> None:
    self.data_table = data_table
    self.grid_generator_a: GridGenerator = GridGenerator(self.data_table)
    self.grid_generator_b: GridGenerator = GridGenerator(self.data_table)

    # The following lists have placeholder values for one-indexing
    self.level_start_rooms: List[RoomNum] = [RoomNum(-1)]
    self.level_entrance_directions: List[Direction] = [Direction.NO_DIRECTION]

    self.level_positions: List[List[int]] = [[]]
    self.level_position_dict: Dict[RoomType, int] = {}

    self.level_rooms_a: List[List[RoomNum]] = []
    self.level_rooms_b: List[List[RoomNum]] = []
    self.room_grid_a: List[Room] = []
    self.room_grid_b: List[Room] = []
    self.sprite_sets: List[SpriteSet] = []
    self.boss_sprite_sets: List[SpriteSet] = []

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
    self.RandomizeOverworldCaves()
    self.RandomizeShops()

    self.GenerateRoomPositions()
    self.GenerateLevelStartRooms()
    self.CreateLevelRooms()
    self.RandomizeSpriteSets()
    self.RandomizeStuff()
    self.RandomizePalettes()
    self.data_table.RandomizeBombUpgrades()

    self.data_table.SetLevelGrid(GridId.GRID_A, self.room_grid_a)
    self.data_table.SetLevelGrid(GridId.GRID_B, self.room_grid_b)

  def _GetGridIdForLevel(self, level_num: LevelNum) -> GridId:
    return GridId.GRID_B if level_num in [7, 8, 9] else GridId.GRID_A

  def _GetRoomNumsForLevel(self, level_num: LevelNum) -> List[RoomNum]:
    assert level_num in Range.VALID_LEVEL_NUMBERS
    grid_id = self._GetGridIdForLevel(level_num)
    if grid_id == GridId.GRID_A:
      return self.level_rooms_a[level_num].copy()
    return self.level_rooms_b[level_num].copy()

  def _GetStairwayRoomsForGrid(self, grid_id: GridId) -> List[RoomNum]:
    if grid_id == GridId.GRID_A:
      return self.level_rooms_a[0]
    return self.level_rooms_b[0]

  def _GetGridGenerator(self, grid_id: GridId) -> GridGenerator:
    return self.grid_generator_a if grid_id == GridId.GRID_A else self.grid_generator_b

  def _GetLevelNumForRoomNum(self, room_num: RoomNum, grid_id: GridId) -> LevelNum:
    return self._GetGridGenerator(grid_id).GetLevelNumForRoomNum(room_num)

  def _GetRoomInLevel(self, room_num: RoomNum, level_num: LevelNum) -> Room:
    assert level_num in Range.VALID_LEVEL_NUMBERS
    grid_id = self._GetGridIdForLevel(level_num)
    return self._GetRoom(room_num, grid_id)

  def _GetRoom(self, room_num: RoomNum, grid_id: GridId) -> Room:
    assert room_num in Range.VALID_ROOM_NUMBERS
    room_grid = self.room_grid_a if grid_id == GridId.GRID_A else self.room_grid_b
    return room_grid[room_num]

  def RandomizeShops(self) -> None:
    minor_items: List[Tuple[Item, int]] = []

    is_done = False
    while not is_done:
      minor_items = [(Item.BOMBS, random.randrange(5, 20)), (Item.BOMBS, random.randrange(20, 35)),
                     (Item.MAGICAL_SHIELD, random.randrange(90, 125)),
                     (Item.MAGICAL_SHIELD, random.randrange(125, 160)),
                     (Item.SINGLE_HEART, random.randrange(1, 20)),
                     (Item.SINGLE_HEART, random.randrange(1, 20)),
                     (Item.KEY, random.randrange(70, 90)), (Item.KEY, random.randrange(90, 110))]
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
    screen_nums: List[int] = []
    any_road_screen_nums: List[int] = []
    recorder_screen_nums: List[int] = [-1] * 8

    all_screen_nums = Screen.ALL_SCREENS_WITH_1Q_CAVES.copy()
    all_screen_nums.sort()
    for screen_num in all_screen_nums:
      dest = self.data_table.GetCaveDestination(screen_num)
      screen_nums.append(dest)
      try:
        print(CaveType(dest))
      except ValueError:
        print(LevelNum(dest))
    random.shuffle(screen_nums)
    for screen_num in Screen.ALL_SCREENS_WITH_1Q_CAVES:
      destination = screen_nums.pop()
      self.data_table.SetCaveDestination(screen_num, destination)
      if destination == CaveType.ANY_ROAD_CAVE:
        any_road_screen_nums.append(screen_num)
      elif destination in range(1, 9):  # Levels 1-8
        recorder_screen_nums[destination - 1] = screen_num - 1
    assert -1 not in recorder_screen_nums
    self.data_table.UpdateAnyRoadAndRecorderScreensNums(any_road_screen_nums, recorder_screen_nums)

  def RandomizeSpriteSets(self) -> None:
    sprite_sets = [
        SpriteSet.GORIYA_SPRITE_SET, SpriteSet.DARKNUT_SPRITE_SET, SpriteSet.WIZZROBE_SPRITE_SET
    ]
    sprite_set_pool: List[SpriteSet] = []
    sprite_set_pool.extend(sprite_sets)
    sprite_set_pool.extend(sprite_sets)
    for unused_counter in range(0, 3):
      sprite_set_pool.append(random.choice(sprite_sets))
    random.shuffle(sprite_set_pool)
    sprite_set_pool.insert(0, SpriteSet.NO_SPRITE_SET)  # For one-indexing
    self.sprite_sets = sprite_set_pool

    boss_sprite_sets = [
        SpriteSet.DODONGO_SPRITE_SET, SpriteSet.GLEEOK_SPRITE_SET, SpriteSet.PATRA_SPRITE_SET
    ]
    boss_sprite_set_pool: List[SpriteSet] = []
    boss_sprite_set_pool.extend(boss_sprite_sets)
    boss_sprite_set_pool.extend(boss_sprite_sets)
    for unused_counter in range(0, 3):
      boss_sprite_set_pool.append(random.choice(boss_sprite_sets))
    random.shuffle(boss_sprite_set_pool)
    while boss_sprite_set_pool[8] != SpriteSet.PATRA_SPRITE_SET:
      random.shuffle(boss_sprite_set_pool)
    boss_sprite_set_pool.insert(0, SpriteSet.NO_SPRITE_SET)  # For one-indexing
    self.boss_sprite_sets = boss_sprite_set_pool

    for level_num in Range.VALID_LEVEL_NUMBERS:
      self.data_table.SetSpriteSetsForLevel(level_num, self.sprite_sets[level_num],
                                            self.boss_sprite_sets[level_num])

  def RandomizePalettes(self) -> None:
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
    for level_num in Range.VALID_LEVEL_NUMBERS:
      (dark, medium, light, water) = palettes[level_num]
      self.data_table.WriteDungeonPalette(level_num, palettes[level_num])

  def GenerateRoomPositions(self) -> None:
    # For each level, pick four random item drop positions such that at least one will be a valid
    # and accessible tile (i.e. not on top of blocks, water, etc.). They get numbered 0-3.
    # Then, create a dictionary for each level mapping each room type to the position number (0-3)
    # that is valid for the room type.
    positions = [0x89, 0x88, 0x87, 0xCC]  #AC?
    for level_num in Range.VALID_LEVEL_NUMBERS:
      self.data_table.SetItemPositionsForLevel(level_num, positions)
    for room_type in range(0x00, 0x2A):
      room_type = RoomType(room_type)
      values = [0, 1, 2, 3]
      random.shuffle(values)
      for v in values:
        if room_type in [
            RoomType.VERTICAL_CHUTE_ROOM, RoomType.HORIZONTAL_CHUTE_ROOM,
            RoomType.HORIZONTAL_MOAT_ROOM, RoomType.DOUBLE_MOAT_ROOM
        ]:
          self.level_position_dict[room_type] = 0
          break
        elif room_type in [RoomType.CIRCLE_BLOCK_WALL_ROOM, RoomType.DIAMOND_STAIR_ROOM]:
          self.level_position_dict[room_type] = 3
          break
        elif RoomType.IsValidPositionForRoomType(positions[v], room_type):
          self.level_position_dict[room_type] = v
          break

      assert room_type in self.level_position_dict
    self.level_position_dict[RoomType(0x3F)] = 0
    self.level_position_dict[RoomType(0x31)] = 0
    self.level_position_dict[RoomType(0x32)] = 0
    self.level_position_dict[RoomType(0x33)] = 0
    assert self.level_position_dict[RoomType.AQUAMENTUS_ROOM] != 3
    assert self.level_position_dict[RoomType.DIAMOND_STAIR_ROOM] == 3

  def _PickStartRoomForLevel(self, level_num: LevelNum  ) -> Tuple[RoomNum, Direction]:
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
      if self._GetLevelNumForRoomNum(room_num, grid_id) == level_num:
        potential_gateway = GetNextRoomNum(room_num, entrance_direction)
        if (potential_gateway not in Range.VALID_ROOM_NUMBERS or
            level_num != self._GetLevelNumForRoomNum(potential_gateway, grid_id)):
          possible_start_rooms.append((room_num, entrance_direction))
    return random.choice(possible_start_rooms)

  def GenerateLevelStartRooms(self) -> None:
    for level_num in Range.VALID_LEVEL_NUMBERS:
      #entrance_direction = Direction.RandomCardinalDirection()
      (start_room, entrance_direction) = self._PickStartRoomForLevel(level_num) #, entrance_direction)
      print("Chose start room %x for level %d" % (start_room, level_num))
      print("Direction is %s" % entrance_direction)
      self.data_table.SetStartRoomDataForLevel(level_num, start_room, entrance_direction)
      self.level_start_rooms.append(start_room)
      self.level_entrance_directions.append(entrance_direction)

  def CreateLevelRooms(self) -> None:
    for grid_id in [GridId.GRID_A, GridId.GRID_B]:
      room_grid = [Room() for unused_counter in Range.VALID_ROOM_NUMBERS]
      for room_num in Range.VALID_ROOM_NUMBERS:
        level_num = self._GetLevelNumForRoomNum(room_num, grid_id)
        if level_num not in Range.VALID_LEVEL_NUMBERS:
          continue
        for direction in Range.CARDINAL_DIRECTIONS:
          new_room_num = GetNextRoomNum(room_num, direction)
          if (direction == self.level_entrance_directions[level_num] and
              room_num == self.level_start_rooms[level_num]):
            print("Setting start room %x for level %d" % (room_num, level_num))
            print("Direction is %s" % direction)
            room_grid[room_num].SetWallType(direction, WallType.OPEN_DOOR)
          elif new_room_num not in Range.VALID_ROOM_NUMBERS:
            continue
          elif (self._GetLevelNumForRoomNum(room_num, grid_id) == self._GetLevelNumForRoomNum(
              new_room_num,
              grid_id,
          )):
            room_grid[room_num].SetWallType(direction, WallType.OPEN_DOOR)

      if grid_id == GridId.GRID_A:
        print("Grid A complete")
        self.room_grid_a = room_grid
      else:
        print("Grid B complete")
        self.room_grid_b = room_grid

  # Main Logic starts here

  def RandomizeStuff(self) -> None:
    # Create global (inter-level) pools and settings

    # 1) Elders/Enemies
    elder_assignments: List[List[Enemy]] = [[], [], [], [], [], [], [], [], []]
    elder_assignments.append(
        [Enemy.TRIFORCE_CHECKER_PLACEHOLDER_ELDER, Enemy.ELDER_2, Enemy.ELDER_3,
         Enemy.ELDER_4])  # L9
    level_pool: List[int] = [1, 2, 3, 4, 5, 6, 7, 8]
    level_pool_a: List[int] = []
    level_pool_b: List[int] = []
    random.shuffle(level_pool)
    for unused_counter in range(0, 4):
      level_pool_a.append(level_pool.pop(0))
      level_pool_b.append(level_pool.pop(0))
    assert not level_pool
    level_pool_a.sort(reverse=True)
    level_pool_b.sort(reverse=True)

    elder_group_a: List[Enemy] = [
        Enemy.BOMB_UPGRADER, Enemy.BOMB_UPGRADER, Enemy.HUNGRY_ENEMY, Enemy.ELDER_5
    ]
    elder_group_b: List[Enemy] = [Enemy.ELDER, Enemy.ELDER_2, Enemy.ELDER_3, Enemy.ELDER_4]
    random.shuffle(elder_group_a)
    random.shuffle(elder_group_b)

    for n in range(0, 4):
      elder_assignments[level_pool_a[n]].append(elder_group_a.pop(0))
      elder_assignments[level_pool_b[n]].append(elder_group_b.pop(0))
    assert not elder_group_a and not elder_group_b

    """
    for level_num in level_pool_a:
      self.data_table.SetTextGroup(level_num, "a")
      print("Level %d in group A" % level_num)
    for level_num in level_pool_b:
      print("Level %d in group B" % level_num)
      self.data_table.SetTextGroup(level_num, "b")
    """
    # For debugging bomb upgrades
    for level_num in [1,2,3,4,5,6,7,8]:
      self.data_table.SetTextGroup(level_num, "a")


    # 2) Items
    major_item_pool = [
        Item.BOW, Item.BOOMERANG, Item.MAGICAL_BOOMERANG, Item.RAFT, Item.LADDER, Item.RECORDER,
        Item.WAND, Item.RED_CANDLE, Item.BOOK, Item.MAGICAL_KEY, Item.SILVER_ARROWS, Item.RED_RING
    ]
    random.shuffle(major_item_pool)
    major_item_assignments: List[List[Item]] = [[], [], [], [], [], [], [], [], [], []]
    for n in Range.VALID_LEVEL_NUMBERS:
      major_item_assignments[n].append(major_item_pool.pop(0))
      if n in [7, 8, 9]:
        major_item_assignments[n].append(major_item_pool.pop(0))

    print(major_item_assignments)

    # 3) Staircases
    item_stairway_assignments: List[List[RoomNum]] = [[], [], [], [], [], [], [], [], [], []]
    transport_stairway_assignments: List[List[RoomNum]] = [[], [], [], [], [], [], [], [], [], []]
    stairway_rooms_a = self._GetStairwayRoomsForGrid(GridId.GRID_A)
    stairway_rooms_b = self._GetStairwayRoomsForGrid(GridId.GRID_B)
    assert len(stairway_rooms_a) == 8 and len(stairway_rooms_b) == 12
    for level_num in [1, 2, 3, 4, 5, 6]:
      item_stairway_assignments[level_num].append(stairway_rooms_a.pop(0))
    for level_num in [5, 6]:
      transport_stairway_assignments[level_num].append(stairway_rooms_a.pop(0))
    for level_num in [7, 8, 9]:
      item_stairway_assignments[level_num].append(stairway_rooms_b.pop(0))
      item_stairway_assignments[level_num].append(stairway_rooms_b.pop(0))
      transport_stairway_assignments[level_num].append(stairway_rooms_b.pop(0))
    for unused_counter in range(3):
      transport_stairway_assignments[9].append(stairway_rooms_b.pop(0))
    assert len(stairway_rooms_a) == 0 and len(stairway_rooms_b) == 0
    print(item_stairway_assignments)
    print(transport_stairway_assignments)

    # Main level creation loop

    for level_num in Range.VALID_LEVEL_NUMBERS:
      counter = 0
      while True:
        counter += 1
        if counter > 15:
          print("Reached main counter timeout")
          exit()
        if not self.AddRoomTypes(level_num,
                                 item_stairway_assignments[level_num],
                                 transport_stairway_assignments[level_num],
                                 elder_assignments=elder_assignments[level_num]):
          continue

        if not self.AddInteriorWalls(level_num):
          print("\nTIMEOUT! level %d, step %d\n" % (level_num, 2))
          continue

        if not self.AddEnemies(level_num, elder_assignments[level_num]):
          print("\nTIMEOUT! level %d, step %d\n" % (level_num, 3))
          continue

        if not self.AddItems(level_num, major_item_assignments[level_num]):
          print("\nTIMEOUT! level %d, step %d\n" % (level_num, 4))
          continue

        if not self.AddFinishingTouches(level_num):
          print("\nTIMEOUT! level %d, step %d\n" % (level_num, 5))
          continue

        print("Level #%d complete!" % level_num)
        break

    print(self.sprite_sets)
    print(self.boss_sprite_sets)
    print()

  # ----- Step 1: Add RoomTypes -----
  def AddRoomTypes(self, level_num: LevelNum, item_staircase_room_list: List[RoomNum],
                   transport_staircase_room_list: List[RoomNum],
                   elder_assignments: List[Enemy]) -> bool:
    assert level_num in Range.VALID_LEVEL_NUMBERS
    num_rooms = len(self._GetRoomNumsForLevel(level_num))

    # Create pool of room types to place. Use item/transport staircase types as placeholders
    # for the rooms with stairways that will lead to those respective staircases.
    room_type_pool_template: List[RoomType] = []
    room_type_pool_template.append(RoomType.ENTRANCE_ROOM)
    for elder in elder_assignments:
      if elder == Enemy.HUNGRY_ENEMY:
        room_type_pool_template.append(RoomType.HUNGRY_ENEMY_PLACEHOLDER_ROOM_TYPE)
        continue
      if elder == Enemy.TRIFORCE_CHECKER_PLACEHOLDER_ELDER:
        room_type_pool_template.append(RoomType.TRIFORCE_CHECK_PLACEHOLDER_ROOM_TYPE)
        continue
      room_type_pool_template.append(RoomType.ELDER_PLACEHOLDER_ROOM_TYPE)
    for unused_counter in range(len(item_staircase_room_list)):
      room_type_pool_template.append(RoomType.ITEM_STAIRCASE)
    for unused_counter in range(len(transport_staircase_room_list)):
      room_type_pool_template.append(RoomType.TRANSPORT_STAIRCASE)
      room_type_pool_template.append(RoomType.TRANSPORT_STAIRCASE)
    if level_num == LevelNum.LEVEL_9:
      room_type_pool_template.append(RoomType.KIDNAPPED_ROOM)
      room_type_pool_template.append(RoomType.BEAST_ROOM)

    while len(room_type_pool_template) < num_rooms:
      allow_hard_to_place = random.choice([True, False])
      room_type_pool_template.append(RoomType.RandomValue(allow_hard_to_place))

    transport_stairway_rooms_template: List[Tuple[RoomNum, Direction]] = []
    for transport_stairway_room in transport_staircase_room_list:
      transport_stairway_rooms_template.append((transport_stairway_room, Direction.WEST))
      transport_stairway_rooms_template.append((transport_stairway_room, Direction.EAST))
    room_nums_template = self._GetRoomNumsForLevel(level_num)

    counter = 0
    while True:
      counter += 1
      print()
      print("-- Level %d, Step 1 (Add RoomTypes), Iteration %d ---" % (level_num, counter))
#      print()
#      print(room_type_pool_template)
#      print(transport_stairway_rooms_template)
#      PrintListInHex(item_staircase_room_list)
#      PrintListInHex(room_nums_template)
#      print()
      #input()
      random.shuffle(room_type_pool_template)
      random.shuffle(transport_stairway_rooms_template)
      random.shuffle(item_staircase_room_list)
      random.shuffle(room_nums_template)

      if self.ReallyAddRoomTypes(
          level_num,
          room_nums_template.copy(),
          room_type_pool_template.copy(),
          item_staircase_room_list.copy(),
          transport_stairway_rooms_template.copy(),
      ):
        print("---- Success after %d attempts ---" % counter)
        return True
      if counter >= 100:
        print("\n---- TIMEOUT after %d attempts\n" % counter)
        return False

  def ReallyAddRoomTypes(self, level_num: LevelNum, room_nums: List[RoomNum],
                         room_type_pool: List[RoomType], item_stairway_rooms: List[RoomNum],
                         transport_stairway_room_pool: List[Tuple[RoomNum, Direction]]) -> bool:
    grid_id = GridId.GetGridIdForLevelNum(level_num)
    self.data_table.ClearStaircaseRoomNumbersForLevel(level_num)
    for room_num in room_nums:
      #print("Assigning roomtype for room number 0x%x" % room_num)
      counter = 0
      while True:
        counter += 1

        random.shuffle(room_type_pool)
        room = self._GetRoom(room_num, grid_id)
        room.ClearStairsDestination()
        room_type = room_type_pool[0]
        room.SetRoomType(room_type)

        if self._RoomTypeChecksPass(level_num, room_num, room):
          break
        if counter >= 200:
          return False

      assert room_type == room_type_pool.pop(0)

      room.SetRoomType(room_type)
      room.SetOuterPalette(DungeonPalette.PRIMARY)
      room.SetInnerPalette(DungeonPalette.PRIMARY)

      #TODO: Condense the ITEM_STAIRCASE and TRANSPORT_STAIRCASE cases.
      if room_type == RoomType.ITEM_STAIRCASE:
        stairway_room_num = item_stairway_rooms.pop(0)
        stairway_room = self._GetRoom(stairway_room_num, grid_id)
        stairway_room.SetRoomType(RoomType.ITEM_STAIRCASE)
        stairway_room.SetStairwayRoomExit(room_num=room_num, is_right_side=True)
        stairway_room.SetStairwayRoomExit(room_num=room_num, is_right_side=False)
        assert self.level_position_dict[room_type] == 0
        stairway_room.SetItemPositionCode(self.level_position_dict[room_type])
        room.SetStairsDestination(stairway_room_num)
        room.SetInnerPalette(DungeonPalette.WATER)
        room.SetRoomType(RoomType.DIAMOND_STAIR_ROOM)  # Temp fix -- can take out?
        room_type = RoomType.RandomValueOkayForStairs()
        room.SetRoomType(room_type)
        stairway_room.SetReturnPosition(
            0x85 if room_type.NeedsOffCenterStairReturnPosition() else 0x89)
        self.data_table.AddStaircaseRoomNumberForLevel(level_num, stairway_room_num)
      if room_type == RoomType.TRANSPORT_STAIRCASE:
        (stairway_room_num, ladder_side) = transport_stairway_room_pool.pop()
        stairway_room = self._GetRoom(stairway_room_num, grid_id)
        stairway_room.SetRoomType(RoomType.TRANSPORT_STAIRCASE)
        stairway_room.SetStairwayRoomExit(room_num=room_num,
                                          is_right_side=(ladder_side == Direction.EAST))
        stairway_room.SetRoomAction(RoomAction.NO_ROOM_ACTION)
        stairway_room.SetItem(Item.NOTHING)
        room.SetStairsDestination(stairway_room_num)
        room.SetRoomType(RoomType.DIAMOND_STAIR_ROOM)  # Temp fix -- can take out?
        room_type = RoomType.RandomValueOkayForStairs()
        room.SetRoomType(room_type)
        stairway_room.SetReturnPosition(
            0x85 if room_type.NeedsOffCenterStairReturnPosition() else 0x89)
        room.SetInnerPalette(DungeonPalette.WATER)
        # Only want to add this once.
        if ladder_side == Direction.EAST:
          self.data_table.AddStaircaseRoomNumberForLevel(level_num, stairway_room_num)

      room.SetItemPositionCode(self.level_position_dict[room_type])
      #if room_type == RoomType.ELDER_ROOM:
      #  room.SetInnerPalette(DungeonPalette.BLACK_AND_WHITE)
      if room_type.HasWater() or room_type == RoomType.ENTRANCE_ROOM:
        room.SetInnerPalette(DungeonPalette.WATER)
      elif room.HasStairs():
        room.SetInnerPalette(DungeonPalette.WATER)
      elif room_type in [  RoomType.ELDER_PLACEHOLDER_ROOM_TYPE,
  RoomType.HUNGRY_ENEMY_PLACEHOLDER_ROOM_TYPE ,
  RoomType.TRIFORCE_CHECK_PLACEHOLDER_ROOM_TYPE ]:
        room.SetInnerPalette(DungeonPalette.BLACK_AND_WHITE)
      else:
        room.SetInnerPalette(DungeonPalette.PRIMARY)
      room.SetDarkRoomBit(False)
      room.SetBossRoarSound(False)

    # If we get to this point, the for loop should have finished and all rooms were assigned
    assert len(room_type_pool) == 0
    #print("All Room Types Assigned.  Success!!!")
    return True

  def _RoomTypeChecksPass(self, level_num: LevelNum, room_num: RoomNum, room: Room) -> bool:
    result = self._PerformRoomTypeChecks(level_num, room_num, room)
    if result.message == "OK":
      #print("... checks passed :)")
      return True
    #print("... check failed:  " + result.message)
    return False

  def _PerformRoomTypeChecks(self, level_num: LevelNum, room_num: RoomNum,
                             room: Room) -> CheckResult:
    room_type = room.GetRoomType()
    if room_num == self.level_start_rooms[level_num] and room_type != RoomType.ENTRANCE_ROOM:
      return CheckResult("Entrance room doesn't have an Entrance room type")
    if (room_type == RoomType.KIDNAPPED_ROOM and
        abs(self.level_start_rooms[level_num] - room_num) in [0x1, 0x2, 0xF, 0x10, 0x11, 0x20]):
      return CheckResult("Kidnapped room too close to entrance room")

    if (level_num == LevelNum.LEVEL_9 and
        room_type == RoomType.TRIFORCE_CHECK_PLACEHOLDER_ROOM_TYPE and
        (room_num - self.level_start_rooms[level_num]) not in [-0x10, -0x1, 0x1]):
      return CheckResult("Triforce check room needs to be next to entrance")
    if (room_type in [room_type == RoomType.KIDNAPPED_ROOM, RoomType.T_ROOM] and
        room.GetWallType(Direction.SOUTH) == WallType.SOLID_WALL):
      return CheckResult("T room has no access to 'T' part")
    return CheckResult("OK")

  # ----- Step 2: Add Interior Walls -----
  def AddInteriorWalls(self, level_num: LevelNum) -> bool:
    grid_id = GridId.GetGridIdForLevelNum(level_num)

    start_room = self.level_start_rooms[level_num]
    entrance_dir = self.level_entrance_directions[level_num]
    """
    if level_num == LevelNum.LEVEL_9:
      start_room =  self._GetRoom(start_room_num, grid_id)
      for direction in Direction.CARDINAL_DIRECTIONS:
        if direction == entrance_dir:
          start_room.SetWallType(direction, WallType.OPEN_DOOR)
          continue
        maybe_triforce_check_room_num = GetNextRoomNum(room_num, direction)
        if (maybe_triforce_check_room_num in Range.VALID_ROOM_NUMBERS and 
            self._GetRoom(maybe_triforce_check_room_num, grid_id).GetRoomType() ==
              RoomType.TRIFORCE_CHECK_PLACEHOLDER_ROOM_TYPE):
          start_room.SetWallType(direction, WallType.OPEN_DOOR)
          self._GetRoom(maybe_triforce_check_room_num, grid_id).SwtWallType(direction.inverse(), )
"""
    # 1) Figure out the number of "interior walls" there are (defined as walls that separate two
    # rooms in the level).
    interior_walls: List[Tuple[RoomNum, Direction, RoomNum, Direction]] = []
    for room_num in Range.VALID_ROOM_NUMBERS:
      if self._GetLevelNumForRoomNum(room_num, grid_id) == level_num:
        east_room = GetNextRoomNum(room_num, Direction.EAST)
        if room_num % 0x10 != 0xF and self._GetLevelNumForRoomNum(east_room, grid_id) == level_num:              
          interior_walls.append((room_num, Direction.EAST, east_room, Direction.WEST))
          self._GetRoom(room_num, grid_id).SetWallType(Direction.EAST, WallType.OPEN_DOOR)
          self._GetRoom(east_room, grid_id).SetWallType(Direction.WEST, WallType.OPEN_DOOR)
        south_room = GetNextRoomNum(room_num, Direction.SOUTH)
        if room_num < 0x70 and self._GetLevelNumForRoomNum(south_room, grid_id) == level_num:
          interior_walls.append((room_num, Direction.SOUTH, south_room, Direction.NORTH))
          self._GetRoom(room_num, grid_id).SetWallType(Direction.SOUTH, WallType.OPEN_DOOR)
          self._GetRoom(south_room, grid_id).SetWallType(Direction.NORTH, WallType.OPEN_DOOR)
                


    # 2) Decide on the number of interior walls should be non-open doors. Create a pool of walls
    #    with a random-ish number of each wall types.
    wall_type_pool_template: List[WallType] = []
    num_interior_walls = len(interior_walls)
    num_bombholes = random.randrange(2, math.floor(num_interior_walls / 5)+1)
    num_lockeddoors = random.randrange(2, math.floor(num_interior_walls / 5)+1)
    num_shutterdoors = random.randrange(2, math.floor(num_interior_walls / 5)+1)
    num_solidwalls = random.randrange(0, math.floor(num_interior_walls / 6)+1)
    if level_num in [LevelNum.LEVEL_7, LevelNum.LEVEL_8]:
      num_solidwalls = random.randrange(6, math.floor(num_interior_walls / 5) + 1)
    #if level_num == LevelNum.LEVEL_9:
    #  num_solidwalls = 40
    #  num_shutterdoors = 4
    #  num_lockeddoors = 6
    #  num_bombholes = 5

    for unused_counter in range(num_bombholes):
      wall_type_pool_template.append(WallType.BOMB_HOLE)
    for unused_counter in range(num_lockeddoors):
      wall_type_pool_template.append(WallType.LOCKED_DOOR_1)
    for unused_counter in range(num_shutterdoors):
      wall_type_pool_template.append(WallType.SHUTTER_DOOR)
    for unused_counter in range(num_solidwalls):
      wall_type_pool_template.append(WallType.SOLID_WALL)
    while len(wall_type_pool_template) < num_interior_walls:
      wall_type_pool_template.append(WallType.OPEN_DOOR)

    counter = 0
    while True:
      counter += 1
      print("--- Level %d, Step 2 (Add WallTypes), Iteration %d ---" % (level_num, counter))
      random.shuffle(wall_type_pool_template)
      random.shuffle(interior_walls)

      if self.ReallyAddInteriorWalls(level_num, interior_walls.copy(),
                                     wall_type_pool_template.copy()):
        print("---- Success after %d attempts ---" % counter)
        return True
      if counter >= 50:
        print("\n---- TIMEOUT after %d attempts\n" % counter)
        return False

  def ReallyAddInteriorWalls(self, level_num: LevelNum,
                             interior_walls: List[Tuple[RoomNum, Direction, RoomNum, Direction]],
                             wall_type_pool: List[WallType]) -> bool:
    grid_id = GridId.GetGridIdForLevelNum(level_num)
    # 3) Take each wall type from the pool and assign it to a random interior wall.
    #print("Start of for loop")
    #    a = 0
    for (room_num_1, direction_1, room_num_2, direction_2) in interior_walls:
      #      a += 1
      #      print()
      #      print("Assigning wall for room 0x%x, %s wall (and counterpart)" % (room_num_1, direction_1))
      #      print("%d / %d sets of interior walls to go" %(a, len(interior_walls)))
      #      print()
      counter = 0
      while True:
        counter += 1
        if counter >= 100:
          #print("---Inner counter timeout----")
          #print()
          return False
        random.shuffle(wall_type_pool)
        wall_type = wall_type_pool[0]
        room_1 = self._GetRoom(room_num_1, grid_id)
        room_2 = self._GetRoom(room_num_2, grid_id)

        #print("---")
        if level_num == LevelNum.LEVEL_9:
         if room_1.GetRoomType() == RoomType.ENTRANCE_ROOM:
          if room_2.GetRoomType() == RoomType.TRIFORCE_CHECK_PLACEHOLDER_ROOM_TYPE:
            if wall_type != WallType.OPEN_DOOR:
              continue
          elif wall_type != WallType.SHUTTER_DOOR:
              continue
         if room_2.GetRoomType() == RoomType.ENTRANCE_ROOM:
          if room_1.GetRoomType() == RoomType.TRIFORCE_CHECK_PLACEHOLDER_ROOM_TYPE:
            if wall_type != WallType.OPEN_DOOR:
              continue
          elif wall_type != WallType.SHUTTER_DOOR:
              continue
         if room_1.GetRoomType() == RoomType.TRIFORCE_CHECK_PLACEHOLDER_ROOM_TYPE:
          if room_2.GetRoomType() != RoomType.ENTRANCE_ROOM:
            if wall_type not in [WallType.SHUTTER_DOOR, WallType.SOLID_WALL]:
              continue
         if room_2.GetRoomType() == RoomType.TRIFORCE_CHECK_PLACEHOLDER_ROOM_TYPE:
          if room_1.GetRoomType() != RoomType.ENTRANCE_ROOM:
            if wall_type not in [WallType.SHUTTER_DOOR, WallType.SOLID_WALL]:
              continue
        
        if (self._SingleWallTypeChecksPass(room_1.GetRoomType(), direction_1, wall_type,
                                           room_1.HasStairs()) and
            self._SingleWallTypeChecksPass(room_2.GetRoomType(), direction_2, wall_type,
                                           room_2.HasStairs())):
          #print("--- A")

          break
        #print("--- B")

      #print("CCCC")
      assert wall_type == wall_type_pool.pop(0)
      room_1.SetWallType(direction_1, wall_type)
      room_2.SetWallType(direction_2, wall_type)

    #print("DDDD")
    # Check room wide wall types now that all have been assigned
    for (room_num_1, unused_direction_1, room_num_2, unused_direction_2) in interior_walls:
      if not self._RoomWideWallTypeChecksPass(self._GetRoom(room_num_1, grid_id)):
        #print("Uh oh!")
        return False
      if not self._RoomWideWallTypeChecksPass(self._GetRoom(room_num_2, grid_id)):
        #print("Uh oh")
        return False

    # Should be a 1:1 correspondence between walltypes in the pool and actual interior walls.
    assert len(wall_type_pool) == 0

    # 4) Make sure solid walls don't partition the level in half. Throw an exception if so.
    # TODO: In larger levels, this may actually be desired (not something to avoid) as long as
    # there are transport stairways between the partitions.
    start_room = self.level_start_rooms[level_num]
    entrance_dir = self.level_entrance_directions[level_num]
    rooms_visited: Dict[RoomNum, List[Direction]] = {}
    rooms_visited[start_room] = [Direction.NORTH, Direction.SOUTH, Direction.EAST, Direction.WEST]

    for direction in Range.CARDINAL_DIRECTIONS:
      if (direction != entrance_dir and
          self._GetRoom(start_room, grid_id).GetWallType(direction) != WallType.SOLID_WALL):
        self._RecursivelyVisitRoom(
            level_num,
            GetNextRoomNum(start_room, direction),
            direction.Reverse(),
            rooms_visited,
        )

    expected = self._GetRoomNumsForLevel(level_num)
    expected.sort()
    actual = list(rooms_visited.keys())
    actual.sort()
    print("Expected: vs. Actual: ")
    PrintListInHex(expected)
    PrintListInHex(actual)
    print()
    if len(self._GetRoomNumsForLevel(level_num)) < len(rooms_visited):
      print("len(self._GetRoomNumsForLevel(level_num)) %d < len(rooms_visited) %d" %
            (len(self._GetRoomNumsForLevel(level_num)), len(rooms_visited)))
      print()

      exit(1)
    if len(self._GetRoomNumsForLevel(level_num)) != len(rooms_visited):
      print("len(self._GetRoomNumsForLevel(level_num)) %d != len(rooms_visited) %d" %
            (len(self._GetRoomNumsForLevel(level_num)), len(rooms_visited)))
      #input()
      return False
    else:
      print("len(self._GetRoomNumsForLevel(level_num)) %d == len(rooms_visited) %d" %
            (len(self._GetRoomNumsForLevel(level_num)), len(rooms_visited)))
    #input()
    return True

  # ----- Step 3: Add Enemies -----
  def AddEnemies(self, level_num: LevelNum, elders_list: List[Enemy]) -> bool:

    sprite_set = self.sprite_sets[level_num]
    boss_sprite_set = self.boss_sprite_sets[level_num]
    num_rooms = len(self._GetRoomNumsForLevel(level_num))

    enemy_pool_template: List[Enemy] = []
    enemy_pool_template.extend(elders_list)
    enemy_pool_template.append(Enemy.NOTHING)
    enemy_pool_template.append(Enemy.NOTHING)
    enemy_pool_template.append(Enemy.NOTHING)
    enemy_pool_template.append(Enemy.NOTHING)
    if level_num == LevelNum.LEVEL_9:
      enemy_pool_template.append(Enemy.THE_BEAST)
      enemy_pool_template.append(Enemy.THE_KIDNAPPED)
    num_bosses = math.floor(num_rooms / 10) + 1
    for unused_counter in range(num_bosses):
      enemy_pool_template.append(Enemy.RandomBossFromSpriteSet(boss_sprite_set))
    while len(enemy_pool_template) < num_rooms:
      enemy_pool_template.append(
          Enemy.RandomEnemyOkayForSpriteSet(sprite_set,
                                            must_be_in_sprite_set=(len(enemy_pool_template) %
                                                                   2 == 0)))
    room_nums = self._GetRoomNumsForLevel(level_num)

    counter = 0
    while True:
      counter += 1
      print("--- Level %d, Step 3 (Add Enemies), Iteration %d ---" % (level_num, counter))
      random.shuffle(enemy_pool_template)
      random.shuffle(room_nums)
      if self.ReallyAddEnemies(level_num, room_nums.copy(), enemy_pool_template.copy()):
        print("---- Success after %d attempts ---" % counter)
        #input("sds")
        return True
      #input("sds")
      if counter >= 100:
        print("\n---- TIMEOUT after %d attempts\n" % counter)
        return False

  def ReallyAddEnemies(self, level_num: LevelNum, room_nums: List[RoomNum],
                       enemy_pool: List[Enemy]) -> bool:
    grid_id = GridId.GetGridIdForLevelNum(level_num)
    for room_num in room_nums:
      room = self._GetRoom(room_num, grid_id)
      room_type = room.GetRoomType()
      #print()
      #print("Room type: %s" % room_type)

      counter = 0
      while True:
        counter += 1
        random.shuffle(enemy_pool)
        enemy = enemy_pool[0]
        #        print("Trying Enemy %s" % enemy)
        if self._EnemyChecksPass(room_type, enemy):
          #          print("OK")
          break


#       print("")
        if counter >= 200:
          return False
      assert enemy == enemy_pool.pop(0)
      #print("Enemies left to place: %d" % len(enemy_pool))
      #print("Num rooms in level: %d" % len(self._GetRoomNumsForLevel(level_num)))
      #print("Placing %s in room 0x%x" % (enemy, room_num))
      room.SetEnemy(enemy)
      if enemy == [Enemy.SINGLE_DODONGO, Enemy.TRIPLE_DODONGO]:
        room.SetEnemyQuantityCode(random.randrange(0, 1))
      elif enemy.HasBubbles():
        room.SetEnemyQuantityCode(random.randrange(2, 3))
      else:
        room.SetEnemyQuantityCode(random.randrange(0, 3))
    assert len(enemy_pool) == 0
    #print("Add Enemies success. Yay!")
    return True

  # Step 4
  def AddItems(self, level_num: LevelNum, major_item_pool_template: List[Item]) -> bool:
    assert level_num in Range.VALID_LEVEL_NUMBERS
    print("Add Items")
    num_rooms = len(self._GetRoomNumsForLevel(level_num))
    num_keys = min(4, math.floor(num_rooms / 5))
    minor_item_pool_template = [Item.MAP, Item.COMPASS]
    if level_num != 9:
      minor_item_pool_template.extend([Item.TRIFORCE, Item.HEART_CONTAINER])
    for unused_counter in range(num_keys):
      minor_item_pool_template.append(Item.KEY)
    while len(minor_item_pool_template) < num_rooms:
      minor_item_pool_template.append(random.choice([Item.BOMBS, Item.FIVE_RUPEES, Item.NOTHING]))
    counter = 0
    while True:
      print("-- Level %d, Step 4 (Add Enemies), Iteration %d ---" % (level_num, counter))
      counter += 1
      random.shuffle(minor_item_pool_template)
      random.shuffle(major_item_pool_template)
      if self.ReallyAddItems(level_num, major_item_pool_template.copy(),
                             minor_item_pool_template.copy()):
        print("\n---- Success after %d attempts\n" % counter)
        return True
      if counter >= 100:
        print("\n---- TIMEOUT after %d attempts\n" % counter)
        return False

  def ReallyAddItems(self, level_num: LevelNum, major_item_pool: List[Item],
                     minor_item_pool: List[Item]) -> bool:
    room_nums = self._GetRoomNumsForLevel(level_num)
    random.shuffle(room_nums)
    for room_num in room_nums:
      counter = 0
      room = self._GetRoomInLevel(room_num, level_num)
      while True:
        counter += 1
        random.shuffle(minor_item_pool)
        item = minor_item_pool[0]
        if self._ItemChecksPass(item, room):
          assert item == minor_item_pool.pop(0)
          break
        if counter >= 100:
          return False

      room.SetItem(item)

      if item == Item.TRIFORCE:
        self.data_table.UpdateCompassPointer(Location(level_num=level_num, room_num=room_num))
      #if item == Item.HEART_CONTAINER:
      #  room.SetBossRoarSound(True)
      #else:
      #  room.SetBossRoarSound(False)
        

      if room.HasStairs():
        staircase_room_num = room.GetStairsDestination()
        staircase_room = self._GetRoomInLevel(staircase_room_num, level_num)
        if staircase_room.IsItemStaircase():
          staircase_room.SetItem(major_item_pool.pop(0))
        else:
          staircase_room.SetItem(Item.NOTHING)
      room.SetRoomAction(self.GetRoomAction(room, item))
    for room_num in room_nums:
      if room.GetEnemy() == Enemy.THE_BEAST:
        room.SetItem(Item.NOTHING)
        for direction in Range.CARDINAL_DIRECTIONS:
          if room.GetWallType(direction) in [
              WallType.OPEN_DOOR, WallType.LOCKED_DOOR_1, WallType.LOCKED_DOOR_2
          ]:
            room.SetWallType(direction, WallType.SHUTTER_DOOR)
        room.SetOuterPalette(DungeonPalette.PRIMARY)
        room.SetInnerPalette(DungeonPalette.PRIMARY)
        room.SetEnemyQuantityCode(0)
        room.SetDarkRoomBit(True)
        room.SetRoomAction(RoomAction.KILLING_THE_BEAST_OPENS_SHUTTER_DOORS)

    assert len(minor_item_pool) == 0
    return True

  def GetRoomAction(self, room: Room, item: Item) -> RoomAction:
    room_type = room.GetRoomType()
    if room_type == RoomType.TURNSTILE_ROOM:
      assert not room.HasStairs()
      return RoomAction.PUSHABLE_BLOCK_OPENS_SHUTTER_DOORS
    if room_type == RoomType.DIAMOND_STAIR_ROOM:
      assert room.HasStairs()
      # If there's a room item, give it a 50/50 whether it's a drop or standing item.
      # Drop case: Killing enemies -> item drop and shutter doors open.
      # Standing item/no item case: Killing enemies -> pushing block -> shutter doors open
      if item != Item.NOTHING and random.choice([True, False]):
        return RoomAction.KILLING_ENEMIES_OPENS_SHUTTER_DOORS_DROPS_ITEM_AND_MAKES_BLOCK_PUSHABLE
      return RoomAction.PUSHABLE_BLOCK_OPENS_SHUTTER_DOORS

    # Case for rooms stairways that don't appear at room load
    # (i.e. all stairway rooms that aren't diamond, spiral, or L3 raft room)
    # These can't have shutter doors.
    if room.HasStairs() and not room.GetRoomType().HasUnobstructedStairs():
      assert not room.HasShutterDoor()
      return RoomAction.PUSHABLE_BLOCK_MAKES_STAIRS_APPEAR
    # Make the item a drop around 50/50 of the time vs. a standing item.
    # HCs should be drops because we want them to be guarded by bosses.
    if item != Item.NOTHING and (item == Item.HEART_CONTAINER or random.choice([True, False])):
      return RoomAction.KILLING_ENEMIES_OPENS_SHUTTER_DOORS_AND_DROPS_ITEM

    if room.HasShutterDoor():
      if room.GetRoomType().CanHavePushBlock():
        return RoomAction.PUSHABLE_BLOCK_OPENS_SHUTTER_DOORS
      else:
        return RoomAction.KILLING_ENEMIES_OPENS_SHUTTER_DOORS
    return RoomAction.NO_ROOM_ACTION

  def _ItemChecksPass(self, item: Item, room: Room) -> bool:
    result = self._PerformItemChecks(item, room)
    if result.message == "OK":
      return True
    #print(result.message)
    return False

  def _PerformItemChecks(self, item: Item, room: Room) -> CheckResult:
    enemy = room.GetEnemy()
    if item != Item.NOTHING:
      if enemy.IsElderOrHungryEnemy() or enemy == Enemy.TRIFORCE_CHECKER_PLACEHOLDER_ELDER:
        return CheckResult("An Elder or Hungry Enemy can't have a room item")
      if room.GetRoomType() in [RoomType.ENTRANCE_ROOM, RoomType.TURNSTILE_ROOM]:
        return CheckResult("An item can't be in an entrance or turnstile room")
    if item == Item.HEART_CONTAINER and not room.GetEnemy().IsBoss():
      return CheckResult("Before further shuffling, heart containers must be in boss rooms")
    return CheckResult("OK")

  def AddFinishingTouches(self, level_num: LevelNum) -> bool:
    if level_num != LevelNum.LEVEL_9:
      return True
    print("---- AddFinishingTouches Level %s" % level_num)
    start_room_num = self.level_start_rooms[level_num]
    entrance_dir = self.level_entrance_directions[level_num]
    grid_id = self._GetGridIdForLevel(level_num)
    room_nums = self._GetRoomNumsForLevel(level_num)
    triforce_check_room_num: RoomNum

    for room_num in room_nums:
      # Add roars around Gannon
      room = self._GetRoom(room_num, grid_id)
      if room.GetEnemy() == Enemy.THE_BEAST:
        room.SetDarkRoomBit(True)
        room.SetInnerPalette(DungeonPalette.WATER)
        for direction in Range.CARDINAL_DIRECTIONS:
          next_room_num = GetNextRoomNum(room_num, direction)
          if next_room_num in room_nums:
            self._GetRoom(next_room_num, grid_id).SetBossRoarSound(True)
      # Add shutter doors around the kidnapped
      if room.GetEnemy() == Enemy.THE_KIDNAPPED:
        for direction in Range.CARDINAL_DIRECTIONS:
          if room.GetWallType(direction) == WallType.SOLID_WALL:
            continue
          room.SetWallType(direction, WallType.OPEN_DOOR)
          next_room_num = GetNextRoomNum(room_num, direction)
          if next_room_num in room_nums:
            next_room = self._GetRoom(next_room_num, grid_id)
            next_room.SetRoomAction(RoomAction.KILLING_THE_BEAST_OPENS_SHUTTER_DOORS)
            next_room.SetWallType(direction.Reverse(), WallType.SHUTTER_DOOR)
      if room.GetRoomType() == RoomType.TRIFORCE_CHECK_PLACEHOLDER_ROOM_TYPE:
        triforce_check_room_num = room_num
        input("Found tri check")
    
    # Make sure there isn't a way around the triforce check  
    assert triforce_check_room_num in Range.VALID_ROOM_NUMBERS  
    start_room = self._GetRoom(start_room_num, grid_id)
    check_diff = triforce_check_room_num - start_room_num
    assert check_diff in [-0x1, 0x1, 0x10]
    check_direction = Direction(check_diff)
    for direction in Range.CARDINAL_DIRECTIONS:
      input(direction)
      if direction == entrance_dir or direction == check_direction:
        assert start_room.GetWallType(direction) == WallType.OPEN_DOOR
      else:
        assert start_room.GetWallType(direction) == WallType.SOLID_WALL
        start_room.SetWallType(direction, WallType.SOLID_WALL)
    return True

  def _RecursivelyVisitRoom(self,
                            level_num: LevelNum,
                            room_num: RoomNum,
                            entry_direction: Direction,
                            rooms_visited: Dict[RoomNum, List[Direction]],
                            factor_in_room_type: bool = False) -> None:
    room = self._GetRoomInLevel(room_num, level_num)
    # An item staircase room is a dead-end.
    if room.IsItemStaircase():
      return

    # For a transport staircase, we don't know whether we came in through the left or right.
    # So try to leave both ways; the one that we came from will have already been marked as
    # visited and just return.
    if room.IsTransportStaircase():
      for room_num_to_visit in [room.GetStairwayRoomLeftExit(), room.GetStairwayRoomRightExit()]:
        self._RecursivelyVisitRoom(level_num, room_num_to_visit, Direction.STAIRCASE, rooms_visited,
                                   factor_in_room_type)
      return

    if room_num in rooms_visited:
      if entry_direction in rooms_visited[room_num]:
        return
      rooms_visited[room_num].append(entry_direction)
    else:
      rooms_visited[room_num] = [entry_direction]

    #print(" -- type is %s" % room.GetRoomType())
    for exit_direction in Range.CARDINAL_DIRECTIONS:
      if entry_direction == exit_direction:
        #print("-- can't go %s because that's where I came from" % exit_direction)
        continue
      if (factor_in_room_type and not room.GetRoomType().AllowsDoorToDoorMovement(
          entry_direction, exit_direction, has_ladder=True)):
        #print("-- can't go %s for some reason." % exit_direction)
        continue
      if room.GetWallType(exit_direction) != WallType.SOLID_WALL:
        #print("-- can go %s!" % exit_direction)
        self._RecursivelyVisitRoom(level_num, GetNextRoomNum(room_num, exit_direction),
                                   exit_direction.Reverse(), rooms_visited, factor_in_room_type)
    if room.HasStairs():
      self._RecursivelyVisitRoom(level_num, room.GetStairsDestination(), Direction.STAIRCASE,
                                 rooms_visited, factor_in_room_type)

  def _EnemyChecksPass(self, room_type: RoomType, enemy: Enemy) -> bool:
    result = self._PerformEnemyChecks(room_type, enemy)
    if result.message == "OK":
      return True
    print(result.message)
    return False

  def _PerformEnemyChecks(self, room_type: RoomType, enemy: Enemy) -> CheckResult:
    if enemy != Enemy.TRIFORCE_CHECKER_PLACEHOLDER_ELDER and room_type == RoomType.TRIFORCE_CHECK_PLACEHOLDER_ROOM_TYPE:
      return CheckResult("Triforce check needs the right type of elder")
    if enemy == Enemy.TRIFORCE_CHECKER_PLACEHOLDER_ELDER and room_type != RoomType.TRIFORCE_CHECK_PLACEHOLDER_ROOM_TYPE:
      return CheckResult("Triforce check guy not in right type of room.")
    if enemy == Enemy.THE_KIDNAPPED and room_type != RoomType.KIDNAPPED_ROOM:
      return CheckResult("Kidnapped not in their room")
    if enemy != Enemy.THE_KIDNAPPED and room_type == RoomType.KIDNAPPED_ROOM:
      return CheckResult("Kidnapped room without kidnapped")
    if enemy == Enemy.THE_BEAST and room_type != RoomType.BEAST_ROOM:
      return CheckResult("Beast not in their room")
    if enemy != Enemy.THE_BEAST and room_type == RoomType.BEAST_ROOM:
      return CheckResult("Beast room without beast")
    if enemy == Enemy.HUNGRY_ENEMY and room_type != RoomType.HUNGRY_ENEMY_PLACEHOLDER_ROOM_TYPE:
      return CheckResult("Hungry enemy not in their room")
    if enemy != Enemy.HUNGRY_ENEMY and room_type == RoomType.HUNGRY_ENEMY_PLACEHOLDER_ROOM_TYPE:
      return CheckResult("Hungry enemy room without hungry enemy")
    if enemy.IsElder() and room_type != RoomType.ELDER_PLACEHOLDER_ROOM_TYPE:
      return CheckResult("Elder not in elder room")
    if not enemy.IsElder() and room_type == RoomType.ELDER_PLACEHOLDER_ROOM_TYPE:
      return CheckResult("Elder room without elder")
    if enemy != Enemy.NOTHING and room_type == RoomType.ENTRANCE_ROOM:
      return CheckResult("Enemies in entrance room, which is a no-no")
    if enemy in [Enemy.BLUE_LANMOLA, Enemy.RED_LANMOLA] and room_type.IsBadForLanmola():
      return CheckResult("Lanmolas in rooms that are bad for them")
    if room_type.IsPartitionedByBlockWalls() and not enemy.CanMoveThroughBlockWalls():
      return CheckResult("Enemies that can't move block walls in partitioned rooms")
    if (enemy.HasTraps() or enemy.HasRedWizzrobes() and room_type.IsBadForTraps()):
      return CheckResult("Traps/red wizzies in a bad room for traps")
    if (enemy.IsBoss() or enemy == Enemy.RUPEE_BOSS) and room_type.IsBadForBosses():
      return CheckResult("Boss in a room that's not 'open' enough for boss fights")
    if (enemy.HasBlueWizzrobes() or enemy.IsBoss()) and room_type.HasBeamoses():
      return CheckResult("Bosses/Blue wizzrobes in room with beamoses")
    if enemy != Enemy.NOTHING and room_type == RoomType.TURNSTILE_ROOM:
      return CheckResult("Enemies in a turnstile/four-way block room")
    if enemy in [Enemy.PATRA_1, Enemy.PATRA_2] and room_type.IsBadForPatra():
      return CheckResult("Patra in a room that's bad for Patra")
    return CheckResult("OK")

  def _SingleWallTypeChecksPass(self, room_type: RoomType, direction: Direction,
                                wall_type: WallType, has_stairs: bool) -> bool:
    result = self._PerformSingleWallTypeChecks(room_type, direction, wall_type, has_stairs)
    #print("%s %s %s %s %s" % (result.message, room_type, direction, wall_type, has_stairs))
    if result.message == "OK":
      return True
    return False

  def _RoomWideWallTypeChecksPass(self, room: Room) -> bool:
    result = self._PerformRoomWideWallTypeChecks(room)
    if result.message == "OK":
      return True
    print(result.message)
    return False

  def _PerformRoomWideWallTypeChecks(self, room: Room) -> CheckResult:
    room_type = room.GetRoomType()
    if (room_type == RoomType.T_ROOM and
        room.GetWallType(Direction.NORTH) == WallType.SOLID_WALL and
        room.GetWallType(Direction.WEST) == WallType.SOLID_WALL and
        room.GetWallType(Direction.EAST) == WallType.SOLID_WALL):
      return CheckResult("Perimiter of T room isn't accessible")
    if room_type == RoomType.SECOND_QUEST_T_LIKE_ROOM:
      if (room.GetWallType(Direction.WEST) == WallType.SOLID_WALL and
          room.GetWallType(Direction.SOUTH) == WallType.SOLID_WALL):
        return CheckResult("2Q T room has no access to southwest")
      if (room.GetWallType(Direction.NORTH) == WallType.SOLID_WALL and
          room.GetWallType(Direction.EAST) == WallType.SOLID_WALL):
        return CheckResult("2Q T room has no access to northeast")
    if (room_type == RoomType.HORIZONTAL_CHUTE_ROOM and
        room.GetWallType(Direction.EAST) == WallType.SOLID_WALL and
        room.GetWallType(Direction.WEST) == WallType.SOLID_WALL):
      return CheckResult("Oh chute! (horizontal)")
    if (room_type == RoomType.VERTICAL_CHUTE_ROOM and
        room.GetWallType(Direction.NORTH) == WallType.SOLID_WALL and
        room.GetWallType(Direction.SOUTH) == WallType.SOLID_WALL):
      return CheckResult("Check Fail: Oh chute! (vertical)")
    return CheckResult("OK")

  def _PerformSingleWallTypeChecks(self, room_type: RoomType, direction: Direction,
                                   wall_type: WallType, has_stairs: bool) -> CheckResult:
    if (room_type == RoomType.TRIFORCE_CHECK_PLACEHOLDER_ROOM_TYPE and
        wall_type in [WallType.LOCKED_DOOR_1, WallType.LOCKED_DOOR_2, WallType.BOMB_HOLE]):
      return CheckResult("Triforce check can't have locked doors or bombholes")
    if (room_type == RoomType.NARROW_STAIR_ROOM and direction == Direction.EAST and
        wall_type != WallType.SOLID_WALL):
      return CheckResult("Narrow stairway room needs a solid wall to the east.")
    if (room_type == RoomType.HUNGRY_ENEMY_PLACEHOLDER_ROOM_TYPE and
        direction == Direction.NORTH and wall_type == WallType.SOLID_WALL and
        # Added this to avoid deadlocks -- doesn't ALWAYS have to
        random.choice([True, True, True, False])):
      return CheckResult("Hungry Enemy doesn't have a passage to guard")
    if room_type == RoomType.KIDNAPPED_ROOM:
      if direction == Direction.SOUTH and wall_type == WallType.SOLID_WALL:
        return CheckResult("Kidnapped room can't have a south solid wall")
      if direction != Direction.SOUTH and wall_type != WallType.SOLID_WALL:
        return CheckResult("Kidnapped room north, east, and west walls must be solid")
    if (room_type == RoomType.T_ROOM and direction == Direction.SOUTH and
        wall_type == WallType.SOLID_WALL):
      return CheckResult("T room bottom part must be accessible")
    if room_type == RoomType.ELDER_PLACEHOLDER_ROOM_TYPE:
      if direction == Direction.NORTH and wall_type != WallType.SOLID_WALL:
        return CheckResult("Need solid wall above elder rooms")
      if wall_type == WallType.SHUTTER_DOOR:
        return CheckResult("Elder Room shouldn't have a shutter door")
    if has_stairs and not room_type.HasOpenStairs() and wall_type == WallType.SHUTTER_DOOR:
      return CheckResult("A pushblock can't both open shutter doors and make a stairway appear")
    return CheckResult("OK")
