import time
from collections import defaultdict
from multiprocessing import Process, Queue
from typing import Any, Dict, List, Tuple

import attrs
import rtmidi
from mingus.core import keys

from .configs import InitConfig
from .functionalities import (
    MFunctionality,
    SFunctionality,
    ValidModes,
    ValidSettings,
    init_modes,
    init_settings,
)


class Sequencer:
    def __init__(self):
        self.internal_config = InitConfig()
        self.settings: Dict[ValidSettings, SFunctionality] = dict()
        self.modes: Dict[ValidModes, MFunctionality] = dict()
        self.n_midis = 0
        self.sequences: Dict[int, Dict[int, Dict[int, Dict[ValidModes, List[int]]]]] = (
            dict()
        )

    def debug(self) -> None:
        import json
        import os

        fh = open(f"{self.__class__.__name__}.{os.getpid()}.json", "w")
        json.dump(self.sequences, indent=2, sort_keys=True, fp=fh)
        fh.close()

    def init_data(self) -> None:
        self.settings = init_settings(self.n_midis)
        self.modes = init_modes()
        sequences: Dict[int, Dict[int, Dict[int, Dict[ValidModes, List[int]]]]] = (
            defaultdict(
                lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
            )
        )
        steps = self.internal_config.steps
        for midi in range(len(self.settings[ValidSettings.MIDI].values)):
            for channel in range(len(self.settings[ValidSettings.CHANNEL].values)):
                for part in range(len(self.settings[ValidSettings.PART].values)):
                    mode: ValidModes
                    for mode in list(ValidModes):
                        first_only = self.modes[mode].first_only
                        def_ind = self.modes[mode].def_ind
                        if first_only:
                            sequence = [0] * steps
                            sequence[0] = def_ind
                        else:
                            sequence = [def_ind] * steps
                        sequences[midi][channel][part][mode] = sequence
        self.sequences = sequences

    def get_current_pos(self) -> Tuple[int, int, int, ValidModes, int]:
        midi_ind = self.settings[ValidSettings.MIDI].ind
        channel_ind = self.settings[ValidSettings.CHANNEL].ind
        part_ind = self.settings[ValidSettings.PART].ind
        mode_ind = self.settings[ValidSettings.MODE].ind
        mode = ValidModes(self.settings[ValidSettings.MODE].values[mode_ind])
        step_ind = self.settings[ValidSettings.STEP].ind
        return midi_ind, channel_ind, part_ind, mode, step_ind

    def set_step(self, key: MFunctionality) -> None:
        if self.settings[ValidSettings.RECORD].ind == 1:
            midi, channel, part, key_type, step = self.get_current_pos()
            self.sequences[midi][channel][part][key_type][step] = key.values[key.ind]
            ind = self.settings[ValidSettings.STEP].ind
            ind += 1
            if ind >= self.internal_config.steps:
                ind = 0
            self.settings[ValidSettings.STEP].ind = ind
        self.debug()

    def set_option(self, option: SFunctionality) -> None:
        valid_setting = ValidSettings(option.name)
        self.settings[valid_setting].ind = option.ind


class MiDi:
    def __init__(self, port_id: int):
        super().__init__()
        self.port_id = port_id
        self.internal_config = InitConfig()

    def play_note(self, key_enum: ValidModes, key_fun: "MFunctionality") -> None:
        midi_out: rtmidi.MidiOut = rtmidi.MidiOut()
        midi_out.open_port(self.port_id)
        note_on = [0x90, 60, 255]  # channel 1, middle C, velocity 112
        note_off = [0x80, 60, 0]
        with midi_out:
            midi_out.send_message(note_on)
            time.sleep(0.5)
            midi_out.send_message(note_off)
            pass


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

    @staticmethod
    def init_midis() -> Dict[int, MiDi]:
        midis: Dict[int, MiDi] = dict()
        midi_out = rtmidi.MidiOut()
        port_names = midi_out.get_ports()
        for i in range(len(port_names)):
            midis[i] = MiDi(port_id=i)
        if not len(midis):
            raise ValueError("At least 1 usb midi device is needed")
        return midis

    def detach(self) -> None:
        self.process.start()

    def start(self) -> None:
        self.init_data()
        self.run_schedule()

    def run_schedule(self) -> None:
        while True:
            if not self.func_queue.empty():
                func_dict: Dict[str, Any] = self.func_queue.get()
                if "hex_codes" in func_dict:
                    mode = self.convert_to_mode(func_dict)
                    self.set_step(key=mode)
                else:
                    setting = self.convert_to_setting(func_dict)
                    self.set_option(option=setting)

    def convert_to_setting(self, setting_dict: Dict[str, Any]) -> SFunctionality:
        valid_setting = ValidSettings(setting_dict["name"])
        setting_value = self.settings[valid_setting]
        setting_value.ind = setting_dict["ind"]
        return setting_value

    def convert_to_mode(self, mode_dict: Dict[str, Any]) -> MFunctionality:
        valid_mode = ValidModes(mode_dict["name"])
        mode_value = self.modes[valid_mode]
        mode_value.ind = mode_dict["ind"]
        return mode_value

    def send_mode(self, mode: MFunctionality) -> None:
        self.set_step(key=mode)
        self.func_queue.put(attrs.asdict(mode))

    def send_setting(self, setting: SFunctionality) -> None:
        self.set_option(option=setting)
        self.func_queue.put(attrs.asdict(setting))

    def send_delete(self) -> None:
        midi, channel, part, mode, step = self.get_current_pos()
        key = self.modes[mode]
        key.ind = key.def_ind
        self.send_mode(mode=key)

    def send_pos(self, midi: int, channel: int, part: int, mode: ValidModes) -> None:
        self.settings[ValidSettings.MIDI].ind = midi
        self.settings[ValidSettings.CHANNEL].ind = channel
        self.settings[ValidSettings.PART].ind = part
        self.settings[ValidSettings.MODE].ind = self.settings[
            ValidSettings.MODE
        ].values.index(mode)
        self.send_setting(self.settings[ValidSettings.MIDI])
        self.send_setting(self.settings[ValidSettings.CHANNEL])
        self.send_setting(self.settings[ValidSettings.PART])
        self.send_setting(self.settings[ValidSettings.MODE])
        self.send_reset_step()

    def send_reset_step(self):
        self.settings[ValidSettings.STEP].ind = 0
        self.send_setting(setting=self.settings[ValidSettings.STEP])

    def send_next_step(self):
        step_ind = self.settings[ValidSettings.STEP].ind
        step_ind += 1
        if step_ind >= len(self.settings[ValidSettings.STEP].values):
            step_ind = 0
        self.settings[ValidSettings.STEP].ind = step_ind
        self.send_setting(setting=self.settings[ValidSettings.STEP])
