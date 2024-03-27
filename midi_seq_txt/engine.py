import random
import time
from collections import defaultdict
from copy import deepcopy
from multiprocessing import Process, Queue
from typing import Any, Dict, List, Optional, Tuple

import attrs
import mingus.core.scales as scales
import rtmidi
from rtmidi import MidiOut

from .configs import InitConfig
from .functionalities import (
    MFunctionality,
    SFunctionality,
    ValidButtons,
    ValidModes,
    ValidSettings,
    init_modes,
    init_settings,
)

DEBUG: bool = True


class Sequencer:
    def __init__(self):
        self.internal_config = InitConfig()
        self.settings: Dict[ValidSettings, SFunctionality] = dict()
        self.modes: Dict[ValidModes, MFunctionality] = dict()
        self.n_midis = 0
        self.sequences: Dict[
            int, Dict[int, Dict[int, Dict[int, Dict[ValidModes, List[List[int]]]]]]
        ] = dict()

    def debug(self) -> None:
        import json
        import os

        fh = open(f"{self.__class__.__name__}.{os.getpid()}.json", "w")
        json.dump(self.sequences, indent=2, sort_keys=True, fp=fh)
        fh.close()

    def init_data(self) -> None:
        self.settings = init_settings(self.n_midis)
        self.modes = init_modes()
        sequences: Dict[
            int, Dict[int, Dict[int, Dict[int, Dict[ValidModes, List[List[int]]]]]]
        ] = defaultdict(
            lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
        )
        for midi in self.settings[ValidSettings.MIDI].values:
            for part in self.settings[ValidSettings.PART].values:
                for step in self.settings[ValidSettings.STEP].values:
                    for channel in self.settings[ValidSettings.CHANNEL].values:
                        for mode_str in list(ValidModes):
                            valid_mode = ValidModes(mode_str)
                            mode = self.modes[valid_mode].new(lock=False)
                            sequences[int(midi)][int(part)][int(step)][int(channel)][
                                valid_mode
                            ] = mode.get_indexes()
        self.sequences = sequences

    def get_current_pos(self) -> Tuple[int, int, int, int, ValidModes]:
        midi = int(self.settings[ValidSettings.MIDI].get_value())
        part = int(self.settings[ValidSettings.PART].get_value())
        step = int(self.settings[ValidSettings.STEP].get_value())
        channel = int(self.settings[ValidSettings.CHANNEL].get_value())
        valid_mode = ValidModes(str(self.settings[ValidSettings.MODE].get_value()))
        return midi, part, step, channel, valid_mode

    def get_first_step_mode(
        self, valid_mode: Optional[ValidModes] = None
    ) -> MFunctionality:
        midi, part, step, channel, mode = self.get_current_pos()
        if valid_mode is None:
            valid_mode = mode
        indexes = self.sequences[midi][part][1][channel][valid_mode]
        first_mode = self.modes[valid_mode].new_with_indexes(indexes=indexes)
        return first_mode

    def get_current_step_mode(
        self, valid_mode: Optional[ValidModes] = None
    ) -> MFunctionality:
        midi, part, step, channel, mode = self.get_current_pos()
        if valid_mode is None:
            valid_mode = mode
        indexes = self.sequences[midi][part][step][channel][valid_mode]
        current_mode = self.modes[valid_mode].new_with_indexes(indexes=indexes)
        return current_mode

    def get_current_new_mode(
        self, valid_mode: Optional[ValidModes] = None
    ) -> MFunctionality:
        midi, part, step, channel, mode = self.get_current_pos()
        if valid_mode is None:
            valid_mode = mode
        current_mode = self.modes[valid_mode].new(lock=False)
        return current_mode

    def get_current_proto_mode(
        self, valid_mode: Optional[ValidModes] = None
    ) -> MFunctionality:
        midi, part, step, channel, mode = self.get_current_pos()
        if valid_mode is None:
            valid_mode = mode
        return self.modes[valid_mode]

    def get_sound_properties(self) -> Tuple[List[str], List[str]]:
        current_mode = self.get_current_step_mode()
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
        if (
            self.settings[ValidSettings.RECORD].get_ind() == 1
            or self.settings[ValidSettings.COPY].get_ind() == 1
        ) and mode.get_single_value_by_lab(exe=0, lab="Note") != ValidButtons.NEXT:
            midi, part, step, channel, valid_mode = self.get_current_pos()
            if mode.first_only:
                step = 0
            self.sequences[midi][part][step][channel][valid_mode] = mode.get_indexes()
            if not mode.first_only:
                self.settings[ValidSettings.STEP].next_ind()
            else:
                self.settings[ValidSettings.STEP].update_with_ind(0)
        self.debug() if DEBUG else None

    def set_option(self, option: SFunctionality) -> None:
        valid_setting = ValidSettings(option.name)
        self.settings[valid_setting].update_with_ind(option.get_ind())


class MiDi:
    def __init__(self, port_id: int, clock_sync: float):
        super().__init__()
        self.port_id = port_id
        self.internal_config = InitConfig()
        self.sequencer: Optional[Sequencer] = None
        self.tempo: int = self.internal_config.init_tempo
        self.interval_quant: float = 0.0
        self.next_tick = clock_sync + self.interval_quant
        self.scheduled_steps: Dict[
            float, List[Dict[int, Dict[ValidModes, MFunctionality]]]
        ] = defaultdict(list)
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
            midi, part, step, ch, mo = self.sequencer.get_current_pos()
            if channel is None:
                channel = ch
            if valid_mode is None:
                valid_mode = mo
            full_step = {channel: {valid_mode: mode}}
            self.scheduled_steps[next_tick].append(full_step)

    def run_midi_schedule(self, new_mode: Optional[MFunctionality]) -> None:
        if (
            new_mode is not None
            and self.sequencer is not None
            and self.sequencer.get_current_pos()[0] == self.port_id
            and new_mode.get_single_value_by_lab(0, "Note") != ValidButtons.NA
            and new_mode.get_single_value_by_lab(0, "Note") != ValidButtons.NEXT
        ):
            self.add_to_schedule(next_tick=self.next_tick, mode=new_mode)
        if time.time() >= self.next_tick:
            self.play_scheduled()
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
        self.interval_quant = round(
            self.tempo / (60 * self.internal_config.n_quants), 4
        )

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
                            with midi_out:
                                self.channel_message(
                                    midi_out=midi_out,
                                    command=message[0],
                                    ch=channel,
                                    data=message[1:3],
                                )
                            if message[3] > 0:
                                self.add_to_schedule(
                                    next_tick=time_tick
                                    + (message[3] * self.interval_quant),
                                    mode=mode,
                                )
                            old_schedule.append(
                                (time_tick, i_step, channel, valid_mode)
                            )
        self.remove_from_schedule(old_schedule=old_schedule)

    def remove_from_schedule(
        self, old_schedule: List[Tuple[float, int, int, ValidModes]]
    ) -> None:
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


class Engine(Sequencer):
    """
    This class spawns sequencer as a separate process.
    It maintains communication between UI and all MIDIs.
    """

    def __init__(self):
        super().__init__()
        self.modes: Dict[ValidModes, MFunctionality] = dict()
        self.settings: Dict[ValidSettings, SFunctionality] = dict()
        self.midis: Dict[int, MiDi] = self.init_midis()
        self.n_midis = len(self.midis)
        self.process = Process(target=self.start)
        self.func_queue: Queue[Dict[str, Any]] = Queue()
        self.detached = False

    @staticmethod
    def init_midis() -> Dict[int, MiDi]:
        clock_sync = round(time.time() + InitConfig().init_time)
        midis: Dict[int, MiDi] = dict()
        midi_out = rtmidi.MidiOut()
        port_names = midi_out.get_ports()
        for i in range(len(port_names)):
            midis[i] = MiDi(port_id=i, clock_sync=clock_sync)
        if not len(midis):
            raise ValueError("At least 1 usb midi device is needed")
        return midis

    def detach(self) -> None:
        self.process.start()

    def start(self) -> None:
        self.detached = True
        self.init_data()
        for midi_id in self.midis.keys():
            self.midis[midi_id].attach(sequencer=self)
        self.run_sequencer_schedule()

    def run_sequencer_schedule(self) -> None:
        while True:
            mode = None
            if not self.func_queue.empty():
                func_dict: Dict[str, Any] = self.func_queue.get()
                if "indexes" in func_dict:
                    mode = self.convert_to_mode(func_dict)
                    self.set_step(mode=mode)
                else:
                    setting = self.convert_to_setting(func_dict)
                    self.set_option(option=setting)
            for midi_id in self.midis.keys():
                self.midis[midi_id].reset_intervals()
                self.midis[midi_id].run_midi_schedule(new_mode=mode)
            time.sleep(self.internal_config.sleep)

    def convert_to_setting(self, setting_dict: Dict[str, Any]) -> SFunctionality:
        valid_setting = ValidSettings(setting_dict["name"])
        setting_value = self.settings[valid_setting]
        setting_value.update_with_ind(int(setting_dict["ind"]))
        return setting_value

    def convert_to_mode(self, mode_dict: Dict[str, Any]) -> MFunctionality:
        valid_mode = ValidModes(mode_dict["name"])
        mode_value = self.modes[valid_mode].new(lock=False)
        mode_value.set_indexes(mode_dict["indexes"])
        return mode_value

    def send_mode(self, mode: MFunctionality) -> None:
        self.set_step(mode=mode)
        self.func_queue.put(attrs.asdict(mode))

    def send_setting(self, setting: SFunctionality) -> None:
        self.set_option(option=setting)
        self.func_queue.put(attrs.asdict(setting))

    def send_delete(self) -> None:
        midi, part, step, channel, valid_mode = self.get_current_pos()
        mode = self.modes[valid_mode].new(lock=True)
        self.send_mode(mode=mode)

    def send_pos(self, midi: int, channel: int, part: int, mode: ValidModes) -> None:
        self.settings[ValidSettings.MIDI].update_with_value(midi)
        self.settings[ValidSettings.CHANNEL].update_with_value(channel)
        self.settings[ValidSettings.PART].update_with_value(part)
        self.settings[ValidSettings.MODE].update_with_value(mode)
        self.send_setting(self.settings[ValidSettings.MIDI])
        self.send_setting(self.settings[ValidSettings.CHANNEL])
        self.send_setting(self.settings[ValidSettings.PART])
        self.send_setting(self.settings[ValidSettings.MODE])
        self.send_reset_step()

    def send_reset_step(self) -> None:
        self.settings[ValidSettings.STEP].update_with_ind(0)
        self.send_setting(setting=self.settings[ValidSettings.STEP])

    def send_next_step(self) -> None:
        self.settings[ValidSettings.STEP].next_ind()
        self.send_setting(setting=self.settings[ValidSettings.STEP])

    def send_copy(
        self,
        f_midi: int,
        f_channel: int,
        f_part: int,
        f_mode: Optional[ValidModes],
        button: ValidButtons,
    ) -> None:
        t_mode = self.get_current_new_mode()
        shuffle = list(range(1, self.internal_config.n_steps + 1))
        random.shuffle(shuffle)
        for f_step in self.settings[ValidSettings.STEP].values:
            for valid_mode_str in [str(x) for x in list(ValidModes)]:
                valid_mode = ValidModes(valid_mode_str)
                if f_mode is None or f_mode == valid_mode:
                    mode_setting = self.settings[ValidSettings.MODE].update_with_value(
                        valid_mode
                    )
                    f_sequence = self.sequences[f_midi][f_part][int(f_step)][f_channel][
                        valid_mode
                    ]
                    t_step: int = -1
                    if button == ValidButtons.C_AS_IS:
                        t_step = int(f_step)
                    elif button == ValidButtons.C_REVERSE:
                        t_step = self.internal_config.n_steps - int(f_step) + 1
                    elif button == ValidButtons.C_RANDOM:
                        t_step = shuffle[int(f_step) - 1]
                    if t_step > 0:
                        step_setting = self.settings[
                            ValidSettings.STEP
                        ].update_with_value(t_step)
                        t_mode = t_mode.set_indexes(f_sequence)
                        self.send_setting(mode_setting)
                        self.send_setting(step_setting)
                        self.send_mode(t_mode)
