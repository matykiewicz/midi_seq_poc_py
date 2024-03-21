from argparse import Namespace
from typing import Callable, Dict, Optional, List

import attrs
from textual.app import App, ComposeResult
from textual.widgets import Footer, Label, Sparkline, Static

from .configs import InitConfig
from .functionalities import (
    NFunctionality,
    MFunctionality,
    SFunctionality,
    ValidModes,
    ValidNav,
    ValidSettings,
)
from .sequencers import MiDi, Sequencers


class KeysUI(Static):

    def __init__(
        self,
        sequencers: Sequencers,
    ):
        super().__init__()
        self.internal_config = InitConfig()
        self.sequencers: Sequencers = sequencers
        self.data_pos_view = Label("")
        self.data_vis_view = Sparkline(data=[0] * self.internal_config.steps)
        self.data_pos_edit = Label("")
        self.data_vis_edit = Sparkline(data=[0] * self.internal_config.steps)
        self.update_options: Optional[Callable] = None
        self.send_option: Optional[Callable] = None

    def update_edit(self):
        midi, channel, part, key_type, _ = self.get_current_pos()
        self.data_vis_edit.data = self.sequences[midi][channel][part][key_type].copy()

    def update_view(self):
        midi, channel, part, key_type, _ = self.get_current_pos()
        self.data_vis_view.data = self.sequences[midi][channel][part][key_type].copy()

    def compose(self) -> ComposeResult:
        yield self.data_pos_view
        yield self.data_vis_view
        yield self.data_pos_edit
        yield self.data_vis_edit

    def send_key(self, key: MFunctionality) -> None:
        for midi_id in self.midis.keys():
            midi: MiDi = self.midis[midi_id]
            midi.func_queue.put(attrs.asdict(key))

    def update_all(self) -> None:
        self.update_edit()
        if self.update_options is not None:
            self.update_options()

    def config_key(self, key_value: int) -> MFunctionality:
        key_type_id = self.options[ValidOptions.KEY_TYPE].ind
        key_type_name = self.options[ValidOptions.KEY_TYPE].values[key_type_id]
        key_type = ValidKeys(key_type_name)
        key = self.keys[key_type]
        key.ind = key.values.index(key_value)
        return key

    def key_1(self):
        # key = 0 is a delete command
        key = self.config_key(key_value=1)
        self.send_key(key=key)
        self.set_step(key_val=key)
        self.update_all()

    def key_2(self):
        key = self.config_key(key_value=2)
        self.send_key(key=key)
        self.set_step(key_val=key)
        self.update_all()

    def key_3(self):
        key = self.config_key(key_value=3)
        self.send_key(key=key)
        self.set_step(key_val=key)
        self.update_all()

    def key_4(self):
        key = self.config_key(key_value=4)
        self.send_key(key=key)
        self.set_step(key_val=key)
        self.update_all()

    def key_5(self):
        key = self.config_key(key_value=5)
        self.send_key(key=key)
        self.set_step(key_val=key)
        self.update_all()

    def key_6(self):
        key = self.config_key(key_value=6)
        self.send_key(key=key)
        self.set_step(key_val=key)
        self.update_all()

    def key_7(self):
        key = self.config_key(key_value=7)
        self.send_key(key=key)
        self.set_step(key_val=key)
        self.update_all()

    def key_8(self):
        key = self.config_key(key_value=8)
        self.send_key(key=key)
        self.set_step(key_val=key)
        self.update_all()


class NavigationUI(Static):

    def __init__(
        self,
        sequencers: Sequencers,
    ):
        super().__init__()
        self.internal_config = InitConfig()
        self.sequencers = sequencers
        self.settings_vis = Label("")
        self.button_vis = Label("")
        self.keys_vis = Label("")
        self.valid_nav = list(ValidNav)
        self.nav_id = 0
        # self.update_all()

    def compose(self) -> ComposeResult:
        yield self.settings_vis
        yield self.button_vis
        yield self.keys_vis

    def update_all(self):
        current_nav = self.valid_nav[self.nav_id]
        navigation = self.sequencers.navigation[current_nav]
        n_name = navigation.name
        n_index = navigation.ind

        self.option_vis.update(f"{f_name[0:5]:>5}:{f_value[0:5]:>5}")
        # - - -
        buttons = navigation.buttons
        b_ind = navigation.b_ind
        button_1 = str(buttons[b_ind * 4 + 0])
        button_2 = str(buttons[b_ind * 4 + 1])
        button_3 = str(buttons[b_ind * 4 + 2])
        button_4 = str(buttons[b_ind * 4 + 3])
        self.button_vis.update(
            f"{button_1[0:5]:>5}|{button_2[0:5]:>5}|{button_3[0:5]:>5}|{button_4[0:5]:>5}"
        )

    def nav_1(self):
        set_index = self.current_option
        b_ind = self.option_list[set_index].b_ind
        button = self.option_list[set_index].buttons[b_ind * 4 + 0]
        if button == ValidNav.OPT_DOWN:
            set_index = self.current_option
            set_index -= 1
            if set_index < 0:
                set_index = len(self.option_list) - 1
            self.current_option = set_index
        elif button == ValidNav.BACK:
            self.option_list[set_index].b_ind = 0
            self.option_list[self.current_option].ind = 0
        self.update_all()

    def nav_2(self):
        set_index = self.current_option
        b_ind = self.option_list[set_index].b_ind
        button = self.option_list[set_index].buttons[b_ind * 4 + 1]
        if button == ValidNav.OPT_UP:
            set_index += 1
            if set_index >= len(self.option_list):
                set_index = 0
            self.current_option = set_index
        elif button == ValidNav.PREVIOUS:
            options = self.move_pos(direction=-1)
            for option in options:
                self.send_option(option)
            self.update_edit()
        self.update_all()

    def nav_3(self):
        set_index = self.current_option
        b_ind = self.option_list[set_index].b_ind
        button = self.option_list[set_index].buttons[b_ind * 4 + 2]
        if button == ValidNav.SET_DOWN:
            val_index = self.option_list[self.current_option].ind
            val_index -= 1
            if val_index < 0:
                val_index = len(self.option_list[self.current_option].values) - 1
            self.option_list[self.current_option].ind = val_index
            self.send_option(self.option_list[self.current_option])
        elif button == ValidNav.ENTER:
            self.option_list[set_index].b_ind = 1
            self.option_list[self.current_option].ind = 1
            self.send_option(self.option_list[self.current_option])
        elif button == ValidNav.NEXT:
            options = self.move_pos(direction=1)
            for option in options:
                self.send_option(option)
            self.update_edit()
        self.update_all()

    def nav_4(self):
        set_index = self.current_option
        b_ind = self.option_list[set_index].b_ind
        button = self.option_list[set_index].buttons[b_ind * 4 + 3]
        if button == ValidNav.SET_UP:
            val_index = self.option_list[self.current_option].ind
            val_index += 1
            if val_index >= len(self.option_list[self.current_option].values):
                val_index = 0
            self.option_list[self.current_option].ind = val_index
            self.send_option(self.option_list[self.current_option])
        elif button == ValidNav.DELETE:
            key = self.delete_step()
            self.send_key(key=key)
            self.update_edit()
        elif button == ValidNav.VIEW:
            if self.update_view is not None:
                self.update_view()
        elif button == ValidNav.PLAY:
            pass
        self.update_all()

    def send_setting(self, setting: SFunctionality) -> None:
        self.sequencers.send_setting(setting=setting)


class UI(App):

    CSS_PATH = "ui.tcss"
    BINDINGS = [
        ("a", "nav_1", "N1"),
        ("b", "nav_2", "N2"),
        ("c", "nav_3", "N3"),
        ("d", "nav_4", "N4"),
        ("4", "nav_5", "N5"),
        ("6", "nav_6", "N6"),
        ("7", "nav_7", "N7"),
        ("9", "nav_8", "N8"),
        ("e", "key_1", "K1"),
        ("f", "key_2", "K2"),
        ("g", "key_3", "K3"),
        ("h", "key_4", "K4"),
        ("i", "key_5", "K5"),
        ("j", "key_6", "K6"),
        ("k", "key_7", "K7"),
        ("l", "key_8", "K8"),
    ]

    def __init__(self, args: Namespace):
        super().__init__()
        self.sequencers = Sequencers()
        self.keys_ui = KeysUI(sequencers=self.sequencers)
        self.navigation_ui = NavigationUI(sequencers=self.sequencers)
        for midi in self.sequencers.midis.values():
            midi.detach()

    def compose(self) -> ComposeResult:
        yield self.keys_ui
        yield self.navigation_ui
        yield Footer()

    def action_nav_1(self) -> None:
        self.navigation_ui.nav_1()

    def action_nav_2(self) -> None:
        self.navigation_ui.nav_2()

    def action_set_3(self) -> None:
        self.navigation_ui.nav_3()

    def action_nav_4(self) -> None:
        self.navigation_ui.nav_4()

    def action_nav_5(self) -> None:
        self.navigation_ui.nav_5()

    def action_nav_6(self) -> None:
        self.navigation_ui.nav_6()

    def action_nav_7(self) -> None:
        self.navigation_ui.nav_7()

    def action_nav_8(self) -> None:
        self.navigation_ui.nav_8()

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
