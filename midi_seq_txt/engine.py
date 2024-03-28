import random
import time
from multiprocessing import Process, Queue
from typing import Any, Dict, List, Tuple

import attrs
import rtmidi

from .configs import InitConfig
from .functionalities import (
    MFunctionality,
    SFunctionality,
    ValidButtons,
    ValidIndexes,
    ValidModes,
    ValidSettings,
)
from .sequencer import MiDi, Sequencer


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
        f_mode: ValidModes,
        button: ValidButtons,
    ) -> None:
        t_mode = self.get_current_new_mode()
        shuffle = list(range(1, self.internal_config.n_steps + 1))
        random.shuffle(shuffle)
        for f_step in self.settings[ValidSettings.STEP].values:
            f_sequence = self.sequences[f_midi][f_part][int(f_step)][f_channel][f_mode]
            t_step: int = -1
            if button == ValidButtons.C_AS_IS:
                t_step = int(f_step)
            elif button == ValidButtons.C_REVERSE:
                t_step = self.internal_config.n_steps - int(f_step) + 1
            elif button == ValidButtons.C_RANDOM:
                t_step = shuffle[int(f_step) - 1]
            if t_step > 0:
                step_setting = self.settings[ValidSettings.STEP].update_with_value(t_step)
                t_mode = t_mode.set_indexes(f_sequence)
                self.send_setting(step_setting)
                self.send_mode(t_mode)
        step_setting = self.settings[ValidSettings.STEP].update_with_value(1)
        self.send_setting(step_setting)

    def find_positions_with_music(self) -> List[Tuple[int, int, int, int, ValidModes]]:
        positions_with_music = list()
        for midi in self.sequences.keys():
            for part in self.sequences[midi].keys():
                for step in self.sequences[midi][part].keys():
                    for channel in self.sequences[midi][part][step].keys():
                        for valid_mode in self.sequences[midi][part][step][channel].keys():
                            indexes = self.sequences[midi][part][step][channel][valid_mode]
                            has_note = indexes[ValidIndexes.VIS_INDEX_1.value][
                                ValidIndexes.VIS_INDEX_2.value
                            ]
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
