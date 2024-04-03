from argparse import Namespace
from typing import Union

import attrs
import yaml

from .functionalities import MFunctionality, MMappings, MMusic


def read_all_presets():
    pass


def read_preset():
    pass


def write_preset(preset: Union[MMappings, MFunctionality, MMusic], loc: str) -> None:
    preset_dict = attrs.asdict(preset)
    with open(f"{loc}/{preset.name}.yaml") as fh:
        yaml.dump(preset_dict, fh)


def write_all_presets(args: Namespace) -> None:
    loc: str = args.dir
    pass
