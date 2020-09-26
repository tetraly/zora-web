import random
from typing import List
from .constants import LevelNum, Range, RoomNum, WallType
from .direction import Direction
from .data_table import DataTable


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

    new_direction_pool.extend([random.choice([Direction.EAST, Direction.WEST])])

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
