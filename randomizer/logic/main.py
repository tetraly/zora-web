import random
from typing import List

from .data_table import DataTable
from .dungeon_generator import DungeonGenerator
from .item_randomizer import ItemRandomizer, NotAllItemsWereShuffledAndIDontKnowWhyException
from .level_generator import LevelGenerator
from .patch import Patch
from .settings import Settings
from .text_data_table import TextDataTable
from .validator import Validator
from . import flags

VERSION = '1.0'


class ZoraRandomizer():

  def __init__(self, seed: int, settings: Settings) -> None:
    self.seed = seed
    self.settings = settings
    self.data_table = DataTable()
    self.level_generator = LevelGenerator(self.data_table)
    self.item_randomizer = ItemRandomizer(self.data_table, self.settings)
    self.validator = Validator(self.data_table, self.settings)

  def Randomize(self) -> None:
    random.seed(self.seed)

    done = False
    while not done:
      self.data_table.ResetToVanilla()
      self.dungeon_generator = DungeonGenerator(self.data_table)
      self.dungeon_generator.Generate()
      random.seed(12345)
      counter = 0
      while True:
        counter += 1
        print()
        print("Re-randomizing items")
        print()
        try:
          self.item_randomizer.Randomize()
        except NotAllItemsWereShuffledAndIDontKnowWhyException:
          print("NotAllItemsWereShuffledAndIDontKnowWhyException")
          break
        print()
        print("Back to Validating")
        print()
        if self.validator.IsSeedValid():
          done = True
          break
        if counter > 1000:
          break

  def OldRandomize(self) -> None:
    random.seed(self.seed)

    done = False
    while not done:
      self.data_table.ResetToVanilla()
      self.level_generator = LevelGenerator(self.data_table)
      self.level_generator.Generate()

      counter = 0
      while True:
        counter += 1
        print()
        print("Re-randomizing items")
        print()
        try:
          self.item_randomizer.Randomize()
        except NotAllItemsWereShuffledAndIDontKnowWhyException:
          print("NotAllItemsWereShuffledAndIDontKnowWhyException")
          break
        print()
        print("Back to Validating")
        print()
        if self.validator.IsSeedValid():
          done = True
          break
        if counter > 100:
          break

  def GetPatch(self) -> Patch:
    patch = self.data_table.GetPatch()

    # Turn off low health warning
    patch.AddData(0x1ED33, [0x00])

    # Make rare (vanilla blue ring) shop single purchase only
    patch.AddData(0x45F3, [0x7A])

    # Disable triforce flashing
    patch.AddData(0x1A283, [0x18])
    # Disable bomb explosion flashing
    patch.AddData(0x6A3B, [0x60])

    # Auto-"use" the letter the first time entering a potion shop
    patch.AddData(0x4708, [0xEA, 0xEA, 0xEA, 0xEA, 0xEA, 0xEA, 0xAD, 0x66, 0x06, 0xC9, 0x01, 0xF0])

    # Randomize secret prices
    patch.AddData(0x18680, [random.randrange(25, 40)])
    patch.AddData(0x18683, [random.randrange(80, 125)])
    patch.AddData(0x18686, [random.randrange(5, 24)])
    # Door repair
    patch.AddData(0x48A0, [random.randrange(15, 25)])

    # Ropes.  DF = Burn only. Overwrite 2nd quest stuff w/ NOPs
    # patch.AddData(0x112D7, [0xA9, 0xDF, 0x99, 0xB3, 0x04, 0xEA, 0xEA, 0xEA, 0xEA, 0xEA, 0xEA, 0xEA])

    # Make red/black keese boomerang-only
    patch.AddData(0x10448, [0xA9, 0xFD, 0x99, 0xB3, 0x04])

    # A9 E2      LDA #$E2. -- E2 is damage types
    # 99 B3 04   STA $04B3,Y

    # Manhandala's damage type bit. Vanilla E2. Make wand only
    patch.AddData(0x12138, [0xEF])

    # Temporary L2 PB change
    patch.AddData(0x14C90, [0xAD, 0x65, 0x06, 0xD0, 0xA4])

    # For fast scrolling. Puts NOPs instead of branching based on dungeon vs. Level 0 (OW)
    for addr in [0x141F3, 0x1426B, 0x1446B, 0x14478, 0x144AD]:
      patch.AddData(addr, [0xEA, 0xEA])

    zeros: List[int] = []
    for unused_counter in range(0x26):
      zeros.append(0x00)
    patch.AddData(0x1FB5E, zeros)

    patch.AddData(0x16fd8, [
        0xFF, 0xA5, 0xEC, 0x30, 0x0B, 0x49, 0x80, 0xCD, 0xA1, 0x6B, 0xD0, 0x09, 0xA4, 0x10, 0xF0,
        0x05, 0x85, 0xEC, 0x4C, 0x47, 0xB5, 0x4C, 0x59, 0xB5, 0xAC, 0xBB, 0x6B, 0xB9, 0xF1, 0xAF,
        0x85, 0x98, 0xB9, 0xF6, 0xAF, 0x85, 0x70, 0xB9, 0xFB, 0xAF, 0x60, 0x00, 0x04, 0x08, 0x01,
        0x02, 0x78, 0x78, 0x78, 0x00, 0xF0, 0x8D, 0x3D, 0xDD, 0x8D, 0x8D
    ])
    patch.AddData(0x17058, [0xA9, 0x78, 0x85, 0x70, 0x20, 0xE0, 0xAF, 0x85])
    patch.AddData(0x17550, [0x20, 0xC0, 0xB8, 0x4C, 0xC9, 0xAF, 0x12, 0x20])
    patch.AddData(0x178D0, [0xAD, 0x22, 0x05, 0xC9, 0x01, 0xF0, 0x03, 0x4C, 0x2F, 0x75, 0x60])
    patch.AddData(0x1934D, [0x00])

    # Fix for ganon triforce
    #patch.AddData(0x6BFB, [0x20, 0xE4, 0xFF])
    #patch.AddData(0x1FFF4, [0x8E, 0x02, 0x06, 0x8E, 0x72, 0x06, 0xEE, 0x4F, 0x03, 0x60])

    self._AddExtras(patch)
    return patch

  def _AddExtras(self, patch: Patch) -> None:
    if self.settings.IsEnabled(flags.ProgressiveItems):

      patch.AddData(0x6D06, [0x18, 0x79, 0x57, 0x06, 0xEA])
      #patch.AddData(0x6B49, [0x11, 0x12, 0x13])  # Swords
      #patch.AddData(0x6B4E, [0x11, 0x12])  # Candles
      #patch.AddData(0x6B50, [0x11, 0x12])  # Arrows
      # patch.AddData(0x6B5A, [0x11, 0x12])  # Rings
      #patch.AddData(0x6B65, [0x11, 0x12])  # Boomerangs

    # Change "no item" code from 0x03 (Mags) to 0x0E (Triforce of Power)
    patch.AddData(0x1785F, [0x0E])

    # Include everything above in the hash code.
    hash_code = patch.GetHashCode()
    patch.AddData(0xAFD0, hash_code)
    patch.AddData(0xA4CD, [0x4C, 0x90, 0xAF])
    patch.AddData(0xAFA0, [
        0xA2, 0x0A, 0xA9, 0xFF, 0x95, 0xAC, 0xCA, 0xD0, 0xFB, 0xA2, 0x04, 0xA0, 0x60, 0xBD, 0xBF,
        0xAF, 0x9D, 0x44, 0x04, 0x98, 0x69, 0x1B, 0xA8, 0x95, 0x70, 0xA9, 0x20, 0x95, 0x84, 0xA9,
        0x00, 0x95, 0xAC, 0xCA, 0xD0, 0xE9, 0x20, 0x9D, 0x97, 0xA9, 0x14, 0x85, 0x14, 0xE6, 0x13,
        0x60, 0xFF, 0xFF, 0x1E, 0x0A, 0x06, 0x01
    ])

    #Ring fix (TODO)
    #  patch.AddData(0x6C71, [0x4C, 0xD8, 0xFF])
    #  patch.AddData(0x1FFE8, [0x4C, 0xB5, 0x73])

    # What does this do?
    patch.AddData(
        0x1A129,
        [0x0C, 0x18, 0x0D, 0x0E, 0x24, 0x24, 0x24, 0x24, 0x24, 0x24, 0x24, 0x24, 0x24, 0x24, 0x24])

    if self.settings.IsEnabled(flags.SelectSwap):
      patch.AddData(0x1EC4C, [0x4C, 0xC0, 0xFF])
      patch.AddData(0x1FFD0, [
          0xA9, 0x05, 0x20, 0xAC, 0xFF, 0xAD, 0x56, 0x06, 0xC9, 0x0F, 0xD0, 0x02, 0xA9, 0x07, 0xA8,
          0xA9, 0x01, 0x20, 0xC8, 0xB7, 0x4C, 0x58, 0xEC
      ])

    text_data_table = TextDataTable(self.settings, self.data_table)
    patch += text_data_table.GetPatch()
