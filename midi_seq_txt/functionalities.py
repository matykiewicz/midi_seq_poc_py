from enum import StrEnum
from typing import Dict, List, Tuple, Union

import mingus.core.scales as scales
from attrs import AttrsInstance, define
from mingus.core import keys

from .configs import InitConfig


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
    ValidButtons.EMPTY,
    ValidButtons.SKIP,
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
    VOICE_3 = "Vo3"
    SCALE = "Sca"
    MOTION_1 = "Mo1"
    MOTION_2 = "Mo2"
    MOTION_3 = "Mo3"


@define
class NFunctionality(AttrsInstance):
    # Navigation & Menus
    name: str
    ind: int
    buttons: Tuple[ValidButtons, ...]


@define
class SFunctionality(AttrsInstance):
    # Sequencers & Settings
    name: str
    ind: int
    values: List[Union[str, int]]


@define
class MFunctionality(AttrsInstance):
    # MIDI & Modes
    name: str
    ind: int
    offset: int
    first_only: bool
    values: List[str]
    codes: List[int] = [0]


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
        super().__init__(
            name=ValidSettings.TEMPO,
            ind=0,
            values=[
                str(i * InitConfig().tempo_step)
                for i in range(InitConfig().tempo_min, InitConfig().tempo_max + 1)
            ],
        )


class PartS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.PART,
            ind=0,
            values=[i for i in range(1, InitConfig().parts + 1)],
        )


class StepS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.STEP,
            ind=0,
            values=[i for i in range(1, InitConfig().steps + 1)],
        )


class MIDIS(SFunctionality):
    def __init__(self, n_midis: int):
        super().__init__(
            name=ValidSettings.MIDI,
            ind=0,
            values=[i for i in range(n_midis)],
        )


class ChannelS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.CHANNEL,
            ind=0,
            values=[i for i in range(1, InitConfig().n_channels + 1)],
        )


class ModeS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.MODE,
            ind=0,
            values=[k for k in ValidModes],
        )


class RecordS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.RECORD,
            ind=0,
            values=["Off", "On"],
        )


class ViewS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.VIEW,
            ind=0,
            values=["Off", "On"],
        )


class PlayS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.PLAY,
            ind=0,
            values=["Off", "On"],
        )


class CopyS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.COPY,
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


def init_modes() -> Dict[ValidModes, MFunctionality]:

    class Voice1(MFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidModes.VOICE_1,
                ind=0,
                offset=1 + 8 * 2,
                first_only=False,
                codes=[0x90, 0x80],
                values=create_notes("C"),
            )

    class Voice2(MFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidModes.VOICE_2,
                ind=0,
                offset=1 + 8 * 2,
                first_only=False,
                codes=[0x90, 0x80],
                values=create_notes("C"),
            )

    class Voice3(MFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidModes.VOICE_3,
                ind=0,
                offset=1 + 8 * 2,
                first_only=False,
                codes=[0x90, 0x80],
                values=create_notes("C"),
            )

    class Motion1(MFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidModes.MOTION_1,
                ind=0,
                offset=1,
                first_only=False,
                values=create_motions(),
            )

    class Motion2(MFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidModes.MOTION_2,
                ind=0,
                offset=1,
                first_only=False,
                values=create_motions(),
            )

    class Motion3(MFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidModes.MOTION_3,
                ind=0,
                offset=1,
                first_only=False,
                values=create_motions(),
            )

    class Scale(MFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidModes.SCALE,
                ind=0,
                offset=9,
                first_only=True,
                values=create_scales(),
            )

    return {
        ValidModes.VOICE_1: Voice1(),
        ValidModes.VOICE_2: Voice2(),
        ValidModes.VOICE_3: Voice3(),
        ValidModes.SCALE: Scale(),
        ValidModes.MOTION_1: Motion1(),
        ValidModes.MOTION_2: Motion2(),
        ValidModes.MOTION_3: Motion3(),
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
    button_notes = ["NA"]
    for octave in range(1, InitConfig().octaves + 1):
        for note in notes:
            no_button_notes.append(f"{note}{octave}")
    n_keys = InitConfig().n_keys
    for i in range(len(no_button_notes)):
        if (i + 1) % (n_keys - 1) == 0:
            button_notes.append(no_button_notes[i])
            button_notes.append(ValidButtons.NEXT)
        else:
            button_notes.append(no_button_notes[i])
    return button_notes


def create_motions() -> List[str]:
    no_button_motions = list()
    button_motions = ["0"]
    for i in range(1, InitConfig().n_motions):
        motion = round((i / InitConfig().n_motions) * 127)
        no_button_motions.append(motion)
    n_keys = InitConfig().n_keys
    for i in range(len(no_button_motions)):
        if (i + 1) % (n_keys - 1) == 0:
            button_motions.append(str(no_button_motions[i]))
            button_motions.append(ValidButtons.NEXT)
        else:
            button_motions.append(str(no_button_motions[i]))
    return button_motions
