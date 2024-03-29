import time
from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple

import mingus.core.scales as scales
import rtmidi
from rtmidi import MidiOut

from .configs import InitConfig
from .const import ValidButtons, ValidModes, ValidSettings
from .functionalities import MFunctionality, SFunctionality, init_modes, init_settings

DEBUG: bool = False


class Sequencer:
    def __init__(self):
        self.internal_config = InitConfig()
        self.settings: Dict[ValidSettings, SFunctionality] = dict()
        self.modes: Dict[ValidModes, MFunctionality] = dict()
        self.n_midis = 0
        self.detached = False
        self.sequences: Dict[
            int, Dict[int, Dict[int, Dict[int, Dict[ValidModes, List[List[int]]]]]]
        ] = dict()

    def debug(self) -> None:
        import json

        fh = open(f"{self.__class__.__name__}.{self.detached}.json", "w")
        json.dump(self.sequences, indent=2, sort_keys=True, fp=fh)
        fh.close()

    def init_data(self) -> None:
        self.settings = init_settings(self.n_midis)
        self.modes = init_modes()
        sequences: Dict[int, Dict[int, Dict[int, Dict[int, Dict[ValidModes, List[List[int]]]]]]] = (
            defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(dict))))
        )
        for midi in self.settings[ValidSettings.E_MIDI_O].values:
            for channel in self.settings[ValidSettings.E_CHANNEL].values:
                for part in self.settings[ValidSettings.E_PART].values:
                    for step in self.settings[ValidSettings.E_STEP].values:
                        for mode_str in list(ValidModes):
                            valid_mode = ValidModes(mode_str)
                            mode = self.modes[valid_mode].new(lock=False)
                            sequences[int(midi)][int(channel)][int(part)][int(step)][
                                valid_mode
                            ] = mode.get_indexes()
        self.sequences = sequences

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

    def get_first_step_mode(self, valid_mode: Optional[ValidModes] = None) -> MFunctionality:
        midi, channel, part, step, mode = self.get_current_e_pos()
        if valid_mode is None:
            valid_mode = mode
        first_step = int(self.settings[ValidSettings.E_STEP].get_first_value())
        indexes = self.sequences[midi][channel][part][first_step][valid_mode]
        first_mode = self.modes[valid_mode].new_with_indexes(indexes=indexes)
        return first_mode

    def get_current_e_step_mode(self, valid_mode: Optional[ValidModes] = None) -> MFunctionality:
        midi, channel, part, step, mode = self.get_current_e_pos()
        if valid_mode is None:
            valid_mode = mode
        indexes = self.sequences[midi][channel][part][step][valid_mode]
        current_mode = self.modes[valid_mode].new_with_indexes(indexes=indexes)
        return current_mode

    def get_current_v_step_mode(self, valid_mode: Optional[ValidModes] = None) -> MFunctionality:
        midi, channel, part, step, mode = self.get_current_v_pos()
        if valid_mode is None:
            valid_mode = mode
        indexes = self.sequences[midi][channel][part][step][valid_mode]
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
            self.sequences[midi][channel][part][step][valid_mode] = mode.get_indexes()
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
        for midi in self.sequences.keys():
            for channel in self.sequences[midi].keys():
                for part in self.sequences[midi][channel].keys():
                    for step in self.sequences[midi][channel][part].keys():
                        for valid_mode in self.sequences[midi][channel][part][step].keys():
                            indexes = self.sequences[midi][channel][part][step][valid_mode]
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
        for midi in self.sequences.keys():
            for channel in self.sequences[midi].keys():
                for part in self.sequences[midi][channel].keys():
                    for step in self.sequences[midi][channel][part].keys():
                        for valid_mode in self.sequences[midi][channel][part][step].keys():
                            indexes = self.sequences[midi][channel][part][step][valid_mode]
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
        return play_positions


class MiDiO:
    def __init__(self, port_id: int, clock_sync: float):
        super().__init__()
        self.port_id = port_id
        self.internal_config = InitConfig()
        self.sequencer: Optional[Sequencer] = None
        self.tempo: int = self.internal_config.init_tempo
        self.scale: str = self.internal_config.init_scale
        self.scheduled_steps: Dict[float, Dict[int, List[MFunctionality]]] = dict()
        self.scheduled_notes: Dict[float, Dict[int, MFunctionality]] = dict()
        self.part_i = 1
        self.step_i = 1
        self.quant_i = 1
        self.quant_interval: float = 0.0
        self.step_interval: float = 0.0
        self.part_interval: float = 0.0
        self.reset_intervals()
        self.quant_tick = clock_sync
        self.step_tick = clock_sync
        self.part_tick = clock_sync

    def reset_intervals(self) -> None:
        if self.step_i == self.internal_config.n_steps and self.sequencer is not None:
            self.tempo = int(self.sequencer.settings[ValidSettings.TEMPO].get_value())
        self.quant_interval = round(self.tempo / (60 * self.internal_config.n_quants), 4)
        self.step_interval = self.quant_interval * self.internal_config.n_quants
        self.part_interval = self.step_interval * self.internal_config.n_steps

    def reset_scale(self):
        if self.step_i == self.internal_config.n_steps and self.sequencer is not None:
            pass

    def attach(self, sequencer: Sequencer) -> None:
        self.sequencer = sequencer
        self.scheduled_steps = defaultdict(lambda: defaultdict(list))
        self.scheduled_notes = defaultdict(dict)

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

    def play_note_schedule(self) -> None:
        pass

    def update_note_schedule(self) -> None:
        pass

    # - - SCHEDULE - - #

    def add_parts_to_step_schedule(self) -> None:
        if self.sequencer is not None:
            play_positions = self.sequencer.get_play_positions()
            if len(play_positions):
                for midi in play_positions.keys():
                    for channel in play_positions[midi].keys():
                        for part in play_positions[midi][channel].keys():
                            part_tick = self.part_tick + self.part_interval * part
                            self.add_steps_to_step_schedule(
                                midi=midi, channel=channel, part=part, part_tick=part_tick
                            )

    def add_steps_to_step_schedule(
        self, midi: int, channel: int, part: int, part_tick: float
    ) -> None:
        if midi == self.port_id and self.sequencer is not None:
            for step in self.sequencer.sequences[midi][channel][part].keys():
                step_tick = part_tick + (step - 1) * self.step_interval
                for valid_mode in self.sequencer.sequences[midi][channel][part][step].keys():
                    indexes = self.sequencer.sequences[midi][channel][part][step][valid_mode]
                    mode = self.sequencer.get_current_new_mode(valid_mode=valid_mode)
                    if not mode.first_only:
                        mode.set_indexes(indexes=indexes)
                        main_label = mode.get_vis_label()
                        if mode.get_single_value_by_lab(exe=0, lab=main_label) != ValidButtons.NA:
                            self.scheduled_steps[step_tick][channel].append(mode)

    def play_step_schedule(self) -> None:
        midi_out: MidiOut = rtmidi.MidiOut()
        midi_out.open_port(self.port_id)
        old_schedule: Dict[float, Dict[int, List[int]]] = defaultdict(lambda: defaultdict(list))
        new_schedule: Dict[float, Dict[int, List[MFunctionality]]] = defaultdict(
            lambda: defaultdict(list)
        )
        for step_tick in sorted(self.scheduled_steps.keys()):
            if time.time() >= step_tick:
                for channel in self.scheduled_steps[step_tick].keys():
                    for i, mode in enumerate(self.scheduled_steps[step_tick][channel]):
                        message: List[int] = mode.get_message()
                        if len(message) >= 3 and min(message) >= 0:
                            with midi_out:
                                self.channel_message(
                                    midi_out=midi_out,
                                    command=message[0],
                                    ch=channel,
                                    data=message[1:3],
                                )
                        if len(message) > 3 and message[3] > 0 and min(message) >= 0:
                            next_tick = step_tick + float(message[3] * self.quant_interval)
                            new_schedule[next_tick][channel].append(mode.new(lock=False))
                        old_schedule[step_tick][channel].append(i)
        self.update_step_schedule(old_schedule=old_schedule, new_schedule=new_schedule)

    def update_step_schedule(
        self,
        old_schedule: Dict[float, Dict[int, List[int]]],
        new_schedule: Dict[float, Dict[int, List[MFunctionality]]],
    ) -> None:
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
        self.play_note_schedule()
        if time.time() >= self.quant_tick:
            if self.quant_i > self.internal_config.n_quants:
                self.quant_i = 1
                self.step_i += 1
                self.step_tick += self.internal_config.n_quants * self.quant_interval
            if self.step_i > self.internal_config.n_steps:
                self.step_i = 1
                self.part_i += 1
                self.part_tick += self.internal_config.n_steps * self.step_interval
            if self.part_i > self.internal_config.n_parts:
                self.part_i = 1
            self.play_step_schedule()
            self.quant_i += 1
            self.quant_tick += self.quant_interval

    @staticmethod
    def channel_message(midi_out: MidiOut, command: int, data: List[int], ch=None):
        """Send a MIDI channel mode message."""
        command = (command & 0xF0) | ((ch if ch else 1) - 1 & 0xF)
        msg = [command] + [value & 0x7F for value in data]
        midi_out.send_message(msg)
