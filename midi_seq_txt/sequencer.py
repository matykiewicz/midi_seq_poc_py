import time
from enum import StrEnum
from multiprocessing import Process, Queue
from typing import Any, Dict, List, Optional, Tuple, Union

from attrs import define

from .configs import InternalConfig

SEQUENCER: Optional["Sequencer"] = None


class ValidOptions(StrEnum):
    REC_KEYS = "RecKS"
    PLAY_KEYS = "Play"
    SET_TEMPO = "Tempo"
    SET_MIDI = "MiDiD"
    KEY_TYPE = "KeyTP"


class ValidKeys(StrEnum):
    NOTE = "Note"


class MiDi:
    def __init__(self, port_id: int, port_name: str):
        self.port_name = port_name
        self.port_id = port_id
        self.internal_config = InternalConfig()
        self.process = Process(target=self.start)
        self.option_queue: Queue[Dict[str, Any]] = Queue()
        self.key_queue: Queue[Dict[str, Any]] = Queue()
        self.options: Dict[ValidOptions, Functionality] = {}
        self.keys: Dict[ValidKeys, Functionality] = {}
        self.sequences: List[List[Functionality]] = []

    def detach(self):
        self.process.start()

    def start(self):
        import rtmidi

        self.keys: Dict[ValidKeys, Functionality] = get_keys()
        self.options: Dict[ValidOptions, Functionality] = get_options()
        midi_out: rtmidi.MidiOut = rtmidi.MidiOut()
        midi_out.open_port(self.port_id)
        while True:
            if not self.option_queue.empty():
                option_dict: Dict[str, Any] = self.option_queue.get()
                option_enum, option_fun = self.convert_option_dict(option_dict)
                self.set_option(
                    midi_out=midi_out, option_enum=option_enum, option_fun=option_fun
                )
            if not self.key_queue.empty():
                key_dict: Dict[str, Any] = self.key_queue.get()
                key_enum, key_fun = self.convert_key_dict(key_dict)
                self.set_key(midi_out=midi_out, key_enum=key_enum, key_fun=key_fun)
            time.sleep(self.internal_config.sleep)

    def convert_option_dict(
        self, option_dict: Dict[str, Any]
    ) -> Tuple[ValidOptions, "Functionality"]:
        valid_option = ValidOptions(option_dict["name"])
        option = self.options[valid_option]
        option.ind = option_dict["ind"]
        return valid_option, option

    def convert_key_dict(
        self, key_dict: Dict[str, Any]
    ) -> Tuple[ValidKeys, "Functionality"]:
        valid_key = ValidKeys(key_dict["name"])
        key = self.keys[valid_key]
        key.ind = key_dict["ind"]
        return valid_key, key

    def set_key(self, midi_out, key_enum: ValidKeys, key_fun: "Functionality") -> None:
        pass

    def set_option(
        self, midi_out, option_enum: ValidOptions, option_fun: "Functionality"
    ) -> None:
        with midi_out:
            note_on = [0x90, 60, 255]  # channel 1, middle C, velocity 112
            note_off = [0x80, 60, 0]
            midi_out.send_message(note_on)
            time.sleep(0.5)
            midi_out.send_message(note_off)
            time.sleep(0.1)


@define
class Functionality:
    name: str
    buttons: Tuple[str, str]
    ind: int
    values: List[Union[str, int]]
    midis: List[int] = list()


class Sequencer:

    def __init__(self):
        self.keys: Dict[ValidKeys, Functionality] = self.init_keys()
        self.midis: Dict[int, MiDi] = self.init_midis()
        self.options: Dict[ValidOptions, Functionality] = self.init_options(
            n_midis=len(self.midis)
        )

    @staticmethod
    def init_midis() -> Dict[int, MiDi]:
        midis: Dict[int, MiDi] = dict()
        import rtmidi

        midi_out = rtmidi.MidiOut()
        port_names = midi_out.get_ports()
        for i, port_name in enumerate(port_names):
            midis[i] = MiDi(port_id=i, port_name=port_name)
        return midis

    @staticmethod
    def init_options(n_midis) -> Dict[ValidOptions, Functionality]:
        class PlayKeys(Functionality):
            def __init__(self):
                super().__init__(
                    name=ValidOptions.PLAY_KEYS.value,
                    buttons=("Start", "Stop"),
                    ind=0,
                    values=["Start, Stop"],
                )

        class RecKeys(Functionality):
            def __init__(self):
                super().__init__(
                    name=ValidOptions.REC_KEYS.value,
                    buttons=("Step", "Slide"),
                    ind=0,
                    values=["Step", "Slide"],
                )

        class SetTempo(Functionality):
            def __init__(self):
                super().__init__(
                    name=ValidOptions.SET_TEMPO.value,
                    buttons=("-10", "+10"),
                    ind=0,
                    values=[i * 10 for i in range(5, 20)],
                )

        class SetMiDi(Functionality):
            def __init__(self):
                super().__init__(
                    name=ValidOptions.SET_MIDI.value,
                    buttons=("-1", "+1"),
                    ind=0,
                    values=[i for i in range(n_midis)],
                )

        class KeyType(Functionality):
            def __init__(self):
                super().__init__(
                    name=ValidOptions.KEY_TYPE.value,
                    buttons=("-T", "+T"),
                    ind=0,
                    values=[k.value for k in ValidKeys],
                )

        return {
            ValidOptions.REC_KEYS: RecKeys(),
            ValidOptions.PLAY_KEYS: PlayKeys(),
            ValidOptions.SET_TEMPO: SetTempo(),
            ValidOptions.SET_MIDI: SetMiDi(),
            ValidOptions.KEY_TYPE: KeyType(),
        }

    @staticmethod
    def init_keys() -> Dict[ValidKeys, Functionality]:
        class Note(Functionality):
            def __init__(self):
                super().__init__(
                    name="Note",
                    buttons=("-1", "+1"),
                    ind=0,
                    values=[i for i in range(8)],
                )

        return {ValidKeys.NOTE: Note()}


def get_midis() -> Dict[int, MiDi]:
    global SEQUENCER
    if SEQUENCER is None:
        SEQUENCER = Sequencer()
    return SEQUENCER.midis


def get_options() -> Dict[ValidOptions, Functionality]:
    global SEQUENCER
    if SEQUENCER is None:
        SEQUENCER = Sequencer()
    return SEQUENCER.options


def get_keys() -> Dict[ValidKeys, Functionality]:
    global SEQUENCER
    if SEQUENCER is None:
        SEQUENCER = Sequencer()
    return SEQUENCER.keys
