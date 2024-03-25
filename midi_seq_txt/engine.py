import random
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Process, Queue
from typing import Any, Dict, List, Optional, Tuple

import attrs
import mingus.core.scales as scales
import rtmidi
from mingus.containers import Note

from .configs import InitConfig
from .functionalities import (
    MFunctionality,
    SFunctionality,
    ValidButtons,
    ValidModes,
    ValidSettings,
    INTERVAL_MATCHES,
    init_modes,
    init_settings,
)

DEBUG: bool = True
DEFAULT_STEP: Tuple[float, int] = (1.0, 0)


class Sequencer:
    def __init__(self):
        self.internal_config = InitConfig()
        self.settings: Dict[ValidSettings, SFunctionality] = dict()
        self.modes: Dict[ValidModes, MFunctionality] = dict()
        self.n_midis = 0
        self.sequences: Dict[
            int, Dict[int, Dict[int, Dict[ValidModes, List[Tuple[float, int]]]]]
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
            int, Dict[int, Dict[int, Dict[ValidModes, List[Tuple[float, int]]]]]
        ] = defaultdict(
            lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        )
        steps = self.internal_config.steps
        for midi in range(len(self.settings[ValidSettings.MIDI].values)):
            for channel in range(len(self.settings[ValidSettings.CHANNEL].values)):
                for part in range(len(self.settings[ValidSettings.PART].values)):
                    for mode_str in list(ValidModes):
                        valid_mode = ValidModes(mode_str)
                        sequences[midi][channel][part][valid_mode] = [
                            DEFAULT_STEP
                        ] * steps
        self.sequences = sequences

    def get_current_pos(self) -> Tuple[int, int, int, ValidModes, int]:
        midi_ind = self.settings[ValidSettings.MIDI].get()
        channel_ind = self.settings[ValidSettings.CHANNEL].get()
        part_ind = self.settings[ValidSettings.PART].get()
        mode = ValidModes(str(self.settings[ValidSettings.MODE].get_value()))
        step_ind = self.settings[ValidSettings.STEP].get()
        return midi_ind, channel_ind, part_ind, mode, step_ind

    def get_first_mode(self, valid_mode: Optional[ValidModes] = None) -> MFunctionality:
        midi, channel, part, mode, _ = self.get_current_pos()
        if valid_mode is None:
            valid_mode = mode
        length, mode_ind = self.sequences[midi][channel][part][valid_mode][0]
        first_mode = self.modes[valid_mode].update(length, mode_ind)
        return first_mode

    def get_current_step_mode(
        self, valid_mode: Optional[ValidModes] = None
    ) -> MFunctionality:
        midi, channel, part, mode, step = self.get_current_pos()
        if valid_mode is None:
            valid_mode = mode
        length, mode_ind = self.sequences[midi][channel][part][valid_mode][step]
        current_mode = self.modes[valid_mode].update(length, mode_ind)
        return current_mode

    def get_current_new_mode(
        self, valid_mode: Optional[ValidModes] = None
    ) -> MFunctionality:
        midi, channel, part, mode, step = self.get_current_pos()
        if valid_mode is None:
            valid_mode = mode
        current_mode = self.modes[valid_mode]
        return current_mode

    def get_sound_properties(self) -> Tuple[str, str, str, float]:
        current_mode = self.get_current_step_mode()
        mode_value = current_mode.get_value()
        mode_length = current_mode.get_first_length()
        scale_value = self.get_current_scale()
        return (
            scale_value,
            current_mode.name,
            mode_value,
            mode_length,
        )

    def get_current_notes(self) -> List[str]:
        scale_value = self.get_current_scale()
        notes = scales.get_notes(key=scale_value)
        notes += [notes[0]]
        return notes

    def get_current_scale(self) -> str:
        scale = self.get_first_mode(ValidModes.SCALE)
        scale_value = scale.get_value()
        return scale_value

    def set_step(self, mode: MFunctionality) -> None:
        if (
            self.settings[ValidSettings.RECORD].get() == 1
            or self.settings[ValidSettings.COPY].get() == 1
        ) and mode.get_value() != ValidButtons.NEXT:
            midi, channel, part, valid_mode, step = self.get_current_pos()
            if mode.first_only:
                step = 0
            self.sequences[midi][channel][part][valid_mode][step] = mode.get()
            if not mode.first_only:
                ind = self.settings[ValidSettings.STEP].get()
                ind += 1
                if ind >= self.internal_config.steps:
                    ind = 0
                self.settings[ValidSettings.STEP].update(ind)
            else:
                self.settings[ValidSettings.STEP].update(0)
        self.debug() if DEBUG else None

    def set_option(self, option: SFunctionality) -> None:
        valid_setting = ValidSettings(option.name)
        self.settings[valid_setting].update(option.get())


class MiDi:
    def __init__(self, port_id: int, clock_sync: float):
        super().__init__()
        self.port_id = port_id
        self.internal_config = InitConfig()
        self.sequencer: Optional[Sequencer] = None
        self.thread_pool: Optional[ThreadPoolExecutor] = None
        self.tempo: int = self.internal_config.init_tempo
        self.interval_FULL: float = 0.0
        self.interval_HALF: float = 0.0
        self.interval_QUARTER: float = 0.0
        self.n_quarter_intervals = (
            self.internal_config.steps * self.internal_config.n_quarters
        )
        self.reset_intervals()
        self.next_tick = clock_sync + self.interval_QUARTER
        self.last_note: Optional[MFunctionality] = None

    def run_midi_schedule(self, last_note: Optional[MFunctionality]) -> None:
        if (
            last_note is not None
            and self.sequencer.get_current_pos()[0] == self.port_id
            and last_note.get_value() != ValidButtons.NA
            and last_note.get_value() != ValidButtons.NEXT
        ):
            self.last_note = last_note
            self.play(self.last_note)
            self.last_note = None
        i_quarter = 1
        i_step = 1
        if time.time() >= self.next_tick:
            self.next_tick += self.interval_QUARTER

    def reset_intervals(self) -> None:
        self.interval_QUARTER = round(self.tempo / (60 * 4), 4)
        self.interval_HALF = self.interval_QUARTER * 2
        self.interval_FULL = self.interval_QUARTER * 4

    def attach(self, sequencer: Sequencer) -> None:
        self.sequencer = sequencer
        self.thread_pool = ThreadPoolExecutor(
            max_workers=self.internal_config.midi_workers
        )

    def play_note(self, note: "MFunctionality") -> None:
        if self.sequencer is not None:
            tempo = int(self.sequencer.settings[ValidSettings.TEMPO].get_value())

        midi_out: rtmidi.MidiOut = rtmidi.MidiOut()
        midi_out.open_port(self.port_id)
        note_int = int(Note(note.get_value())) + 12

        note_on = [0x90, note_int, 127]  # channel 1, middle C, velocity 112
        note_off = [0x80, note_int, 0]
        with midi_out:
            midi_out.send_message(note_on)
            time.sleep(0.1)
            midi_out.send_message(note_off)
            pass

    def play(self, note: Optional[MFunctionality]) -> None:
        if (
            note is not None
            and note.get_value() != ValidButtons.NEXT
            and note.get_value() != ValidButtons.NA
        ):
            midi_out: rtmidi.MidiOut = rtmidi.MidiOut()
            midi_out.open_port(self.port_id)
            note_int = int(Note(note.get_value())) + 12
            note_on = [0x90, note_int, 126]
            note_off = [0x80, note_int, 0]
            with midi_out:
                fh = open("xxx", "a")
                fh.write(f"{note_int}\n")
                midi_out.send_message(note_on)
                time.sleep(0.1)
                midi_out.send_message(note_off)
                fh.close()


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
                if "codes" in func_dict:
                    mode = self.convert_to_mode(func_dict)
                    self.set_step(mode=mode)
                else:
                    setting = self.convert_to_setting(func_dict)
                    self.set_option(option=setting)
            for midi_id in self.midis.keys():
                self.midis[midi_id].run_midi_schedule(last_note=mode)
            time.sleep(self.internal_config.sleep)

    def convert_to_setting(self, setting_dict: Dict[str, Any]) -> SFunctionality:
        valid_setting = ValidSettings(setting_dict["name"])
        setting_value = self.settings[valid_setting]
        setting_value.ind = setting_dict["ind"]
        setting_value.values = setting_dict["values"]
        return setting_value

    def convert_to_mode(self, mode_dict: Dict[str, Any]) -> MFunctionality:
        valid_mode = ValidModes(mode_dict["name"])
        mode_value = self.modes[valid_mode]
        mode_value.ind = mode_dict["ind"]
        mode_value.offset = mode_dict["offset"]
        mode_value.first_only = mode_dict["first_only"]
        mode_value.lengths = mode_dict["lengths"]
        mode_value.codes = mode_dict["codes"]
        mode_value.values = mode_dict["values"]
        return mode_value

    def send_mode(self, mode: MFunctionality) -> None:
        self.set_step(mode=mode)
        self.func_queue.put(attrs.asdict(mode))

    def send_setting(self, setting: SFunctionality) -> None:
        self.set_option(option=setting)
        self.func_queue.put(attrs.asdict(setting))

    def send_delete(self) -> None:
        midi, channel, part, valid_mode, step = self.get_current_pos()
        mode = self.modes[valid_mode]
        mode = mode.update(1.0, 0)
        self.send_mode(mode=mode)

    def send_pos(self, midi: int, channel: int, part: int, mode: ValidModes) -> None:
        self.settings[ValidSettings.MIDI].update(midi)
        self.settings[ValidSettings.CHANNEL].update(channel)
        self.settings[ValidSettings.PART].update(part)
        self.settings[ValidSettings.MODE].update(
            self.settings[ValidSettings.MODE].values.index(mode)
        )
        self.send_setting(self.settings[ValidSettings.MIDI])
        self.send_setting(self.settings[ValidSettings.CHANNEL])
        self.send_setting(self.settings[ValidSettings.PART])
        self.send_setting(self.settings[ValidSettings.MODE])
        self.send_reset_step()

    def send_reset_step(self) -> None:
        self.settings[ValidSettings.STEP].update(0)
        self.send_setting(setting=self.settings[ValidSettings.STEP])

    def send_next_step(self) -> None:
        step_ind = self.settings[ValidSettings.STEP].get()
        step_ind += 1
        if step_ind >= len(self.settings[ValidSettings.STEP].values):
            step_ind = 0
        self.settings[ValidSettings.STEP].update(step_ind)
        self.send_setting(setting=self.settings[ValidSettings.STEP])

    def send_copy(
        self,
        f_midi: int,
        f_channel: int,
        f_part: int,
        f_mode: ValidModes,
        button: ValidButtons,
    ) -> None:
        f_sequence = self.sequences[f_midi][f_channel][f_part][f_mode]
        t_mode = self.get_current_new_mode()
        shuffle = list(range(len(f_sequence)))
        random.shuffle(shuffle)
        for i in range(len(f_sequence)):
            if button == ValidButtons.C_AS_IS:
                t_mode = t_mode.update(*f_sequence[i])
            elif button == ValidButtons.C_REVERSE:
                t_mode = t_mode.update(*f_sequence[self.internal_config.steps - i - 1])
            elif button == ValidButtons.C_RANDOM:
                t_mode = t_mode.update(*f_sequence[shuffle[i]])
            self.send_mode(t_mode)
