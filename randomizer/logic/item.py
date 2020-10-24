from enum import IntEnum
from typing import Dict
import random


class Item(IntEnum):
  BOMBS = 0x00
  WOOD_SWORD = 0x01
  WHITE_SWORD = 0x02
  MAGICAL_SWORD = 0x03
  BAIT = 0x04
  RECORDER = 0x05
  BLUE_CANDLE = 0x06
  RED_CANDLE = 0x07
  WOOD_ARROWS = 0x08
  SILVER_ARROWS = 0x09
  BOW = 0x0A
  MAGICAL_KEY = 0x0B
  RAFT = 0x0C
  LADDER = 0x0D
  NOTHING = 0x0E
  FIVE_RUPEES = 0x0F
  WAND = 0x10
  BOOK = 0x11
  BLUE_RING = 0x12
  RED_RING = 0x13
  POWER_BRACELET = 0x14
  LETTER = 0x15
  COMPASS = 0x16
  MAP = 0x17
  RUPEE = 0x18
  KEY = 0x19
  HEART_CONTAINER = 0x1A
  TRIFORCE = 0x1B
  MAGICAL_SHIELD = 0x1C
  BOOMERANG = 0x1D
  MAGICAL_BOOMERANG = 0x1E
  BLUE_POTION = 0x1F
  RED_POTION = 0x20
  CLOCK = 0x21
  SINGLE_HEART = 0x22
  FAIRY = 0x23
  OVERWORLD_NO_ITEM = 0x3F
  # Not actual codes -- only for Inventory class
  TRIFORCE_OF_POWER_PLACEHOLDER_ITEM = 0x3D
  KIDNAPPED_PLACEHOLDER_ITEM = 0x3E

  def GetHintText(self) -> str:
    return {
        Item.BLUE_CANDLE: "FIRE IGNITER",
        Item.RECORDER: "MELODY MAKER",
        Item.BOOK: "LOVELY BOOK TO READ",
        Item.BOW: "TOOL FOR ARCHERY",
        Item.WOOD_ARROWS: "POINTY PROJECTILE",
        Item.SILVER_ARROWS: "POINTY PROJECTILE",
        Item.MAGICAL_KEY: "LOCKED DOOR OPENER",
        Item.LETTER: "POTION PRESCRIPTION",
        Item.WAND: "MAGICAL WEAPON",
        Item.RAFT: "FLOATATION DEVICE",
        Item.LADDER: "WATER STEPPING TOOL",
        Item.WOOD_SWORD: "NEW FENCING WEAPON",
        Item.POWER_BRACELET: "STRENGTHENING DEVICE",
        Item.BLUE_RING: "JEWEL OF PROTECTION",
        Item.RED_RING: "JEWEL OF PROTECTION",
        Item.BOOMERANG: "MIGHTY BANANA",
        Item.MAGICAL_BOOMERANG: "MIGHTY BANANA",
        Item.BAIT: "GORIYA'S LIGHT SNACK",
        Item.MAGICAL_SHIELD: "HARDENED BARRIER",
    }[self]

  def GetLetterCaveText(self) -> str:
    return {
        Item.BLUE_CANDLE: "ONLY YOU|CAN PREVENT|FOREST FIRES",
        Item.RECORDER: "ONE TOOT ON THIS|WHISTLE WILL TAKE YOU|TO A FAR AWAY LAND",
        Item.BOOK: "PLEASE RETURN THIS|TO YOUR LOCAL LIBRARY",
        Item.BOW: "Archers give|gifts tied|with a bow.",
        Item.WOOD_ARROWS: "THIS ONE IS FREE|BUT THE REST|WILL COST YA",
        Item.MAGICAL_KEY: "THIS SHOULD|NEVER HAPPEN",
        Item.LETTER: "HEY EVERYONE!|I GOT PAPER!",
        Item.WAND: "WANDERFUL",
        Item.RAFT: "SAIL AWAY|SAIL AWAY|SAIL AWAY",
        Item.LADDER: "MIND THE GAP!",
        Item.WOOD_SWORD: "DID SOMEBODY SAY ...|WOOD?",
        Item.POWER_BRACELET: "DO YOU EVEN LIFT?",
        Item.BLUE_RING: "IF YOU LIKED IT|THEN YOU SHOULD HAVE|PUT A RING ON IT|",
        Item.RED_RING: "IF YOU LIKED IT|THEN YOU SHOULD HAVE|PUT A RING ON IT|",
        Item.BOOMERANG: "RING RING RING|RING RING ...|BANANAPHONE!",
        Item.BAIT: "MEAT ON A STICK!|GET IT WHILE IT'S|STILL ON A STICK!",
        Item.MAGICAL_SHIELD: "BE CAREFUL!|LIKE LIKES REALLY,|LIKE, LIKE THIS",
        Item.HEART_CONTAINER: "YOU GOTTA|HAVE HEART",
    }[self]

  def GetShortNameDict(self) -> Dict["Item", str]:
    return {Item.NOTHING: "No Item"}

  def GetShortName(self) -> str:
    try:
      return self.GetShortNameDict()[self]
    except KeyError:
      return self.name[0:10]

  def IsMajorItem(self) -> bool:
    return self in [
        Item.WOOD_SWORD,
        Item.WHITE_SWORD,
        Item.MAGICAL_SWORD,
        Item.BLUE_CANDLE,
        Item.WOOD_ARROWS,
        Item.RAFT,
        Item.LADDER,
        Item.RECORDER,
        Item.WAND,
        Item.RED_CANDLE,
        Item.SILVER_ARROWS,
        Item.BOW,
        Item.MAGICAL_KEY,
        Item.BOOK,
        Item.BLUE_RING,
        Item.RED_RING,
        Item.POWER_BRACELET,
        Item.LETTER,
        Item.HEART_CONTAINER,
        Item.BOOMERANG,
        Item.MAGICAL_BOOMERANG,
        Item.BAIT,
        Item.MAGICAL_SHIELD,
    ]

  def IsAnIncrementalUpgradeItem(self) -> bool:
    return self in [
        Item.WOOD_SWORD,
        Item.WHITE_SWORD,
        Item.MAGICAL_SWORD,
        Item.BLUE_CANDLE,
        Item.RED_CANDLE,
        Item.WOOD_ARROWS,
        Item.SILVER_ARROWS,  # Item.BLUE_RING, Item.RED_RING, 
        Item.BOOMERANG,
        Item.MAGICAL_BOOMERANG
    ]

  def IsSwordOrWand(self) -> bool:
    return self in [Item.WOOD_SWORD, Item.WHITE_SWORD, Item.MAGICAL_SWORD, Item.WAND]


class BorderType(IntEnum):
  #STUN_ONLY_ENEMY_BOOMERANG_BLOCK = 0x1D
  NO_BORDER_TYPE = 0x00
  BOMB_HOLE = 0x16
  MINI_BOSS = 0x02
  BOSS = 0x03
  LADDER_BLOCK = 0x0D
  LOCKED_DOOR = 0x19
  BAIT_BLOCK = 35
  BOOMERANG_BLOCK = 36,
  CANDLE_BLOCK = 37,
  BOW_BLOCK = 38,
  RECORDER_BLOCK = 39,
  WAND_BLOCK = 40,
  POWER_BRACELET_BLOCK = 41
  TRIFORCE_CHECK = 9
  TRIFORCE_ROOM = 123
  THE_KIDNAPPED = 99
  THE_BEAST = 100
  MUGGER = 43

  def CanBeTransportStaircaseBorder(self) -> bool:
    return self in [
        BorderType.MINI_BOSS, BorderType.BOOMERANG_BLOCK, BorderType.CANDLE_BLOCK,
        BorderType.BOW_BLOCK, BorderType.RECORDER_BLOCK, BorderType.WAND_BLOCK
    ]
