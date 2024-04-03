from typing import Union

import attrs
import yaml

from .functionalities import MFunctionality, MMappings


def read_presets():
    pass


def write_as_preset(preset: Union[MMappings, MFunctionality], loc: str) -> None:
    preset_dict = attrs.asdict(preset)
    with open(f"{loc}/{preset.name}.yaml") as fh:
        yaml.dump(preset_dict, fh)
