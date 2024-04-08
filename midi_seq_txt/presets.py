import os
from argparse import Namespace
from glob import iglob
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple, Type, Union

import attrs
import yaml

from .functionalities import MOutFunctionality, MMappings, MMusic, MInFunctionality

PRESET_TYPES: Dict[str, Union[Type[MOutFunctionality], Type[MMappings], Type[MMusic], Type[MInFunctionality]]] = {
    "MMappings": MMappings,
    "MOutFunctionality": MOutFunctionality,
    "MInFunctionality": MInFunctionality,
    "MMusic": MMusic,
}


def read_all_presets(
    args: Namespace,
) -> Tuple[List[MOutFunctionality], Set[str], List[MInFunctionality], List[MMappings], List[MMusic]]:
    loc: str = args.dir
    all_modes: List[MOutFunctionality] = list()
    all_messages: List[MInFunctionality] = list()
    all_mappings: List[MMappings] = list()
    all_music: List[MMusic] = list()
    all_instruments: Set[str] = set()
    for file_path in iglob(f"{loc}/*/*.yaml"):
        path = Path(file_path)
        class_name = path.parts[-2]
        if class_name == "MOutFunctionality":
            mode_dict = read_preset(file_path=file_path)
            mode = MOutFunctionality(**mode_dict)
            all_modes.append(mode)
            for instrument in mode.instruments:
                all_instruments.add(instrument)
        elif class_name == "MInFunctionality":
            message_dict = read_preset(file_path=file_path)
            message = MInFunctionality(**message_dict)
            all_messages.append(message)
        elif class_name == "MMappings":
            mappings_dict = read_preset(file_path=file_path)
            mapping = MMappings(**mappings_dict)
            all_mappings.append(mapping)
        elif class_name == "MMusic":
            music_dict = read_preset(file_path=file_path)
            music = MMusic(**music_dict)
            all_music.append(music)
    return all_modes, all_instruments, all_messages, all_mappings, all_music


def read_preset(file_path: str) -> Dict[str, Any]:
    with open(file_path, "r") as fh:
        preset_dict = yaml.load(fh, yaml.Loader)
    return preset_dict


def read_preset_type(file_path: str) -> Union[MMappings, MOutFunctionality, MMusic]:
    path = Path(file_path)
    class_name = path.parts[-2]
    with open(file_path, "r") as fh:
        preset_dict = yaml.load(fh, yaml.Loader)
    preset_type: Union[Type[MOutFunctionality], Type[MMappings], Type[MMusic]] = PRESET_TYPES[
        class_name
    ]
    return preset_type(**preset_dict)  # noqa


def write_preset_type(preset: Union[MMappings, MOutFunctionality, MMusic], loc: str) -> None:
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

    presets: List[Union[MMappings, MOutFunctionality, MMusic]] = list()
    for obj_name in dir(midi_seq_txt.init):
        if "_" in obj_name:
            obj = getattr(midi_seq_txt.init, obj_name)
            if obj.__class__.__name__ in ["MMappings", "MOutFunctionality", "MMusic", "MInFunctionality"]:
                presets.append(obj)
    for preset in presets:
        write_preset_type(preset=preset, loc=loc)
