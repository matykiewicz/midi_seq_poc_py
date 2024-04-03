from collections import defaultdict
from typing import Any, Dict, List

import mingus.core.scales as scales
from mingus.core import keys

from .configs import InitConfig
from .const import (
    ValidButtons,
    ValidInstruments,
    ValidLengths,
    ValidModes,
    ValidNav,
    ValidPresets,
    ValidSettings,
)
from .functionalities import (
    CopyN,
    CopyS,
    EChannelS,
    EditsN,
    EMiDiOS,
    EModeS,
    EPartS,
    EStepS,
    MFunctionality,
    NFunctionality,
    PlayFS,
    PlayN,
    PlaySS,
    PresetsN,
    RecordN,
    RecordS,
    SFunctionality,
    SMapping,
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
)


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


def init_nav() -> Dict[ValidNav, NFunctionality]:
    return {
        ValidNav.RECORD: RecordN(),
        ValidNav.VIEW: ViewN(),
        ValidNav.PLAY: PlayN(),
        ValidNav.TEMPO: TempoN(),
        ValidNav.COPY: CopyN(),
        ValidNav.PRESETS: PresetsN(),
        ValidNav.EDITS: EditsN(),
    }


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


VOICE_1 = MFunctionality(
    name=str(ValidModes.VOICE_1),
    first_only=False,
    indexes=[[1, 0, 6, 1], [2, 0, 0, 0]],
    offsets=[1, 1 + 8 * 2, 6, 1],
    labels=["Code", "Note", "Velocity", "Length"],
    vis_ind=(0, 1),
    instruments=[ValidInstruments.GENERIC],
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


VOICE_2 = MFunctionality(
    name=str(ValidModes.VOICE_2),
    first_only=False,
    indexes=[[1, 0, 6, 1], [2, 0, 0, 0]],
    offsets=[1, 1 + 8 * 2, 6, 1],
    labels=["Code", "Note", "Velocity", "Length"],
    vis_ind=(0, 1),
    instruments=[ValidInstruments.GENERIC],
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


SCALE = MFunctionality(
    name=str(ValidModes.SCALE),
    first_only=True,
    indexes=[[0]],
    offsets=[1],
    labels=["Scale"],
    instruments=[ValidInstruments.GENERIC],
    vis_ind=(0, 0),
    data=[create_scales()],
)


def init_modes() -> Dict[ValidModes, MFunctionality]:
    return {
        ValidModes.VOICE_1: VOICE_1,
        ValidModes.VOICE_2: VOICE_2,
        ValidModes.SCALE: SCALE,
    }


def init_mappings() -> List[SMapping]:
    return [
        SMapping(0, 1, ValidInstruments.GENERIC),
        SMapping(1, 1, ValidInstruments.VOLCA_BASS),
        SMapping(2, 1, ValidInstruments.VOLCA_KEYS),
        SMapping(3, 1, ValidInstruments.VOLCA_FM2),
        SMapping(4, 1, ValidInstruments.VOLCA_DRUM),
    ]


def init_music(
    n_midis: int,
) -> Dict[int, Dict[int, Dict[int, Dict[int, Dict[ValidModes, List[List[int]]]]]]]:
    sequences: Dict[int, Dict[int, Dict[int, Dict[int, Dict[ValidModes, List[List[int]]]]]]] = (
        defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(dict))))
    )
    for midi in range(n_midis):
        for channel in EChannelS().values:
            for part in EPartS().values:
                for step in EStepS().values:
                    for mode_str in list(ValidModes):
                        valid_mode = ValidModes(mode_str)
                        mode = self.modes[valid_mode].new(lock=False)
                        sequences[int(midi)][int(channel)][int(part)][int(step)][
                            valid_mode
                        ] = mode.get_indexes()
    return sequences


def init_presets() -> Dict[ValidPresets, Any]:
    return dict()
