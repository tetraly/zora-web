from absl import logging as log
import collections
from typing import Dict, List, Optional, Set, Type
from .flags import Flag, CATEGORIES


class Settings:

  def __init__(self,
               seed: int,
               flag_string: str = '',
               mode: str = 'standard',
               debug_mode: bool = False) -> None:
    """Provide either form data fields or flag string to set flags on creation.

        Args:
            mode (str): Should be standard or open.
            debug_mode (bool): Debug flag.
            flag_string (str): Flag string if parsing flags from string.
        """
    self._seed = seed
    self._mode = mode
    self._debug_mode = debug_mode
    self._enabled_flags: Set[Type[Flag]] = set()
    # If flag string provided, make fake form data based on it to parse.
    flag_data: Dict[str, List[str]] = {}
    for flag in flag_string.strip().split():
      if flag[0] not in flag_data:
        flag_data[flag[0]] = []
      flag_data[flag[0]] += [c for c in flag[1:]]
    # Get flags from form data.
    for category in CATEGORIES:
      for flag2 in category.flags:
        self._check_flag_from_form_data(flag2, flag_data)

    # Sanity check.
    if debug_mode:
      provided_parts = set(flag_string.strip().split())
      parsed_parts = set(self.flag_string.split())
      if provided_parts != parsed_parts:
        raise ValueError("Generated flags {!r} don't match provided {!r} - difference: {!r}".format(
            parsed_parts, provided_parts, provided_parts - parsed_parts))

  def _check_flag_from_form_data(self, flag: Type[Flag], flag_data: Dict[str, List[str]]) -> None:
    """
        Args:
            flag (randomizer.logic.flags.Flag): Flag to check if enabled.
            flag_data (dict): Form data dictionary.

        """
    if flag.available_in_mode(self.mode):
      if flag.value.startswith('-'):
        # Solo flag that begins with a dash.
        if flag_data.get(flag.value):
          self._enabled_flags.add(flag)
      else:
        # Flag that may be on its own with choices and/or suboptions.
        if flag.value.startswith('@'):
          if flag.value[1] in flag_data:
            self._enabled_flags.add(flag)
        else:
          char = flag.value[0]
          rest = flag.value[1:]

          # Single character flag, just check if it's enabled.  Otherwise, make sure the small char is there.
          if rest:
            if rest in flag_data.get(char, []):
              self._enabled_flags.add(flag)
          elif char in flag_data:
            self._enabled_flags.add(flag)

      # If flag was enabled, check choices/options recursively.
      if self.IsEnabled(flag):
        for choice in flag.choices:
          self._check_flag_from_form_data(choice, flag_data)
        for option in flag.options:
          self._check_flag_from_form_data(option, flag_data)

  @property
  def mode(self) -> str:
    return self._mode

  @property
  def debug_mode(self) -> bool:
    return self._debug_mode

  @property
  def seed(self) -> int:
    return self._seed

  def _build_flag_string_part(self, flag: Type[Flag], flag_strings: Dict[str, List[str]]) -> None:
    """

        Args:
            flag (randomizer.logic.flags.Flag): Flag to process.
            flag_strings (dict): Dictionary for flag strings.

        """
    if self.IsEnabled(flag):
      # Solo flag that begins with a dash.
      #if flag.value.startswith('-'):
      #    flag_strings[flag.value] = True
      # Flag that may have a subsection of choices and/or options.
      #else:
      rest = ''
      if flag.value.startswith('@'):
        char = flag.value[1]
        flag_strings['@'].append(char)
      else:
        char = flag.value[0]
        rest = flag.value[1:]

      # Check if this key is in the map yet.
      if char not in flag_strings:
        flag_strings[char] = []
      if rest:
        flag_strings[char].append(rest)

      for choice in flag.choices:
        self._build_flag_string_part(choice, flag_strings)

      for option in flag.options:
        self._build_flag_string_part(option, flag_strings)

  @property
  def flag_string(self) -> str:
    flag_strings: Dict[str, List[str]] = collections.OrderedDict()
    flag_strings['@'] = []

    for category in CATEGORIES:
      for flag in category.flags:
        self._build_flag_string_part(flag, flag_strings)

    flag_string = ''
    for key, vals in flag_strings.items():
      if key != '@':
        if key.startswith('-'):
          flag_string += key + ' '
        elif vals or key not in flag_strings['@']:
          flag_string += key + ''.join(vals) + ' '

    return flag_string.strip()

  def IsEnabled(self, flag: Type[Flag]) -> bool:
    return flag in self._enabled_flags

  def get_flag_choice(self, flag: Type[Flag]) -> Optional[Type[Flag]]:
    for choice in flag.choices:
      if self.IsEnabled(choice):
        return choice
    return None
