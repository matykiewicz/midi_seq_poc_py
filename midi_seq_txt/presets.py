import os
from argparse import Namespace
from typing import List, Union

import attrs
import yaml

from .functionalities import MFunctionality, MMappings, MMusic


def read_all_presets():
    pass


def read_preset():
    pass


def write_preset(preset: Union[MMappings, MFunctionality, MMusic], loc: str) -> None:
    preset_type = preset.__class__.__name__
    preset_dict = attrs.asdict(preset)
    os.makedirs(f"{loc}/{preset_type}", exist_ok=True)
    with open(f"{loc}/{preset_type}/{preset.name}.yaml", "w") as fh:
        yaml.dump(preset_dict, fh)


def write_all_presets(args: Namespace) -> None:
    loc: str = args.dir
    import midi_seq_txt.init

    presets: List[Union[MMappings, MFunctionality, MMusic]] = list()
    for obj_name in dir(midi_seq_txt.init):
        if "_" in obj_name:
            obj = getattr(midi_seq_txt.init, obj_name)
            if obj.__class__.__name__ in ["MMappings", "MFunctionality", "MMusic"]:
                presets.append(obj)
    for preset in presets:
        write_preset(preset=preset, loc=loc)
