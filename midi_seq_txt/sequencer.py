import math
import time
from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple

import mingus.core.scales as scales
import rtmidi
from rtmidi import MidiOut

from .configs import InitConfig
from .const import ValidButtons, ValidModes, ValidSettings
from .functionalities import MFunctionality, MMappings, MMusic, SFunctionality
from .init import init_mappings, init_modes, init_music, init_settings

DEBUG: bool = False


class Sequencer:
    def __init__(self):
        self.internal_config = InitConfig()
        self.settings: Dict[ValidSettings, SFunctionality] = dict()
        self.modes: Dict[ValidModes, MFunctionality] = dict()
        self.n_midis = 0
        self.detached = False
        self.mappings: MMappings = init_mappings()
        self.sequences: MMusic = MMusic("", dict())
        self.tempo: int = self.internal_config.init_tempo
        self.scale: str = self.internal_config.init_scale
        self.clock_sync = 0.0
        self.quant_interval: float = 0.0
        self.step_interval: float = 0.0
        self.part_interval: float = 0.0
        self.reset_intervals()
        self.reset_scale()

    def debug(self) -> None:
        import json

        fh = open(f"{self.__class__.__name__}.{self.detached}.json", "w")
        json.dump(self.sequences.data, indent=2, sort_keys=True, fp=fh)
        fh.close()

    def reset_intervals(self) -> None:
        if ValidSettings.TEMPO in self.settings:
            self.tempo = int(self.settings[ValidSettings.TEMPO].get_value())
        self.quant_interval = round((1 / (self.tempo / 60)) / self.internal_config.n_quants, 4)
        self.step_interval = self.quant_interval * self.internal_config.n_quants
        self.part_interval = self.step_interval * self.internal_config.n_steps

    def reset_scale(self):
        pass

    def init_data(self) -> None:
        self.settings = init_settings(self.n_midis)
        self.modes = init_modes()
        self.sequences = init_music(n_midis=self.n_midis, mappings=self.mappings)

    def get_current_e_pos(self, first_only: bool = False) -> Tuple[int, int, int, int, ValidModes]:
        midi = int(self.settings[ValidSettings.E_MIDI_O].get_value())
        channel = int(self.settings[ValidSettings.E_CHANNEL].get_value())
        part = int(self.settings[ValidSettings.E_PART].get_value())
        step = int(self.settings[ValidSettings.E_STEP].get_value())
        valid_mode = ValidModes(str(self.settings[ValidSettings.E_MODE].get_value()))
        if first_only:
            step = int(self.settings[ValidSettings.E_STEP].get_first_value())
        return midi, channel, part, step, valid_mode

    def get_current_v_pos(self, first_only: bool = False) -> Tuple[int, int, int, int, ValidModes]:
        midi = int(self.settings[ValidSettings.V_MIDI_O].get_value())
        channel = int(self.settings[ValidSettings.V_CHANNEL].get_value())
        part = int(self.settings[ValidSettings.V_PART].get_value())
        step = int(self.settings[ValidSettings.V_STEP].get_value())
        valid_mode = ValidModes(str(self.settings[ValidSettings.V_MODE].get_value()))
        if first_only:
            step = int(self.settings[ValidSettings.V_STEP].get_first_value())
        return midi, channel, part, step, valid_mode

    def next_e_pos(self, valid_setting: ValidSettings) -> Optional["SFunctionality"]:
        c_midi, c_channel, c_part, c_step, c_valid_mode = self.get_current_e_pos()
        n_midi_set = self.settings[ValidSettings.E_MIDI_O].new()
        n_channel_set = self.settings[ValidSettings.E_CHANNEL].new()
        n_part_set = self.settings[ValidSettings.E_PART].new()
        n_step_set = self.settings[ValidSettings.E_STEP].new()
        n_mode_set = self.settings[ValidSettings.E_MODE].new()
        exists_in = False
        while not exists_in:
            if valid_setting == ValidSettings.E_MIDI_O:
                check_in_m = self.sequences.data
                n_midi_set.next_ind()
                n_midi = n_midi_set.get_value()
                if int(n_midi) in check_in_m:
                    exists_in = True
                    return n_midi_set
            elif valid_setting == ValidSettings.E_CHANNEL:
                check_in_c = self.sequences.data[int(c_midi)]
                n_channel_set.next_ind()
                n_channel = n_channel_set.get_value()
                if int(n_channel) in check_in_c:
                    exists_in = True
                    return n_channel_set
            elif valid_setting == ValidSettings.E_PART:
                check_in_p = self.sequences.data[int(c_midi)][int(c_channel)]
                n_part_set.next_ind()
                n_part = n_part_set.get_value()
                if int(n_part) in check_in_p:
                    exists_in = True
                    return n_part_set
            elif valid_setting == ValidSettings.E_STEP:
                check_in_s = self.sequences.data[int(c_midi)][int(c_channel)][int(c_part)]
                n_step_set.next_ind()
                n_step = n_step_set.get_value()
                if int(n_step) in check_in_s:
                    exists_in = True
                    return n_step_set
            elif valid_setting == ValidSettings.E_MODE:
                check_in_v = self.sequences.data[int(c_midi)][int(c_channel)][int(c_part)][
                    int(c_step)
                ]
                n_mode_set.next_ind()
                n_valid_mode = n_mode_set.get_value()
                if ValidModes(str(n_valid_mode)) in check_in_v:
                    exists_in = True
                    return n_mode_set
            else:
                return None
        return None

    def next_v_pos(self, valid_setting: ValidSettings) -> Optional["SFunctionality"]:
        c_midi, c_channel, c_part, c_step, c_valid_mode = self.get_current_v_pos()
        n_midi_set = self.settings[ValidSettings.V_MIDI_O].new()
        n_channel_set = self.settings[ValidSettings.V_CHANNEL].new()
        n_part_set = self.settings[ValidSettings.V_PART].new()
        n_step_set = self.settings[ValidSettings.V_STEP].new()
        n_mode_set = self.settings[ValidSettings.V_MODE].new()
        exists_in = False
        while not exists_in:
            if valid_setting == ValidSettings.V_MIDI_O:
                check_in_m = self.sequences.data
                n_midi_set.next_ind()
                n_midi = n_midi_set.get_value()
                if int(n_midi) in check_in_m:
                    exists_in = True
                    return n_midi_set
            elif valid_setting == ValidSettings.V_CHANNEL:
                check_in_c = self.sequences.data[int(c_midi)]
                n_channel_set.next_ind()
                n_channel = n_channel_set.get_value()
                if int(n_channel) in check_in_c:
                    exists_in = True
                    return n_channel_set
            elif valid_setting == ValidSettings.V_PART:
                check_in_p = self.sequences.data[int(c_midi)][int(c_channel)]
                n_part_set.next_ind()
                n_part = n_part_set.get_value()
                if int(n_part) in check_in_p:
                    exists_in = True
                    return n_part_set
            elif valid_setting == ValidSettings.V_STEP:
                check_in_s = self.sequences.data[int(c_midi)][int(c_channel)][int(c_part)]
                n_step_set.next_ind()
                n_step = n_step_set.get_value()
                if int(n_step) in check_in_s:
                    exists_in = True
                    return n_step_set
            elif valid_setting == ValidSettings.V_MODE:
                check_in_v = self.sequences.data[int(c_midi)][int(c_channel)][int(c_part)][
                    int(c_step)
                ]
                n_mode_set.next_ind()
                n_valid_mode = n_mode_set.get_value()
                if ValidModes(str(n_valid_mode)) in check_in_v:
                    exists_in = True
                    return n_mode_set
            else:
                return None
        return None

    def get_first_step_mode(self, valid_mode: Optional[ValidModes] = None) -> MFunctionality:
        midi, channel, part, step, mode = self.get_current_e_pos()
        if valid_mode is None:
            valid_mode = mode
        first_step = int(self.settings[ValidSettings.E_STEP].get_first_value())
        indexes = self.sequences.data[midi][channel][part][first_step][valid_mode]
        first_mode = self.modes[valid_mode].new_with_indexes(indexes=indexes)
        return first_mode

    def get_current_e_step_mode(self, valid_mode: Optional[ValidModes] = None) -> MFunctionality:
        midi, channel, part, step, mode = self.get_current_e_pos()
        if valid_mode is None:
            valid_mode = mode
        indexes = self.sequences.data[midi][channel][part][step][valid_mode]
        current_mode = self.modes[valid_mode].new_with_indexes(indexes=indexes)
        return current_mode

    def get_current_v_step_mode(self, valid_mode: Optional[ValidModes] = None) -> MFunctionality:
        midi, channel, part, step, mode = self.get_current_v_pos()
        if valid_mode is None:
            valid_mode = mode
        indexes = self.sequences.data[midi][channel][part][step][valid_mode]
        current_mode = self.modes[valid_mode].new_with_indexes(indexes=indexes)
        return current_mode

    def get_current_new_mode(self, valid_mode: Optional[ValidModes] = None) -> MFunctionality:
        midi, channel, part, step, mode = self.get_current_e_pos()
        if valid_mode is None:
            valid_mode = mode
        current_mode = self.modes[valid_mode].new(lock=False)
        return current_mode

    def get_current_proto_mode(self, valid_mode: Optional[ValidModes] = None) -> MFunctionality:
        midi, channel, part, step, mode = self.get_current_e_pos()
        if valid_mode is None:
            valid_mode = mode
        return self.modes[valid_mode]

    def get_sound_properties(self) -> Tuple[List[str], List[str]]:
        current_mode = self.get_current_e_step_mode()
        mode_values = current_mode.get_row_values(exe=0)
        mode_labels = current_mode.get_labels()
        scale_values = self.get_current_scale_values()
        scale_labels = self.get_current_scale_labels()
        all_labels = ["Mode"] + mode_labels + scale_labels
        all_values = [current_mode.name] + mode_values + scale_values
        return all_labels, all_values

    def get_current_notes(self) -> List[str]:
        scale_values = self.get_current_scale_values()
        notes = scales.get_notes(key=scale_values[0])
        notes += [notes[0]]
        return notes

    def get_current_scale_values(self) -> List[str]:
        scale = self.get_first_step_mode(ValidModes.SCALE)
        return scale.get_row_values(exe=0)

    def get_current_scale_labels(self) -> List[str]:
        scale = self.get_first_step_mode(ValidModes.SCALE)
        return scale.get_labels()

    def set_step(self, mode: MFunctionality) -> None:
        positions_to_set: List[Tuple[int, int, int, int, ValidModes]] = list()
        if self.settings[ValidSettings.RECORD].get_value() == ValidButtons.ON:
            positions_to_set += self.get_record_positions(mode=mode)
        elif self.settings[ValidSettings.COPY].get_value() == ValidButtons.ON:
            positions_to_set += self.get_copy_positions(mode=mode)
        for position_to_set in positions_to_set:
            midi, channel, part, step, valid_mode = position_to_set
            self.sequences.data[midi][channel][part][step][valid_mode] = mode.get_indexes()
        self.debug() if DEBUG else None

    def get_record_positions(
        self, mode: MFunctionality
    ) -> List[Tuple[int, int, int, int, ValidModes]]:
        main_label = mode.get_vis_label()
        positions_to_record: List[Tuple[int, int, int, int, ValidModes]] = list()
        if mode.get_single_value_by_lab(exe=0, lab=main_label) != ValidButtons.NEXT:
            positions_to_record += [self.get_current_e_pos(first_only=mode.first_only)]
            self.settings[ValidSettings.E_STEP].next_ind()
            if self.settings[ValidSettings.VIEW_FUNCTION].get_value() == ValidButtons.VIEW_REC:
                position_to_record = self.get_current_v_pos(first_only=mode.first_only)
                self.settings[ValidSettings.V_STEP].next_ind()
                if position_to_record not in positions_to_record:
                    positions_to_record += [position_to_record]
        return positions_to_record

    def get_copy_positions(
        self, mode: MFunctionality
    ) -> List[Tuple[int, int, int, int, ValidModes]]:
        main_label = mode.get_vis_label()
        positions_to_copy: List[Tuple[int, int, int, int, ValidModes]] = list()
        if mode.get_single_value_by_lab(exe=0, lab=main_label) != ValidButtons.NEXT:
            positions_to_copy += [self.get_current_v_pos(first_only=mode.first_only)]
        return positions_to_copy

    def set_option(self, option: SFunctionality) -> None:
        valid_setting = ValidSettings(option.name)
        self.settings[valid_setting].update_with_ind(option.get_ind())

    def find_all_to_play(self) -> Dict[int, Dict[int, Dict[int, bool]]]:
        all_to_play: Dict[int, Dict[int, Dict[int, bool]]] = defaultdict(lambda: defaultdict(dict))
        midis: Set[int] = set()
        parts: Set[int] = set()
        midi_channel: Dict[int, Set[int]] = defaultdict(set)
        for midi in self.sequences.data.keys():
            for channel in self.sequences.data[midi].keys():
                for part in self.sequences.data[midi][channel].keys():
                    for step in self.sequences.data[midi][channel][part].keys():
                        for valid_mode in self.sequences.data[midi][channel][part][step].keys():
                            indexes = self.sequences.data[midi][channel][part][step][valid_mode]
                            mode = self.get_current_proto_mode(valid_mode=valid_mode)
                            if not mode.first_only:
                                vis_index_1, vis_index_2 = mode.get_vis_ind()
                                has_note = indexes[vis_index_1][vis_index_2]
                                if has_note > 0:
                                    midis.add(midi)
                                    parts.add(part)
                                    midi_channel[midi].add(channel)
        for midi in midis:
            for channel in midi_channel[midi]:
                for part in parts:
                    all_to_play[midi][channel][part] = True
        return all_to_play

    def find_part_to_play(self) -> Dict[int, Dict[int, Dict[int, bool]]]:
        part_to_play: Dict[int, Dict[int, Dict[int, bool]]] = defaultdict(lambda: defaultdict(dict))
        midi, channel, part, step, valid_mode = self.get_current_e_pos()
        part_to_play[midi][channel][part] = True
        if self.settings[ValidSettings.VIEW_FUNCTION].get_value() == ValidButtons.VIEW_PLAY:
            midi, channel, part, step, valid_mode = self.get_current_v_pos()
            part_to_play[midi][channel][part] = True
        return part_to_play

    def find_view_to_play(self) -> Dict[int, Dict[int, Dict[int, bool]]]:
        part_to_play: Dict[int, Dict[int, Dict[int, bool]]] = defaultdict(lambda: defaultdict(dict))
        if self.settings[ValidSettings.VIEW_FUNCTION].get_value() == ValidButtons.VIEW_PLAY:
            midi, channel, part, step, valid_mode = self.get_current_v_pos()
            part_to_play[midi][channel][part] = True
        return part_to_play

    def find_parts_to_play(self) -> Dict[int, Dict[int, Dict[int, bool]]]:
        parts_to_play: Dict[int, Dict[int, Dict[int, bool]]] = defaultdict(
            lambda: defaultdict(dict)
        )
        midis: Set[int] = set()
        parts: Set[int] = set()
        midi_channel: Dict[int, Set[int]] = defaultdict(set)
        midi, channel, part, step, valid_mode = self.get_current_e_pos()
        parts.add(part)
        if self.settings[ValidSettings.VIEW_FUNCTION].get_value() == ValidButtons.VIEW_PLAY:
            midi, channel, part, step, valid_mode = self.get_current_v_pos()
            parts.add(part)
        for midi in self.sequences.data.keys():
            for channel in self.sequences.data[midi].keys():
                for part in self.sequences.data[midi][channel].keys():
                    for step in self.sequences.data[midi][channel][part].keys():
                        for valid_mode in self.sequences.data[midi][channel][part][step].keys():
                            indexes = self.sequences.data[midi][channel][part][step][valid_mode]
                            mode = self.get_current_proto_mode(valid_mode=valid_mode)
                            if not mode.first_only:
                                vis_index_1, vis_index_2 = mode.get_vis_ind()
                                has_note = indexes[vis_index_1][vis_index_2]
                                if has_note > 0:
                                    midis.add(midi)
                                    midi_channel[midi].add(channel)
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
        if self.settings[ValidSettings.PLAY_SHOW].get_value() == ValidButtons.OFF:
            self.clock_sync = 0.0


class MiDiO:
    def __init__(self, port_id: int):
        super().__init__()
        self.port_id = port_id
        self.midi_out: Optional[MidiOut] = None
        self.internal_config = InitConfig()
        self.sequencer: Optional[Sequencer] = None
        self.scheduled_steps: Dict[float, Dict[int, List[MFunctionality]]] = dict()
        self.scheduled_notes: Dict[float, Dict[int, MFunctionality]] = dict()

    def attach(self, sequencer: Sequencer) -> None:
        self.sequencer = sequencer
        self.scheduled_steps = defaultdict(lambda: defaultdict(list))
        self.scheduled_notes = defaultdict(dict)
        self.midi_out = rtmidi.MidiOut()
        self.midi_out.open_port(self.port_id)

    # - - NOTES - - #

    def add_note_to_note_schedule(self, mode: MFunctionality) -> None:
        if mode is not None:
            main_label = mode.get_vis_label()
            if (
                self.sequencer is not None
                and self.sequencer.get_current_e_pos()[0] == self.port_id
                and mode.get_single_value_by_lab(0, main_label) != ValidButtons.NA
                and mode.get_single_value_by_lab(0, main_label) != ValidButtons.NEXT
            ):
                pass

    def play_note_schedule(self, offset_time: float = 0.0) -> None:
        pass

    def update_note_schedule(self) -> None:
        pass

    # - - SCHEDULE - - #

    def add_parts_to_step_schedule(self) -> None:
        if self.sequencer is not None:
            play_positions = self.sequencer.get_play_positions()
            if len(play_positions) and len(self.scheduled_steps) == 0:
                self.sequencer.clock_sync = 0.0
                self.sequencer.sync_clock()
                for midi in play_positions.keys():
                    for channel in play_positions[midi].keys():
                        for part in play_positions[midi][channel].keys():
                            part_tick = self.sequencer.part_interval * (part - 1)
                            self.add_steps_to_step_schedule(
                                midi=midi, channel=channel, part=part, part_tick=part_tick
                            )

    def add_steps_to_step_schedule(
        self, midi: int, channel: int, part: int, part_tick: float
    ) -> None:
        if midi == self.port_id and self.sequencer is not None:
            for step in self.sequencer.sequences.data[midi][channel][part].keys():
                step_tick = part_tick + (step - 1) * self.sequencer.step_interval
                for valid_mode in self.sequencer.sequences.data[midi][channel][part][step].keys():
                    indexes = self.sequencer.sequences.data[midi][channel][part][step][valid_mode]
                    mode = self.sequencer.get_current_new_mode(valid_mode=valid_mode)
                    if not mode.first_only:
                        mode.set_indexes(indexes=indexes)
                        main_label = mode.get_vis_label()
                        if mode.get_single_value_by_lab(exe=0, lab=main_label) != ValidButtons.NA:
                            self.scheduled_steps[step_tick][channel].append(mode)

    def play_step_schedule(self, offset_time: float = 0.0) -> None:
        old_schedule: Dict[float, Dict[int, List[int]]] = defaultdict(lambda: defaultdict(list))
        new_schedule: Dict[float, Dict[int, List[MFunctionality]]] = defaultdict(
            lambda: defaultdict(list)
        )
        if self.midi_out is not None and not self.midi_out.is_port_open():
            self.midi_out.open_port(self.port_id)
        for step_tick in sorted(self.scheduled_steps.keys()):
            if time.time() >= step_tick + offset_time:
                for channel in self.scheduled_steps[step_tick].keys():
                    for i, mode in enumerate(self.scheduled_steps[step_tick][channel]):
                        message: List[int] = mode.get_message()
                        if len(message) >= 3 and min(message) >= 0:
                            self.channel_message(
                                midi_out=self.midi_out,
                                command=message[0],
                                ch=channel,
                                data=message[1:3],
                            )
                        if len(message) > 3 and message[3] > 0 and min(message) >= 0:
                            if self.sequencer is not None:
                                next_tick = step_tick + float(
                                    message[3] * self.sequencer.quant_interval
                                )
                                new_schedule[next_tick][channel].append(mode.new(lock=False))
                        old_schedule[step_tick][channel].append(i)
                break
        self.update_step_schedule(old_schedule=old_schedule, new_schedule=new_schedule)

    def update_step_schedule(
        self,
        old_schedule: Dict[float, Dict[int, List[int]]],
        new_schedule: Dict[float, Dict[int, List[MFunctionality]]],
    ) -> None:
        if len(old_schedule) or len(new_schedule):
            for step_tick in self.scheduled_steps.keys():
                for channel in self.scheduled_steps[step_tick].keys():
                    for i, mode in enumerate(self.scheduled_steps[step_tick][channel]):
                        if (
                            step_tick not in old_schedule
                            and channel not in old_schedule[step_tick]
                            and i not in old_schedule[step_tick][channel]
                        ):
                            new_schedule[step_tick][channel].append(mode)
            self.scheduled_steps = new_schedule

    # - - BOTH - - #

    def run_note_and_step_schedule(self) -> None:
        if self.sequencer is not None:
            self.play_note_schedule(offset_time=self.sequencer.clock_sync)
            self.play_step_schedule(offset_time=self.sequencer.clock_sync)

    @staticmethod
    def channel_message(midi_out: MidiOut, command: int, data: List[int], ch=None):
        """Send a MIDI channel mode message."""
        command = (command & 0xF0) | ((ch if ch else 1) - 1 & 0xF)
        msg = [command] + [value & 0x7F for value in data]
        midi_out.send_message(msg)
