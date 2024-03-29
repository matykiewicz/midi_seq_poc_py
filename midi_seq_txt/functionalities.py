from copy import deepcopy
from typing import Dict, List, Optional, Tuple, Union

import mingus.core.scales as scales
from attrs import AttrsInstance, define
from mingus.containers import Note
from mingus.core import keys

from .configs import InitConfig
from .const import (
    BUT_COPY,
    BUT_PLAY,
    BUT_REC,
    BUT_TEMPO,
    BUT_VIEW,
    ValidButtons,
    ValidLengths,
    ValidModes,
    ValidNav,
    ValidSettings,
)


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
    first_only: bool
    indexes: List[List[int]]
    labels: List[str]
    offsets: List[int]
    data: List[List[str]]
    vis_ind: Tuple[int, int]
    _exe_: int = 0
    _lock_: bool = True

    def update_offsets_with_lab(self, lab: str, by: int) -> "MFunctionality":
        if lab in self.labels:
            off_int = self.labels.index(lab)
            if off_int < len(self.data):
                if self.offsets[off_int] + by >= len(self.data[off_int]):
                    self.offsets[off_int] = 1
                else:
                    self.offsets[off_int] += by
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
        return ValidButtons.NA

    def get_single_value_by_lab(self, exe: int, lab: str) -> str:
        if exe < len(self.indexes):
            if lab in self.labels:
                ind = self.labels.index(lab)
                if ind < len(self.indexes[exe]):
                    return deepcopy(self.data[ind][self.indexes[exe][ind]])
        return ValidButtons.NA

    def get_row_values(self, exe: int) -> List[str]:
        values: List[str] = list()
        if exe < len(self.indexes):
            for j in range(len(self.indexes[exe])):
                values.append(deepcopy(self.data[j][self.indexes[exe][j]]))
        return values

    def get_vis_ind(self) -> Tuple[int, int]:
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
            elif lab == "Scale":
                value_int = 0
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


def init_nav() -> Dict[ValidNav, NFunctionality]:
    return {
        ValidNav.RECORD: RecordN(),
        ValidNav.VIEW: ViewN(),
        ValidNav.PLAY: PlayN(),
        ValidNav.TEMPO: TempoN(),
        ValidNav.COPY: CopyN(),
    }


# - - EDIT POS - - #


class EMiDiOS(SFunctionality):
    def __init__(self, n_midis: int):
        super().__init__(
            name=ValidSettings.E_MIDI_O.value,
            ind=0,
            values=[i for i in range(n_midis)],
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
    def __init__(self):
        super().__init__(
            name=ValidSettings.E_MODE.value,
            ind=0,
            values=[k for k in ValidModes],
        )


# - - VIEW - - #


class VMiDiOS(SFunctionality):
    def __init__(self, n_midis: int):
        super().__init__(
            name=ValidSettings.V_MIDI_O.value,
            ind=0,
            values=[i for i in range(n_midis)],
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
    def __init__(self):
        super().__init__(
            name=ValidSettings.V_MODE.value,
            ind=0,
            values=[k for k in ValidModes],
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
            values=[ValidButtons.PLAY_PART, ValidButtons.PLAY_PARTS, ValidButtons.PLAY_ALL],
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


def init_settings(n_midis: int) -> Dict[ValidSettings, SFunctionality]:
    return {
        ValidSettings.E_MIDI_O: EMiDiOS(n_midis=n_midis),
        ValidSettings.E_CHANNEL: EChannelS(),
        ValidSettings.E_PART: EPartS(),
        ValidSettings.E_STEP: EStepS(),
        ValidSettings.E_MODE: EModeS(),
        ValidSettings.V_MIDI_O: VMiDiOS(n_midis=n_midis),
        ValidSettings.V_CHANNEL: VChannelS(),
        ValidSettings.V_PART: VPartS(),
        ValidSettings.V_STEP: VStepS(),
        ValidSettings.V_MODE: VModeS(),
        ValidSettings.TEMPO: TempoS(),
        ValidSettings.RECORD: RecordS(),
        ValidSettings.COPY: CopyS(),
        ValidSettings.VIEW_SHOW: ViewSS(),
        ValidSettings.VIEW_FUNCTION: ViewFS(),
        ValidSettings.PLAY_SHOW: PlaySS(),
        ValidSettings.PLAY_FUNCTION: PlayFS(),
    }


class Voice1(MFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidModes.VOICE_1.value,
            first_only=False,
            indexes=[[1, 0, 6, 1], [2, 0, 0, 0]],
            offsets=[1, 1 + 8 * 2, 6, 1],
            labels=["Code", "Note", "Velocity", "Length"],
            vis_ind=(0, 1),
            data=[
                [str(0), str(0x90), str(0x80)],
                create_notes(scale="C"),
                [
                    str(i * InitConfig().velocity_step)
                    for i in range(InitConfig().velocity_min, InitConfig().velocity_max + 1)
                ],
                [str(x.value) for x in list(ValidLengths)],
            ],
        )


class Voice2(MFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidModes.VOICE_2.value,
            first_only=False,
            indexes=[[1, 0, 6, 1], [2, 0, 0, 0]],
            offsets=[1, 1 + 8 * 2, 6, 1],
            labels=["Code", "Note", "Velocity", "Length"],
            vis_ind=(0, 1),
            data=[
                [str(0), str(0x90), str(0x80)],
                create_notes(scale="C"),
                [
                    str(i * InitConfig().velocity_step)
                    for i in range(InitConfig().velocity_min, InitConfig().velocity_max + 1)
                ],
                [str(x.value) for x in list(ValidLengths)],
            ],
        )


# class Motion1(MFunctionality):
#    def __init__(self):
#        super().__init__(
#            name=ValidModes.MOTION_1.value,
#            ind=0,
#            offset=1,
#            first_only=False,
#            values=create_motions(),
#        )


class Scale(MFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidModes.SCALE.value,
            first_only=True,
            indexes=[[0]],
            offsets=[1],
            labels=["Scale"],
            vis_ind=(0, 0),
            data=[create_scales()],
        )


def init_modes() -> Dict[ValidModes, MFunctionality]:
    return {
        ValidModes.VOICE_1: Voice1(),
        ValidModes.VOICE_2: Voice2(),
        ValidModes.SCALE: Scale(),
    }


def create_scales() -> List[str]:
    no_button_scales = keys.major_keys + keys.minor_keys
    button_scale = ["C"]
    n_keys = InitConfig().n_keys
    for i in range(len(no_button_scales)):
        if (i + 1) % (n_keys - 1) == 0:
            button_scale.append(no_button_scales[i])
            button_scale.append(ValidButtons.NEXT)
        else:
            button_scale.append(no_button_scales[i])
    return button_scale


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
    return button_notes


def create_motions() -> List[str]:
    no_button_motions = list()
    button_motions = [ValidButtons.ZERO.value]
    for i in range(1, InitConfig().n_motions):
        motion = round((i / InitConfig().n_motions) * 127)
        no_button_motions.append(motion)
    n_keys = InitConfig().n_keys
    for i in range(len(no_button_motions)):
        if (i + 1) % (n_keys - 1) == 0:
            button_motions.append(str(no_button_motions[i]))
            button_motions.append(ValidButtons.NEXT.value)
        else:
            button_motions.append(str(no_button_motions[i]))
    return button_motions
