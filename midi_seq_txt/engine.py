import random
import time
from multiprocessing import Process, Queue
from typing import Any, Dict, List, Tuple

import attrs

from .const import ValidButtons, ValidSettings
from .functionalities import MMiDi, MOutFunctionality, SFunctionality
from .sequencer import MiDiIn, MiDiOut, Sequencer


class Engine(Sequencer):
    """
    This class spawns sequencer as a separate process.
    It maintains communication between MSApp and all MIDIs.
    """

    def __init__(self, loc: str):
        super().__init__(loc=loc)
        self.settings: Dict[ValidSettings, SFunctionality] = dict()
        self.midi_ins: Dict[int, MiDiIn] = self.create_midi_ins()
        self.midi_outs: Dict[int, MiDiOut] = self.create_midi_outs()
        self.midi_outs_ids = sorted(self.midi_outs.keys())
        self.midi_ins_ids = sorted(self.midi_ins.keys())
        from midi_seq_txt.sequencer import DEBUG

        self.process = Process(target=self.start, args=(DEBUG,))
        self.detached_func_queue: Queue[Dict[str, Any]] = Queue()
        self.attached_func_queue: Queue[Dict[str, Any]] = Queue()
        self.current_step_id: Queue[int] = Queue()

    def create_midi_ins(self) -> Dict[int, MiDiIn]:
        midis: Dict[int, MMiDi] = self.mappings.init_midi_ins()
        midi_ins: Dict[int, MiDiIn] = dict()
        for midi_id in midis.keys():
            midi_ins[midi_id] = MiDiIn(midi=midis[midi_id])
        return midi_ins

    def create_midi_outs(self) -> Dict[int, MiDiOut]:
        midis: Dict[int, MMiDi] = self.mappings.init_midi_outs()
        midi_outs: Dict[int, MiDiOut] = dict()
        for midi_id in midis.keys():
            midi_outs[midi_id] = MiDiOut(midi=midis[midi_id])
        return midi_outs

    def midi_id_to_port_id(self, midi_id: int) -> int:
        if midi_id in self.midi_outs:
            return self.midi_outs[midi_id].port_id
        if midi_id in self.midi_ins:
            return self.midi_ins[midi_id].port_id
        return -1

    def detach(self) -> None:
        self.process.start()

    def start(self, debug: bool = False) -> None:
        self.detached = True
        import midi_seq_txt.sequencer

        setattr(midi_seq_txt.sequencer, "DEBUG", debug)
        self.init_data()
        for midi_id in self.midi_ins.keys():
            self.midi_ins[midi_id].attach(sequencer=self)
        for midi_id in self.midi_outs.keys():
            self.midi_outs[midi_id].attach(sequencer=self)
        self.run_sequencer_schedule()

    def run_sequencer_schedule(self) -> None:
        while True:
            midi_channel_out_modes: List[Tuple[int, int, MOutFunctionality]] = list()
            out_midi, out_channel, _, _, _ = self.get_current_e_pos()
            for in_midi in self.midi_ins.keys():
                for out_midi, channel, out_mode in self.midi_ins[in_midi].run_message_bus(
                    out_midi=out_midi, out_channel=out_channel
                ):
                    self.set_step(out_mode=out_mode)
                    self.send_out_mode(out_mode=out_mode)
                    midi_channel_out_modes.append((out_midi, out_channel, out_mode))
            self.ingest_func_data(
                midi_channel_out_modes=midi_channel_out_modes,
                out_midi=out_midi,
                out_channel=out_channel,
            )
            while len(midi_channel_out_modes):
                out_midi, out_channel, out_mode = midi_channel_out_modes.pop()
                self.midi_outs[out_midi].unscheduled_step.append((out_channel, out_mode))
            min_step: int = 2 * self.internal_config.n_steps
            for out_midi in self.midi_outs.keys():
                if len(self.midi_outs[out_midi].scheduled_steps):
                    min_step_tick = min(self.midi_outs[out_midi].scheduled_steps.keys())
                    step = int(min_step_tick / self.step_interval)
                    if step < min_step:
                        min_step = step
            if min_step <= self.internal_config.n_steps:
                self.current_step_id.put(min_step)
            for out_midi in self.midi_outs.keys():
                self.midi_outs[out_midi].run_message_bus()
            time.sleep(self.internal_config.sleep)

    def ingest_func_data(
        self,
        midi_channel_out_modes: List[Tuple[int, int, MOutFunctionality]],
        out_midi: int,
        out_channel: int,
    ) -> None:
        if self.detached:
            queue = self.detached_func_queue
        else:
            queue = self.attached_func_queue
        if not queue.empty():
            func_dict: Dict[str, Any] = self.detached_func_queue.get()
            if "indexes" in func_dict:
                out_mode = self.convert_to_out_mode(func_dict)
                midi_channel_out_modes.append((out_midi, out_channel, out_mode))
                self.set_step(out_mode=out_mode)
            else:
                setting = self.convert_to_setting(func_dict)
                self.set_option(option=setting)

    def convert_to_setting(self, setting_dict: Dict[str, Any]) -> SFunctionality:
        valid_setting = ValidSettings(setting_dict["name"])
        setting_value = self.settings[valid_setting]
        setting_value.update_with_ind(int(setting_dict["ind"]))
        return setting_value

    def convert_to_out_mode(self, out_mode_dict: Dict[str, Any]) -> MOutFunctionality:
        valid_out_mode = out_mode_dict["name"]
        out_mode_value = self.out_modes[valid_out_mode].new(lock=False)
        out_mode_value.set_indexes(out_mode_dict["indexes"])
        return out_mode_value

    def send_out_mode(self, out_mode: MOutFunctionality) -> None:
        if self.detached:
            self.attached_func_queue.put(attrs.asdict(out_mode))
        else:
            self.set_step(out_mode=out_mode)
            self.detached_func_queue.put(attrs.asdict(out_mode))

    def send_setting(self, setting: SFunctionality) -> None:
        if self.detached:
            self.attached_func_queue.put(attrs.asdict(setting))
        else:
            self.set_option(option=setting)
            self.detached_func_queue.put(attrs.asdict(setting))

    def send_delete(self) -> None:
        midi, channel, part, step, valid_out_mode = self.get_current_e_pos()
        out_mode = self.out_modes[valid_out_mode].new(lock=True)
        self.send_out_mode(out_mode=out_mode)

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
        f_out_mode: str,
        button: ValidButtons,
    ) -> None:
        t_out_mode = self.get_current_new_out_mode()
        shuffle = list(range(1, self.internal_config.n_steps + 1))
        random.shuffle(shuffle)
        for f_step in self.settings[ValidSettings.E_STEP].values:
            f_sequence = self.sequences.data[f_midi][f_channel][f_part][int(f_step)][f_out_mode]
            t_step: int = -1
            if button == ValidButtons.C_AS_IS:
                t_step = int(f_step)
            elif button == ValidButtons.C_REVERSE:
                t_step = self.internal_config.n_steps - int(f_step) + 1
            elif button == ValidButtons.C_RANDOM:
                t_step = shuffle[int(f_step) - 1]
            if t_step > 0:
                step_setting = self.settings[ValidSettings.V_STEP].update_with_value(t_step)
                t_out_mode = t_out_mode.set_indexes(f_sequence)
                self.send_setting(step_setting)
                self.send_out_mode(t_out_mode)
        step_setting = self.settings[ValidSettings.V_STEP].update_with_value(1)
        self.send_setting(step_setting)
