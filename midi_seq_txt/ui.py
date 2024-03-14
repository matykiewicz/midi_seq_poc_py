from argparse import Namespace
from typing import Dict, List

import attrs
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import Footer, Label, Static

from .configs import ExternalConfig, InternalConfig
from .sequencer import (
    Functionality,
    MiDi,
    ValidKeys,
    ValidOptions,
    get_keys,
    get_midis,
    get_options,
)


class OptionsUI(Static):
    name_index = reactive(0)
    val_index = reactive(0)

    def __init__(self, midis: Dict[int, MiDi], options: List[Functionality]):
        super().__init__()
        self.internal_config = InternalConfig()
        self.options = options
        self.midis = midis
        self.f_name = Label("")
        self.f_value = Label("")
        self.name_index: int = 0
        self.val_index: int = 0

    def compose(self) -> ComposeResult:
        yield self.f_name
        yield self.f_value

    def update_all(self):
        f_name = str(self.options[self.name_index].name)
        f_value = str(self.options[self.name_index].values[self.val_index])
        button_1 = str(self.options[self.name_index].buttons[0])
        button_2 = str(self.options[self.name_index].buttons[1])
        self.f_name.update(f"{f_name[0:5]:>5}")
        self.f_value.update(
            f"{button_1[0:5]:>5} | {f_value[0:5]:>5} | {button_2[0:5]:>5}"
        )

    def watch_name_index(self):
        self.update_all()

    def watch_value_index(self):
        self.update_all()

    def function_up(self):
        name_index = self.name_index
        name_index += 1
        if name_index >= len(self.options):
            name_index = 0
        self.name_index = name_index

    def function_down(self):
        name_index = self.name_index
        name_index -= 1
        if name_index < 0:
            name_index = len(self.options) - 1
        self.name_index = name_index

    def value_up(self):
        val_index = self.val_index
        val_index += 1
        if val_index >= len(self.options[self.name_index].values):
            val_index = 0
        self.options[self.name_index].ind = val_index
        self.send_option(self.options[self.name_index])
        self.val_index = val_index

    def value_down(self):
        val_index = self.val_index
        val_index -= 1
        if val_index < 0:
            val_index = len(self.options[self.name_index].values) - 1
        self.options[self.name_index].ind = val_index
        self.send_option(self.options[self.name_index])
        self.val_index = val_index

    def send_option(self, option: Functionality) -> None:
        for midi in self.midis.keys():
            self.midis[midi].option_queue.put(attrs.asdict(option))


class KeysUI(Static):

    def __init__(
        self,
        midis: Dict[int, MiDi],
        options: Dict[ValidOptions, Functionality],
        keys: Dict[ValidKeys, Functionality],
    ):
        super().__init__()
        self.midis = midis
        self.options = options
        self.keys = keys

    def send_key(self, key: Functionality) -> None:
        for midi_id in key.midis:
            midi: MiDi = self.midis[midi_id]
            midi.key_queue.put(attrs.asdict(key))

    def config_key(self, key_value: int) -> Functionality:
        midi_id = self.options[ValidOptions.SET_MIDI].ind
        key_type_id = self.options[ValidOptions.KEY_TYPE].ind
        key_type_name = self.options[ValidOptions.KEY_TYPE].values[key_type_id]
        key_type = ValidKeys(key_type_name)
        key = self.keys[key_type]
        key.ind = key.values.index(key_value)
        key.midis = [midi_id]
        return key

    def key_1(self):
        key = self.config_key(key_value=1)
        self.send_key(key=key)

    def key_2(self):
        key = self.config_key(key_value=2)
        self.send_key(key=key)

    def key_3(self):
        key = self.config_key(key_value=3)
        self.send_key(key=key)

    def key_4(self):
        key = self.config_key(key_value=4)
        self.send_key(key=key)

    def key_5(self):
        key = self.config_key(key_value=5)
        self.send_key(key=key)

    def key_6(self):
        key = self.config_key(key_value=6)
        self.send_key(key=key)

    def key_7(self):
        key = self.config_key(key_value=7)
        self.send_key(key=key)

    def key_8(self):
        key = self.config_key(key_value=8)
        self.send_key(key=key)


class UI(App):

    CSS_PATH = "ui.tcss"
    BINDINGS = [
        ("a", "function_down", "F-"),
        ("b", "function_up", "F+"),
        ("c", "value_down", "V-"),
        ("d", "value_up", "V+"),
        ("e", "key_1", "N1"),
        ("f", "key_2", "N2"),
        ("g", "key_3", "N3"),
        ("h", "key_4", "N4"),
        ("i", "key_5", "N5"),
        ("j", "key_6", "N6"),
        ("k", "key_7", "N7"),
        ("l", "key_8", "N8"),
    ]

    def __init__(self, args: Namespace):
        super().__init__()
        self.external_config = ExternalConfig(**vars(args))
        self.midis: Dict[int, MiDi] = get_midis()
        self.options: Dict[ValidOptions, Functionality] = get_options()
        self.keys: Dict[ValidKeys, Functionality] = get_keys()
        self.options_ui = OptionsUI(
            midis=self.midis, options=list(self.options.values())
        )
        self.keys_ui = KeysUI(midis=self.midis, options=self.options, keys=self.keys)
        for midi in self.midis.values():
            midi.detach()

    def compose(self) -> ComposeResult:
        yield self.options_ui
        yield self.keys_ui
        yield Footer()

    def action_function_down(self) -> None:
        self.options_ui.function_down()

    def action_function_up(self) -> None:
        self.options_ui.function_up()

    def action_value_down(self) -> None:
        self.options_ui.value_down()

    def action_value_up(self) -> None:
        self.options_ui.value_up()

    def action_key_1(self) -> None:
        self.keys_ui.key_1()

    def action_key_2(self) -> None:
        self.keys_ui.key_2()

    def action_key_3(self) -> None:
        self.keys_ui.key_3()

    def action_key_4(self) -> None:
        self.keys_ui.key_4()

    def action_key_5(self) -> None:
        self.keys_ui.key_5()

    def action_key_6(self) -> None:
        self.keys_ui.key_6()

    def action_key_7(self) -> None:
        self.keys_ui.key_7()

    def action_key_8(self) -> None:
        self.keys_ui.key_8()
