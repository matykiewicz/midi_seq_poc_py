from enum import StrEnum
from typing import Dict, List, Tuple, Union

from attrs import AttrsInstance, define
from mingus.core import keys

from .configs import InitConfig


class ValidButtons(StrEnum):
    OPT_UP = "Opt+"
    OPT_DOWN = "Opt-"
    SET_UP = "Set+"
    SET_DOWN = "Set-"
    BACK = "Back"
    ENTER = "Enter"
    EMPTY = ""
    DELETE = "Delete"
    VIEW = "View"
    PLAY = "Play"
    NEXT = "Next"
    PREVIOUS = "Previous"


BUT_REC = (
    ValidButtons.OPT_DOWN,
    ValidButtons.OPT_UP,
    ValidButtons.ENTER,
    ValidButtons.EMPTY,
    ValidButtons.BACK,
    ValidButtons.PREVIOUS,
    ValidButtons.NEXT,
    ValidButtons.DELETE,
)

BUT_PLAY = (
    ValidButtons.OPT_DOWN,
    ValidButtons.OPT_UP,
    ValidButtons.ENTER,
    ValidButtons.EMPTY,
    ValidButtons.BACK,
    ValidButtons.PREVIOUS,
    ValidButtons.NEXT,
    ValidButtons.PLAY,
)

BUT_VIEW = (
    ValidButtons.OPT_DOWN,
    ValidButtons.OPT_UP,
    ValidButtons.ENTER,
    ValidButtons.EMPTY,
    ValidButtons.BACK,
    ValidButtons.PREVIOUS,
    ValidButtons.NEXT,
    ValidButtons.VIEW,
)


class ValidNav(StrEnum):
    RECORD = "Record"
    VIEW = "View"
    PLAY = "Play"


class ValidSettings(StrEnum):
    TEMPO = "Tempo"
    MIDI = "MIDI"
    MODE = "Mode"
    SCALE = "Scale"
    PART = "Part"
    STEP = "Step"
    CHANNEL = "Channel"
    RECORD = "Channel"


class ValidModes(StrEnum):
    VOICE_1 = "Vo1"
    OCTAVE_1 = "Oc1"
    VOICE_2 = "Vo2"
    OCTAVE_2 = "Oc2"
    VOICE_3 = "Vo3"
    OCTAVE_3 = "Oc3"
    MOTION_1 = "Mo1"
    MOTION_2 = "Mo2"
    MOTION_3 = "Mo3"


@define
class NFunctionality(AttrsInstance):
    # Navigation & Menus
    name: str
    ind: int
    b_ind: int
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
    def_ind: int
    values: List[Union[str, int]]
    hex_codes: List[int] = list()


def init_nav() -> Dict[ValidNav, NFunctionality]:

    class Play(NFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidNav.PLAY,
                buttons=BUT_PLAY,
                ind=0,
                b_ind=0,
            )

    class Record(NFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidNav.RECORD,
                buttons=BUT_REC,
                ind=0,
                b_ind=0,
            )

    class View(NFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidNav.VIEW,
                buttons=BUT_VIEW,
                ind=0,
                b_ind=0,
            )

    return {
        ValidNav.RECORD: Record(),
        ValidNav.VIEW: View(),
        ValidNav.PLAY: Play(),
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

    class Scale(SFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidSettings.SCALE,
                ind=7,
                values=keys.major_keys + keys.minor_keys,
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
                name=ValidSettings.MODE,
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
        ValidSettings.SCALE: Scale(),
        ValidSettings.RECORD: Record(),
    }


def init_modes() -> Dict[ValidModes, MFunctionality]:

    class Octave1(MFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidModes.OCTAVE_1.value,
                ind=2,
                def_ind=2,
                values=[
                    i for i in range(-InitConfig().octaves, InitConfig().octaves + 1)
                ],
            )

    class Octave2(MFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidModes.OCTAVE_2.value,
                ind=2,
                def_ind=2,
                values=[
                    i for i in range(-InitConfig().octaves, InitConfig().octaves + 1)
                ],
            )

    class Octave3(MFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidModes.OCTAVE_3.value,
                ind=2,
                def_ind=2,
                values=[
                    i for i in range(-InitConfig().octaves, InitConfig().octaves + 1)
                ],
            )

    class Voice1(MFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidModes.VOICE_1.value,
                ind=0,
                def_ind=0,
                values=[i for i in range(0, InitConfig().n_keys + 1)],
            )

    class Voice2(MFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidModes.VOICE_2.value,
                ind=0,
                def_ind=0,
                values=[i for i in range(0, InitConfig().n_keys + 1)],
            )

    class Voice3(MFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidModes.VOICE_3.value,
                ind=0,
                def_ind=0,
                values=[i for i in range(0, InitConfig().n_keys + 1)],
            )

    class Motion1(MFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidModes.MOTION_1.value,
                ind=0,
                def_ind=0,
                values=[i for i in range(0, InitConfig().n_keys + 1)],
            )

    class Motion2(MFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidModes.MOTION_2.value,
                ind=0,
                def_ind=0,
                values=[i for i in range(0, InitConfig().n_keys + 1)],
            )

    class Motion3(MFunctionality):
        def __init__(self):
            super().__init__(
                name=ValidModes.MOTION_3.value,
                ind=0,
                def_ind=0,
                values=[i for i in range(0, InitConfig().n_keys + 1)],
            )

    return {
        ValidModes.VOICE_1: Voice1(),
        ValidModes.OCTAVE_1: Octave1(),
        ValidModes.VOICE_2: Voice2(),
        ValidModes.OCTAVE_2: Octave2(),
        ValidModes.VOICE_3: Voice3(),
        ValidModes.OCTAVE_3: Octave3(),
        ValidModes.MOTION_1: Motion1(),
        ValidModes.MOTION_2: Motion2(),
        ValidModes.MOTION_3: Motion3(),
    }
