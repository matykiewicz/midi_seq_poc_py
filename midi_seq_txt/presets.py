import os
from argparse import Namespace
from glob import iglob
from pathlib import Path
from typing import List, Tuple, Union, Dict, Any

import attrs
import yaml

from .functionalities import MFunctionality, MMappings, MMusic


def read_all_presets(args: Namespace) -> Tuple[List[MFunctionality], List[MMappings], List[MMusic]]:
    loc: str = args.dir
    modes: List[MFunctionality] = list()
    mappings: List[MMappings] = list()
    all_music: List[MMusic] = list()
    for file_path in iglob(f"{loc}/*/*.yaml"):
        path = Path(file_path)
        class_name = path.parts[-2]
        if class_name == "MFunctionality":
            mode_dict = read_preset(file_path=file_path)
            mode = MFunctionality(**mode_dict)
            modes.append(mode)
        elif class_name == "MMappings":
            mappings_dict = read_preset(file_path=file_path)
            mapping = MMappings(**mappings_dict)
            mappings.append(mapping)
        elif class_name == "MMusic":
            music_dict = read_preset(file_path=file_path)
            music = MMusic(**music_dict)
            all_music.append(music)
    return modes, mappings, all_music


def read_preset(file_path: str) -> Dict[str, Any]:
    with open(file_path, "r") as fh:
        preset_dict = yaml.load(fh, yaml.Loader)
    return preset_dict


def write_preset(preset: Union[MMappings, MFunctionality, MMusic], loc: str) -> None:
    preset_type = preset.__class__.__name__
    preset_dict = attrs.asdict(preset)
    os.makedirs(f"{loc}/{preset_type}", exist_ok=True)
    with open(f"{loc}/{preset_type}/{preset.name}.yaml", "w") as fh:
        if "_exe_" in preset_dict:
            del preset_dict["_exe_"]
        if "_lock_" in preset_dict:
            del preset_dict["_lock_"]
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
