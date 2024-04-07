from collections import defaultdict
from typing import Dict, List

from mingus.core import keys

from .configs import InitConfig
from .const import ValidButtons, ValidInstruments, ValidLengths, ValidNav, ValidSettings
from .functionalities import (
    CopyN,
    CopyS,
    EChannelS,
    EMiDiOS,
    EModeS,
    EPartS,
    EStepS,
    MFunctionality,
    MMapping,
    MMappings,
    MMusic,
    NFunctionality,
    PlayFS,
    PlayN,
    PlaySS,
    PresetsN,
    RecordN,
    RecordS,
    SFunctionality,
    TempoN,
    TempoS,
    VChannelS,
    ViewFS,
    ViewN,
    ViewSS,
    VMiDiOS,
    VModeS,
    VPartS,
    VStepS,
    create_notes,
)


def create_scales() -> List[str]:
    return ["C"] + keys.major_keys + keys.minor_keys


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
    if button_motions[-1] != ValidButtons.NEXT.value:
        button_motions.append(ValidButtons.NEXT.value)
    return button_motions


VOICE_1 = MFunctionality(
    name="GeVo1",
    comment="Generic MIDI start and stop of a note.",
    indexes=[[1, 0, 6, 1, 0], [2, 0, 0, 0, 0]],
    offsets=[1, 1 + 8 * 2, 6, 1, 0],
    labels=["Code", "Note", "Velocity", "Length", "Scale"],
    vis_ind=[0, 1],
    instruments=[str(ValidInstruments.GENERIC)],
    data=[
        [str(0), str(0x90), str(0x80)],
        create_notes(scale="C"),
        [
            str(i * InitConfig().velocity_step)
            for i in range(InitConfig().velocity_min, InitConfig().velocity_max + 1)
        ],
        [str(x.value) for x in list(ValidLengths)],
        create_scales(),
    ],
)

VOICE_2 = MFunctionality(
    name="GeVo2",
    comment="Generic MIDI start and stop of a note.",
    indexes=[[1, 0, 6, 1, 0], [2, 0, 0, 0, 0]],
    offsets=[1, 1 + 8 * 2, 6, 1, 0],
    labels=["Code", "Note", "Velocity", "Length", "Scale"],
    vis_ind=[0, 1],
    instruments=[str(ValidInstruments.GENERIC)],
    data=[
        [str(0), str(0x90), str(0x80)],
        create_notes(scale="C"),
        [
            str(i * InitConfig().velocity_step)
            for i in range(InitConfig().velocity_min, InitConfig().velocity_max + 1)
        ],
        [str(x.value) for x in list(ValidLengths)],
        create_scales(),
    ],
)

CUTOFF_EG_INT = MFunctionality(
    name="VBCuEgIn",
    comment="Volca Bass Cutoff EG Int CC.",
    indexes=[[1, 0]],
    offsets=[1, 1],
    labels=["Code", "Cutoff"],
    vis_ind=[0, 1],
    instruments=[str(ValidInstruments.VOLCA_BASS)],
    data=[
        [str(0), str(0x90), str(0x80)],
        create_motions(),
    ],
)


MAPPINGS_GENERIC_4 = MMappings(
    name="Generic_4_map",
    mappings=[
        MMapping(
            midi_id=1,
            port_name="USB MIDI Interface",
            channel=1,
            is_out=True,
            instruments=[str(ValidInstruments.GENERIC)],
        ),
        MMapping(
            midi_id=0,
            port_name="USB2.0-MIDI Port 2",
            channel=1,
            is_out=True,
            instruments=[str(ValidInstruments.GENERIC)],
        ),
        MMapping(
            midi_id=3,
            port_name="USB MIDI Interface",
            channel=1,
            is_out=True,
            instruments=[str(ValidInstruments.GENERIC)],
        ),
        MMapping(
            midi_id=2,
            port_name="USB2.0-MIDI Port 2",
            channel=1,
            is_out=True,
            instruments=[str(ValidInstruments.GENERIC)],
        ),
    ],
)

MAPPINGS_VOLCA_DBKF = MMappings(
    name="Volca_DBKF_map",
    mappings=[
        MMapping(
            midi_id=0,
            channel=1,
            is_out=True,
            instruments=[str(ValidInstruments.VOLCA_DRUM), str(ValidInstruments.GENERIC)],
            port_name="",
        ),
        MMapping(
            midi_id=1,
            channel=1,
            is_out=True,
            instruments=[str(ValidInstruments.VOLCA_BASS), str(ValidInstruments.GENERIC)],
            port_name="",
        ),
        MMapping(
            midi_id=2,
            channel=1,
            is_out=True,
            instruments=[str(ValidInstruments.VOLCA_KEYS), str(ValidInstruments.GENERIC)],
            port_name="",
        ),
        MMapping(
            midi_id=3,
            channel=1,
            is_out=True,
            instruments=[str(ValidInstruments.VOLCA_FM2), str(ValidInstruments.GENERIC)],
            port_name="",
        ),
    ],
)


def init_nav() -> Dict[ValidNav, NFunctionality]:
    return {
        ValidNav.RECORD: RecordN(),
        ValidNav.VIEW: ViewN(),
        ValidNav.PLAY: PlayN(),
        ValidNav.TEMPO: TempoN(),
        ValidNav.COPY: CopyN(),
        ValidNav.PRESETS: PresetsN(),
    }


def init_settings(
    midi_ids: List[int], valid_modes: List[str]
) -> Dict[ValidSettings, SFunctionality]:
    return {
        ValidSettings.E_MIDI_O: EMiDiOS(midi_ids=midi_ids),
        ValidSettings.E_CHANNEL: EChannelS(),
        ValidSettings.E_PART: EPartS(),
        ValidSettings.E_STEP: EStepS(),
        ValidSettings.E_MODE: EModeS(valid_modes=valid_modes),
        ValidSettings.V_MIDI_O: VMiDiOS(midi_ids=midi_ids),
        ValidSettings.V_CHANNEL: VChannelS(),
        ValidSettings.V_PART: VPartS(),
        ValidSettings.V_STEP: VStepS(),
        ValidSettings.V_MODE: VModeS(valid_modes=valid_modes),
        ValidSettings.TEMPO: TempoS(),
        ValidSettings.RECORD: RecordS(),
        ValidSettings.COPY: CopyS(),
        ValidSettings.VIEW_SHOW: ViewSS(),
        ValidSettings.VIEW_FUNCTION: ViewFS(),
        ValidSettings.PLAY_SHOW: PlaySS(),
        ValidSettings.PLAY_FUNCTION: PlayFS(),
    }


def init_modes_mem() -> Dict[str, MFunctionality]:
    return {
        VOICE_1.name: VOICE_1,
        VOICE_2.name: VOICE_2,
        CUTOFF_EG_INT.name: CUTOFF_EG_INT,
    }


def init_mappings_mem() -> MMappings:
    return MAPPINGS_GENERIC_4


def init_music_mem(
    midi_ids: List[int],
    mappings: MMappings,
) -> MMusic:
    sequences: Dict[int, Dict[int, Dict[int, Dict[int, Dict[str, List[List[int]]]]]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
    )
    modes = init_modes_mem()
    mappings_dict = mappings.to_dict(modes=modes)
    for midi_id in midi_ids:
        for channel in EChannelS().values:
            if int(channel) in mappings_dict[int(midi_id)]:
                for part in EPartS().values:
                    for step in EStepS().values:
                        for valid_mode in modes.keys():
                            if valid_mode in mappings_dict[int(midi_id)][int(channel)]:
                                mode = modes[valid_mode].new(lock=False)
                                sequences[int(midi_id)][int(channel)][int(part)][int(step)][
                                    valid_mode
                                ] = mode.get_indexes()
    m_music = MMusic(name="Empty", data=sequences, mappings_name=mappings.name)
    return m_music


MUSIC_GENERIC_4 = init_music_mem(midi_ids=list(range(4)), mappings=MAPPINGS_GENERIC_4)
