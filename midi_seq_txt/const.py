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
    O_MODE = "OMode"
    TEMPO_UP = "Temp+"
    TEMPO_DOWN = "Temp-"
    NEXT = "Next"
    NA = "NA"
    LENGTH = "Length"
    ZERO = "0"
    VELOCITY = "Velocity"
    SCALE = "Scale"
    PLAY_PART = "PPrt"
    PLAY_PARTS = "PPrts"
    PLAY_ALL = "PAll"
    VIEW_ONLY = "VOnly"
    VIEW_REC = "VRec"
    VIEW_PLAY = "VPlay"
    ON = "On"
    OFF = "Off"
    PRESETS_OFF_MUSIC = "MusOff"
    PRESETS_ON_MUSIC = "MusOn"
    PRESETS_L_MUSIC = "LoMusic"
    PRESETS_N_MUSIC = "+Music"
    PRESETS_S_MUSIC = "SaMusic"
    PRESETS_OFF_MAP = "MapOff"
    PRESETS_ON_MAP = "MapOn"
    PRESETS_L_MAP = "LoMap"
    PRESETS_N_MAP = "+Map"
    PRESETS_S_MAP = "SaMap"
    PRESETS_E_MAP_ON = "EdMaOn"
    PRESETS_E_MAP_OFF = "EdMaOff"
    PRESETS_E_MAP_N_CONN = "+Conn"
    PRESETS_E_MAP_N_MIDI = "+Midi"
    PRESETS_E_MAP_N_DIR = "+Dir"
    PRESETS_E_MAP_N_CH = "+Chan"
    PRESETS_E_MAP_N_PNAME = "+PoNa"
    PRESETS_E_MAP_N_INSTR_1 = "+Ins1"
    PRESETS_E_MAP_N_INSTR_2 = "+Ins2"


BUT_PRES = (
    ValidButtons.OPT_DOWN,
    ValidButtons.OPT_UP,
    ValidButtons.PRESETS_ON_MUSIC,
    ValidButtons.PRESETS_ON_MAP,
    ValidButtons.MIDI,
    ValidButtons.CHANNEL,
    ValidButtons.PART,
    ValidButtons.O_MODE,
    ValidButtons.PRESETS_OFF_MUSIC,
    ValidButtons.PRESETS_N_MUSIC,
    ValidButtons.PRESETS_L_MUSIC,
    ValidButtons.PRESETS_S_MUSIC,
    ValidButtons.MIDI,
    ValidButtons.CHANNEL,
    ValidButtons.PART,
    ValidButtons.O_MODE,
    ValidButtons.PRESETS_OFF_MAP,
    ValidButtons.PRESETS_N_MAP,
    ValidButtons.PRESETS_L_MAP,
    ValidButtons.PRESETS_S_MAP,
    ValidButtons.PRESETS_E_MAP_ON,
    ValidButtons.EMPTY,
    ValidButtons.EMPTY,
    ValidButtons.EMPTY,
    ValidButtons.PRESETS_E_MAP_OFF,
    ValidButtons.PRESETS_E_MAP_N_CONN,
    ValidButtons.PRESETS_E_MAP_N_DIR,
    ValidButtons.PRESETS_E_MAP_N_MIDI,
    ValidButtons.PRESETS_E_MAP_N_PNAME,
    ValidButtons.PRESETS_E_MAP_N_CH,
    ValidButtons.PRESETS_E_MAP_N_INSTR_1,
    ValidButtons.PRESETS_E_MAP_N_INSTR_2,
)

BUT_TEMPO = (
    ValidButtons.OPT_DOWN,
    ValidButtons.OPT_UP,
    ValidButtons.TEMPO_DOWN,
    ValidButtons.TEMPO_UP,
    ValidButtons.MIDI,
    ValidButtons.CHANNEL,
    ValidButtons.PART,
    ValidButtons.O_MODE,
)

BUT_REC = (
    ValidButtons.OPT_DOWN,
    ValidButtons.OPT_UP,
    ValidButtons.REC_ON,
    ValidButtons.EMPTY,
    ValidButtons.MIDI,
    ValidButtons.CHANNEL,
    ValidButtons.PART,
    ValidButtons.O_MODE,
    ValidButtons.REC_OFF,
    ValidButtons.VELOCITY,
    ValidButtons.LENGTH,
    ValidButtons.SCALE,
    ValidButtons.SKIP,
    ValidButtons.DELETE,
    ValidButtons.PART,
    ValidButtons.O_MODE,
)

BUT_PLAY = (
    ValidButtons.OPT_DOWN,
    ValidButtons.OPT_UP,
    ValidButtons.PLAY_ON,
    ValidButtons.EMPTY,
    ValidButtons.MIDI,
    ValidButtons.CHANNEL,
    ValidButtons.PART,
    ValidButtons.O_MODE,
    ValidButtons.PLAY_OFF,
    ValidButtons.PLAY_PART,
    ValidButtons.PLAY_PARTS,
    ValidButtons.PLAY_ALL,
    ValidButtons.MIDI,
    ValidButtons.CHANNEL,
    ValidButtons.PART,
    ValidButtons.O_MODE,
)

BUT_VIEW = (
    ValidButtons.OPT_DOWN,
    ValidButtons.OPT_UP,
    ValidButtons.VIEW_ON,
    ValidButtons.EMPTY,
    ValidButtons.MIDI,
    ValidButtons.CHANNEL,
    ValidButtons.PART,
    ValidButtons.O_MODE,
    ValidButtons.VIEW_OFF,
    ValidButtons.VIEW_ONLY,
    ValidButtons.VIEW_REC,
    ValidButtons.VIEW_PLAY,
    ValidButtons.MIDI,
    ValidButtons.CHANNEL,
    ValidButtons.PART,
    ValidButtons.O_MODE,
)

BUT_COPY = (
    ValidButtons.OPT_DOWN,
    ValidButtons.OPT_UP,
    ValidButtons.COPY_ON,
    ValidButtons.EMPTY,
    ValidButtons.MIDI,
    ValidButtons.CHANNEL,
    ValidButtons.PART,
    ValidButtons.O_MODE,
    ValidButtons.COPY_OFF,
    ValidButtons.C_RANDOM,
    ValidButtons.C_REVERSE,
    ValidButtons.C_AS_IS,
    ValidButtons.MIDI,
    ValidButtons.CHANNEL,
    ValidButtons.PART,
    ValidButtons.O_MODE,
)


class ValidNav(StrEnum):
    RECORD = "Record"
    COPY = "Copy"
    VIEW = "View"
    PLAY = "Play"
    TEMPO = "Tempo"
    PRESETS = "Presets"


class ValidSettings(StrEnum):
    E_MIDI_O = "EMiDiO"
    E_PART = "EPart"
    E_STEP = "EStep"
    E_CHANNEL = "EChannel"
    E_O_MODE = "EOMode"
    V_MIDI_O = "VMiDiO"
    V_PART = "VPart"
    V_STEP = "VStep"
    V_CHANNEL = "VChannel"
    V_O_MODE = "VOMode"
    VIEW_SHOW = "ViewS"
    VIEW_FUNCTION = "ViewF"
    PLAY_SHOW = "PlayS"
    PLAY_FUNCTION = "PlayF"
    RECORD = "Record"
    COPY = "COPY"
    TEMPO = "Tempo"
    PRESETS = "Presets"
    MUS_NAME = "MusName"
    MAP_NAME = "MapName"
    MAP_E_CONN = "MapEditConn"
    MAP_E_MIDI = "MapEditMidi"
    MAP_E_DIR = "MapEditDir"
    MAP_E_CH = "MapEditCh"
    MAP_E_PNAME = "MapEditPortName"
    MAP_E_INSTR_1 = "MapEditInstr1"
    MAP_E_INSTR_2 = "MapEditInstr2"


class ValidInstruments(StrEnum):
    GENERIC_IN = "GenericIn"
    GENERIC_OUT = "GenericOut"
    VOLCA_DRUM_OUT = "Volca Drum Out"
    VOLCA_KEYS_OUT = "Volca Keys Out"
    VOLCA_BASS_OUT = "Volca Bass Out"
    VOLCA_FM2_OUT = "Volca FM2 Out"
    VOLCA_FM2_IN = "Volca FM2 In"
