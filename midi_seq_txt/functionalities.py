from collections import defaultdict
from copy import deepcopy
from typing import Dict, List, Optional, Tuple, Union

import mingus.core.scales as scales
from attrs import AttrsInstance, define
from mingus.containers import Note

from .configs import InitConfig
from .const import (
    BUT_COPY,
    BUT_PLAY,
    BUT_PRES,
    BUT_REC,
    BUT_TEMPO,
    BUT_VIEW,
    ValidButtons,
    ValidNav,
    ValidSettings,
)


def create_notes(scale: str) -> List[str]:
    notes = scales.get_notes(key=scale)
    no_button_notes = list()
    button_notes = [ValidButtons.NA.value]
    for octave in range(1, InitConfig().octaves + 1):
        for note in notes:
            no_button_notes.append(f"{note}-{octave}")
    n_keys = InitConfig().n_keys
    for i in range(len(no_button_notes)):
        if (i + 1) % (n_keys - 1) == 0:
            button_notes.append(no_button_notes[i])
            button_notes.append(ValidButtons.NEXT.value)
        else:
            button_notes.append(no_button_notes[i])
    if button_notes[-1] != ValidButtons.NEXT.value:
        button_notes.append(ValidButtons.NEXT.value)
    return button_notes


@define
class MMapping(AttrsInstance):
    midi_id: int
    port_name: str
    channel: int
    is_out: bool
    instruments: List[str]


@define
class MMappings(AttrsInstance):
    name: str
    comment: str
    mappings: List[MMapping]

    def filter_midis(self, port_names) -> List[Tuple[int, int]]:
        found_ports: List[int] = list()
        found_mappings: List[int] = list()
        found_midis: List[int] = list()
        for i, port_name in enumerate(port_names):
            for j, mapping in enumerate(self.mappings):
                if (
                    port_name == mapping.port_name
                    and i not in found_ports
                    and j not in found_mappings
                ):
                    found_ports.append(i)
                    found_mappings.append(j)
                    found_midis.append(self.mappings[j].midi_id)
        return list(zip(found_ports, found_midis))

    def to_dict(self, modes: Dict[str, "MFunctionality"]) -> Dict[int, Dict[int, List[str]]]:
        mappings_dict: Dict[int, Dict[int, List[str]]] = defaultdict(lambda: defaultdict(list))
        instruments_dict: Dict[str, List[str]] = defaultdict(list)
        for valid_mode in modes.keys():
            mode = modes[valid_mode]
            for instrument in mode.instruments:
                instruments_dict[instrument].append(valid_mode)
        for mapping in self.mappings:
            midi_id = mapping.midi_id
            channel = mapping.channel
            instruments = mapping.instruments
            for instrument in instruments:
                for valid_mode in instruments_dict[instrument]:
                    mappings_dict[midi_id][channel].append(valid_mode)
        return mappings_dict


@define
class MMusic(AttrsInstance):
    name: str
    mappings_name: str
    comment: str
    data: Dict[int, Dict[int, Dict[int, Dict[int, Dict[str, List[List[int]]]]]]]


@define
class NFunctionality(AttrsInstance):
    # Navigation & Menus
    name: str
    ind: int
    buttons: Tuple[ValidButtons, ...]

    def update_with_dir(self, direction: int) -> "NFunctionality":
        ind = self.ind
        ind += direction
        if ind >= len(self.buttons):
            ind = 0
        if ind < 0:
            ind = len(self.buttons) - 1
        self.ind = ind
        return self

    def get_buttons(self, interval: int) -> List[ValidButtons]:
        buttons = list()
        for i in range(self.ind * interval, (self.ind + 1) * interval):
            buttons.append(self.buttons[i])
        return buttons


@define
class SFunctionality(AttrsInstance):
    # Sequencers & Settings
    name: str
    ind: int
    values: List[Union[str, int]]

    def new(self) -> "SFunctionality":
        return deepcopy(self)

    def update_with_ind(self, ind: int) -> "SFunctionality":
        self.ind = ind
        return self

    def update_with_value(self, value: Union[str, int]) -> "SFunctionality":
        ind = self.values.index(value)
        self.ind = ind
        return self

    def change(self, direction: int) -> "SFunctionality":
        ind = self.ind
        ind += direction
        if ind >= len(self.values):
            ind = 0
        if ind < 0:
            ind = len(self.values) - 1
        self.ind = ind
        return self

    def get_ind(self) -> int:
        return self.ind

    def set_value(self, value: str) -> "SFunctionality":
        ind = self.values.index(value)
        self.ind = ind
        return self

    def get_value(self) -> Union[str, int]:
        return self.values[self.ind]

    def get_first_value(self) -> Union[str, int]:
        return self.values[0]

    def next_ind(self) -> "SFunctionality":
        ind = self.ind
        ind += 1
        if ind >= len(self.values):
            ind = 0
        self.ind = ind
        return self


@define
class MFunctionality(AttrsInstance):
    # MIDI & Modes
    name: str
    indexes: List[List[int]]
    labels: List[str]
    offsets: List[int]
    data: List[List[str]]
    vis_ind: List[int]
    instruments: List[str]
    comment: str
    _exe_: int = 0
    _lock_: bool = True

    def get_exe(self) -> int:
        return self._exe_

    def update_offsets_with_lab(self, lab: str, by: int) -> "MFunctionality":
        if lab in self.labels:
            off_int = self.labels.index(lab)
            if off_int < len(self.data):
                if self.offsets[off_int] + by >= len(self.data[off_int]):
                    self.offsets[off_int] = 1
                else:
                    self.offsets[off_int] += by
        else:
            raise ValueError(f"Label {lab} not found!")
        return self

    def get_indexes(self) -> List[List[int]]:
        return deepcopy(self.indexes)

    def get_labels(self) -> List[str]:
        return deepcopy(self.labels)

    def get_values(self, indexes: Optional[List[List[int]]] = None) -> List[List[str]]:
        values: List[List[str]] = list()
        if indexes is None:
            indexes = self.indexes
        for i in range(len(indexes)):
            value = list()
            for j, index in enumerate(indexes[i]):
                value.append(deepcopy(self.data[j][index]))
            values.append(value)
        return values

    def get_single_value_by_off(self, off: str, ind: int) -> str:
        if off in self.labels:
            off_int = self.labels.index(off)
            if off_int < len(self.data):
                ind = self.offsets[off_int] + ind
                if ind < len(self.data[off_int]):
                    return deepcopy(self.data[off_int][ind])
        else:
            raise ValueError(f"Offset {off} not found!")
        return ValidButtons.NA

    def get_single_value_by_lab(self, exe: int, lab: str) -> str:
        if exe < len(self.indexes):
            if lab in self.labels:
                ind = self.labels.index(lab)
                if ind < len(self.indexes[exe]):
                    return deepcopy(self.data[ind][self.indexes[exe][ind]])
            else:
                raise ValueError(f"Label {lab} not found!")
        return ValidButtons.NA

    def get_row_values(self, exe: int) -> List[str]:
        values: List[str] = list()
        if exe < len(self.indexes):
            if "Note" in self.labels and "Scale" in self.labels:
                scale = self.get_single_value_by_off(off="Scale", ind=0)
                self.set_data_with_lab(lab="Note", data=create_notes(scale=scale))
            for j in range(len(self.indexes[exe])):
                values.append(deepcopy(self.data[j][self.indexes[exe][j]]))
        return values

    def get_vis_ind(self) -> List[int]:
        return self.vis_ind

    def get_vis_label(self) -> str:
        return self.labels[self.vis_ind[1]]

    def new(self, lock: bool) -> "MFunctionality":
        new = deepcopy(self)
        new._lock_ = lock
        return new

    def new_with_indexes(self, indexes: List[List[int]]) -> "MFunctionality":
        new_mode = self.new(lock=False)
        new_mode = new_mode.set_indexes(indexes=deepcopy(indexes))
        return new_mode

    def new_with_off(self, off: str, ind: int, exe: Optional[int]) -> "MFunctionality":
        new_mode = self.new(lock=False)
        new_mode.set_indexes_with_off(off=off, ind=ind, exe=exe)
        return new_mode

    def set_data_with_lab(self, lab: str, data: List[str]) -> "MFunctionality":
        if lab in self.labels:
            ind = self.labels.index(lab)
            self.data[ind] = data
        else:
            raise ValueError(f"Label {lab} not found!")
        return self

    def set_indexes_with_off(
        self, off: str, ind: int, exe: Optional[int] = None
    ) -> "MFunctionality":
        if self._lock_:
            raise PermissionError(f"{self.name} mode is locked!")
        if off in self.labels:
            off_int = self.labels.index(off)
            ind = self.offsets[off_int] + ind
            if off_int < len(self.data):
                for i in range(len(self.indexes)):
                    if exe is None or exe == i:
                        if ind < len(self.data[off_int]):
                            self.indexes[i][off_int] = ind
        else:
            raise ValueError(f"Offset {off} not found!")
        return self

    def set_indexes(self, indexes: List[List[int]]) -> "MFunctionality":
        if self._lock_:
            raise PermissionError(f"{self.name} mode is locked!")
        for i in range(len(indexes)):
            for j in range(len(indexes[i])):
                if i < len(self.indexes):
                    if j < len(self.indexes[i]):
                        self.indexes[i][j] = indexes[i][j]
        return self

    def get_message(self) -> List[int]:
        if self._lock_:
            raise PermissionError(f"{self.name} mode is locked!")

        def convert_value_to_int(lab: str, value: str) -> int:
            value_int = 0
            if lab == "Note":
                if value != ValidButtons.NA:
                    value_int = int(Note(value)) + 12
                else:
                    value_int = -1
            else:
                value_int = int(value)
            return value_int

        values_int: List[int] = list()
        if self._exe_ < len(self.indexes):
            values_str = self.get_row_values(exe=self._exe_)
            labels_str = self.get_labels()
            for i, value_str in enumerate(values_str):
                values_int.append(convert_value_to_int(lab=labels_str[i], value=value_str))
        self._exe_ += 1
        return values_int


class PlayN(NFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidNav.PLAY.value,
            buttons=BUT_PLAY,
            ind=0,
        )


class RecordN(NFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidNav.RECORD.value,
            buttons=BUT_REC,
            ind=0,
        )


class ViewN(NFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidNav.VIEW.value,
            buttons=BUT_VIEW,
            ind=0,
        )


class TempoN(NFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidNav.TEMPO.value,
            buttons=BUT_TEMPO,
            ind=0,
        )


class CopyN(NFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidNav.COPY.value,
            buttons=BUT_COPY,
            ind=0,
        )


class PresetsN(NFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidNav.PRESETS.value,
            buttons=BUT_PRES,
            ind=0,
        )


# - - EDIT POS - - #


class EMiDiOS(SFunctionality):
    def __init__(self, midi_ids: List[int]):
        super().__init__(
            name=ValidSettings.E_MIDI_O.value,
            ind=0,
            values=deepcopy(sorted(midi_ids)),
        )


class EPartS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.E_PART.value,
            ind=0,
            values=[i for i in range(1, InitConfig().n_parts + 1)],
        )


class EStepS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.E_STEP.value,
            ind=0,
            values=[i for i in range(1, InitConfig().n_steps + 1)],
        )


class EChannelS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.E_CHANNEL.value,
            ind=0,
            values=[i for i in range(1, InitConfig().n_channels + 1)],
        )


class EModeS(SFunctionality):
    def __init__(self, valid_modes: List[str]):
        super().__init__(
            name=ValidSettings.E_MODE.value,
            ind=0,
            values=[k for k in valid_modes],
        )


# - - VIEW - - #


class VMiDiOS(SFunctionality):
    def __init__(self, midi_ids: List[int]):
        super().__init__(
            name=ValidSettings.V_MIDI_O.value,
            ind=0,
            values=deepcopy(sorted(midi_ids)),
        )


class VPartS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.V_PART.value,
            ind=0,
            values=[i for i in range(1, InitConfig().n_parts + 1)],
        )


class VStepS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.V_STEP.value,
            ind=0,
            values=[i for i in range(1, InitConfig().n_steps + 1)],
        )


class VChannelS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.V_CHANNEL.value,
            ind=0,
            values=[i for i in range(1, InitConfig().n_channels + 1)],
        )


class VModeS(SFunctionality):
    def __init__(self, valid_modes: List[str]):
        super().__init__(
            name=ValidSettings.V_MODE.value,
            ind=0,
            values=[k for k in valid_modes],
        )


# - - OTHER - - #


class ViewSS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.VIEW_SHOW.value,
            ind=0,
            values=[ValidButtons.OFF.value, ValidButtons.ON.value],
        )


class ViewFS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.VIEW_FUNCTION.value,
            ind=0,
            values=[
                ValidButtons.VIEW_ONLY,
                ValidButtons.VIEW_PLAY,
                ValidButtons.VIEW_REC,
            ],
        )


class PlaySS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.PLAY_SHOW.value,
            ind=0,
            values=[ValidButtons.OFF.value, ValidButtons.ON.value],
        )


class PlayFS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.PLAY_FUNCTION.value,
            ind=0,
            values=[
                ValidButtons.NA,
                ValidButtons.PLAY_PART,
                ValidButtons.PLAY_PARTS,
                ValidButtons.PLAY_ALL,
            ],
        )


class RecordS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.RECORD.value,
            ind=0,
            values=[ValidButtons.OFF.value, ValidButtons.ON.value],
        )


class CopyS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.COPY.value,
            ind=0,
            values=[ValidButtons.OFF.value, ValidButtons.ON.value],
        )


class TempoS(SFunctionality):
    def __init__(self):
        tempos = [
            i * InitConfig().tempo_step
            for i in range(InitConfig().tempo_min, InitConfig().tempo_max + 1)
        ]
        ind = tempos.index(InitConfig().init_tempo)
        super().__init__(
            name=ValidSettings.TEMPO.value,
            ind=ind,
            values=[str(tempo) for tempo in tempos],
        )


class PresetsS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.PRESETS.value,
            ind=0,
            values=[
                ValidButtons.PRESETS_OFF_MUSIC,
                ValidButtons.PRESETS_OFF_MAP,
                ValidButtons.PRESETS_ON_MUSIC,
                ValidButtons.PRESETS_ON_MAP,
                ValidButtons.PRESETS_L_MUSIC,
                ValidButtons.PRESETS_L_MAP,
            ],
        )


class MusNameS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.MUS_NAME.value,
            ind=0,
            values=[f"Music_{i:02}" for i in range(InitConfig().music_count)],
        )


class MapNameS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.MAP_NAME.value,
            ind=0,
            values=[f"Mappings_{i:02}" for i in range(InitConfig().map_count)],
        )
