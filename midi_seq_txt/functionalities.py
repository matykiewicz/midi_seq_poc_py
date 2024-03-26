from copy import deepcopy
from enum import Enum, StrEnum
from typing import Any, Dict, List, Optional, Tuple, Type, Union

import mingus.core.scales as scales
from attrs import AttrsInstance, define
from mingus.core import keys

from .configs import InitConfig


class ValidLengths(Enum):
    ZERO = 0
    FULL = InitConfig().n_quants
    HALF = InitConfig().n_quants // 2
    QUARTER = InitConfig().n_quants // 4


INTERVAL_MATCHES: Dict[int, ValidLengths] = {
    4: ValidLengths.FULL,
    2: ValidLengths.HALF,
    1: ValidLengths.QUARTER,
}


class ValidButtons(StrEnum):
    OPT_UP = "Opt+"
    OPT_DOWN = "Opt-"
    EMPTY = ""
    REC_ON = "RecOn"
    REC_OFF = "RecOff"
    VIEW_ON = "ViewSet"
    VIEW_OFF = "ViewExit"
    PLAY_ON = "PlayOn"
    PLAY_OFF = "PlayOff"
    COPY_ON = "CopyOn"
    COPY_OFF = "CopyOff"
    C_RANDOM = "Random"
    C_REVERSE = "Reverse"
    C_AS_IS = "AsIs"
    SKIP = "Skip"
    DELETE = "Delete"
    MIDI = "Midi"
    CHANNEL = "Channel"
    PART = "Part"
    MODE = "Mode"
    TEMPO_UP = "Temp+"
    TEMPO_DOWN = "Temp-"
    NEXT = "Next"
    NA = "NA"
    LENGTH = "Length"
    ZERO = "0"
    VELOCITY = "Velocity"


BUT_TEMPO = (
    ValidButtons.OPT_DOWN,
    ValidButtons.OPT_UP,
    ValidButtons.TEMPO_DOWN,
    ValidButtons.TEMPO_UP,
    ValidButtons.MIDI,
    ValidButtons.CHANNEL,
    ValidButtons.PART,
    ValidButtons.MODE,
)

BUT_REC = (
    ValidButtons.OPT_DOWN,
    ValidButtons.OPT_UP,
    ValidButtons.REC_ON,
    ValidButtons.EMPTY,
    ValidButtons.MIDI,
    ValidButtons.CHANNEL,
    ValidButtons.PART,
    ValidButtons.MODE,
    ValidButtons.REC_OFF,
    ValidButtons.LENGTH,
    ValidButtons.VELOCITY,
    ValidButtons.DELETE,
    ValidButtons.MIDI,
    ValidButtons.CHANNEL,
    ValidButtons.PART,
    ValidButtons.MODE,
)

BUT_PLAY = (
    ValidButtons.OPT_DOWN,
    ValidButtons.OPT_UP,
    ValidButtons.PLAY_ON,
    ValidButtons.EMPTY,
    ValidButtons.MIDI,
    ValidButtons.CHANNEL,
    ValidButtons.PART,
    ValidButtons.MODE,
    ValidButtons.PLAY_OFF,
    ValidButtons.EMPTY,
    ValidButtons.EMPTY,
    ValidButtons.EMPTY,
    ValidButtons.MIDI,
    ValidButtons.CHANNEL,
    ValidButtons.PART,
    ValidButtons.MODE,
)

BUT_VIEW = (
    ValidButtons.OPT_DOWN,
    ValidButtons.OPT_UP,
    ValidButtons.VIEW_ON,
    ValidButtons.EMPTY,
    ValidButtons.MIDI,
    ValidButtons.CHANNEL,
    ValidButtons.PART,
    ValidButtons.MODE,
    ValidButtons.VIEW_OFF,
    ValidButtons.EMPTY,
    ValidButtons.EMPTY,
    ValidButtons.EMPTY,
    ValidButtons.MIDI,
    ValidButtons.CHANNEL,
    ValidButtons.PART,
    ValidButtons.MODE,
)

BUT_COPY = (
    ValidButtons.OPT_DOWN,
    ValidButtons.OPT_UP,
    ValidButtons.COPY_ON,
    ValidButtons.EMPTY,
    ValidButtons.MIDI,
    ValidButtons.CHANNEL,
    ValidButtons.PART,
    ValidButtons.MODE,
    ValidButtons.COPY_OFF,
    ValidButtons.C_RANDOM,
    ValidButtons.C_REVERSE,
    ValidButtons.C_AS_IS,
    ValidButtons.MIDI,
    ValidButtons.CHANNEL,
    ValidButtons.PART,
    ValidButtons.MODE,
)


class ValidNav(StrEnum):
    RECORD = "Record"
    COPY = "Copy"
    VIEW = "View"
    PLAY = "Play"
    TEMPO = "Tempo"


class ValidSettings(StrEnum):
    TEMPO = "Tempo"
    MIDI = "MIDI"
    MODE = "Mode"
    PART = "Part"
    STEP = "Step"
    CHANNEL = "Channel"
    RECORD = "Record"
    PLAY = "Play"
    VIEW = "View"
    COPY = "COPY"


class ValidModes(StrEnum):
    VOICE_1 = "Vo1"
    VOICE_2 = "Vo2"
    SCALE = "Sca"


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
        return self.indexes

    def get_offsets(self) -> List[int]:
        return self.offsets

    def get_labels(self) -> List[str]:
        return self.labels

    def get_values(self, indexes: Optional[List[List[int]]] = None) -> List[List[str]]:
        values: List[List[str]] = list()
        if indexes is None:
            indexes = self.indexes
        for i in range(len(indexes)):
            value = list()
            for j, index in enumerate(indexes[i]):
                value.append(self.data[j][index])
            values.append(value)
        return values

    def get_single_value_by_off(self, off: str, ind: int) -> str:
        off_int = self.labels.index(off)
        if off_int < len(self.data):
            ind = self.offsets[off_int] + ind
            if ind < len(self.data[off_int]):
                return self.data[off_int][ind]
        return ValidButtons.NA

    def get_single_value_by_lab(self, exe: int, lab: str) -> str:
        if exe < len(self.indexes):
            if lab in self.labels:
                ind = self.labels.index(lab)
                if ind < len(self.indexes[exe]):
                    return self.data[ind][self.indexes[exe][ind]]
        return ValidButtons.NA

    def get_row_values(self, exe: int) -> List[str]:
        values: List[str] = list()
        if exe < len(self.indexes):
            for j in range(len(self.indexes[exe])):
                values.append(self.data[j][self.indexes[exe][j]])
        return values

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
        off_int = self.labels.index(off)
        ind = self.offsets[off_int] + ind
        if off_int < len(self.data):
            for i in range(len(self.indexes)):
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

    def set_schedule(self, clock: float) -> "MFunctionality":
        pass

    def get_schedule(self) -> float:
        pass

    def execute(self, types: List[Type]) -> List[Any]:
        values_any: List[Any] = list()
        if self._exe_ < len(self.indexes):
            values_str = self.get_row_values(exe=self._exe_)
            for i, cast in enumerate(types):
                values_any.append(cast(values_str[i]))
        self._exe_ += 1
        return values_any


class PlayN(NFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidNav.PLAY,
            buttons=BUT_PLAY,
            ind=0,
        )


class RecordN(NFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidNav.RECORD,
            buttons=BUT_REC,
            ind=0,
        )


class ViewN(NFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidNav.VIEW,
            buttons=BUT_VIEW,
            ind=0,
        )


class TempoN(NFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidNav.TEMPO,
            buttons=BUT_TEMPO,
            ind=0,
        )


class CopyN(NFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidNav.COPY,
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


class PartS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.PART.value,
            ind=0,
            values=[i for i in range(1, InitConfig().n_parts + 1)],
        )


class StepS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.STEP.value,
            ind=0,
            values=[i for i in range(1, InitConfig().n_steps + 1)],
        )


class MIDIS(SFunctionality):
    def __init__(self, n_midis: int):
        super().__init__(
            name=ValidSettings.MIDI.value,
            ind=0,
            values=[i for i in range(n_midis)],
        )


class ChannelS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.CHANNEL.value,
            ind=0,
            values=[i for i in range(1, InitConfig().n_channels + 1)],
        )


class ModeS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.MODE.value,
            ind=0,
            values=[k for k in ValidModes],
        )


class RecordS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.RECORD.value,
            ind=0,
            values=["Off", "On"],
        )


class ViewS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.VIEW.value,
            ind=0,
            values=["Off", "On"],
        )


class PlayS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.PLAY.value,
            ind=0,
            values=["Off", "On"],
        )


class CopyS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.COPY.value,
            ind=0,
            values=["Off", "On"],
        )


def init_settings(n_midis: int) -> Dict[ValidSettings, SFunctionality]:
    return {
        ValidSettings.TEMPO: TempoS(),
        ValidSettings.MIDI: MIDIS(n_midis=n_midis),
        ValidSettings.CHANNEL: ChannelS(),
        ValidSettings.MODE: ModeS(),
        ValidSettings.PART: PartS(),
        ValidSettings.STEP: StepS(),
        ValidSettings.RECORD: RecordS(),
        ValidSettings.VIEW: ViewS(),
        ValidSettings.PLAY: PlayS(),
        ValidSettings.COPY: CopyS(),
    }


class Voice1(MFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidModes.VOICE_1.value,
            first_only=False,
            indexes=[[1, 0, 6, 1], [2, 0, 0, 0]],
            offsets=[1, 1 + 8 * 2, 6, 1],
            labels=["Code", "Note", "Velocity", "Length"],
            data=[
                [str(0), str(0x90), str(0x80)],
                create_notes(scale="C"),
                [
                    str(i * InitConfig().velocity_step)
                    for i in range(
                        InitConfig().velocity_min, InitConfig().velocity_max + 1
                    )
                ],
                [str(x.value) for x in list(ValidLengths)],
            ],
        )


class Voice2(MFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidModes.VOICE_1.value,
            first_only=False,
            indexes=[[1, 0, 6, 1], [2, 0, 0, 0]],
            offsets=[1, 1 + 8 * 2, 1, 6],
            labels=["Code", "Note", "Velocity", "Length"],
            data=[
                [str(0), str(0x90), str(0x80)],
                create_notes(scale="C"),
                [
                    str(i * InitConfig().velocity_step)
                    for i in range(
                        InitConfig().velocity_min, InitConfig().velocity_max + 1
                    )
                ],
                [str(x) for x in list(ValidLengths)],
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
