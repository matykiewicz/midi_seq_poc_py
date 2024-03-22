from enum import StrEnum
from typing import Dict, List, Tuple, Union

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
    OCTAVE_1 = "Oc1"
    VOICE_2 = "Vo2"
    OCTAVE_2 = "Oc2"
    VOICE_3 = "Vo3"
    OCTAVE_3 = "Oc3"
    SCALE = "Sca"
    MOTION_1 = "Mo1"
    MOTION_2 = "Mo2"
    MOTION_3 = "Mo3"


@define
class NFunctionality(AttrsInstance):
    # Navigation & Menus
    name: str
    ind: int
    buttons: Tuple[ValidNav, ...]


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
    first_only: bool
    values: List[Union[str, int]]
    codes: List[int] = [0]


def init_nav() -> Dict[ValidNav, NFunctionality]:

    class Play(NFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidNav.PLAY,
                buttons=BUT_PLAY,
                ind=0,
            )

    class Record(NFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidNav.RECORD,
                buttons=BUT_REC,
                ind=0,
            )

    class View(NFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidNav.VIEW,
                buttons=BUT_VIEW,
                ind=0,
            )

    class Tempo(NFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidNav.TEMPO,
                buttons=BUT_TEMPO,
                ind=0,
            )

    class Copy(NFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidNav.COPY,
                buttons=BUT_COPY,
                ind=0,
            )

    return {
        ValidNav.RECORD: Record(),
        ValidNav.VIEW: View(),
        ValidNav.PLAY: Play(),
        ValidNav.TEMPO: Tempo(),
        ValidNav.COPY: Copy(),
    }


def init_settings(n_midis: int) -> Dict[ValidSettings, SFunctionality]:

    class Tempo(SFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidSettings.TEMPO,
                ind=0,
                values=[
                    i * InitConfig().tempo_step
                    for i in range(InitConfig().tempo_min, InitConfig().tempo_max + 1)
                ],
            )

    class Part(SFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidSettings.PART,
                ind=0,
                values=[i for i in range(1, InitConfig().parts + 1)],
            )

    class Step(SFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidSettings.STEP,
                ind=0,
                values=[i for i in range(1, InitConfig().steps + 1)],
            )

    class MIDI(SFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidSettings.MIDI,
                ind=0,
                values=[i for i in range(n_midis)],
            )

    class Channel(SFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidSettings.CHANNEL,
                ind=0,
                values=[i for i in range(1, InitConfig().n_channels + 1)],
            )

    class Mode(SFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidSettings.MODE,
                ind=0,
                values=[k for k in ValidModes],
            )

    class Record(SFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidSettings.RECORD,
                ind=0,
                values=["Off", "On"],
            )

    class View(SFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidSettings.VIEW,
                ind=0,
                values=["Off", "On"],
            )

    class Play(SFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidSettings.PLAY,
                ind=0,
                values=["Off", "On"],
            )

    class Copy(SFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidSettings.COPY,
                ind=0,
                values=["Off", "On"],
            )

    return {
        ValidSettings.TEMPO: Tempo(),
        ValidSettings.MIDI: MIDI(),
        ValidSettings.CHANNEL: Channel(),
        ValidSettings.MODE: Mode(),
        ValidSettings.PART: Part(),
        ValidSettings.STEP: Step(),
        ValidSettings.RECORD: Record(),
        ValidSettings.VIEW: View(),
        ValidSettings.PLAY: Play(),
        ValidSettings.COPY: Copy(),
    }


def init_modes() -> Dict[ValidModes, MFunctionality]:

    class Octave1(MFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidModes.OCTAVE_1,
                ind=0,
                first_only=False,
                values=[0]
                + [i for i in range(-InitConfig().octaves, InitConfig().octaves + 1)],
            )

    class Octave2(MFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidModes.OCTAVE_2,
                ind=0,
                first_only=False,
                values=[0]
                + [i for i in range(-InitConfig().octaves, InitConfig().octaves + 1)],
            )

    class Octave3(MFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidModes.OCTAVE_3,
                ind=0,
                first_only=False,
                values=[0]
                + [i for i in range(-InitConfig().octaves, InitConfig().octaves + 1)],
            )

    class Voice1(MFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidModes.VOICE_1,
                ind=0,
                first_only=False,
                values=[i for i in range(0, InitConfig().n_keys + 1)],
            )

    class Voice2(MFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidModes.VOICE_2,
                ind=0,
                first_only=False,
                values=[i for i in range(0, InitConfig().n_keys + 1)],
            )

    class Voice3(MFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidModes.VOICE_3,
                ind=0,
                first_only=False,
                values=[i for i in range(0, InitConfig().n_keys + 1)],
            )

    class Motion1(MFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidModes.MOTION_1,
                ind=0,
                first_only=False,
                values=[
                    round((i / InitConfig().n_keys) * 127)
                    for i in range(0, InitConfig().n_keys + 1)
                ],
            )

    class Motion2(MFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidModes.MOTION_2,
                ind=0,
                first_only=False,
                values=[
                    round((i / InitConfig().n_keys) * 127)
                    for i in range(0, InitConfig().n_keys + 1)
                ],
            )

    class Motion3(MFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidModes.MOTION_3,
                ind=0,
                first_only=False,
                values=[
                    round((i / InitConfig().n_keys) * 127)
                    for i in range(0, InitConfig().n_keys + 1)
                ],
            )

    class Scale(MFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidModes.SCALE,
                ind=0,
                first_only=True,
                values=["C"] + keys.major_keys + keys.minor_keys,
            )

    return {
        ValidModes.VOICE_1: Voice1(),
        ValidModes.OCTAVE_1: Octave1(),
        ValidModes.VOICE_2: Voice2(),
        ValidModes.OCTAVE_2: Octave2(),
        ValidModes.VOICE_3: Voice3(),
        ValidModes.OCTAVE_3: Octave3(),
        ValidModes.SCALE: Scale(),
        ValidModes.MOTION_1: Motion1(),
        ValidModes.MOTION_2: Motion2(),
        ValidModes.MOTION_3: Motion3(),
    }
