import math
import time
from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple, Type, Union

import rtmidi
from rtmidi import MidiIn, MidiOut

from .configs import InitConfig
from .const import ValidButtons, ValidSettings
from .functionalities import (
    MInFunctionality,
    MMappings,
    MMiDi,
    MMusic,
    MOutFunctionality,
    SFunctionality,
)
from .init import (
    init_io_modes_and_instruments_mem,
    init_mappings_mem,
    init_music_mem,
    init_settings,
)
from .presets import read_preset_type

DEBUG: bool = True


class Sequencer:
    def __init__(self, loc: str):
        self.loc = loc
        self.clock_sync = 0.0
        self.quant_interval: float = 0.0
        self.step_interval: float = 0.0
        self.part_interval: float = 0.0
        self.tempo: int = 0
        self.detached = False
        self.internal_config = InitConfig()
        self.settings: Dict[ValidSettings, SFunctionality] = dict()
        self.in_modes: Dict[str, MInFunctionality] = dict()
        self.out_modes: Dict[str, MOutFunctionality] = dict()
        self.in_instruments: List[str] = list()
        self.out_instruments: List[str] = list()
        self.midi_outs_ids: List[int] = list()
        self.midi_ins_ids: List[int] = list()
        self.valid_out_modes: List[str] = list()
        self.valid_in_modes: List[str] = list()
        self.port_names_comb: List[Tuple[int, str, bool]] = list()
        self.mappings: MMappings = init_mappings_mem()
        self.sequences: MMusic = MMusic("", "", "", dict())
        self.tempo = self.internal_config.init_tempo
        self.reset_intervals()

    def debug_sequence(self) -> None:
        import json

        fh = open(f"{self.__class__.__name__}.seq.{self.detached}.json", "w")
        json.dump(self.sequences.data, indent=2, sort_keys=True, fp=fh)
        fh.close()

    def reset_intervals(self) -> None:
        if ValidSettings.TEMPO in self.settings:
            self.tempo = int(self.settings[ValidSettings.TEMPO].get_value())
        self.quant_interval = round((1 / (self.tempo / 60)) / self.internal_config.n_quants, 4)
        self.step_interval = self.quant_interval * self.internal_config.n_quants
        self.part_interval = self.step_interval * self.internal_config.n_steps

    def init_data(self) -> None:
        self.port_names_comb = self.mappings.get_port_names_comb()
        self.out_modes, self.out_instruments, self.in_modes, self.in_instruments = (
            init_io_modes_and_instruments_mem()
        )
        self.valid_out_modes = list(self.out_modes.keys())
        self.valid_in_modes = list(self.in_modes.keys())
        self.settings = init_settings(
            midi_ids=self.midi_outs_ids,
            valid_out_modes=self.valid_out_modes,
            port_names_comb=self.port_names_comb,
            out_instruments=self.out_instruments,
            in_instruments=self.in_instruments,
        )
        self.sequences = init_music_mem(mappings=self.mappings)

    def get_current_e_pos(self) -> Tuple[int, int, int, int, str]:
        midi = int(self.settings[ValidSettings.E_MIDI_O].get_value())
        channel = int(self.settings[ValidSettings.E_CHANNEL].get_value())
        part = int(self.settings[ValidSettings.E_PART].get_value())
        step = int(self.settings[ValidSettings.E_STEP].get_value())
        valid_out_mode = str(self.settings[ValidSettings.E_O_MODE].get_value())
        return midi, channel, part, step, valid_out_mode

    def get_current_v_pos(self) -> Tuple[int, int, int, int, str]:
        midi = int(self.settings[ValidSettings.V_MIDI_O].get_value())
        channel = int(self.settings[ValidSettings.V_CHANNEL].get_value())
        part = int(self.settings[ValidSettings.V_PART].get_value())
        step = int(self.settings[ValidSettings.V_STEP].get_value())
        valid_out_mode = str(self.settings[ValidSettings.V_O_MODE].get_value())
        return midi, channel, part, step, valid_out_mode

    def next_e_pos(self, valid_setting: ValidSettings) -> Optional["SFunctionality"]:
        c_midi, c_channel, c_part, c_step, c_valid_out_mode = self.get_current_e_pos()
        n_midi_set = self.settings[ValidSettings.E_MIDI_O].new()
        n_channel_set = self.settings[ValidSettings.E_CHANNEL].new()
        n_part_set = self.settings[ValidSettings.E_PART].new()
        n_step_set = self.settings[ValidSettings.E_STEP].new()
        n_out_mode_set = self.settings[ValidSettings.E_O_MODE].new()
        exists_in = False
        check_map: Dict[ValidSettings, Dict] = {
            ValidSettings.E_MIDI_O: self.sequences.data,
            ValidSettings.E_CHANNEL: self.sequences.data[int(c_midi)],
            ValidSettings.E_PART: self.sequences.data[int(c_midi)][int(c_channel)],
            ValidSettings.E_STEP: self.sequences.data[int(c_midi)][int(c_channel)][int(c_part)],
            ValidSettings.E_O_MODE: self.sequences.data[int(c_midi)][int(c_channel)][int(c_part)][
                int(c_step)
            ],
        }
        next_map: Dict[ValidSettings, SFunctionality] = {
            ValidSettings.E_MIDI_O: n_midi_set,
            ValidSettings.E_CHANNEL: n_channel_set,
            ValidSettings.E_PART: n_part_set,
            ValidSettings.E_STEP: n_step_set,
            ValidSettings.E_O_MODE: n_out_mode_set,
        }
        conv_map: Dict[ValidSettings, Type[Union[str, int]]] = {
            ValidSettings.E_MIDI_O: int,
            ValidSettings.E_CHANNEL: int,
            ValidSettings.E_PART: int,
            ValidSettings.E_STEP: int,
            ValidSettings.E_O_MODE: str,
        }
        while not exists_in:
            check_in = check_map[valid_setting]
            next_set = next_map[valid_setting]
            next_set.next_ind()
            n_val = next_set.get_value()
            conv = conv_map[valid_setting]
            if conv(n_val) in check_in:
                exists_in = True
                return next_set
        return None

    def next_v_pos(self, valid_setting: ValidSettings) -> Optional["SFunctionality"]:
        c_midi, c_channel, c_part, c_step, c_valid_out_mode = self.get_current_e_pos()
        n_midi_set = self.settings[ValidSettings.V_MIDI_O].new()
        n_channel_set = self.settings[ValidSettings.V_CHANNEL].new()
        n_part_set = self.settings[ValidSettings.V_PART].new()
        n_step_set = self.settings[ValidSettings.V_STEP].new()
        n_out_mode_set = self.settings[ValidSettings.V_O_MODE].new()
        exists_in = False
        check_map: Dict[ValidSettings, Dict] = {
            ValidSettings.V_MIDI_O: self.sequences.data,
            ValidSettings.V_CHANNEL: self.sequences.data[int(c_midi)],
            ValidSettings.V_PART: self.sequences.data[int(c_midi)][int(c_channel)],
            ValidSettings.V_STEP: self.sequences.data[int(c_midi)][int(c_channel)][int(c_part)],
            ValidSettings.V_O_MODE: self.sequences.data[int(c_midi)][int(c_channel)][int(c_part)][
                int(c_step)
            ],
        }
        next_map: Dict[ValidSettings, SFunctionality] = {
            ValidSettings.V_MIDI_O: n_midi_set,
            ValidSettings.V_CHANNEL: n_channel_set,
            ValidSettings.V_PART: n_part_set,
            ValidSettings.V_STEP: n_step_set,
            ValidSettings.V_O_MODE: n_out_mode_set,
        }
        conv_map: Dict[ValidSettings, Type[Union[str, int]]] = {
            ValidSettings.V_MIDI_O: int,
            ValidSettings.V_CHANNEL: int,
            ValidSettings.V_PART: int,
            ValidSettings.V_STEP: int,
            ValidSettings.V_O_MODE: str,
        }
        while not exists_in:
            check_in = check_map[valid_setting]
            next_set = next_map[valid_setting]
            next_set.next_ind()
            n_val = next_set.get_value()
            conv = conv_map[valid_setting]
            if conv(n_val) in check_in:
                exists_in = True
                return next_set
        return None

    def get_current_e_step_out_mode(
        self, valid_out_mode: Optional[str] = None
    ) -> MOutFunctionality:
        midi, channel, part, step, out_mode = self.get_current_e_pos()
        if valid_out_mode is None:
            valid_out_mode = out_mode
        indexes = self.sequences.data[midi][channel][part][step][valid_out_mode]
        current_out_mode = self.out_modes[valid_out_mode].new_with_indexes(indexes=indexes)
        return current_out_mode

    def get_current_v_step_out_mode(
        self, valid_out_mode: Optional[str] = None
    ) -> MOutFunctionality:
        midi, channel, part, step, out_mode = self.get_current_v_pos()
        if valid_out_mode is None:
            valid_out_mode = out_mode
        indexes = self.sequences.data[midi][channel][part][step][valid_out_mode]
        current_out_mode = self.out_modes[valid_out_mode].new_with_indexes(indexes=indexes)
        return current_out_mode

    def get_current_new_out_mode(self, valid_out_mode: Optional[str] = None) -> MOutFunctionality:
        midi, channel, part, step, out_mode = self.get_current_e_pos()
        if valid_out_mode is None:
            valid_out_mode = out_mode
        current_out_mode = self.out_modes[valid_out_mode].new(lock=False)
        return current_out_mode

    def get_current_proto_mode(self, valid_out_mode: Optional[str] = None) -> MOutFunctionality:
        midi, channel, part, step, out_mode = self.get_current_e_pos()
        if valid_out_mode is None:
            valid_out_mode = out_mode
        return self.out_modes[valid_out_mode]

    def get_sound_properties(self) -> Tuple[List[str], List[str]]:
        current_out_mode = self.get_current_e_step_out_mode()
        out_mode_values = current_out_mode.get_row_values(exe=0)
        out_mode_labels = current_out_mode.get_labels()
        all_labels = ["Mode"] + out_mode_labels
        all_values = [current_out_mode.name] + out_mode_values
        return all_labels, all_values

    def set_step(self, out_mode: MOutFunctionality) -> None:
        positions_to_set: List[Tuple[int, int, int, int, str]] = list()
        if self.settings[ValidSettings.RECORD].get_value() == ValidButtons.ON:
            positions_to_set += self.get_record_positions(out_mode=out_mode)
        elif self.settings[ValidSettings.COPY].get_value() == ValidButtons.ON:
            positions_to_set += self.get_copy_positions(out_mode=out_mode)
        for position_to_set in positions_to_set:
            midi, channel, part, step, valid_out_mode = position_to_set
            self.sequences.data[midi][channel][part][step][valid_out_mode] = out_mode.get_indexes()
        self.debug_sequence() if DEBUG else None

    def get_record_positions(
        self, out_mode: MOutFunctionality
    ) -> List[Tuple[int, int, int, int, str]]:
        button_label = out_mode.get_but_label()
        positions_to_record: List[Tuple[int, int, int, int, str]] = list()
        if out_mode.get_single_value_by_lab(exe=0, lab=button_label) != ValidButtons.NEXT:
            positions_to_record += [self.get_current_e_pos()]
            self.settings[ValidSettings.E_STEP].next_ind()
            if self.settings[ValidSettings.VIEW_FUNCTION].get_value() == ValidButtons.VIEW_REC:
                position_to_record = self.get_current_v_pos()
                self.settings[ValidSettings.V_STEP].next_ind()
                if position_to_record not in positions_to_record:
                    positions_to_record += [position_to_record]
        return positions_to_record

    def get_copy_positions(
        self, out_mode: MOutFunctionality
    ) -> List[Tuple[int, int, int, int, str]]:
        button_label = out_mode.get_but_label()
        positions_to_copy: List[Tuple[int, int, int, int, str]] = list()
        if out_mode.get_single_value_by_lab(exe=0, lab=button_label) != ValidButtons.NEXT:
            positions_to_copy += [self.get_current_v_pos()]
        return positions_to_copy

    def set_option(self, option: SFunctionality) -> None:
        valid_setting = ValidSettings(option.name)
        self.settings[valid_setting].update_with_ind(option.get_ind())
        if self.settings[valid_setting].get_value() == ValidButtons.PRESETS_L_MUSIC:
            self.load_music()
        elif self.settings[valid_setting].get_value() == ValidButtons.PRESETS_L_MAP:
            self.load_map()
        elif valid_setting in [
            ValidSettings.MAP_E_DIR,
            ValidSettings.MAP_E_MIDI,
            ValidSettings.MAP_E_CH,
            ValidSettings.MAP_E_INSTR_1,
            ValidSettings.MAP_E_INSTR_2,
            ValidSettings.MAP_E_PNAME,
        ]:
            self.edit_mappings(valid_setting=valid_setting)

    def edit_mappings(self, valid_setting: ValidSettings):
        conn_id = int(self.settings[ValidSettings.MAP_E_CONN].get_value())
        is_out = str(self.settings[ValidSettings.MAP_E_DIR].get_value()) == "True"
        midi_id = int(self.settings[ValidSettings.MAP_E_MIDI].get_value())
        port_name = str(self.settings[ValidSettings.MAP_E_PNAME].get_value())
        channel = int(self.settings[ValidSettings.MAP_E_CH].get_value())
        instr_1 = str(self.settings[ValidSettings.MAP_E_INSTR_1].get_value())
        instr_2 = str(self.settings[ValidSettings.MAP_E_INSTR_2].get_value())
        conns = self.mappings.conns
        if valid_setting == ValidSettings.MAP_E_DIR:
            if conns[conn_id].is_out != is_out:
                conns[conn_id].instruments = [""] * self.internal_config.max_instr
            conns[conn_id].is_out = is_out
        elif valid_setting == ValidSettings.MAP_E_MIDI:
            conns[conn_id].midi_id = midi_id
        elif valid_setting == ValidSettings.MAP_E_PNAME:
            conns[conn_id].port_name = port_name
        elif valid_setting == ValidSettings.MAP_E_CH:
            conns[conn_id].channel = channel
        elif valid_setting == ValidSettings.MAP_E_INSTR_1:
            conns[conn_id].instruments[0] = instr_1
        elif valid_setting == ValidSettings.MAP_E_INSTR_2:
            conns[conn_id].instruments[1] = instr_2

    def load_music(self):
        music_name = str(self.settings[ValidSettings.MUS_NAME].get_value())
        file_path = f"{self.loc}/{MMusic.__name__}/{music_name}.yaml"
        preset = read_preset_type(file_path=file_path)
        if isinstance(preset, MMusic):
            self.sequences = preset

    def load_map(self):
        map_name = str(self.settings[ValidSettings.MAP_NAME].get_value())
        file_path = f"{self.loc}/{MMappings.__name__}/{map_name}.yaml"
        preset = read_preset_type(file_path=file_path)
        if isinstance(preset, MMappings):
            self.mappings = preset

    def find_all_to_play(self) -> Dict[int, Dict[int, Dict[int, bool]]]:
        all_to_play: Dict[int, Dict[int, Dict[int, bool]]] = defaultdict(lambda: defaultdict(dict))
        midis: Set[int] = set()
        parts: Set[int] = set()
        midi_channel: Dict[int, Set[int]] = defaultdict(set)
        for midi_id in self.sequences.data.keys():
            for channel in self.sequences.data[midi_id].keys():
                for part in self.sequences.data[midi_id][channel].keys():
                    for step in self.sequences.data[midi_id][channel][part].keys():
                        for valid_out_mode in self.sequences.data[midi_id][channel][part][
                            step
                        ].keys():
                            self.apply_vis_element(
                                midi_id=midi_id,
                                channel=channel,
                                part=part,
                                parts=parts,
                                step_data=self.sequences.data[midi_id][channel][part][step],
                                valid_out_mode=valid_out_mode,
                                midi_channel=midi_channel,
                                midis=midis,
                            )
        for midi in midis:
            for channel in midi_channel[midi]:
                for part in parts:
                    all_to_play[midi][channel][part] = True
        return all_to_play

    def find_part_to_play(self) -> Dict[int, Dict[int, Dict[int, bool]]]:
        part_to_play: Dict[int, Dict[int, Dict[int, bool]]] = defaultdict(lambda: defaultdict(dict))
        midi, channel, part, step, valid_out_mode = self.get_current_e_pos()
        part_to_play[midi][channel][part] = True
        if self.settings[ValidSettings.VIEW_FUNCTION].get_value() == ValidButtons.VIEW_PLAY:
            midi, channel, part, step, valid_out_mode = self.get_current_v_pos()
            part_to_play[midi][channel][part] = True
        return part_to_play

    def find_view_to_play(self) -> Dict[int, Dict[int, Dict[int, bool]]]:
        part_to_play: Dict[int, Dict[int, Dict[int, bool]]] = defaultdict(lambda: defaultdict(dict))
        if self.settings[ValidSettings.VIEW_FUNCTION].get_value() == ValidButtons.VIEW_PLAY:
            midi, channel, part, step, valid_out_mode = self.get_current_v_pos()
            part_to_play[midi][channel][part] = True
        return part_to_play

    def apply_vis_element(
        self,
        midi_id: int,
        channel: int,
        part: int,
        valid_out_mode: str,
        step_data: Dict[str, List[List[int]]],
        midis: Set[int],
        midi_channel: Dict[int, Set[int]],
        parts: Set[int],
    ) -> bool:
        indexes = step_data[valid_out_mode]
        out_mode = self.get_current_proto_mode(valid_out_mode=valid_out_mode)
        has_vis_element = False
        vis_index_1, vis_index_2 = out_mode.get_vis_ind()
        has_note = indexes[vis_index_1][vis_index_2]
        if has_note > 0:
            midis.add(midi_id)
            midi_channel[midi_id].add(channel)
            parts.add(part)
        return has_vis_element

    def find_parts_to_play(self) -> Dict[int, Dict[int, Dict[int, bool]]]:
        parts_to_play: Dict[int, Dict[int, Dict[int, bool]]] = defaultdict(
            lambda: defaultdict(dict)
        )
        midis: Set[int] = set()
        parts: Set[int] = set()
        midi_channel: Dict[int, Set[int]] = defaultdict(set)
        midi, channel, part, step, valid_out_mode = self.get_current_e_pos()
        parts.add(part)
        if self.settings[ValidSettings.VIEW_FUNCTION].get_value() == ValidButtons.VIEW_PLAY:
            midi, channel, part, step, valid_out_mode = self.get_current_v_pos()
            parts.add(part)
        for midi_id in self.sequences.data.keys():
            for channel in self.sequences.data[midi_id].keys():
                for part in self.sequences.data[midi_id][channel].keys():
                    for step in self.sequences.data[midi_id][channel][part].keys():
                        for valid_out_mode in self.sequences.data[midi_id][channel][part][
                            step
                        ].keys():
                            self.apply_vis_element(
                                midi_id=midi_id,
                                channel=channel,
                                part=part,
                                parts=set(),
                                step_data=self.sequences.data[midi][channel][part][step],
                                valid_out_mode=valid_out_mode,
                                midi_channel=midi_channel,
                                midis=midis,
                            )
        for midi in midis:
            for channel in midi_channel[midi]:
                for part in parts:
                    parts_to_play[midi][channel][part] = True
        return parts_to_play

    def get_play_positions(self) -> Dict[int, Dict[int, Dict[int, bool]]]:
        play_show_value = self.settings[ValidSettings.PLAY_SHOW].get_value()
        play_function_value = self.settings[ValidSettings.PLAY_FUNCTION].get_value()
        if play_show_value == ValidButtons.ON and play_function_value == ValidButtons.PLAY_ALL:
            # Play all music
            play_positions = self.find_all_to_play()
        elif play_show_value == ValidButtons.ON and play_function_value == ValidButtons.PLAY_PART:
            # Play single part
            play_positions = self.find_part_to_play()
        elif play_show_value == ValidButtons.ON and play_function_value == ValidButtons.PLAY_PARTS:
            # Play multiple parts
            play_positions = self.find_parts_to_play()
        else:
            # Play view part
            play_positions = self.find_view_to_play()
        if play_show_value == ValidButtons.OFF:
            play_positions = dict()
        return play_positions

    def sync_clock(self) -> None:
        if (
            self.clock_sync == 0.0
            and self.settings[ValidSettings.PLAY_SHOW].get_value() == ValidButtons.ON
        ):
            self.reset_intervals()
            self.clock_sync = float(math.ceil(time.time() + InitConfig().init_time))


class MiDiIn:
    def __init__(self, midi: MMiDi):
        self.port_id = midi.port_id
        self.midi_id = midi.midi_id
        self.port_name = midi.port_name
        self.channels: List[int] = midi.channels
        self.internal_config = InitConfig()
        self.sequencer: Optional[Sequencer] = None
        self.midi_in: Optional[MidiIn] = None
        self.in_modes: List[MInFunctionality] = list()
        self.allowed_valid_in_modes: List[str] = list()

    def attach(self, sequencer: Sequencer) -> None:
        self.sequencer = sequencer
        self.midi_in = rtmidi.MidiIn()
        self.midi_in.open_port(self.port_id)
        self.reset_in_modes()

    def reset_in_modes(self):
        if self.sequencer is not None:
            allowed_instruments: List[str] = list()
            for conn in self.sequencer.mappings.get_sorted():
                if not conn.is_out and conn.midi_id == self.midi_id:
                    for instrument in conn.instruments:
                        allowed_instruments.append(instrument)
            for in_mode in self.sequencer.in_modes.values():
                for instrument in in_mode.instruments:
                    if instrument in allowed_instruments:
                        self.allowed_valid_in_modes.append(in_mode.name)
                        if in_mode.name in self.sequencer.in_modes:
                            self.in_modes.append(
                                self.sequencer.in_modes[in_mode.name].new(lock=False)
                            )

    def run_message_bus(
        self, out_midi: int, out_channel: int
    ) -> List[Tuple[int, int, MOutFunctionality]]:
        midi_ch_out_modes: List[Tuple[int, int, MOutFunctionality]] = list()
        if self.sequencer is not None and self.midi_in is not None:
            messages: List[List[int]] = list()
            ts: List[float] = list()
            while True:
                message_t = self.midi_in.get_message()
                if message_t is None:
                    break
                else:
                    message, t = message_t
                    messages.append(message)
                    ts.append(t)
            if len(ts):
                ts[0] = 0.0
            for midi, channel, out_mode in self.translate_ins_to_outs(messages=messages, ts=ts):
                if midi < 0:
                    midi = out_midi
                if channel < 0:
                    channel = out_channel
                midi_ch_out_modes.append((midi, channel, out_mode))
        return midi_ch_out_modes

    def translate_ins_to_outs(
        self,
        messages: List[List[int]],
        ts: List[float],
    ) -> List[Tuple[int, int, MOutFunctionality]]:
        midi_ch_out_modes: List[Tuple[int, int, MOutFunctionality]] = list()
        while len(messages):
            midi_ch_out_mode = self.translate_ins_to_out(messages=messages, ts=ts)
            if midi_ch_out_mode is not None:
                midi_ch_out_modes.append(midi_ch_out_mode)
        return midi_ch_out_modes

    def translate_ins_to_out(
        self, messages: List[List[int]], ts: List[float]
    ) -> Optional[Tuple[int, int, MOutFunctionality]]:
        if self.sequencer is not None:
            t1 = time.time()
            while len(messages):
                message = messages.pop()
                self.fix_command_length_channel(message=message)
                t2 = ts.pop()
                for in_mode in self.in_modes:
                    in_mode.set_with_message_and_time(message=message, t=(t1, t2))
                    if not in_mode.has_next():
                        return in_mode.convert_with_out_modes_and_tempo(
                            out_modes=self.sequencer.out_modes,
                            tempo=self.sequencer.tempo,
                            n_quants=self.internal_config.n_quants,
                        )
            return None
        else:
            raise ValueError("Sequencer is not ready!")

    @staticmethod
    def fix_command_length_channel(message: List[int]) -> None:
        command = message[0]
        channel = (command & 0x0F) + 1
        command = command & 0xF0
        message[0] = command
        message.append(0)
        message.append(channel)


class MiDiOut:
    def __init__(self, midi: MMiDi):
        self.port_id = midi.port_id
        self.midi_id = midi.midi_id
        self.port_name = midi.port_name
        self.channels: List[int] = midi.channels
        self.midi_out: Optional[MidiOut] = None
        self.internal_config = InitConfig()
        self.sequencer: Optional[Sequencer] = None
        self.allowed_valid_out_modes: List[str] = list()
        self.unscheduled_step: List[Tuple[int, MOutFunctionality]] = list()
        self.scheduled_steps: Dict[float, Dict[int, List[MOutFunctionality]]] = dict()
        self.max_part_tick = 0.0

    def debug_midi(
        self,
        time_now: float,
        midi_id: int,
        channel: int,
        step_tick: float,
        offset_time: float,
        next_tick: float,
        valid_out_mode: str,
        exe: int,
        message: List[int],
    ) -> None:
        if self.sequencer is not None:
            fh = open(
                f"{self.__class__.__name__}.midi.{self.midi_id}."
                f"{self.port_id}.{self.sequencer.detached}.txt",
                "a",
            )
            fh.write(
                f"{offset_time} {round(time_now,3)} {step_tick} "
                f"{next_tick} {midi_id} {channel} {valid_out_mode} {exe} {message}\n"
            )
            fh.close()

    def attach(self, sequencer: Sequencer) -> None:
        self.sequencer = sequencer
        self.unscheduled_step = list()
        self.scheduled_steps = defaultdict(lambda: defaultdict(list))
        self.midi_out = rtmidi.MidiOut()
        self.midi_out.open_port(self.port_id)
        self.reset_out_modes()

    def reset_out_modes(self):
        if self.sequencer is not None:
            allowed_instruments: List[str] = list()
            for conn in self.sequencer.mappings.get_sorted():
                if conn.is_out and conn.midi_id == self.midi_id:
                    for instrument in conn.instruments:
                        allowed_instruments.append(instrument)
            for out_mode in self.sequencer.out_modes.values():
                for instrument in out_mode.instruments:
                    if instrument in allowed_instruments:
                        self.allowed_valid_out_modes.append(out_mode.name)

    # - - SCHEDULE - - #

    def add_parts_to_step_schedule(self) -> None:
        if self.sequencer is not None:
            play_positions = self.sequencer.get_play_positions()
            time_now = time.time()
            if (
                len(play_positions)
                and len(self.scheduled_steps) == 0
                and time_now >= self.max_part_tick + self.sequencer.clock_sync
            ):
                self.sequencer.clock_sync = 0.0
                self.sequencer.sync_clock()
                self.max_part_tick = 0.0
                for midi in play_positions.keys():
                    for channel in play_positions[midi].keys():
                        for part in play_positions[midi][channel].keys():
                            part_tick = self.sequencer.part_interval * (part - 1)
                            self.add_steps_to_step_schedule(
                                midi=midi, channel=channel, part=part, part_tick=part_tick
                            )
                            last_part_tick = self.sequencer.part_interval * (part + 0)
                            if last_part_tick > self.max_part_tick:
                                self.max_part_tick = last_part_tick

    def add_steps_to_step_schedule(
        self, midi: int, channel: int, part: int, part_tick: float
    ) -> None:
        if midi == self.midi_id and self.sequencer is not None:
            for step in self.sequencer.sequences.data[midi][channel][part].keys():
                step_tick = part_tick + (step - 1) * self.sequencer.step_interval
                for valid_out_mode in self.sequencer.sequences.data[midi][channel][part][
                    step
                ].keys():
                    indexes = self.sequencer.sequences.data[midi][channel][part][step][
                        valid_out_mode
                    ]
                    out_mode = self.sequencer.get_current_new_out_mode(
                        valid_out_mode=valid_out_mode
                    )
                    out_mode.set_indexes(indexes=indexes)
                    button_label = out_mode.get_but_label()
                    if out_mode.get_single_value_by_lab(exe=0, lab=button_label) != ValidButtons.NA:
                        self.scheduled_steps[step_tick][channel].append(out_mode)

    def play_later_and_schedule(self) -> None:
        self.add_parts_to_step_schedule()
        if self.sequencer is not None:
            offset_time = self.sequencer.clock_sync
            old_schedule: Dict[float, Dict[int, List[int]]] = defaultdict(lambda: defaultdict(list))
            new_schedule: Dict[float, Dict[int, List[MOutFunctionality]]] = defaultdict(
                lambda: defaultdict(list)
            )
            if self.midi_out is not None and not self.midi_out.is_port_open():
                self.midi_out.open_port(self.port_id)
            for step_tick in sorted(self.scheduled_steps.keys()):
                time_now = time.time()
                if time_now >= (step_tick + offset_time):
                    for channel in self.scheduled_steps[step_tick].keys():
                        self.play_now(
                            step_tick=step_tick,
                            time_now=time_now,
                            offset_time=offset_time,
                            channel=channel,
                            out_modes=self.scheduled_steps[step_tick][channel],
                            old_schedule=old_schedule,
                            new_schedule=new_schedule,
                        )
                    break
            self.update_step_schedule(old_schedule=old_schedule, new_schedule=new_schedule)

    def play_now_and_schedule(self) -> None:
        old_schedule: Dict[float, Dict[int, List[int]]] = defaultdict(lambda: defaultdict(list))
        new_schedule: Dict[float, Dict[int, List[MOutFunctionality]]] = defaultdict(
            lambda: defaultdict(list)
        )
        if self.midi_out is not None and not self.midi_out.is_port_open():
            self.midi_out.open_port(self.port_id)
        if self.sequencer is not None:
            self.sequencer.reset_intervals()
            while len(self.unscheduled_step):
                channel, out_mode = self.unscheduled_step.pop()
                # self.play_now(
                #    step_tick=0,
                #    time_now=time_now,
                #    channel=channel,
                #    old_schedule=old_schedule,
                #    new_schedule=new_schedule,
                #    out_modes=[out_mode],
                # )
                # self.sequencer.clock_sync = time_now
            self.update_step_schedule(old_schedule=old_schedule, new_schedule=new_schedule)

    def play_now(
        self,
        step_tick: float,
        time_now: float,
        offset_time: float,
        channel: int,
        out_modes: List["MOutFunctionality"],
        old_schedule: Dict[float, Dict[int, List[int]]],
        new_schedule: Dict[float, Dict[int, List[MOutFunctionality]]],
    ) -> None:
        for i, out_mode in enumerate(out_modes):
            if out_mode.name in self.allowed_valid_out_modes:
                message: List[int] = out_mode.get_as_message()
                if len(message) >= 3 and min(message) >= 0:
                    self.channel_message(
                        midi_out=self.midi_out,
                        command=message[0],
                        ch=channel,
                        data=message[1:3],
                    )
                    (
                        self.debug_midi(
                            midi_id=self.midi_id,
                            channel=channel,
                            time_now=time_now,
                            step_tick=step_tick,
                            next_tick=0.0,
                            offset_time=offset_time,
                            exe=out_mode.get_exe(),
                            valid_out_mode=out_mode.name,
                            message=message,
                        )
                        if DEBUG
                        else None
                    )
                if len(message) > 3 and min(message) >= 0 and out_mode.has_next():
                    if self.sequencer is not None:
                        next_tick = step_tick + float(message[3] * self.sequencer.quant_interval)
                        new_schedule[next_tick][channel].append(out_mode.new(lock=False))
                        (
                            self.debug_midi(
                                midi_id=self.midi_id,
                                channel=-channel,
                                time_now=time_now,
                                step_tick=step_tick,
                                next_tick=next_tick,
                                offset_time=offset_time,
                                exe=out_mode.get_exe(),
                                valid_out_mode=out_mode.name,
                                message=message,
                            )
                            if DEBUG
                            else None
                        )
                old_schedule[step_tick][channel].append(i)

    def update_step_schedule(
        self,
        old_schedule: Dict[float, Dict[int, List[int]]],
        new_schedule: Dict[float, Dict[int, List[MOutFunctionality]]],
    ) -> None:
        if len(old_schedule) or len(new_schedule):
            for step_tick in self.scheduled_steps.keys():
                for channel in self.scheduled_steps[step_tick].keys():
                    for i, out_mode in enumerate(self.scheduled_steps[step_tick][channel]):
                        if (
                            step_tick not in old_schedule
                            and channel not in old_schedule[step_tick]
                            and i not in old_schedule[step_tick][channel]
                        ):
                            new_schedule[step_tick][channel].append(out_mode)
            self.scheduled_steps = new_schedule

    # - - BOTH - - #

    def run_message_bus(self) -> None:
        if self.sequencer is not None:
            self.play_now_and_schedule()
            self.play_later_and_schedule()

    @staticmethod
    def channel_message(midi_out: MidiOut, command: int, data: List[int], ch=None):
        """Send a MIDI channel out_mode message."""
        command = (command & 0xF0) | ((ch if ch else 1) - 1 & 0xF)
        msg = [command] + [value & 0x7F for value in data]
        midi_out.send_message(msg)
