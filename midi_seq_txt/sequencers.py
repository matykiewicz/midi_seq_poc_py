import time
from collections import defaultdict
from multiprocessing import Process, Queue
from typing import Any, Dict, List, Tuple

import rtmidi
from mingus.core import keys

from .configs import InitConfig

from .functionalities import (
    NFunctionality,
    MFunctionality,
    SFunctionality,
    ValidModes,
    ValidNav,
    ValidSettings,
    init_nav,
    init_modes,
    init_settings,
)


ValidOptions = 0
ValidKeys = 1


class Sequencer:
    def __init__(self):
        self.internal_config = InitConfig()
        self.navigation: Dict[ValidNav, NFunctionality] = dict()
        self.settings: Dict[ValidSettings, SFunctionality] = dict()
        self.modes: Dict[ValidModes, MFunctionality] = dict()
        self.sequences: Dict[int, Dict[int, Dict[int, Dict[ValidModes, List[int]]]]] = (
            dict()
        )
        self.fh = None

    def wr(self):
        import os

        self.fh = open(f"{self.__class__.__name__}.{os.getpid()}.json", "w")
        import json

        json.dump(self.sequences, indent=2, sort_keys=True, fp=self.fh)
        self.fh.close()

    def init_sequences(self) -> None:
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
                        def_ind = self.modes[mode].def_ind
                        sequences[midi][channel][part][mode] = [def_ind] * steps
        self.sequences = sequences

    def get_current_pos(self) -> Tuple[int, int, int, ValidModes, int]:
        midi_ind = self.settings[ValidSettings.SET_MIDI].ind
        channel_ind = self.settings[ValidSettings.SET_CHANNEL].ind
        part_ind = self.settings[ValidSettings.SET_PART].ind
        mode_ind = self.settings[ValidSettings.SET_MODE].ind
        mode = ValidModes(str(self.settings[ValidSettings.SET_MODE].values[mode_ind]))
        step_ind = self.settings[ValidSettings.SET_STEP].ind
        return midi_ind, channel_ind, part_ind, mode, step_ind

    def set_step(self, value: MFunctionality) -> SFunctionality:
        if self.settings[ValidSettings.RECORD].ind == 1:
            midi, channel, part, key_type, step = self.get_current_pos()
            self.sequences[midi][channel][part][key_type][step] = key_val.values[
                key_val.ind
            ]
            ind = self.options[ValidOptions.SET_STEP].ind
            ind += 1
            if ind >= self.internal_config.steps:
                ind = 0
            self.options[ValidOptions.SET_STEP].ind = ind
        self.wr()
        return self.options[ValidOptions.SET_STEP]

    def delete_step(self) -> MFunctionality:
        midi, channel, part, key_type, step = self.get_current_pos()
        key = self.keys[key_type]
        key.ind = key.def_ind
        self.set_step(key_val=key)
        return key

    def move_pos(
        self, direction: int
    ) -> Tuple[SFunctionality, SFunctionality, SFunctionality, SFunctionality]:
        midi_ind = self.options[ValidOptions.SET_MIDI].ind
        channel_ind = self.options[ValidOptions.SET_CHANNEL].ind
        part_ind = self.options[ValidOptions.SET_PART].ind
        key_ind = self.options[ValidOptions.KEY_TYPE].ind
        key_ind += direction
        overflow = False
        if key_ind >= len(self.options[ValidOptions.KEY_TYPE].values):
            key_ind = 0
            overflow = True
        elif key_ind < 0:
            key_ind = len(self.options[ValidOptions.KEY_TYPE].values) - 1
            overflow = True
        if overflow:
            part_ind += direction
            overflow = False
        if part_ind >= len(self.options[ValidOptions.SET_PART].values):
            part_ind = 0
            overflow = True
        elif part_ind < 0:
            part_ind = len(self.options[ValidOptions.SET_PART].values) - 1
            overflow = True
        if overflow:
            channel_ind += direction
            overflow = False
        if channel_ind >= len(self.options[ValidOptions.SET_CHANNEL].values):
            channel_ind = 0
            overflow = True
        elif channel_ind < 0:
            channel_ind = len(self.options[ValidOptions.SET_CHANNEL].values) - 1
            overflow = True
        if overflow:
            midi_ind += direction
            overflow = False
        if midi_ind >= len(self.options[ValidOptions.SET_MIDI].values):
            midi_ind = 0
            overflow = True
        elif midi_ind < 0:
            midi_ind = len(self.options[ValidOptions.SET_MIDI].values) - 1
            overflow = True
        self.options[ValidOptions.SET_MIDI].ind = midi_ind
        self.options[ValidOptions.SET_CHANNEL].ind = channel_ind
        self.options[ValidOptions.SET_PART].ind = part_ind
        self.options[ValidOptions.KEY_TYPE].ind = key_ind
        return (
            self.options[ValidOptions.SET_MIDI],
            self.options[ValidOptions.SET_CHANNEL],
            self.options[ValidOptions.SET_PART],
            self.options[ValidOptions.KEY_TYPE],
        )

    def set_option(self, value: SFunctionality) -> None:
        pass


class MiDi(Sequencer):
    def __init__(self, port_id: int, port_name: str, n_midis: int):
        super().__init__()
        self.port_name = port_name
        self.port_id = port_id
        self.n_midis = n_midis
        self.internal_config = InitConfig()
        self.process = Process(target=self.start)
        self.func_queue: Queue[Dict[str, Any]] = Queue()

    def detach(self) -> None:
        self.process.start()

    def start(self) -> None:
        self.settings: Dict[ValidOptions, SFunctionality] = init_settings(
            n_midis=self.n_midis
        )
        self.modes: Dict[ValidKeys, MFunctionality] = init_modes()
        self.init_sequences()
        midi_out: rtmidi.MidiOut = rtmidi.MidiOut()
        midi_out.open_port(self.port_id)
        while True:
            if not self.func_queue.empty():
                func_dict: Dict[str, Any] = self.func_queue.get()
                if "hex_codes" in func_dict:
                    mode_value = self.convert_to_mode(func_dict)
                    self.set_step(value=mode_value)
                else:
                    setting_value = self.convert_to_setting(func_dict)
                    self.set_option(value=setting_value)
            time.sleep(self.internal_config.sleep)

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

    @staticmethod
    def play_key(midi_out, key_enum: ValidModes, key_fun: "MFunctionality") -> None:
        note_on = [0x90, 60, 255]  # channel 1, middle C, velocity 112
        note_off = [0x80, 60, 0]
        with midi_out:
            midi_out.send_message(note_on)
            time.sleep(0.5)
            midi_out.send_message(note_off)
            pass


class Sequencers:

    def __init__(self):
        self.modes: Dict[ValidModes, MFunctionality] = init_modes()
        self.midis: Dict[int, MiDi] = self.init_midis()
        self.settings: Dict[ValidSettings, SFunctionality] = init_settings(
            n_midis=len(self.midis)
        )
        self.navigation: Dict[ValidNav, NFunctionality] = init_nav()

    @staticmethod
    def init_midis() -> Dict[int, MiDi]:
        midis: Dict[int, MiDi] = dict()
        midi_out = rtmidi.MidiOut()
        port_names = midi_out.get_ports()
        for i, port_name in enumerate(port_names):
            midis[i] = MiDi(port_id=i, port_name=port_name, n_midis=len(port_names))
        if not len(midis):
            raise ValueError("At least 1 usb midi device is needed")
        return midis
