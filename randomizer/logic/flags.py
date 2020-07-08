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
  modes = ['linear', 'open']
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


# ******** Difficulty


class AvoidHardCombat(Flag):
  name = 'Avoid hard combat'
  description = 'Item placement logic won\'t require "hard" combat without a ring and sword upgrade'
  inverse_description = "(Item placement logic won't be modified for difficulty.)"
  value = 'C'
  modes = ['open']


class ProgressiveItems(Flag):
  name = 'Progressive Items'
  description = 'Makes swords, candles, boomerangs, rings, and arrows progresive upgrades.'
  inverse_description = "(Keeps item levels as is in the vanilla game.)"
  value = 'Ia'
  modes = ['open']


class ShuffleShopItems(Flag):
  name = 'Shuffle Shop Items'
  description = 'Adds bait, blue candle, blue ring, wood arrows to the item shuffle. Also shuffles minor shop items and prices.'
  inverse_description = "(Keeps shops as they are in the vanilla game.)"
  value = 'Ib'
  modes = ['open']


# ********* Extras


class SelectSwap(Flag):
  name = "Enable Select Swap"
  description = "Pressing select will rotate through B button items."
  inverse_description = "(Pressing select will pause and unpause the game.)"
  modes = ['open']
  value = 'S'


class RandomizeLevelText(Flag):
  name = 'randomize_level_text'
  description = 'Chooses a random value (either literally or figuratively) for the "level-#" text displayed in dungeons.'
  inverse_description = "(Keeps 'LEVEL' text when in levels)"
  modes = ['open']
  value = 'Ta'


class SpeedUpText(Flag):
  name = 'speed_up_text'
  description = 'Makes text go speedy.'
  inverse_description = "(Keeps text speed as is)"
  modes = ['open']
  value = 'Tb'


# ************************************** Category classes


class FlagCategory:
  name = ''
  flags: List[Type[Flag]] = []


class DifficultyCategory(FlagCategory):
  name = 'Difficulty Settings'
  flags = [AvoidHardCombat, ProgressiveItems, ShuffleShopItems]


class ExtrasCategory(FlagCategory):
  name = 'Extra settings'
  flags = [
      SelectSwap,
      RandomizeLevelText,
      SpeedUpText,
  ]


# ************************************** Preset classes


class Preset:
  name = ''
  description = ''
  flags = ''


class CasualPreset(Preset):
  name = 'Test'
  description = 'Test flags for a casual playthrough of the game.'
  flags = 'S C'


class AdvancedPreset(Preset):
  name = 'Advanced'
  description = 'More difficult.'
  flags = 'S'


# ************************************** Default lists for the site.

# List of categories for the site.
CATEGORIES = (
    DifficultyCategory,
    ExtrasCategory,
)

# List of presets.
PRESETS = (
    CasualPreset,
    AdvancedPreset,
)
