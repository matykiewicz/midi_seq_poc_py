import random
import time
from collections import defaultdict
from multiprocessing import Process, Queue
from typing import Any, Dict, List, Optional, Tuple

import attrs
import mingus.core.scales as scales
import rtmidi
from mingus.containers import Note
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
        steps = self.internal_config.n_steps
        for midi in self.settings[ValidSettings.MIDI].values:
            for part in self.settings[ValidSettings.PART].values:
                for step in self.settings[ValidSettings.STEP].values:
                    for channel in self.settings[ValidSettings.CHANNEL].values:
                        for mode_str in list(ValidModes):
                            valid_mode = ValidModes(mode_str)
                            mode = self.modes[valid_mode].new(lock=False)
                            sequences[midi][part][step][channel][
                                valid_mode
                            ] = mode.get_indexes()
        self.sequences = sequences

    def get_current_pos(self) -> Tuple[int, int, int, int, ValidModes]:
        midi_ind = self.settings[ValidSettings.MIDI].get_ind()
        part_ind = self.settings[ValidSettings.PART].get_ind()
        step_ind = self.settings[ValidSettings.STEP].get_ind()
        channel_ind = self.settings[ValidSettings.CHANNEL].get_ind()
        valid_mode = ValidModes(str(self.settings[ValidSettings.MODE].get_value()))
        return midi_ind, part_ind, step_ind, channel_ind, valid_mode

    def get_first_step_mode(
        self, valid_mode: Optional[ValidModes] = None
    ) -> MFunctionality:
        midi, part, step, channel, mode = self.get_current_pos()
        if valid_mode is None:
            valid_mode = mode
        indexes = self.sequences[midi][part][0][channel][valid_mode]
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
        self.scheduled_modes: List[MFunctionality] = list()
        self.i_part = 1
        self.i_step = 1
        self.i_quant = 1
        self.reset_intervals()

    def add_to_schedule(self, mode: MFunctionality) -> None:
        # channel = self.sequencer.get_current_pos()
        self.scheduled_modes.append(mode.set_schedule(self.next_tick))

    def run_midi_schedule(self, new_mode: Optional[MFunctionality]) -> None:
        if (
            new_mode is not None
            and self.sequencer.get_current_pos()[0] == self.port_id
            and new_mode.get_single_value_by_lab(0, "Note") != ValidButtons.NA
            and new_mode.get_single_value_by_lab(0, "Note") != ValidButtons.NEXT
        ):
            self.add_to_schedule(mode=new_mode)
        # operate sched
        # play sched
        if time.time() >= self.next_tick:
            self.play_with_clock()
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
        if self.i_step == self.internal_config.n_steps:
            self.tempo = int(self.sequencer.settings[ValidSettings.TEMPO].get_value())
        self.interval_quant = round(
            self.tempo / (60 * self.internal_config.n_quants), 4
        )

    def attach(self, sequencer: Sequencer) -> None:
        self.sequencer = sequencer

    def play_with_clock(self) -> None:
        midi_out: MidiOut = rtmidi.MidiOut()
        midi_out.open_port(self.port_id)
        finished: List[int] = list()
        for i, mode in self.scheduled_modes:
            if self.next_tick >= mode.get_schedule():
                message: List[Any] = mode.execute([int, str, int, int], clock)
                if len(message):
                    message[1] = int(Note(message[1])) + 12
                    with midi_out:
                        self.channel_message(
                            midi_out=midi_out,
                            command=message[0],
                            ch=channel,
                            data=message[1:2],
                        )

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
        self.settings[ValidSettings.MIDI].update_with_ind(midi)
        self.settings[ValidSettings.CHANNEL].update_with_ind(channel)
        self.settings[ValidSettings.PART].update_with_ind(part)
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
        for i in self.settings[ValidSettings.STEP].values:
            for valid_mode in list(ValidModes):
                if f_mode is None or f_mode == valid_mode:
                    self.settings[ValidSettings.MODE].update()
                    if button == ValidButtons.C_AS_IS:
                        t_mode = t_mode.update(*f_sequence[i])
                    elif button == ValidButtons.C_REVERSE:
                        t_mode = t_mode.update(
                            *f_sequence[self.internal_config.n_steps - i - 1]
                        )
                    elif button == ValidButtons.C_RANDOM:
                        t_mode = t_mode.update(*f_sequence[shuffle[i]])
                    self.send_mode(t_mode)
