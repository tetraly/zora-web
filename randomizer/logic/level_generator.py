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
    #    for level_num in [LevelNum(n) for n in range(num_levels, 0, -1)]:
    #      self._ClaimRoomForLevel(level_num, RoomNum(  random.randrange(0, 0x7F)))
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

    original_room_num = random.choice(self.level_room_numbers[level_num])
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
      if random.choice([False,True, True, True]):
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
      return self.level_rooms_a[level_num]
    return self.level_rooms_b[level_num]

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
        recorder_screen_nums[destination - 1] = screen_num
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
    assert self.level_position_dict[RoomType.AQUAMENTUS_ROOM] != 3
    assert self.level_position_dict[RoomType.DIAMOND_STAIR_ROOM] == 3

  def _PickStartRoomForLevel(self, level_num: LevelNum, entrance_direction: Direction) -> RoomNum:
    possible_start_rooms: List[RoomNum] = []
    grid_id = GridId.GetGridIdForLevelNum(level_num)

    for room_num in Range.VALID_ROOM_NUMBERS:
      if self._GetLevelNumForRoomNum(room_num, grid_id) == level_num:
        potential_gateway = GetNextRoomNum(room_num, entrance_direction)
        if (potential_gateway not in Range.VALID_ROOM_NUMBERS or
            level_num != self._GetLevelNumForRoomNum(potential_gateway, grid_id)):
          possible_start_rooms.append(room_num)
    return random.choice(possible_start_rooms)

  def GenerateLevelStartRooms(self) -> None:
    for level_num in Range.VALID_LEVEL_NUMBERS:
      entrance_direction = Direction.RandomCardinalDirection()
      start_room = self._PickStartRoomForLevel(level_num, entrance_direction)
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

  def RandomizeStuff(self) -> None:
    # Global (inter-level) settings

    # 2) Elders/Enemies
    elder_assignments: List[List[Enemy]] = [[], [], [], [], [], [], [], [], []]
    elder_assignments.append([Enemy.ELDER_2, Enemy.ELDER_3])  # Level 9
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
        Enemy.BOMB_UPGRADER, Enemy.BOMB_UPGRADER, Enemy.HUNGRY_ENEMY, Enemy.ELDER
    ]
    elder_group_b: List[Enemy] = [Enemy.ELDER, Enemy.ELDER_2, Enemy.ELDER_3, Enemy.ELDER_4]
    random.shuffle(elder_group_a)
    random.shuffle(elder_group_b)

    for n in range(0, 4):
      elder_assignments[level_pool_a[n]].append(elder_group_a.pop(0))
      elder_assignments[level_pool_b[n]].append(elder_group_b.pop(0))
    assert not elder_group_a and not elder_group_b

    for level_num in level_pool_a:
      self.data_table.SetTextGroup(level_num, "a")
    for level_num in level_pool_b:
      self.data_table.SetTextGroup(level_num, "b")

    # 3) Items
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

    # 1) Staircases
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

    for level_num in Range.VALID_LEVEL_NUMBERS:
      done = False
      while not done:
        try:
          print("----- 1) Add Interior walls ----- ")
          self.AddInteriorWalls(level_num)
          print("----- 2) Add Room Types ----- ")
          self.AddRoomTypes(
              level_num,
              item_stairway_assignments[level_num],
              transport_stairway_assignments[level_num],
              make_room_for_hungry_enemy=(Enemy.HUNGRY_ENEMY in elder_assignments[level_num]))
          print("----- 3) Add Enemies ----- ")
          self.AddEnemies(level_num, elder_assignments[level_num])
          print("----- 4) Add Items ----- ")
          self.AddItems(level_num, major_item_assignments[level_num])
          print("----- 5) Add Finishing Touches ------")
          self.AddFinishingTouches(level_num)
          done = True

        except TimeoutException:
          print("---- Received timeout exception ----")
          done = False
          #sys.exit()
      print("Level #%d complete!" % level_num)
    print(self.sprite_sets)
    print(self.boss_sprite_sets)
    print()

  def AddFinishingTouches(self, level_num: LevelNum) -> None:
    print("Level %s" % level_num)
    start_room_num = self.level_start_rooms[level_num]
    entrance_dir = self.level_entrance_directions[level_num]
    grid_id = self._GetGridIdForLevel(level_num)
    room_nums = self._GetRoomNumsForLevel(level_num)

    for room_num in room_nums:
      # Add roars around Gannon/HCs
      room = self._GetRoom(room_num, grid_id)
      if room.GetEnemy() == Enemy.THE_BEAST or room.GetItem() == Item.HEART_CONTAINER:
        room.SetInnerPalette(DungeonPalette.WATER)
        for direction in Range.CARDINAL_DIRECTIONS:
          next_room_num = GetNextRoomNum(room_num, direction)
          if next_room_num in room_nums:
            self._GetRoom(next_room_num, grid_id).SetBossRoarSound(True)
      # Add shutter doors around the kidnapped
      elif room.GetEnemy() == Enemy.THE_KIDNAPPED:
        for direction in Range.CARDINAL_DIRECTIONS:
          if room.GetWallType(direction) == WallType.SOLID_WALL:
            continue
          room.SetWallType(direction, WallType.OPEN_DOOR)
          next_room_num = GetNextRoomNum(room_num, direction)
          if next_room_num in room_nums:
            next_room = self._GetRoom(next_room_num, grid_id)
            next_room.SetRoomAction(RoomAction.KILLING_THE_BEAST_OPENS_SHUTTER_DOORS)
            next_room.SetWallType(direction.Reverse(), WallType.SHUTTER_DOOR)

    if level_num != LevelNum.LEVEL_9:
      return
    room = self._GetRoom(start_room_num, grid_id)

    print("Going to set up level 9 triforce check(s)")
    created_check_room = False
    print("Start room num is %x, entrance dir is %s" % (start_room_num, entrance_dir))
    for direction in Range.CARDINAL_DIRECTIONS:
      print("Trying %s" % direction)
      if direction == entrance_dir:
        print("Nope, entrance")
        continue
      if room.GetWallType(direction) == WallType.SOLID_WALL:
        print("Nope, solid wall")
        continue
      check_room_num = GetNextRoomNum(start_room_num, direction)
      check_room = self._GetRoom(check_room_num, grid_id)
      print("Found a passage to room %x" % check_room_num)
      if (check_room.HasStairs()):
        print("!!Stairs!!")
      if check_room.GetItem() == Item.MAP:
        print("!!Map!!")
      if check_room.GetItem() == Item.COMPASS:
        print("!!Compass!!")
      if check_room.GetEnemy() == Enemy.THE_BEAST:
        print("!!Beast!!")
      if check_room.GetEnemy() == Enemy.THE_KIDNAPPED:
        print("!!Kidnapped!!")

      if (check_room.HasStairs() or check_room.GetItem() == Item.MAP or
          check_room.GetItem() == Item.COMPASS or check_room.GetEnemy() == Enemy.THE_BEAST or
          check_room.GetEnemy() == Enemy.THE_KIDNAPPED):
        print("Failed one of the entry checks")
        continue
      print("Doesn't seem important so turning it into a check room")
      check_room.SetEnemy(Enemy.ELDER)
      check_room.SetItem(Item.NOTHING)
      check_room.SetRoomType(RoomType.ELDER_ROOM)
      check_room.SetRoomAction(RoomAction.KILLING_ENEMIES_OPENS_SHUTTER_DOORS)
      entry_dir = direction.Reverse()
      for direction_2 in Range.CARDINAL_DIRECTIONS:
        if direction_2 != entry_dir and check_room.GetWallType(direction_2) != WallType.SOLID_WALL:
          print("Making %s door in room %x a shutter door" % (direction_2, check_room_num))
          check_room.SetWallType(direction_2, WallType.SHUTTER_DOOR)
      created_check_room = True
    if not created_check_room:
      print("No eligible check room :(")
      sys.exit()
      raise TimeoutException()

  def _RecursivelyVisitRoom(self,
                            level_num: LevelNum,
                            room_num: RoomNum,
                            entry_direction: Direction,
                            rooms_visited: Dict[RoomNum, List[Direction]],
                            factor_in_room_type: bool = False) -> None:
    if room_num in rooms_visited:
      if entry_direction in rooms_visited[room_num]:
        return

      rooms_visited[room_num].append(entry_direction)
    else:
      rooms_visited[room_num] = [entry_direction]
    room = self._GetRoomInLevel(room_num, level_num)
    for exit_direction in Range.CARDINAL_DIRECTIONS:
      if entry_direction == exit_direction:
        continue
      if (factor_in_room_type and not room.GetRoomType().AllowsDoorToDoorMovement(
          entry_direction, exit_direction, has_ladder=True)):
        continue
      if room.GetWallType(exit_direction) != WallType.SOLID_WALL:
        self._RecursivelyVisitRoom(level_num, GetNextRoomNum(room_num, exit_direction),
                                   exit_direction.Reverse(), rooms_visited, factor_in_room_type)

  def AddInteriorWalls(self, level_num: LevelNum) -> None:
    print()
    print("AddInteriorWalls Level %d" % level_num)
    grid_id = GridId.GetGridIdForLevelNum(level_num)

    # 1) Figure out the number of "interior walls" there are (defined as walls that separate two
    # rooms in the level).
    num_interior_walls = 0
    for room_num in Range.VALID_ROOM_NUMBERS:
      east_room = GetNextRoomNum(room_num, Direction.EAST)
      south_room = GetNextRoomNum(room_num, Direction.SOUTH)
      if self._GetLevelNumForRoomNum(room_num, grid_id) == level_num:
        if room_num % 0x10 != 0xF and self._GetLevelNumForRoomNum(east_room, grid_id) == level_num:
          num_interior_walls += 1
        if room_num < 0x70 and self._GetLevelNumForRoomNum(south_room, grid_id) == level_num:
          num_interior_walls += 1

    # 2) Decide on the number of interior walls should be non-open doors. Create a pool of walls
    #    with a random-ish number of each wall types.
    wall_type_pool: List[WallType] = []
    num_bombholes = random.randrange(2, math.floor(num_interior_walls / 5))
    for unused_counter in range(num_bombholes):
      wall_type_pool.append(WallType.BOMB_HOLE)
    num_lockeddoors = random.randrange(2, math.floor(num_interior_walls / 5))
    for unused_counter in range(num_lockeddoors):
      wall_type_pool.append(WallType.LOCKED_DOOR_1)
    num_shutterdoors = random.randrange(2, math.floor(num_interior_walls / 5))
    for unused_counter in range(num_shutterdoors):
      wall_type_pool.append(WallType.SHUTTER_DOOR)
    num_interiorwalls = random.randrange(2, math.floor(num_interior_walls / 5))
    for unused_counter in range(num_interiorwalls):
      wall_type_pool.append(WallType.SOLID_WALL)
    while len(wall_type_pool) < num_interior_walls:
      wall_type_pool.append(WallType.OPEN_DOOR)
    print(wall_type_pool)
    random.shuffle(wall_type_pool)

    # 3) Take each wall type from the pool and assign it to a random interior wall.
    potential_elder_rooms: List[RoomNum] = []
    for room_num in Range.VALID_ROOM_NUMBERS:
      east_room = GetNextRoomNum(room_num, Direction.EAST)
      south_room = GetNextRoomNum(room_num, Direction.SOUTH)

      if self._GetLevelNumForRoomNum(room_num, grid_id) == level_num:
        if room_num % 0x10 != 0xF and self._GetLevelNumForRoomNum(east_room, grid_id) == level_num:
          # Found an interior east-west wall
          wall_type = wall_type_pool.pop()
          self._GetRoom(room_num, grid_id).SetWallType(Direction.EAST, wall_type)
          self._GetRoom(east_room, grid_id).SetWallType(Direction.WEST, wall_type)
        if room_num < 0x70 and self._GetLevelNumForRoomNum(south_room, grid_id) == level_num:
          #print("pop!")
          wall_type = wall_type_pool.pop()
          self._GetRoom(room_num, grid_id).SetWallType(Direction.SOUTH, wall_type)
          self._GetRoom(south_room, grid_id).SetWallType(Direction.NORTH, wall_type)
          potential_elder_rooms.append(south_room)
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
        #print("going %s" % direction)
        self._RecursivelyVisitRoom(level_num, GetNextRoomNum(start_room, direction),
                                   direction.Reverse(), rooms_visited)
    if len(self._GetRoomNumsForLevel(level_num)) != len(rooms_visited):
      print("len(self._GetRoomNumsForLevel(level_num)) %d != len(rooms_visited) %d" %
            (len(self._GetRoomNumsForLevel(level_num)), len(rooms_visited)))
      print("Timeout adding walls")
      raise TimeoutException()

  def AddRoomTypes(self,
                   level_num: LevelNum,
                   item_staircase_room_list: List[RoomNum],
                   transport_staircase_room_list: List[RoomNum],
                   make_room_for_hungry_enemy: bool = False) -> None:
    print("AddRoomTypes Level %d" % level_num)
    assert level_num in Range.VALID_LEVEL_NUMBERS
    grid_id = GridId.GetGridIdForLevelNum(level_num)
    room_type_pool_template: List[RoomType] = []
    num_rooms = len(self._GetRoomNumsForLevel(level_num))
    room_type_pool_template.append(RoomType.ENTRANCE_ROOM)
    room_type_pool_template.append(RoomType.ELDER_ROOM)
    room_type_pool_template.append(RoomType.ELDER_ROOM)
    room_type_pool_template.append(RoomType.ELDER_ROOM)
    for unused_counter in range(len(item_staircase_room_list)):
      room_type_pool_template.append(RoomType.ITEM_STAIRCASE)
    for unused_counter in range(len(transport_staircase_room_list)):
      room_type_pool_template.append(RoomType.TRANSPORT_STAIRCASE)
      room_type_pool_template.append(RoomType.TRANSPORT_STAIRCASE)

    while len(room_type_pool_template) < num_rooms:
      room_type_pool_template.append(RoomType.RandomValue())
    item_stairway_rooms_template = item_staircase_room_list.copy()
    transport_stairway_rooms_template: List[Tuple[RoomNum, Direction]] = []
    for transport_stairway_room in transport_staircase_room_list:
      transport_stairway_rooms_template.append((transport_stairway_room, Direction.WEST))
      transport_stairway_rooms_template.append((transport_stairway_room, Direction.EAST))

    counter = 0
    done = False
    while not done and counter < 100:
      room_type_pool = room_type_pool_template.copy()
      random.shuffle(room_type_pool)
      item_stairway_rooms = item_stairway_rooms_template.copy()
      transport_stairway_room_pool = transport_stairway_rooms_template.copy()
      random.shuffle(transport_stairway_room_pool)

      self.data_table.ClearStaircaseRoomNumbersForLevel(level_num)
      counter += 1
      room_nums = self._GetRoomNumsForLevel(level_num)
      random.shuffle(room_nums)
      for room_num in room_nums:
        print("Outer counter: %d " % counter)
        all_room_type_checks_passed = False
        inner_counter = 0
        while not all_room_type_checks_passed:
          random.shuffle(room_type_pool)
          room = self._GetRoom(room_num, grid_id)
          room.ClearStairsDestination()
          room_type = room_type_pool[0]
          print("  Inner counter: %d " % inner_counter)
          if inner_counter > 100:
            break
          if room_type != RoomType.ENTRANCE_ROOM and room_num == self.level_start_rooms[level_num]:
            inner_counter += 1
            print("Fail b/c of entrance room")
            continue
          #if (room_type != RoomType.ELDER_ROOM and RoomType.ELDER_ROOM in room_type_pool and
          #    not room.HasShutterDoor() and
          #    room.GetWallType(Direction.NORTH) == WallType.SOLID_WALL):
          #  inner_counter += 1
          #  print("Fail b/c need to match elder room first")
          #  continue
          if room_type == RoomType.ELDER_ROOM and room.HasShutterDoor():
            inner_counter += 1
            print("Fail b/c need to match elder -- shutter door")
            continue
          if not make_room_for_hungry_enemy and room_type == RoomType.ELDER_ROOM and room.GetWallType(
              Direction.NORTH) != WallType.SOLID_WALL:
            inner_counter += 1
            print("Fail b/c need solid wall above elder rooms")
            continue
          if room_type == RoomType.T_ROOM:
            if room.GetWallType(Direction.SOUTH) == WallType.SOLID_WALL:
              inner_counter += 1
              print("Fail b/c T room issue")
              continue
            if (room.GetWallType(Direction.WEST) == WallType.SOLID_WALL and
                room.GetWallType(Direction.NORTH) == WallType.SOLID_WALL and
                room.GetWallType(Direction.EAST) == WallType.SOLID_WALL):
              inner_counter += 1
              print("Fail b/c T room issue")
              continue
          if room_type == RoomType.SECOND_QUEST_T_LIKE_ROOM:
            if (room.GetWallType(Direction.WEST) == WallType.SOLID_WALL and
                room.GetWallType(Direction.SOUTH) == WallType.SOLID_WALL):
              inner_counter += 1
              print("Fail b/c 2Q T room issue")
              continue
            if (room.GetWallType(Direction.NORTH) == WallType.SOLID_WALL and
                room.GetWallType(Direction.EAST) == WallType.SOLID_WALL):
              inner_counter += 1
              print("Fail b/c 2Q T room issue")
              continue
          if room_type == RoomType.HORIZONTAL_CHUTE_ROOM:
            if (room.GetWallType(Direction.EAST) == WallType.SOLID_WALL and
                room.GetWallType(Direction.WEST) == WallType.SOLID_WALL):
              inner_counter += 1
              print("Fail b/c Oh chute!")
              continue
          if room_type == RoomType.VERTICAL_CHUTE_ROOM:
            if (room.GetWallType(Direction.NORTH) == WallType.SOLID_WALL and
                room.GetWallType(Direction.SOUTH) == WallType.SOLID_WALL):
              inner_counter += 1
              print("Fail b/c Oh chute!")
              continue

          assert room_type == room_type_pool.pop(0)
          all_room_type_checks_passed = True

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
            room.SetRoomType(RoomType.DIAMOND_STAIR_ROOM)  # Temp fix
            has_solid_east_wall = room.GetWallType(Direction.EAST) == WallType.SOLID_WALL
            room_type = RoomType.RandomValueOkayForStairs(has_solid_east_wall=has_solid_east_wall,
                                                          has_shutters=room.HasShutterDoor())
            room.SetRoomType(room_type)
            stairway_room.SetReturnPosition(
                0x85 if room_type.NeedsOffCenterStairReturnPosition() else 0x89)
            #room.SetActionBits(pushing_block_makes_stairs_appear=True)
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
            room.SetRoomType(RoomType.DIAMOND_STAIR_ROOM)  # Temp fix
            has_solid_east_wall = room.GetWallType(Direction.EAST) == WallType.SOLID_WALL
            room_type = RoomType.RandomValueOkayForStairs(has_solid_east_wall=has_solid_east_wall,
                                                          has_shutters=room.HasShutterDoor())
            room.SetRoomType(room_type)
            stairway_room.SetReturnPosition(
                0x85 if room_type.NeedsOffCenterStairReturnPosition() else 0x89)
            #room.SetActionBits(pushing_block_makes_stairs_appear=True)
            #room.SetItem(Item.NOTHING)
            room.SetInnerPalette(DungeonPalette.WATER)
            # Only want to add this once.
            if ladder_side == Direction.EAST:
              self.data_table.AddStaircaseRoomNumberForLevel(level_num, stairway_room_num)

          room.SetItemPositionCode(self.level_position_dict[room_type])
          if room_type == RoomType.ELDER_ROOM:
            room.SetInnerPalette(DungeonPalette.BLACK_AND_WHITE)
          elif room_type.HasWater() or room_type == RoomType.ENTRANCE_ROOM:
            room.SetInnerPalette(DungeonPalette.WATER)
          elif room.HasStairs():
            room.SetInnerPalette(DungeonPalette.WATER)
          else:
            room.SetInnerPalette(DungeonPalette.PRIMARY)
          room.SetDarkRoomBit(False)
      if len(room_type_pool) == 0:
        done = True
    if not done:
      print("Timeout adding room types")
      raise TimeoutException()

    start_room = self.level_start_rooms[level_num]
    entrance_dir = self.level_entrance_directions[level_num]
    rooms_visited = {}
    rooms_visited[start_room] = Range.CARDINAL_DIRECTIONS.copy()
    print("Start room is %x" % start_room)
    print("Entrance dir is %s" % entrance_dir)

    for direction in Range.CARDINAL_DIRECTIONS:
      if (direction != entrance_dir and
          self._GetRoom(start_room, grid_id).GetWallType(direction) != WallType.SOLID_WALL):
        self._RecursivelyVisitRoom(level_num,
                                   GetNextRoomNum(start_room, direction),
                                   direction.Reverse(),
                                   rooms_visited,
                                   factor_in_room_type=True)

    if len(self._GetRoomNumsForLevel(level_num)) != len(rooms_visited):
      raise TimeoutException()

    print("Add Room Types Success!!!")

  def AddEnemies(self, level_num: LevelNum, elders_list: List[Enemy]) -> None:
    print("Adding Enemies")
    grid_id = GridId.GetGridIdForLevelNum(level_num)
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

    counter = 0
    done = False
    while not done and counter < 200:
      print("Enemy loop")
      counter += 1
      enemy_pool = enemy_pool_template.copy()
      random.shuffle(enemy_pool)
      room_nums = self._GetRoomNumsForLevel(level_num)
      random.shuffle(room_nums)
      for room_num in room_nums:
        room = self._GetRoom(room_num, grid_id)
        room_type = room.GetRoomType()
        all_enemy_checks_passed = False
        inner_counter = 0
        while not all_enemy_checks_passed:
          #print(enemy_pool)
          #          print("inner counter %d" % inner_counter)
          enemy = enemy_pool[0]
          if inner_counter > 200:
            break
          if room_type.IsPartitionedByBlockWalls() and not enemy.CanMoveThroughBlockWalls():
            #print("Fail b/c of enemies that can't move block walls ")
            random.shuffle(enemy_pool)
            inner_counter += 1
            continue
          if room_num == self.level_start_rooms[level_num] and enemy != Enemy.NOTHING:
            #print("Fail b/c of enemies in entrance room")
            random.shuffle(enemy_pool)
            inner_counter += 1
            continue
          if (enemy.RequiresSolidWallToNorth() and
              room.GetWallType(Direction.NORTH) != WallType.SOLID_WALL):
            #print("  Fail b/c there isn't a solid wall over an elder")
            random.shuffle(enemy_pool)
            inner_counter += 1
            continue
          if enemy in [Enemy.BLUE_LANMOLA, Enemy.RED_LANMOLA] and room_type.IsBadForLanmola():
            random.shuffle(enemy_pool)
            inner_counter += 1
            continue
          #if (enemy == Enemy.HUNGRY_ENEMY and
          #    room.GetWallType(Direction.NORTH) == WallType.SOLID_WALL):
          #print("  Fail b/c there is a solid wall over a hungry enemy")
          #  random.shuffle(enemy_pool)
          #  inner_counter += 1
          #  continue
          if enemy.IsElderOrHungryEnemy() and room.HasShutterDoor():
            #print(" Fails b/c of shutter door w/ elder")
            random.shuffle(enemy_pool)
            inner_counter += 1
            continue
          if enemy.RequiresSolidWallToNorth() and room_type != RoomType.ELDER_ROOM:
            #print("  Fail b/c elder not in an elder room")
            random.shuffle(enemy_pool)
            inner_counter += 1
            continue
          if enemy == Enemy.HUNGRY_ENEMY and room_type != RoomType.ELDER_ROOM:
            #print("  Fail b/c of hungry goriya")
            random.shuffle(enemy_pool)
            inner_counter += 1
            continue
          if (enemy.HasTraps() or enemy.HasRedWizzrobes() and room_type.IsBadForTraps()):
            #print("  Fails b/c of traps in a bad room for traps")
            random.shuffle(enemy_pool)
            inner_counter += 1
            continue
          if (enemy.IsBoss() or enemy == Enemy.RUPEE_BOSS) and room_type.IsBadForBosses():
            #print(" Fails b/c bosses are hard enough as is")
            random.shuffle(enemy_pool)
            inner_counter += 1
            continue
          if (enemy.HasBlueWizzrobes() or enemy.IsBoss()) and room_type.HasBeamoses():
            #print("Blue wizzrobes are bad enough as is")
            random.shuffle(enemy_pool)
            inner_counter += 1
            continue
          if enemy != Enemy.NOTHING and room_type == RoomType.TURNSTILE_ROOM:
            #print(" Fails b/c of four-way block room")
            random.shuffle(enemy_pool)
            inner_counter += 1
            continue
          if enemy in [Enemy.PATRA_1, Enemy.PATRA_2] and room_type.IsBadForPatra():
            #print(" Fails b/c of Patra")
            random.shuffle(enemy_pool)
            inner_counter += 1
            continue
          assert enemy == enemy_pool.pop(0)
          print("Enemies left to place: %d" % len(enemy_pool))
          print("Num rooms in level: %d" % len(self._GetRoomNumsForLevel(level_num)))
          print("Inner counter %d" % inner_counter)
          #print("Placing %s in room 0x%x" % (enemy, room_num))
          room.SetEnemy(enemy)
          if enemy == [Enemy.SINGLE_DODONGO, Enemy.TRIPLE_DODONGO]:
            room.SetEnemyQuantityCode(random.randrange(0, 1))
          else:
            room.SetEnemyQuantityCode(random.randrange(0, 3))
          all_enemy_checks_passed = True
      if len(enemy_pool) == 0:
        done = True
    if not done:
      print("Failure adding enemies")
      print(level_num)
      raise TimeoutException()
    print("Add Enemies success. Yay!")
    print()

  def AddItems(self, level_num: LevelNum, major_item_pool_template: List[Item]) -> None:
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
    random.shuffle(minor_item_pool_template)

    #    print(minor_item_pool_template)
    #    for room_num in self._GetRoomNumsForLevel(level_num):
    #      print("Room 0x%x" % room_num)
    #      room = self._GetRoomInLevel(room_num, level_num)
    #      print(room.GetRoomType())
    #      print(room.GetEnemy())
    #    sys.exit()

    counter = 0
    done = False
    while not done and counter < 100:
      counter += 1
      minor_item_pool = minor_item_pool_template.copy()
      major_item_pool = major_item_pool_template.copy()
      random.shuffle(minor_item_pool)
      random.shuffle(major_item_pool)
      room_nums = self._GetRoomNumsForLevel(level_num)
      random.shuffle(room_nums)
      for room_num in room_nums:
        room = self._GetRoomInLevel(room_num, level_num)

        all_item_checks_passed = False
        inner_counter = 0
        entrance_matched = False
        while not all_item_checks_passed:
          random.shuffle(minor_item_pool)
          item = minor_item_pool[0]
          print("inner counter %d" % inner_counter)
          if inner_counter > 100:
            break
          print("room num 0x%x" % room_num)
          #if not entrance_matched and item == Item.NOTHING and room.GetRoomType() != RoomType.ENTRANCE_ROOM:
          #    print("  Fails b/c entrance room doesn't have its nothing yet")
          #    print(minor_item_pool)
          #    print("Level is %d" % level_num)
          #    inner_counter += 1
          #    continue

          #        if room.GetEnemy().IsBoss() and item != Item.HEART_CONTAINER:
          #            print("  Fails b/c boss doesn't have an HC yet")
          #            print("                                                 Level is %d" % level_num)
          #            inner_counter += 1
          #            continue
          if item != Item.NOTHING:
            if room.GetEnemy().IsElderOrHungryEnemy():
              print("  Fails b/c of an item with an Elder or Hungry goriya")
              print(".                                                Level is %d" % level_num)
              inner_counter += 1
              continue
            if room.GetRoomType() in [RoomType.ENTRANCE_ROOM, RoomType.TURNSTILE_ROOM]:
              print("  Fails b/c of an item in the entrance room")
              inner_counter += 1
              continue
          if item == Item.HEART_CONTAINER and not room.GetEnemy().IsBoss():
            print("  Fails b/c of a HC not in a boss room")
            inner_counter += 1
            continue
          assert item == minor_item_pool.pop(0)
          all_item_checks_passed = True
          room.SetItem(item)
          if room.GetRoomType() == RoomType.ENTRANCE_ROOM:
            entranced_matched = True

          if room.HasStairs():
            staircase_room_num = room.GetStairsDestination()
            staircase_room = self._GetRoomInLevel(staircase_room_num, level_num)
            if staircase_room.IsItemStaircase():
              staircase_room.SetItem(major_item_pool.pop(0))
            else:
              staircase_room.SetItem(Item.NOTHING)
          if room.HasStairs() and room.GetRoomType() == RoomType.DIAMOND_STAIR_ROOM:
            if item != Item.NOTHING and random.choice([True, False]):
              room.SetRoomAction(
                  RoomAction.KILLING_ENEMIES_OPENS_SHUTTER_DOORS_DROPS_ITEM_AND_MAKES_BLOCK_PUSHABLE
              )
            else:
              room.SetRoomAction(RoomAction.PUSHABLE_BLOCK_OPENS_SHUTTER_DOORS)
          elif room.HasStairs() and not room.GetRoomType().HasUnobstructedStairs():
            #print(room.GetRoomType())
            assert not room.HasShutterDoor()
            room.SetRoomAction(RoomAction.PUSHABLE_BLOCK_MAKES_STAIRS_APPEAR)
            #print("Level %d Room %x: pushing_block_makes_stairs_appear" % (level_num, room_num))
          elif item != Item.NOTHING and (item == Item.HEART_CONTAINER or
                                         random.choice([True, False])):
            room.SetRoomAction(RoomAction.KILLING_ENEMIES_OPENS_SHUTTER_DOORS_AND_DROPS_ITEM)
            #print("Level %d Room %x: killing_enemies_opens_shutters_and_drops_item" %
            #      (level_num, room_num))
          elif room.HasShutterDoor():
            if room.GetRoomType().CanHavePushBlock():
              room.SetRoomAction(RoomAction.PUSHABLE_BLOCK_OPENS_SHUTTER_DOORS)
              #print("Level %d Room %x: pushing_block_opens_shutters" % (level_num, room_num))
            else:
              room.SetRoomAction(RoomAction.KILLING_ENEMIES_OPENS_SHUTTER_DOORS)
              #print("Level %d Room %x: killing_enemies_opens_shutters" % (level_num, room_num))
          else:
            room.SetRoomAction(RoomAction.NO_ROOM_ACTION)
            #print("Level %d Room %x: no_action" % (level_num, room_num))
          if room.GetRoomType() == RoomType.TURNSTILE_ROOM:
            room.SetRoomAction(RoomAction.PUSHABLE_BLOCK_OPENS_SHUTTER_DOORS)

          if item == Item.TRIFORCE or room.GetEnemy() == Enemy.THE_KIDNAPPED:
            #print(room_num)
            assert not room.IsItemStaircase()
            self.data_table.UpdateCompassPointer(Location(level_num=level_num, room_num=room_num))

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

      if len(minor_item_pool) == 0:
        done = True
    if not done:
      print("Failure placing items level %d" % (level_num))
      #sys.exit()
      raise TimeoutException()
    print("Num items left over: %d" % len(minor_item_pool))
    assert len(minor_item_pool) == 0
