from enum import IntEnum
from typing import Dict
import random
from .constants import SpriteSet


class Enemy(IntEnum):
  NO_ENEMY = 0x00
  BLUE_GORIYA = 0x05
  RED_GORIYA = 0x06
  RED_DARKNUT = 0x0B
  BLUE_DARKNUT = 0x0C
  VIRE = 0x12
  ZOL = 0x13
  GEL_1 = 0x14
  GEL_2 = 0x15
  POLS_VOICE = 0x16
  LIKE_LIKE = 0x17
  BLUE_KEESE = 0x1B
  RED_KEESE = 0x1C
  DARK_KEESE = 0x1D
  RED_WIZZROBE = 0x23
  BLUE_WIZZROBE = 0x24
  WALLMASTER = 0x27
  ROPE = 0x28
  STALFOS = 0x2A
  BUBBLE = 0x2B
  GIBDO = 0x30
  TRIPLE_DODONGO = 0x31
  SINGLE_DODONGO = 0x32
  BLUE_GOHMA = 0x33
  RED_GOHMA = 0x34
  RUPEE_BOSS = 0x35
  HUNGRY_ENEMY = 0x36
  THE_KIDNAPPED = 0x37
  TRIPLE_DIGDOGGER = 0x38
  SINGLE_DIGDOGGER = 0x39
  RED_LANMOLA = 0x3A
  BLUE_LANMOLA = 0x3B
  MANHANDALA = 0x3C
  AQUAMENTUS = 0x3D
  THE_BEAST = 0x3E
  MINI_DIGDOGGER = 0x18

  BLUE_LYNEL = 0x01
  RED_LYNEL = 0x02
  BLUE_MOBLIN = 0x03
  RED_MOBLIN = 0x04
  RED_OCTOROK = 0x07
  FAST_RED_OCTOROK = 0x08
  BLUE_OCTOROK = 0x09
  FAST_BLUE_OCTOROK = 0x0A
  BLUE_TEKTITE = 0x0D
  RED_TEKTITE = 0x0E
  BLUE_LEEVER = 0x0F
  RED_LEEVER = 0x10
  ZOLA = 0x11
  PEAHAT = 0x1A
  GHINI_MAIN = 0x21
  GHINI_SECONDARY = 0x22
  FAIRY = 0x2F

  # Start of "mixed" enemy types
  MOLDORM = 0x41
  GLEEOK_1 = 0x42
  GLEEOK_2 = 0x43
  GLEEOK_3 = 0x44
  GLEEOK_4 = 0x45
  PATRA_2 = 0x47
  PATRA_1 = 0x48
  THREE_PAIRS_OF_TRAPS = 0x49
  CORNER_TRAPS = 0x4A
  ELDER = 0x4B
  ELDER_2 = 0x4C
  ELDER_3 = 0x4D
  ELDER_4 = 0x4E
  BOMB_UPGRADER = 0x4F
  ELDER_6 = 0x50
  MUGGER = 0x51
  ELDER_8 = 0x52
  ZOL_TRAPS = 0x6D
  ZOL_KEESE = 0x6F
  KEESE_TRAPS = 0x6E
  POLS_VOICE_GIBDO_KEESE = 0x70
  BLUE_WIZZROBE_RED_WIZZROBE_BUBBLE = 0x71
  VIRE_BUBBLE = 0x72
  LIKE_LIKE_ZOL_BUBBLE = 0x73
  BLUE_DARKNUT_RED_DARKNUT_GORIYA_BUBBLE = 0x74
  BLUE_GORIYA_KEESE_BUBBLE = 0x75
  LIKE_LIKE_TRAPS = 0x76
  BLUE_WIZZROBE_RED_WIZZROBE_TRAPS = 0x77
  BLUE_DARKNUT_RED_DARKNUT_POLS_VOICE = 0x78
  WALLMASTER_BUBBLE = 0x79
  BLUE_GORIYA_RED_GORIYA = 0x7A
  BLUE_WIZZROBE_RED_WIZZROBE = 0x7B
  BLUE_WIZZROBE_LIKE_LIKE_BUBBLE = 0x7C
  # DEPRECATED -- DO NOT USE
  TRIFORCE_CHECKER_PLACEHOLDER_ELDER = 0x7F

  def GetShortNameDict(self) -> Dict["Enemy", str]:
    return {Enemy.NO_ENEMY: "No Enemies"}

  def GetShortName(self) -> str:
    try:
      return self.GetShortNameDict()[self]
    except KeyError:
      return self.name[0:10]

  def IsInOverworldSpriteSet(self) -> bool:
    return self in [
        Enemy.BLUE_LYNEL,
        Enemy.RED_LYNEL,
        Enemy.BLUE_MOBLIN,
        Enemy.RED_MOBLIN,
        Enemy.RED_OCTOROK,
        Enemy.FAST_RED_OCTOROK,
        Enemy.BLUE_OCTOROK,
        Enemy.FAST_BLUE_OCTOROK,
        Enemy.BLUE_TEKTITE,
        Enemy.RED_TEKTITE,
        Enemy.BLUE_LEEVER,
        Enemy.RED_LEEVER,  # Enemy.ZOLA, Enemy.PEAHAT,
        #Enemy.FALLING_ROCK_GENERATOR,
        Enemy.GHINI_MAIN  #, Enemy.GHINI_SECONDARY, Enemy.FAIRY
    ]

  def HasBubbles(self) -> bool:
    return self in [
        Enemy.BLUE_WIZZROBE_RED_WIZZROBE_BUBBLE, Enemy.BLUE_DARKNUT_RED_DARKNUT_GORIYA_BUBBLE,
        Enemy.BLUE_GORIYA_KEESE_BUBBLE, Enemy.WALLMASTER_BUBBLE,
        Enemy.BLUE_WIZZROBE_LIKE_LIKE_BUBBLE
    ]

  def CanMoveThroughBlockWalls(self) -> bool:
    return self in [
        Enemy.NO_ENEMY, Enemy.VIRE, Enemy.POLS_VOICE, Enemy.BLUE_KEESE, Enemy.RED_KEESE,
        Enemy.DARK_KEESE, Enemy.RED_WIZZROBE, Enemy.WALLMASTER, Enemy.BUBBLE, Enemy.CORNER_TRAPS,
        Enemy.KEESE_TRAPS, Enemy.VIRE_BUBBLE, Enemy.WALLMASTER_BUBBLE
    ]

  def HasTraps(self) -> bool:
    return self in [
        Enemy.THREE_PAIRS_OF_TRAPS, Enemy.CORNER_TRAPS, Enemy.ZOL_TRAPS, Enemy.LIKE_LIKE_TRAPS,
        Enemy.KEESE_TRAPS, Enemy.BLUE_WIZZROBE_RED_WIZZROBE_TRAPS
    ]

  def IsDigdogger(self) -> bool:
    return self in [Enemy.SINGLE_DIGDOGGER, Enemy.TRIPLE_DIGDOGGER]

  def IsGohma(self) -> bool:
    return self in [Enemy.RED_GOHMA, Enemy.BLUE_GOHMA]

  def HasWizzrobes(self) -> bool:
    return self in [
        Enemy.RED_WIZZROBE, Enemy.BLUE_WIZZROBE, Enemy.BLUE_WIZZROBE_RED_WIZZROBE_BUBBLE,
        Enemy.BLUE_WIZZROBE_RED_WIZZROBE_TRAPS, Enemy.BLUE_WIZZROBE_RED_WIZZROBE,
        Enemy.BLUE_WIZZROBE_LIKE_LIKE_BUBBLE
    ]

  def HasPolsVoice(self) -> bool:
    return self in [
        Enemy.POLS_VOICE, Enemy.POLS_VOICE_GIBDO_KEESE, Enemy.BLUE_DARKNUT_RED_DARKNUT_POLS_VOICE
    ]

  def HasHardCombatEnemies(self) -> bool:
    return self in [
        Enemy.GLEEOK_1, Enemy.GLEEOK_2, Enemy.GLEEOK_3, Enemy.GLEEOK_4, Enemy.PATRA_1,
        Enemy.PATRA_2, Enemy.BLUE_DARKNUT, Enemy.BLUE_DARKNUT_RED_DARKNUT_GORIYA_BUBBLE,
        Enemy.BLUE_DARKNUT_RED_DARKNUT_POLS_VOICE, Enemy.BLUE_WIZZROBE,
        Enemy.BLUE_WIZZROBE_RED_WIZZROBE_BUBBLE, Enemy.BLUE_WIZZROBE_RED_WIZZROBE_TRAPS,
        Enemy.BLUE_WIZZROBE_RED_WIZZROBE, Enemy.BLUE_WIZZROBE_LIKE_LIKE_BUBBLE, Enemy.BLUE_LANMOLA
    ]

  def HasSwordOrWandRequiredEnemies(self) -> bool:
    return self in [
        Enemy.GLEEOK_1, Enemy.GLEEOK_2, Enemy.GLEEOK_3, Enemy.GLEEOK_4, Enemy.PATRA_1,
        Enemy.PATRA_2, Enemy.RED_DARKNUT, Enemy.BLUE_DARKNUT,
        Enemy.BLUE_DARKNUT_RED_DARKNUT_GORIYA_BUBBLE, Enemy.BLUE_DARKNUT_RED_DARKNUT_POLS_VOICE
    ]

  def HasOnlyZeroHPEnemies(self) -> bool:
    return self in [
        Enemy.GEL_1, Enemy.GEL_2, Enemy.BLUE_KEESE, Enemy.RED_KEESE, Enemy.DARK_KEESE,
        Enemy.KEESE_TRAPS
    ]

  #TODO: Need to add more other ELDERs here
  def HasNoEnemiesToKill(self) -> bool:
    return self in [
        Enemy.BUBBLE, Enemy.THREE_PAIRS_OF_TRAPS, Enemy.CORNER_TRAPS, Enemy.THE_KIDNAPPED, Enemy.NO_ENEMY
    ]

  def IsInGoriyaSpriteSet(self) -> bool:
    return self in [
        Enemy.BLUE_GORIYA, Enemy.RED_GORIYA, Enemy.WALLMASTER, Enemy.ROPE, Enemy.STALFOS,
        Enemy.WALLMASTER_BUBBLE, Enemy.BLUE_GORIYA_KEESE_BUBBLE, Enemy.BLUE_GORIYA_RED_GORIYA
    ]

  def IsInDarknutSpriteSet(self) -> bool:
    return self in [
        Enemy.ZOL, Enemy.ZOL_TRAPS, Enemy.ZOL_KEESE, Enemy.RED_DARKNUT, Enemy.BLUE_DARKNUT,
        Enemy.POLS_VOICE, Enemy.GIBDO, Enemy.POLS_VOICE_GIBDO_KEESE,
        Enemy.BLUE_DARKNUT_RED_DARKNUT_GORIYA_BUBBLE, Enemy.BLUE_DARKNUT_RED_DARKNUT_POLS_VOICE
    ]

  def IsInWizzrobeSpriteSet(self) -> bool:
    return self in [
        Enemy.ZOL,
        Enemy.ZOL_TRAPS,
        Enemy.ZOL_KEESE,
        Enemy.VIRE,
        Enemy.LIKE_LIKE,
        Enemy.RED_WIZZROBE,
        Enemy.BLUE_WIZZROBE,
        Enemy.VIRE_BUBBLE,
        Enemy.LIKE_LIKE_ZOL_BUBBLE,
        Enemy.LIKE_LIKE_TRAPS,
        Enemy.BLUE_WIZZROBE_RED_WIZZROBE_TRAPS,
        Enemy.BLUE_WIZZROBE_LIKE_LIKE_BUBBLE,
        Enemy.BLUE_WIZZROBE_RED_WIZZROBE_BUBBLE,
        Enemy.BLUE_WIZZROBE_RED_WIZZROBE,
        Enemy.RED_LANMOLA,
        Enemy.BLUE_LANMOLA,
    ]

  def HasRedWizzrobes(self) -> bool:
    return self in [
        Enemy.RED_WIZZROBE, Enemy.BLUE_WIZZROBE_RED_WIZZROBE_BUBBLE,
        Enemy.BLUE_WIZZROBE_RED_WIZZROBE, Enemy.BLUE_WIZZROBE_RED_WIZZROBE_TRAPS
    ]

  def HasBlueWizzrobes(self) -> bool:
    return self in [
        Enemy.BLUE_WIZZROBE, Enemy.BLUE_WIZZROBE_RED_WIZZROBE_TRAPS,
        Enemy.BLUE_WIZZROBE_LIKE_LIKE_BUBBLE, Enemy.BLUE_WIZZROBE_RED_WIZZROBE_BUBBLE,
        Enemy.BLUE_WIZZROBE_RED_WIZZROBE
    ]

  def IsElder(self) -> bool:
    return self in [
        Enemy.ELDER, Enemy.ELDER_2, Enemy.ELDER_3, Enemy.ELDER_4, Enemy.BOMB_UPGRADER,
        Enemy.ELDER_6, Enemy.MUGGER, Enemy.ELDER_8
    ]

  def IsElderOrHungryEnemy(self) -> bool:
    return self.IsElder() or self == Enemy.HUNGRY_ENEMY

  def IsBoss(self) -> bool:
    return self.IsInDodongoSpriteSet() or self.IsInGleeokSpriteSet() or self.IsInPatraSpriteSet(
    ) or self in [Enemy.RED_LANMOLA, Enemy.BLUE_LANMOLA]

  def IsInDodongoSpriteSet(self) -> bool:
    return self in [
        Enemy.TRIPLE_DODONGO, Enemy.SINGLE_DODONGO, Enemy.TRIPLE_DIGDOGGER, Enemy.SINGLE_DIGDOGGER,
        Enemy.AQUAMENTUS, Enemy.MOLDORM
    ]

  def IsInGleeokSpriteSet(self) -> bool:
    return self in [
        Enemy.BLUE_GOHMA, Enemy.RED_GOHMA, Enemy.MANHANDALA, Enemy.GLEEOK_1, Enemy.GLEEOK_2,
        Enemy.GLEEOK_3, Enemy.GLEEOK_4
    ]

  def IsGleeok(self) -> bool:
    return self in [Enemy.GLEEOK_1, Enemy.GLEEOK_2, Enemy.GLEEOK_3, Enemy.GLEEOK_4]

  def IsInPatraSpriteSet(self) -> bool:
    return self in [Enemy.PATRA_2, Enemy.PATRA_1]

  def IsInAllSpriteSets(self) -> bool:
    return self in [
        Enemy.GEL_1, Enemy.GEL_2, Enemy.BLUE_KEESE, Enemy.RED_KEESE, Enemy.DARK_KEESE, Enemy.BUBBLE,
        Enemy.RUPEE_BOSS, Enemy.THREE_PAIRS_OF_TRAPS, Enemy.CORNER_TRAPS, Enemy.KEESE_TRAPS
    ]

  def IsWandOnly(self) -> bool:
    return self == Enemy.MANHANDALA

  def IsFireOnly(self) -> bool:
    return self in [Enemy.ROPE]

  def IsBoomerangOnly(self) -> bool:
    return self in [Enemy.RED_KEESE, Enemy.DARK_KEESE]

  @classmethod
  def RandomEnemyOkayForSpriteSet(cls,
                                  sprite_set: SpriteSet,
                                  must_be_in_sprite_set: bool = False,
                                  must_be_harder_enemy: bool = False) -> "Enemy":
    while True:
      try:
        enemy = cls(random.randrange(0x0, 0x7F))
      except ValueError:
        continue
      if enemy.HasTraps() and random.choice([True, True, True, True, True, True, True, False]):
        continue

      if ((not must_be_in_sprite_set and enemy.IsInAllSpriteSets()) or
          (sprite_set == SpriteSet.GORIYA_SPRITE_SET and enemy.IsInGoriyaSpriteSet()) or
          (sprite_set == SpriteSet.DARKNUT_SPRITE_SET and enemy.IsInDarknutSpriteSet()) or
          (sprite_set == SpriteSet.WIZZROBE_SPRITE_SET and enemy.IsInWizzrobeSpriteSet())):
        return enemy

  @classmethod
  def RandomBossFromSpriteSet(cls, boss_sprite_set: SpriteSet) -> "Enemy":
    if boss_sprite_set == SpriteSet.DODONGO_SPRITE_SET:
      return random.choice([
          Enemy.SINGLE_DODONGO, Enemy.TRIPLE_DODONGO, Enemy.SINGLE_DIGDOGGER,
          Enemy.TRIPLE_DIGDOGGER, Enemy.AQUAMENTUS, Enemy.AQUAMENTUS, Enemy.MOLDORM, Enemy.MOLDORM
      ])
    if boss_sprite_set == SpriteSet.GLEEOK_SPRITE_SET:
      return random.choice([
          Enemy.BLUE_GOHMA, Enemy.BLUE_GOHMA, Enemy.RED_GOHMA, Enemy.RED_GOHMA, Enemy.MANHANDALA,
          Enemy.MANHANDALA, Enemy.MANHANDALA, Enemy.MANHANDALA, Enemy.GLEEOK_1, Enemy.GLEEOK_2,
          Enemy.GLEEOK_3, Enemy.GLEEOK_4
      ])
    # boss_sprite_set == SpriteSet.PATRA_SPRITE_SET:
    return random.choice([Enemy.PATRA_1, Enemy.PATRA_2])

  @classmethod
  def RandomHardEnemyOrMiniBossOkayForSpriteSets(cls, boss_sprite_set: SpriteSet,
                                                 enemy_sprite_set: SpriteSet) -> "Enemy":
    assert boss_sprite_set in [
        SpriteSet.DODONGO_SPRITE_SET, SpriteSet.GLEEOK_SPRITE_SET, SpriteSet.PATRA_SPRITE_SET
    ]
    assert enemy_sprite_set in [
        SpriteSet.GORIYA_SPRITE_SET, SpriteSet.DARKNUT_SPRITE_SET, SpriteSet.WIZZROBE_SPRITE_SET
    ]
    print(boss_sprite_set)
    print(enemy_sprite_set)
    while True:
      try:
        enemy = cls(random.randrange(0x0, 0x7F))
      except ValueError:
        continue

      #input(enemy)
      if (boss_sprite_set == SpriteSet.DODONGO_SPRITE_SET and
          enemy in [Enemy.SINGLE_DODONGO, Enemy.AQUAMENTUS, Enemy.MOLDORM]):
        return enemy
      if boss_sprite_set == SpriteSet.GLEEOK_SPRITE_SET and enemy in [Enemy.GLEEOK_1]:
        return enemy
      if enemy_sprite_set == SpriteSet.GORIYA_SPRITE_SET and enemy in [
          Enemy.BLUE_GORIYA, Enemy.BLUE_GORIYA_KEESE_BUBBLE, Enemy.BLUE_GORIYA_RED_GORIYA
      ]:
        return enemy
      if enemy_sprite_set == SpriteSet.DARKNUT_SPRITE_SET and enemy in [
          Enemy.BLUE_DARKNUT, Enemy.BLUE_DARKNUT_RED_DARKNUT_GORIYA_BUBBLE,
          Enemy.BLUE_DARKNUT_RED_DARKNUT_POLS_VOICE
      ]:
        return enemy
      if enemy_sprite_set == SpriteSet.WIZZROBE_SPRITE_SET and enemy.HasBlueWizzrobes():
        return enemy
