from enum import Enum, StrEnum

from .configs import InitConfig


class ValidIndexes(Enum):
    VIS_INDEX_1 = 0
    VIS_INDEX_2 = 1


class ValidLengths(Enum):
    ZERO = 0
    DOUBLE = InitConfig().n_quants * 2
    FULL = InitConfig().n_quants
    HALF = InitConfig().n_quants // 2
    QUARTER = InitConfig().n_quants // 4


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
    PLAY_PART = "PPrt"
    PLAY_PARTS = "PPrts"
    PLAY_ALL = "PAll"
    VIEW_ONLY = "VOnly"
    VIEW_REC = "VRec"
    VIEW_PLAY = "VPlay"


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
    ValidButtons.PLAY_PART,
    ValidButtons.PLAY_PARTS,
    ValidButtons.PLAY_ALL,
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
    ValidButtons.VIEW_ONLY,
    ValidButtons.VIEW_REC,
    ValidButtons.VIEW_PLAY,
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
    VIEW_SHOW = "ViewS"
    VIEW_FUNCTION = "ViewF"
    COPY = "COPY"


class ValidModes(StrEnum):
    VOICE_1 = "Vo1"
    VOICE_2 = "Vo2"
    SCALE = "Sca"