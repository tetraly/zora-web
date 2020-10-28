# Flag definitions and logic.
from typing import List, Type
from django.utils.html import mark_safe
from markdown import markdown

# ************************************** Flag classes


class FlagError(ValueError):
  pass


class Flag:
  """Class representing a flag with its description, and possible values/choices/options."""
  name = ''
  description = ''
  inverse_description = ''
  value = ''
  hard = False
  modes = ['itemonly', 'standard']
  choices: List[Type["Flag"]] = []
  options: List[Type["Flag"]] = []

  @classmethod
  def description_as_markdown(cls) -> bool:
    return mark_safe(markdown(cls.description, safe_mode='escape'))

  @classmethod
  def description_or_name_as_markdown(cls) -> bool:
    if cls.description:
      return mark_safe(markdown(cls.description, safe_mode='escape'))
    else:
      return mark_safe(markdown(cls.name, safe_mode='escape'))

  @classmethod
  def inverse_description_as_markdown(cls) -> bool:
    return mark_safe(markdown(cls.inverse_description, safe_mode='escape'))

  @classmethod
  def inverse_description_or_name_as_markdown(cls) -> bool:
    if cls.inverse_description:
      return mark_safe(markdown(cls.inverse_description, safe_mode='escape'))
    else:
      return mark_safe(markdown("(" + cls.name + ")", safe_mode='escape'))

  @classmethod
  def available_in_mode(cls, mode: str) -> bool:
    """

        Args:
            mode (str): Mode to check availability.

        Returns:
            bool: True if this flag is available in the given mode, False otherwise.

        """
    return mode in cls.modes


# ************************************** Category classes


class FlagCategory:
  name = ''
  flags: List[Type[Flag]] = []


# ******** Difficulty


class AvoidHardCombat(Flag):
  name = 'Avoid hard combat'
  description = 'Item placement logic won\'t require "hard" combat without a ring and sword upgrade'
  inverse_description = "(Item placement logic won't be modified for difficulty.)"
  value = 'C'
  modes = ['standard']


class PlusOrMinus2HP(Flag):
  name = 'Plus or Minus 2 Enemy HP'
  description = 'Enemies may have up to two more or fewer hit points than usual.'
  value = 'H2'


class PlusOrMinus4HP(Flag):
  name = 'Plus or Minus 4 Enemy HP'
  description = 'Enemies may have up to four more or fewer hit points than usual.'
  value = 'H4'


class Minus2HP(Flag):
  name = 'Minus 2 HP'
  description = 'Enemies will have up to two fewer HP than usual.'
  value = 'Ht'


class Minus4HP(Flag):
  name = 'Minus 4 HP'
  description = 'Enemies will have up to four fewer HP than usual.'
  value = 'Hm'


class ZeroHP(Flag):
  name = 'Zero HP enemies'
  description = 'Enemies will have no HP and die in one hit.'
  value = 'Hz'


class EnemyHP(Flag):
  name = 'Randomize Enemy HP'
  description = "Randomize or Zero out HP"
  modes = ['standard']
  value = '@H'
  choices = [
      PlusOrMinus2HP,
      PlusOrMinus4HP,
      Minus2HP,
      Minus4HP,
      ZeroHP,
  ]


class DifficultyCategory(FlagCategory):
  name = 'Difficulty Settings'
  flags = [
      AvoidHardCombat,
      EnemyHP,
  ]


# ******** Items
"""class ProgressiveItems(Flag):
  name = 'Progressive Items'
  description = 'Makes swords, candles, boomerangs, rings, and arrows progresive upgrades.'
  inverse_description = "(Keeps item levels as is in the vanilla game.)"
  value = 'Ip'
  modes = ['standard']

class ShuffleShopItems(Flag):
  name = 'Shuffle Shop Items'
  description = 'Adds bait, blue candle, blue ring, wood arrows to the item shuffle. Also shuffles minor shop items and prices.'
  inverse_description = "(Keeps shops as they are in the vanilla game.)"
  value = 'Is'
  modes = ['standard']

class ItemsCategory(FlagCategory):
  name = 'Item Settings'
  flags = [ProgressiveItems, ShuffleShopItems,]
"""
# ******** Speedups


class FastDungeonTransitions(Flag):
  name = 'Fast Dungeon Transitions'
  description = 'Makes dungeon room transition times approximately two times faster.'
  inverse_description = "(Keeps dungeon room transition speed as it is in the vanilla game)"
  modes = ['standard']
  value = 'F'


class FastText(Flag):
  name = 'Fast Text Scrolling'
  description = 'Makes NPC text scroll much more quickly.'
  inverse_description = "(Keeps text speed as it is in the vanilla game)"
  modes = ['standard']
  value = 'T'


class SpeedupsCategory(FlagCategory):
  name = 'Speedups'
  flags = [
      FastDungeonTransitions,
      FastText,
  ]


# ********* Extras


class DisableBeeping(Flag):
  name = "Disable Low Health Beeping"
  description = "There won't be beeping when you have one heart or less of life ."
  inverse_description = "(Low health beeping will occur as it does in the vanilla game.)"
  modes = ['standard']
  value = 'Xb'


class DisableLightFlashes(Flag):
  name = "Disable Light Flashes"
  description = "The background won't brightly flash when a bomb explodes or a triforce is obtained."
  inverse_description = "(Flashing will occur as it does in the vanilla game.)"
  modes = ['standard']
  value = 'Xl'


class RandomizeLevelText(Flag):
  name = 'Randomize Level Text'
  description = 'Chooses a random value for the "level-#" text displayed in dungeons.'
  inverse_description = "(Keeps 'LEVEL' text when in levels)"
  modes = ['standard']
  value = 'Xt'


class EnableSelectSwap(Flag):
  name = "Enable Select Swap"
  description = "Pressing select will rotate through B button items."
  inverse_description = "(Pressing select will pause and unpause the game.)"
  modes = ['standard']
  value = 'Xs'


class FrenchCommunityHints(Flag):
  name = "Add Hints from the French Zelda 1 community"
  description = "Community hints will be in French and come from the Zelda 1 Francophone community."
  inverse_description = "(All hints will be written in English.)"
  modes = ['standard']
  value = 'Xf'


class ExtraCustomizations(Flag):
  name = 'Customization settings that don\'t materially affect gameplay.'
  value = '@X'
  options = [
      DisableBeeping,
      DisableLightFlashes,
      EnableSelectSwap,
      FrenchCommunityHints,
      RandomizeLevelText,
  ]


class ExtrasCategory(FlagCategory):
  name = 'Extra customization settings'
  flags = [
      ExtraCustomizations,
  ]


# ************************************** Preset classes


class Preset:
  name = ''
  description = ''
  flags = ''


class CasualPreset(Preset):
  name = 'Test'
  description = 'Test flags for a casual playthrough of the game.'
  flags = 'Hcm2 Fst'


class AdvancedPreset(Preset):
  name = 'Advanced'
  description = 'More difficult combat settings for the randomizer.'
  flags = 'Hp4 Fst'


# ************************************** Default lists for the site.

# List of categories for the site.
CATEGORIES = (
    DifficultyCategory,
    # ItemsCategory,
    SpeedupsCategory,
    ExtrasCategory,
)

# List of presets.
PRESETS = (
    CasualPreset,
    AdvancedPreset,
)
