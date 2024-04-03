from enum import Enum, StrEnum

from .configs import InitConfig


class ValidLengths(Enum):
    ZERO = 0
    FULL = InitConfig().n_quants
    HALF = InitConfig().n_quants // 2
    QUARTER = InitConfig().n_quants // 4
    DOUBLE = InitConfig().n_quants * 2


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
    ON = "On"
    OFF = "Off"
    PRESETS_EDIT = "PrstEd"
    PRESETS_LOAD = "PrstLo"
    PRESETS_SAVE = "PrstSa"
    PRESETS_L_MSGS = "LMsgs"
    PRESETS_L_INSTR = "LInstr"
    PRESETS_L_MAPPING = "LMap"
    PRESETS_L_MUSIC = "LMusic"
    PRESETS_S_MSGS = "SMsgs"
    PRESETS_S_INSTR = "SInstr"
    PRESETS_S_MAPPING = "SMap"
    PRESETS_S_MUSIC = "SMusic"
    MUSIC_LIST = "MUSIC_LIST"
    MUSIC_NAME = "MUSIC_NAME"
    MAPPING_LIST = "MAPPING_LIST"
    MAPPING_EDIT = "MAPPING_EDIT"
    INSTR_LIST = "INSTR_LIST"
    INSTR_EDIT = "INSTR_EDIT"
    MSGS_LIST = "MSGS_LIST"
    MSGS_EDIT = "MSGS_EDIT"


BUT_PRES = (
    ValidButtons.OPT_DOWN,
    ValidButtons.OPT_UP,
    ValidButtons.PRESETS_LOAD,
    ValidButtons.PRESETS_SAVE,
    ValidButtons.MIDI,
    ValidButtons.CHANNEL,
    ValidButtons.PART,
    ValidButtons.MODE,
)

BUT_EDIT = (
    ValidButtons.OPT_DOWN,
    ValidButtons.OPT_UP,
    ValidButtons.PRESETS_EDIT,
    ValidButtons.EMPTY,
    ValidButtons.MIDI,
    ValidButtons.CHANNEL,
    ValidButtons.PART,
    ValidButtons.MODE,
)

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
    ValidButtons.SKIP,
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
    PRESETS = "Presets"
    EDITS = "Edits"


class ValidSettings(StrEnum):
    E_MIDI_O = "EMiDiO"
    E_PART = "EPart"
    E_STEP = "EStep"
    E_CHANNEL = "EChannel"
    E_MODE = "EMode"
    V_MIDI_O = "VMiDiO"
    V_PART = "VPart"
    V_STEP = "VStep"
    V_CHANNEL = "VChannel"
    V_MODE = "VMode"
    VIEW_SHOW = "ViewS"
    VIEW_FUNCTION = "ViewF"
    PLAY_SHOW = "PlayS"
    PLAY_FUNCTION = "PlayF"
    RECORD = "Record"
    COPY = "COPY"
    TEMPO = "Tempo"


class ValidInstruments(StrEnum):
    GENERIC = "Generic"
    VOLCA_DRUM = "Volca Drum"
    VOLCA_KEYS = "Volca Keys"
    VOLCA_BASS = "Volca Bass"
    VOLCA_FM2 = "Volca FM2"


class ValidPresets(StrEnum):
    INSTRUMENT_MAPPING = "Instrument Mapping"
    SEQUENCED_MUSIC = "Sequenced Music"
