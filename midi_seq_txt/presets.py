import os
from argparse import Namespace
from glob import iglob
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple, Type, Union

import attrs
import yaml
from cattr import structure

from .functionalities import MInFunctionality, MMappings, MMusic, MOutFunctionality

PRESET_TYPES: Dict[
    str, Union[Type[MOutFunctionality], Type[MMappings], Type[MMusic], Type[MInFunctionality]]
] = {
    "MMappings": MMappings,
    "MOutFunctionality": MOutFunctionality,
    "MInFunctionality": MInFunctionality,
    "MMusic": MMusic,
}


def read_all_presets(
    args: Namespace,
) -> Tuple[
    List[MOutFunctionality],
    Set[str],
    List[MInFunctionality],
    Set[str],
    List[MMappings],
    List[MMusic],
]:
    loc: str = args.dir
    all_out_modes: List[MOutFunctionality] = list()
    all_in_modes: List[MInFunctionality] = list()
    all_mappings: List[MMappings] = list()
    all_music: List[MMusic] = list()
    all_in_instruments: Set[str] = set()
    all_out_instruments: Set[str] = set()
    for file_path in iglob(f"{loc}/*/*.yaml"):
        path = Path(file_path)
        class_name = path.parts[-2]
        if class_name == "MOutFunctionality":
            out_mode_dict = read_preset(file_path=file_path)
            out_mode = MOutFunctionality(**out_mode_dict)
            all_out_modes.append(out_mode)
            for instrument in out_mode.instruments:
                all_out_instruments.add(instrument)
        elif class_name == "MInFunctionality":
            in_mode_dict = read_preset(file_path=file_path)
            in_mode = MInFunctionality(**in_mode_dict)
            all_in_modes.append(in_mode)
            for instrument in in_mode.instruments:
                all_in_instruments.add(instrument)
        elif class_name == "MMappings":
            mappings_dict = read_preset(file_path=file_path)
            mapping = MMappings(**mappings_dict)
            all_mappings.append(mapping)
        elif class_name == "MMusic":
            music_dict = read_preset(file_path=file_path)
            music = MMusic(**music_dict)
            all_music.append(music)
    return (
        all_out_modes,
        all_out_instruments,
        all_in_modes,
        all_in_instruments,
        all_mappings,
        all_music,
    )


def read_preset(file_path: str) -> Dict[str, Any]:
    preset_dict: Dict[str, Any] = dict()
    if os.path.exists(file_path):
        with open(file_path, "r") as fh:
            preset_dict = yaml.load(fh, yaml.Loader)
    return preset_dict


def read_preset_type(
    file_path: str,
) -> Union[MMappings, MOutFunctionality, MMusic, MInFunctionality]:
    path = Path(file_path)
    class_name = path.parts[-2]
    preset_dict: Dict[str, Any] = dict()
    if os.path.exists(file_path):
        with open(file_path, "r") as fh:
            preset_dict = yaml.load(fh, yaml.Loader)
    preset_type: Union[
        Type[MOutFunctionality], Type[MMappings], Type[MMusic], Type[MInFunctionality]
    ] = PRESET_TYPES[class_name]
    struct = structure(preset_dict, preset_type)
    if (
        isinstance(struct, MMappings)
        or isinstance(struct, MOutFunctionality)
        or isinstance(struct, MInFunctionality)
        or isinstance(struct, MMusic)
    ):
        return struct
    else:
        raise TypeError("Type mismatch!")


def write_preset_type(
    preset: Union[MMappings, MInFunctionality, MOutFunctionality, MMusic], loc: str
) -> None:
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

    presets: List[Union[MMappings, MInFunctionality, MOutFunctionality, MMusic]] = list()
    for obj_name in dir(midi_seq_txt.init):
        if "_" in obj_name:
            obj = getattr(midi_seq_txt.init, obj_name)
            if obj.__class__.__name__ in [
                "MMappings",
                "MOutFunctionality",
                "MMusic",
                "MInFunctionality",
            ]:
                presets.append(obj)
    for preset in presets:
        write_preset_type(preset=preset, loc=loc)
