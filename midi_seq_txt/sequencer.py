import time
from collections import defaultdict
from copy import deepcopy
from typing import Dict, List, Optional, Tuple

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
            for part in self.settings[ValidSettings.E_PART].values:
                for step in self.settings[ValidSettings.E_STEP].values:
                    for channel in self.settings[ValidSettings.E_CHANNEL].values:
                        for mode_str in list(ValidModes):
                            valid_mode = ValidModes(mode_str)
                            mode = self.modes[valid_mode].new(lock=False)
                            sequences[int(midi)][int(part)][int(step)][int(channel)][
                                valid_mode
                            ] = mode.get_indexes()
        self.sequences = sequences

    def get_current_e_pos(self) -> Tuple[int, int, int, int, ValidModes]:
        midi = int(self.settings[ValidSettings.E_MIDI_O].get_value())
        part = int(self.settings[ValidSettings.E_PART].get_value())
        step = int(self.settings[ValidSettings.E_STEP].get_value())
        channel = int(self.settings[ValidSettings.E_CHANNEL].get_value())
        valid_mode = ValidModes(str(self.settings[ValidSettings.E_MODE].get_value()))
        return midi, part, step, channel, valid_mode

    def get_current_v_pos(self) -> Tuple[int, int, int, int, ValidModes]:
        midi = int(self.settings[ValidSettings.V_MIDI_O].get_value())
        part = int(self.settings[ValidSettings.V_PART].get_value())
        step = int(self.settings[ValidSettings.V_STEP].get_value())
        channel = int(self.settings[ValidSettings.V_CHANNEL].get_value())
        valid_mode = ValidModes(str(self.settings[ValidSettings.V_MODE].get_value()))
        return midi, part, step, channel, valid_mode

    def get_first_step_mode(self, valid_mode: Optional[ValidModes] = None) -> MFunctionality:
        midi, part, step, channel, mode = self.get_current_e_pos()
        if valid_mode is None:
            valid_mode = mode
        indexes = self.sequences[midi][part][1][channel][valid_mode]
        first_mode = self.modes[valid_mode].new_with_indexes(indexes=indexes)
        return first_mode

    def get_current_e_step_mode(self, valid_mode: Optional[ValidModes] = None) -> MFunctionality:
        midi, part, step, channel, mode = self.get_current_e_pos()
        if valid_mode is None:
            valid_mode = mode
        indexes = self.sequences[midi][part][step][channel][valid_mode]
        current_mode = self.modes[valid_mode].new_with_indexes(indexes=indexes)
        return current_mode

    def get_current_v_step_mode(self, valid_mode: Optional[ValidModes] = None) -> MFunctionality:
        midi, part, step, channel, mode = self.get_current_v_pos()
        if valid_mode is None:
            valid_mode = mode
        indexes = self.sequences[midi][part][step][channel][valid_mode]
        current_mode = self.modes[valid_mode].new_with_indexes(indexes=indexes)
        return current_mode

    def get_current_new_mode(self, valid_mode: Optional[ValidModes] = None) -> MFunctionality:
        midi, part, step, channel, mode = self.get_current_e_pos()
        if valid_mode is None:
            valid_mode = mode
        current_mode = self.modes[valid_mode].new(lock=False)
        return current_mode

    def get_current_proto_mode(self, valid_mode: Optional[ValidModes] = None) -> MFunctionality:
        midi, part, step, channel, mode = self.get_current_e_pos()
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
        main_label = mode.get_vis_label()
        if (
            self.settings[ValidSettings.RECORD].get_ind() == 1
            or self.settings[ValidSettings.COPY].get_ind() == 1
        ) and mode.get_single_value_by_lab(exe=0, lab=main_label) != ValidButtons.NEXT:
            midi, part, step, channel, valid_mode = self.get_current_e_pos()
            if mode.first_only:
                step = self.settings[ValidSettings.E_STEP].get_first_value()
            self.sequences[midi][part][step][channel][valid_mode] = mode.get_indexes()
            self.settings[ValidSettings.E_STEP].next_ind()
        self.debug() if DEBUG else None

    def set_option(self, option: SFunctionality) -> None:
        valid_setting = ValidSettings(option.name)
        self.settings[valid_setting].update_with_ind(option.get_ind())

    def find_positions_with_music(self) -> List[Tuple[int, int, int, int, ValidModes]]:
        positions_with_music = list()
        for midi in self.sequences.keys():
            for part in self.sequences[midi].keys():
                for step in self.sequences[midi][part].keys():
                    for channel in self.sequences[midi][part][step].keys():
                        for valid_mode in self.sequences[midi][part][step][channel].keys():
                            indexes = self.sequences[midi][part][step][channel][valid_mode]
                            mode = self.get_current_proto_mode(valid_mode=valid_mode)
                            vis_index_1, vis_index_2 = mode.get_vis_ind()
                            has_note = indexes[vis_index_1][vis_index_2]
                            if has_note > 0:
                                positions_with_music.append((midi, part, step, channel, valid_mode))
        return positions_with_music

    def schedule_parts_to_play(
        self,
        positions_to_play: List[Tuple[int, int, int, int, ValidModes]],
        playback_type: ValidButtons,
    ) -> None:
        self.stop_play()
        pass

    def stop_play(self) -> None:
        pass


class MiDiO:
    def __init__(self, port_id: int, clock_sync: float):
        super().__init__()
        self.port_id = port_id
        self.internal_config = InitConfig()
        self.sequencer: Optional[Sequencer] = None
        self.tempo: int = self.internal_config.init_tempo
        self.interval_quant: float = 0.0
        self.next_tick = clock_sync + self.interval_quant
        self.scheduled_steps: Dict[float, List[Dict[int, Dict[ValidModes, MFunctionality]]]] = (
            defaultdict(list)
        )
        self.i_part = 1
        self.i_step = 1
        self.i_quant = 1
        self.reset_intervals()

    def add_to_schedule(
        self,
        next_tick: float,
        mode: MFunctionality,
        channel: Optional[int] = None,
        valid_mode: Optional[ValidModes] = None,
    ) -> None:
        if self.sequencer is not None:
            midi, part, step, ch, mo = self.sequencer.get_current_e_pos()
            if channel is None:
                channel = ch
            if valid_mode is None:
                valid_mode = mo
            full_step = {channel: {valid_mode: mode}}
            self.scheduled_steps[next_tick].append(full_step)

    def run_midi_schedule(self, new_mode: Optional[MFunctionality]) -> None:
        if new_mode is not None:
            main_label = new_mode.get_vis_label()
            if (
                self.sequencer is not None
                and self.sequencer.get_current_e_pos()[0] == self.port_id
                and new_mode.get_single_value_by_lab(0, main_label) != ValidButtons.NA
                and new_mode.get_single_value_by_lab(0, main_label) != ValidButtons.NEXT
            ):
                self.add_to_schedule(next_tick=time.time(), mode=new_mode)
        self.play_scheduled()
        if time.time() >= self.next_tick:
            self.i_quant += 1
            if self.i_quant > self.internal_config.n_quants:
                self.i_quant = 1
                self.i_step += 1
            if self.i_step > self.internal_config.n_steps:
                self.i_step = 1
                self.i_part += 1
            if self.i_part > self.internal_config.n_parts:
                self.i_part = 1
            self.next_tick += self.interval_quant

    def reset_intervals(self) -> None:
        if self.i_step == self.internal_config.n_steps and self.sequencer is not None:
            self.tempo = int(self.sequencer.settings[ValidSettings.TEMPO].get_value())
        self.interval_quant = round(self.tempo / (60 * self.internal_config.n_quants), 4)

    def attach(self, sequencer: Sequencer) -> None:
        self.sequencer = sequencer

    def play_scheduled(self) -> None:
        midi_out: MidiOut = rtmidi.MidiOut()
        midi_out.open_port(self.port_id)
        old_schedule = list()
        for time_tick in sorted(self.scheduled_steps.keys()):
            if time.time() >= time_tick:
                for i_step, step in enumerate(self.scheduled_steps[time_tick]):
                    for channel in step.keys():
                        for valid_mode in step[channel].keys():
                            mode = step[channel][valid_mode]
                            message: List[int] = mode.get_message()
                            if len(message) >= 3:
                                with midi_out:
                                    self.channel_message(
                                        midi_out=midi_out,
                                        command=message[0],
                                        ch=channel,
                                        data=message[1:3],
                                    )
                            if len(message) > 3 and message[3] > 0:
                                self.add_to_schedule(
                                    next_tick=time_tick + (message[3] * self.interval_quant),
                                    mode=mode,
                                )
                            old_schedule.append((time_tick, i_step, channel, valid_mode))
        self.remove_from_schedule(old_schedule=old_schedule)

    def remove_from_schedule(self, old_schedule: List[Tuple[float, int, int, ValidModes]]) -> None:
        if len(old_schedule):
            new_schedule: Dict[float, List] = defaultdict(list)
            for time_tick in self.scheduled_steps.keys():
                for i_step, step in enumerate(self.scheduled_steps[time_tick]):
                    new_step = deepcopy(step)
                    for channel in step.keys():
                        for valid_mode in step[channel].keys():
                            schedule = (time_tick, i_step, channel, valid_mode)
                            if schedule in old_schedule:
                                del new_step[channel][valid_mode]
                        if len(new_step[channel]) == 0:
                            del new_step[channel]
                    if len(new_step):
                        new_schedule[time_tick].append(new_step)
            self.scheduled_steps = new_schedule

    @staticmethod
    def channel_message(midi_out: MidiOut, command: int, data: List[int], ch=None):
        """Send a MIDI channel mode message."""
        command = (command & 0xF0) | ((ch if ch else 1) - 1 & 0xF)
        msg = [command] + [value & 0x7F for value in data]
        midi_out.send_message(msg)
