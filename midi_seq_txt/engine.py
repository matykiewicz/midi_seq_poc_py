import random
import time
from multiprocessing import Process, Queue
from typing import Any, Dict

import attrs
import rtmidi

from .const import ValidButtons, ValidModes, ValidSettings
from .functionalities import MFunctionality, SFunctionality
from .sequencer import MiDiO, Sequencer


class Engine(Sequencer):
    """
    This class spawns sequencer as a separate process.
    It maintains communication between MSApp and all MIDIs.
    """

    def __init__(self, loc: str):
        super().__init__()
        self.loc = loc
        self.modes: Dict[ValidModes, MFunctionality] = dict()
        self.settings: Dict[ValidSettings, SFunctionality] = dict()
        self.midis: Dict[int, MiDiO] = self.init_midis()
        self.n_midis = len(self.midis)
        from midi_seq_txt.sequencer import DEBUG

        self.process = Process(target=self.start, args=(DEBUG,))
        self.func_queue: Queue[Dict[str, Any]] = Queue()
        self.current_step_id: Queue[int] = Queue()

    @staticmethod
    def init_midis() -> Dict[int, MiDiO]:
        midis: Dict[int, MiDiO] = dict()
        midi_out = rtmidi.MidiOut()
        port_names = midi_out.get_ports()
        for i in range(len(port_names)):
            midis[i] = MiDiO(port_id=i)
        if not len(midis):
            raise ValueError("At least 1 usb midi device is needed")
        return midis

    def detach(self) -> None:
        self.process.start()

    def start(self, debug: bool = False) -> None:
        self.detached = True
        import midi_seq_txt.sequencer

        setattr(midi_seq_txt.sequencer, "DEBUG", debug)
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
                    midi_id = int(self.settings[ValidSettings.E_MIDI_O].get_value())
                    self.midis[midi_id].add_note_to_note_schedule(mode)
                else:
                    setting = self.convert_to_setting(func_dict)
                    self.set_option(option=setting)
            for midi_id in self.midis.keys():
                self.midis[midi_id].add_parts_to_step_schedule()
                self.midis[midi_id].run_note_and_step_schedule()
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
        midi, channel, part, step, valid_mode = self.get_current_e_pos()
        mode = self.modes[valid_mode].new(lock=True)
        self.send_mode(mode=mode)

    def send_reset_step(self) -> None:
        self.settings[ValidSettings.E_STEP].update_with_ind(0)
        self.send_setting(setting=self.settings[ValidSettings.E_STEP])

    def send_next_step(self) -> None:
        self.settings[ValidSettings.E_STEP].next_ind()
        self.send_setting(setting=self.settings[ValidSettings.E_STEP])

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
        for f_step in self.settings[ValidSettings.E_STEP].values:
            f_sequence = self.sequences.data[f_midi][f_channel][f_part][int(f_step)][f_mode]
            t_step: int = -1
            if button == ValidButtons.C_AS_IS:
                t_step = int(f_step)
            elif button == ValidButtons.C_REVERSE:
                t_step = self.internal_config.n_steps - int(f_step) + 1
            elif button == ValidButtons.C_RANDOM:
                t_step = shuffle[int(f_step) - 1]
            if t_step > 0:
                step_setting = self.settings[ValidSettings.V_STEP].update_with_value(t_step)
                t_mode = t_mode.set_indexes(f_sequence)
                self.send_setting(step_setting)
                self.send_mode(t_mode)
        step_setting = self.settings[ValidSettings.V_STEP].update_with_value(1)
        self.send_setting(step_setting)
