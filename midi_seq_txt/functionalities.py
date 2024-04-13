import math
import time
from collections import defaultdict
from copy import deepcopy
from typing import Dict, List, Optional, Tuple, Union

import mingus.core.scales as scales
import rtmidi
from attrs import AttrsInstance, define
from mingus.containers import Note

from .configs import InitConfig
from .const import (
    BUT_COPY,
    BUT_PLAY,
    BUT_PRES,
    BUT_REC,
    BUT_TEMPO,
    BUT_VIEW,
    ValidButtons,
    ValidLengths,
    ValidNav,
    ValidSettings,
)


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
    if button_notes[-1] != ValidButtons.NEXT.value:
        button_notes.append(ValidButtons.NEXT.value)
    return button_notes


@define
class MMiDi(AttrsInstance):
    midi_id: int
    port_id: int
    port_name: str
    is_out: bool
    channels: List[int] = list()


@define
class MConn(AttrsInstance):
    midi_id: int = -1
    port_name: str = ""
    channel: int = -1
    is_out: bool = True
    instruments: List[str] = list()

    def __attrs_post_init__(self):
        max_instr = InitConfig().max_instr
        if len(self.instruments) > max_instr:
            self.instruments = self.instruments[0:3]
        elif len(self.instruments) < max_instr:
            self.instruments += [""] * (max_instr - len(self.instruments))


@define
class MMappings(AttrsInstance):
    name: str = ""
    comment: str = ""
    conns: List[MConn] = [MConn() for i in range(InitConfig().max_conns)]

    def get_sorted(self) -> List[MConn]:
        return sorted(self.conns, key=lambda m: m.midi_id)

    def __attrs_post_init__(self):
        missing = InitConfig().max_conns - len(self.conns)
        if missing:
            for i in range(missing):
                self.conns.append(MConn())

    def filter_midis(
        self, port_names_comb: List[Tuple[int, str, bool]]
    ) -> List[Tuple[int, int, str, bool]]:
        found_ports: List[int] = list()
        found_midis: List[int] = list()
        found_names: List[str] = list()
        found_is_outs: List[bool] = list()
        de_dup: List[Tuple[int, str, bool]] = list()
        for i, port_id_name_is_out in enumerate(port_names_comb):
            port_id, port_name, is_out = port_id_name_is_out
            for j, conn in enumerate(self.conns):
                if (
                    port_name == conn.port_name
                    and is_out == conn.is_out
                    and (port_id, port_name, is_out) not in de_dup
                ):
                    de_dup.append((port_id, port_name, is_out))
                    found_ports.append(port_id)
                    found_midis.append(self.conns[j].midi_id)
                    found_names.append(port_name)
                    found_is_outs.append(is_out)
        return list(zip(found_ports, found_midis, found_names, found_is_outs))

    def init_midi_ins(self) -> Dict[int, MMiDi]:
        port_names_comb = self.get_port_names_comb()
        midi_ins: Dict[int, MMiDi] = dict()
        ports_midis_names_comb = self.filter_midis(port_names_comb=port_names_comb)
        for port_id, midi_id, port_name, is_out in ports_midis_names_comb:
            if not is_out:
                midi_ins[midi_id] = MMiDi(
                    port_id=port_id, midi_id=midi_id, port_name=port_name, is_out=False
                )
        return midi_ins

    @staticmethod
    def get_port_names_comb() -> List[Tuple[int, str, bool]]:
        midi_out = rtmidi.MidiOut()
        midi_in = rtmidi.MidiIn()
        out_port_names = midi_out.get_ports()
        out_port_ids = list(range(len(out_port_names)))
        in_port_names = midi_in.get_ports()
        in_port_ids = list(range(len(in_port_names)))
        port_names_comb = list(
            zip(out_port_ids, out_port_names, [True] * len(out_port_names))
        ) + list(zip(in_port_ids, in_port_names, [False] * len(in_port_names)))
        return port_names_comb

    def init_midi_outs(self) -> Dict[int, MMiDi]:
        port_names_comb = self.get_port_names_comb()
        midi_outs: Dict[int, MMiDi] = dict()
        ports_midis_names_comb = self.filter_midis(port_names_comb=port_names_comb)
        for port_id, midi_id, port_name, is_out in ports_midis_names_comb:
            if is_out:
                midi_outs[midi_id] = MMiDi(
                    port_id=port_id, midi_id=midi_id, port_name=port_name, is_out=True
                )
        return midi_outs

    def to_out_dict(
        self, out_modes: Dict[str, "MOutFunctionality"]
    ) -> Dict[int, Dict[int, List[str]]]:
        mappings_dict: Dict[int, Dict[int, List[str]]] = defaultdict(lambda: defaultdict(list))
        instruments_dict: Dict[str, List[str]] = defaultdict(list)
        for valid_out_mode in out_modes.keys():
            out_mode = out_modes[valid_out_mode]
            for instrument in out_mode.instruments:
                instruments_dict[instrument].append(valid_out_mode)
        for conn in self.conns:
            midi_id = conn.midi_id
            channel = conn.channel
            instruments = conn.instruments
            is_out = conn.is_out
            if midi_id > -1 and channel > -1 and is_out:
                for instrument in instruments:
                    for valid_out_mode in instruments_dict[instrument]:
                        mappings_dict[midi_id][channel].append(valid_out_mode)
        return mappings_dict


@define
class MMusic(AttrsInstance):
    name: str
    mappings_name: str
    comment: str
    data: Dict[int, Dict[int, Dict[int, Dict[int, Dict[str, List[List[int]]]]]]]


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

    def new(self) -> "SFunctionality":
        return deepcopy(self)

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
class MInFunctionality(AttrsInstance):
    # MIDI & In Modes
    name: str
    in_rules: List[List[Union[str, int]]]
    out_rules: List[List[Union[str, int]]]
    data: List[List[int]]
    instruments: List[str]
    comment: str
    _t_1_: float = 0.0
    _t_2_: float = 0.0
    _exe_: int = 0
    _lock_: bool = True

    def new(self, lock: bool) -> "MInFunctionality":
        new = deepcopy(self)
        new._lock_ = lock
        new._t_1_ = time.time()
        new._t_2_ = 0.0
        new.data.clear()
        return new

    def set_with_message_and_time(
        self, message: List[int], t: Tuple[float, float]
    ) -> "MInFunctionality":
        if not self._lock_:
            if self._exe_ < len(self.in_rules):
                self.apply_time(t=t)
                applied = self.rules_apply(self.in_rules[self._exe_], message=message)
                if applied != 0:
                    self.data.append(message)
                    self._exe_ += 1
                    if applied < 0:
                        self.out_rules.append(self.out_rules.pop(0))
        else:
            raise PermissionError(f"{self.name} out_mode is locked!")
        return self

    def apply_time(self, t: Tuple[float, float]) -> "MInFunctionality":
        if self._exe_ == 0:
            self._t_1_ = t[0]
        else:
            if t[1] > 0.0:
                self._t_2_ = self._t_1_ + t[1]
            else:
                self._t_2_ = t[0]
        return self

    def rules_apply(self, rules: List[Union[str, int]], message: List[int]) -> int:
        all_apply = 1
        for i, rule in enumerate(rules):
            if isinstance(rule, int):
                if rule > 0:
                    all_apply = all_apply * int(message[i] == rule)
                else:
                    if message[0] >= abs(rule):
                        all_apply = all_apply
                    else:
                        all_apply = -all_apply
            elif isinstance(rule, str):
                if rule == "match":
                    all_apply = all_apply and (message[i] == self.data[self._exe_ - 1][i])
                elif rule == "":
                    all_apply = all_apply
        return all_apply

    def has_next(self) -> bool:
        return self._exe_ < len(self.in_rules)

    def reset(self) -> "MInFunctionality":
        self._exe_ = 0
        self._t_1_ = 0.0
        self._t_2_ = 0.0
        self.data.clear()
        return self

    def convert_with_out_modes_and_tempo(
        self, out_modes: Dict[str, "MOutFunctionality"], tempo: int, n_quants: int
    ) -> Optional[Tuple[int, int, "MOutFunctionality"]]:
        valid_out_mode, midi_id, channel = self.out_rules[0]
        if valid_out_mode in out_modes:
            out_mode = out_modes[str(valid_out_mode)].new(lock=False).reset_offsets(off=0)
            duration = self._t_2_ - self._t_1_
            length = self.convert_duration_to_length(
                duration=duration, tempo=tempo, n_quants=n_quants
            )
            self.set_length(length=length, exe=0)
            for exe in range(self._exe_):
                data = self.get_row_values(exe=exe)
                for i, lab in enumerate(out_mode.get_labels()):
                    if i < len(data) and lab != "Note" and lab != "Scale" and lab != "Button":
                        out_mode.set_indexes_with_lab_and_val(lab=lab, val=data[i], exe=exe)
            self.reset()
            return int(midi_id), int(channel), out_mode
        else:
            self.reset()
            return None

    @staticmethod
    def convert_duration_to_length(duration: float, tempo: int, n_quants: int) -> int:
        interval = 60 / tempo
        quant = interval / n_quants
        length = math.ceil(duration / quant)
        if length > int(ValidLengths.SEXDECUPLE.value):
            length = int(ValidLengths.SEXDECUPLE.value)
        return length

    def set_length(self, length: int, exe: int) -> "MInFunctionality":
        self.data[exe][3] = length
        return self

    def get_row_values(self, exe: int) -> List[str]:
        values: List[str] = list()
        if exe < len(self.data):
            for value in self.data[exe]:
                values.append(str(value))
        return values


@define
class MOutFunctionality(AttrsInstance):
    # MIDI & Out Modes
    name: str
    indexes: List[List[int]]
    labels: List[str]
    offsets: List[int]
    data: List[List[str]]
    vis_ind: List[int]
    but_ind: List[int]
    instruments: List[str]
    comment: str
    _t_1_: float = 0.0
    _t_2_: float = 0.0
    _exe_: int = 0
    _lock_: bool = True

    def new(self, lock: bool) -> "MOutFunctionality":
        new = deepcopy(self)
        new._lock_ = lock
        new._t_1_ = time.time()
        new._t_2_ = 0.0
        return new

    def reset_offsets(self, off: int) -> "MOutFunctionality":
        for i in range(len(self.offsets)):
            self.offsets[i] = off
        return self

    def get_exe(self) -> int:
        return self._exe_

    def has_next(self) -> bool:
        return self._exe_ < len(self.indexes)

    def update_offsets_with_lab(self, lab: str, by: int) -> "MOutFunctionality":
        if lab in self.labels:
            off_int = self.labels.index(lab)
            if off_int < len(self.data):
                if self.offsets[off_int] + by >= len(self.data[off_int]):
                    self.offsets[off_int] = 1
                else:
                    self.offsets[off_int] += by
        else:
            raise ValueError(f"Label {lab} not found!")
        return self

    def get_indexes(self) -> List[List[int]]:
        return deepcopy(self.indexes)

    def get_labels(self) -> List[str]:
        return deepcopy(self.labels)

    def get_single_value_by_off(self, off: str, ind: int) -> str:
        if off in self.labels:
            off_int = self.labels.index(off)
            if off_int < len(self.data):
                ind = self.offsets[off_int] + ind
                if ind < len(self.data[off_int]):
                    return deepcopy(self.data[off_int][ind])
        else:
            raise ValueError(f"Offset {off} not found!")
        return ValidButtons.NA

    def get_single_value_by_lab(self, exe: int, lab: str) -> str:
        if exe < len(self.indexes):
            if lab in self.labels:
                ind = self.labels.index(lab)
                if ind < len(self.indexes[exe]):
                    return deepcopy(self.data[ind][self.indexes[exe][ind]])
            else:
                raise ValueError(f"Label {lab} not found!")
        return ValidButtons.NA

    def get_row_values(self, exe: int) -> List[str]:
        values: List[str] = list()
        if exe < len(self.indexes):
            for j in range(len(self.indexes[exe])):
                ind = self.indexes[exe][j]
                values.append(deepcopy(self.data[j][ind]))
        return values

    def get_vis_ind(self) -> List[int]:
        return self.vis_ind

    def get_but_label(self) -> str:
        return self.labels[self.but_ind[1]]

    def new_with_indexes(self, indexes: List[List[int]]) -> "MOutFunctionality":
        new_out_mode = self.new(lock=False)
        new_out_mode = new_out_mode.set_indexes(indexes=deepcopy(indexes))
        return new_out_mode

    def new_with_lab(self, lab: str, sub_ind: int, exe: Optional[int]) -> "MOutFunctionality":
        new_out_mode = self.new(lock=False)
        new_out_mode.set_indexes_with_lab_and_off(lab=lab, sub_ind=sub_ind, exe=exe)
        return new_out_mode

    def set_data_with_lab(self, lab: str, data: List[str]) -> "MOutFunctionality":
        if lab in self.labels:
            ind = self.labels.index(lab)
            self.data[ind] = data
        else:
            raise ValueError(f"Label {lab} not found!")
        return self

    def set_indexes_with_lab_and_off(
        self, lab: str, sub_ind: int, exe: Optional[int] = None
    ) -> "MOutFunctionality":
        if self._lock_:
            raise PermissionError(f"{self.name} out_mode is locked!")
        if lab in self.labels:
            off_int = self.labels.index(lab)
            ind = self.offsets[off_int] + sub_ind
            if off_int < len(self.data):
                for i in range(len(self.indexes)):
                    if exe is None or exe == i:
                        if ind < len(self.data[off_int]):
                            self.indexes[i][off_int] = ind
                            if lab == "Note" and "Key" in self.labels:
                                note = self.data[off_int][ind]
                                if "-" in note:
                                    key = str(int(Note(note)) + 12)
                                    self.set_indexes_with_lab_and_val("Key", key)
        else:
            raise ValueError(f"Offset {lab} not found!")
        return self

    def set_indexes_with_lab_and_val(
        self, lab: str, val: str, exe: Optional[int] = None
    ) -> "MOutFunctionality":
        if self._lock_:
            raise PermissionError(f"{self.name} out_mode is locked!")
        if lab in self.labels:
            off_int = self.labels.index(lab)
            if val not in self.data[off_int]:
                ind = self.find_the_closest(val=val, values=self.data[off_int])
            else:
                ind = self.data[off_int].index(val)
            for i in range(len(self.indexes)):
                if exe is None or exe == i:
                    if ind < len(self.data[off_int]):
                        self.indexes[i][off_int] = ind
        else:
            raise ValueError(f"Offset {lab} not found!")
        return self

    @staticmethod
    def find_the_closest(val: str, values: List[str]) -> int:
        val_int = int(val)
        min_dif = 256
        best_ind = -1
        for ind, value in enumerate(values):
            val_dif = abs(val_int - int(value))
            if val_dif < min_dif:
                min_dif = val_dif
                best_ind = ind
        return best_ind

    def set_indexes(self, indexes: List[List[int]]) -> "MOutFunctionality":
        if self._lock_:
            raise PermissionError(f"{self.name} out_mode is locked!")
        for i in range(len(indexes)):
            for j in range(len(indexes[i])):
                if i < len(self.indexes):
                    if j < len(self.indexes[i]):
                        self.indexes[i][j] = indexes[i][j]
        return self

    def get_as_message(self) -> List[int]:
        if self._lock_:
            raise PermissionError(f"{self.name} out_mode is locked!")
        values_int: List[int] = list()
        if self._exe_ < len(self.indexes):
            values_str = self.get_row_values(exe=self._exe_)
            labels_str = self.get_labels()
            for i, value_str in enumerate(values_str):
                if (
                    labels_str[i] != "Note"
                    and labels_str[i] != "Scale"
                    and labels_str[i] != "Button"
                ):
                    values_int.append(int(value_str))
        self._exe_ += 1
        return values_int


class PlayN(NFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidNav.PLAY.value,
            buttons=BUT_PLAY,
            ind=0,
        )


class RecordN(NFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidNav.RECORD.value,
            buttons=BUT_REC,
            ind=0,
        )


class ViewN(NFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidNav.VIEW.value,
            buttons=BUT_VIEW,
            ind=0,
        )


class TempoN(NFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidNav.TEMPO.value,
            buttons=BUT_TEMPO,
            ind=0,
        )


class CopyN(NFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidNav.COPY.value,
            buttons=BUT_COPY,
            ind=0,
        )


class PresetsN(NFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidNav.PRESETS.value,
            buttons=BUT_PRES,
            ind=0,
        )


# - - EDIT POS - - #


class EMiDiOS(SFunctionality):
    def __init__(self, midi_ids: List[int]):
        super().__init__(
            name=ValidSettings.E_MIDI_O.value,
            ind=0,
            values=deepcopy(sorted(midi_ids)),
        )


class EPartS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.E_PART.value,
            ind=0,
            values=[i for i in range(1, InitConfig().n_parts + 1)],
        )


class EStepS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.E_STEP.value,
            ind=0,
            values=[i for i in range(1, InitConfig().n_steps + 1)],
        )


class EChannelS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.E_CHANNEL.value,
            ind=0,
            values=[i for i in range(1, InitConfig().n_channels + 1)],
        )


class EOModeS(SFunctionality):
    def __init__(self, valid_out_modes: List[str]):
        super().__init__(
            name=ValidSettings.E_O_MODE.value,
            ind=0,
            values=[k for k in valid_out_modes],
        )


# - - VIEW - - #


class VMiDiOS(SFunctionality):
    def __init__(self, midi_ids: List[int]):
        super().__init__(
            name=ValidSettings.V_MIDI_O.value,
            ind=0,
            values=deepcopy(sorted(midi_ids)),
        )


class VPartS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.V_PART.value,
            ind=0,
            values=[i for i in range(1, InitConfig().n_parts + 1)],
        )


class VStepS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.V_STEP.value,
            ind=0,
            values=[i for i in range(1, InitConfig().n_steps + 1)],
        )


class VChannelS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.V_CHANNEL.value,
            ind=0,
            values=[i for i in range(1, InitConfig().n_channels + 1)],
        )


class VOModeS(SFunctionality):
    def __init__(self, valid_out_modes: List[str]):
        super().__init__(
            name=ValidSettings.V_O_MODE.value,
            ind=0,
            values=[k for k in valid_out_modes],
        )


# - - OTHER - - #


class ViewSS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.VIEW_SHOW.value,
            ind=0,
            values=[ValidButtons.OFF.value, ValidButtons.ON.value],
        )


class ViewFS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.VIEW_FUNCTION.value,
            ind=0,
            values=[
                ValidButtons.VIEW_ONLY.value,
                ValidButtons.VIEW_PLAY.value,
                ValidButtons.VIEW_REC.value,
            ],
        )


class PlaySS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.PLAY_SHOW.value,
            ind=0,
            values=[ValidButtons.OFF.value, ValidButtons.ON.value],
        )


class PlayFS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.PLAY_FUNCTION.value,
            ind=0,
            values=[
                ValidButtons.NA.value,
                ValidButtons.PLAY_PART.value,
                ValidButtons.PLAY_PARTS.value,
                ValidButtons.PLAY_ALL.value,
            ],
        )


class RecordS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.RECORD.value,
            ind=0,
            values=[ValidButtons.OFF.value, ValidButtons.ON.value],
        )


class CopyS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.COPY.value,
            ind=0,
            values=[ValidButtons.OFF.value, ValidButtons.ON.value],
        )


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


class PresetsS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.PRESETS.value,
            ind=0,
            values=[
                ValidButtons.PRESETS_OFF_MUSIC.value,
                ValidButtons.PRESETS_OFF_MAP.value,
                ValidButtons.PRESETS_ON_MUSIC.value,
                ValidButtons.PRESETS_ON_MAP.value,
                ValidButtons.PRESETS_L_MUSIC.value,
                ValidButtons.PRESETS_S_MUSIC.value,
                ValidButtons.PRESETS_L_MAP.value,
                ValidButtons.PRESETS_S_MAP.value,
                ValidButtons.PRESETS_E_MAP_ON.value,
                ValidButtons.PRESETS_E_MAP_OFF.value,
            ],
        )


class MusNameS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.MUS_NAME.value,
            ind=0,
            values=[f"Music_{i:02}" for i in range(InitConfig().music_count)],
        )


class MapNameS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.MAP_NAME.value,
            ind=0,
            values=[f"Mappings_{i:02}" for i in range(InitConfig().map_count)],
        )


class MapEConnS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.MAP_E_CONN.value,
            ind=0,
            values=[i for i in range(InitConfig().max_conns)],
        )


class MapEMidiS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.MAP_E_MIDI.value,
            ind=0,
            values=[i for i in range(InitConfig().max_midis)],
        )


class MapEDirS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.MAP_E_DIR.value,
            ind=0,
            values=["True", "False"],
        )


class MapEChS(SFunctionality):
    def __init__(self):
        super().__init__(
            name=ValidSettings.MAP_E_CH.value,
            ind=0,
            values=[ch for ch in range(1, InitConfig().n_channels + 1)],
        )


class MapEPNameS(SFunctionality):
    def __init__(self, port_names_comb: List[Tuple[int, str, bool]]):
        port_names: List[Union[str, int]] = list()
        for i, port_id_name_is_out in enumerate(port_names_comb):
            port_id, port_name, is_out = port_id_name_is_out
            if port_name not in port_names:
                port_names.append(port_name)
        super().__init__(
            name=ValidSettings.MAP_E_PNAME.value,
            ind=0,
            values=port_names,
        )


class MapEInstr1S(SFunctionality):
    def __init__(self, in_instruments: List[str], out_instruments: List[str]):
        unique: List[Union[str, int]] = list(set(in_instruments + out_instruments + [""]))
        super().__init__(
            name=ValidSettings.MAP_E_INSTR_1.value,
            ind=0,
            values=unique,
        )


class MapEInstr2S(SFunctionality):
    def __init__(self, in_instruments: List[str], out_instruments: List[str]):
        unique: List[Union[str, int]] = list(set([""] + in_instruments + out_instruments))
        super().__init__(
            name=ValidSettings.MAP_E_INSTR_2.value,
            ind=0,
            values=unique,
        )
