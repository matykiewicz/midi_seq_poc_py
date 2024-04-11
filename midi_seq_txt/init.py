from collections import defaultdict
from typing import Dict, List, Tuple

from mingus.core import keys

from .configs import InitConfig
from .const import ValidButtons, ValidInstruments, ValidLengths, ValidNav, ValidSettings
from .functionalities import (
    CopyN,
    CopyS,
    EChannelS,
    EMiDiOS,
    EOModeS,
    EPartS,
    EStepS,
    MapEChS,
    MapEConS,
    MapEDirS,
    MapEInstrIS,
    MapEInstrOS,
    MapEPNameIS,
    MapEPNameOS,
    MapNameS,
    MConn,
    MInFunctionality,
    MMappings,
    MMusic,
    MOutFunctionality,
    MusNameS,
    NFunctionality,
    PlayFS,
    PlayN,
    PlaySS,
    PresetsN,
    PresetsS,
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
    VOModeS,
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


VOICE_1_OUT = MOutFunctionality(
    name="GeVo1Out",
    comment="Generic MIDI start and stop of a note",
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

VOICE_2_OUT = MOutFunctionality(
    name="GeVo2Out",
    comment="Generic MIDI start and stop of a note",
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

CUTOFF_EG_INT_OUT = MOutFunctionality(
    name="VBCutEGIOut",
    comment="Volca Bass Cutoff EG Intensity CC",
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

MIDI_CLOCK_IN = MInFunctionality(
    name="MidiClockIn", codes=[0xF8], converters=[], instruments=[ValidInstruments.GENERIC]
)

MMAPPINGS_00 = MMappings(
    name="Mappings_00",
    comment="",
    conns=[
        MConn(
            midi_id=1,
            port_name="USB MIDI Interface",
            channel=1,
            is_out=True,
            instruments=[str(ValidInstruments.GENERIC)],
        ),
        MConn(
            midi_id=0,
            port_name="USB2.0-MIDI Port 2",
            channel=1,
            is_out=True,
            instruments=[str(ValidInstruments.GENERIC)],
        ),
        MConn(
            midi_id=3,
            port_name="USB MIDI Interface",
            channel=1,
            is_out=True,
            instruments=[str(ValidInstruments.GENERIC)],
        ),
        MConn(
            midi_id=2,
            port_name="USB2.0-MIDI Port 2",
            channel=1,
            is_out=True,
            instruments=[str(ValidInstruments.GENERIC)],
        ),
        MConn(
            midi_id=1,
            port_name="USB MIDI Interface",
            channel=1,
            is_out=True,
            instruments=[str(ValidInstruments.GENERIC)],
        ),
        MConn(
            midi_id=5,
            port_name="USB MIDI Interface",
            channel=1,
            is_out=False,
            instruments=[str(ValidInstruments.GENERIC)],
        ),
    ],
)

MMAPPINGS_01 = MMappings(
    name="Mappings_01",
    comment="",
    conns=[
        MConn(
            midi_id=0,
            channel=1,
            is_out=True,
            instruments=[str(ValidInstruments.VOLCA_DRUM), str(ValidInstruments.GENERIC)],
            port_name="",
        ),
        MConn(
            midi_id=1,
            channel=1,
            is_out=True,
            instruments=[str(ValidInstruments.VOLCA_BASS), str(ValidInstruments.GENERIC)],
            port_name="",
        ),
        MConn(
            midi_id=2,
            channel=1,
            is_out=True,
            instruments=[str(ValidInstruments.VOLCA_KEYS), str(ValidInstruments.GENERIC)],
            port_name="",
        ),
        MConn(
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
    midi_ids: List[int],
    valid_out_modes: List[str],
    port_names_comb: List[Tuple[int, str, bool]],
    out_instruments: List[str],
    in_instruments: List[str],
) -> Dict[ValidSettings, SFunctionality]:
    return {
        ValidSettings.E_MIDI_O: EMiDiOS(midi_ids=midi_ids),
        ValidSettings.E_CHANNEL: EChannelS(),
        ValidSettings.E_PART: EPartS(),
        ValidSettings.E_STEP: EStepS(),
        ValidSettings.E_O_MODE: EOModeS(valid_out_modes=valid_out_modes),
        ValidSettings.V_MIDI_O: VMiDiOS(midi_ids=midi_ids),
        ValidSettings.V_CHANNEL: VChannelS(),
        ValidSettings.V_PART: VPartS(),
        ValidSettings.V_STEP: VStepS(),
        ValidSettings.V_O_MODE: VOModeS(valid_out_modes=valid_out_modes),
        ValidSettings.TEMPO: TempoS(),
        ValidSettings.RECORD: RecordS(),
        ValidSettings.COPY: CopyS(),
        ValidSettings.VIEW_SHOW: ViewSS(),
        ValidSettings.VIEW_FUNCTION: ViewFS(),
        ValidSettings.PLAY_SHOW: PlaySS(),
        ValidSettings.PLAY_FUNCTION: PlayFS(),
        ValidSettings.PRESETS: PresetsS(),
        ValidSettings.MAP_NAME: MapNameS(),
        ValidSettings.MUS_NAME: MusNameS(),
        ValidSettings.MAP_E_CON: MapEConS(),
        ValidSettings.MAP_E_DIR: MapEDirS(),
        ValidSettings.MAP_E_CH: MapEChS(),
        ValidSettings.MAP_E_PNAME_O: MapEPNameOS(port_names_comb=port_names_comb),
        ValidSettings.MAP_E_INSTR_O: MapEInstrOS(out_instruments=out_instruments),
        ValidSettings.MAP_E_PNAME_I: MapEPNameIS(port_names_comb=port_names_comb),
        ValidSettings.MAP_E_INSTR_I: MapEInstrIS(in_instruments=in_instruments),
    }


def init_io_modes_and_instruments_mem() -> (
    Tuple[Dict[str, MOutFunctionality], List[str], Dict[str, MInFunctionality], List[str]]
):
    out_modes: Dict[str, MOutFunctionality] = {
        VOICE_1_OUT.name: VOICE_1_OUT,
        VOICE_2_OUT.name: VOICE_2_OUT,
        CUTOFF_EG_INT_OUT.name: CUTOFF_EG_INT_OUT,
    }
    in_modes: Dict[str, MInFunctionality] = {
        MIDI_CLOCK_IN.name: MIDI_CLOCK_IN,
    }
    out_instruments: List[str] = list()
    in_instruments: List[str] = list()
    for out_mode in out_modes.values():
        out_instruments += out_mode.instruments
    for in_mode in in_modes.values():
        in_instruments += in_mode.instruments
    out_instruments = list(set(out_instruments))
    in_instruments = list(set(in_instruments))
    return out_modes, out_instruments, in_modes, in_instruments


def init_mappings_mem() -> MMappings:
    return MMAPPINGS_00


def init_music_mem(mappings: MMappings) -> MMusic:
    sequences: Dict[int, Dict[int, Dict[int, Dict[int, Dict[str, List[List[int]]]]]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
    )
    out_modes, _, _, _ = init_io_modes_and_instruments_mem()
    mappings_dict = mappings.to_out_dict(out_modes=out_modes)
    for midi_id in sorted(mappings_dict.keys()):
        for channel in EChannelS().values:
            if int(channel) in mappings_dict[int(midi_id)]:
                for part in EPartS().values:
                    for step in EStepS().values:
                        for valid_out_mode in out_modes.keys():
                            if valid_out_mode in mappings_dict[int(midi_id)][int(channel)]:
                                out_mode = out_modes[valid_out_mode].new(lock=False)
                                sequences[int(midi_id)][int(channel)][int(part)][int(step)][
                                    valid_out_mode
                                ] = out_mode.get_indexes()
    m_music = MMusic(
        name="Music_00", data=sequences, mappings_name=mappings.name, comment="Starter package"
    )
    return m_music


MUSIC_00 = init_music_mem(mappings=MMAPPINGS_00)
