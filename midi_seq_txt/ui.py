from typing import Callable, Dict, List, Optional, Tuple

from textual.app import ComposeResult
from textual.widgets import Label, Sparkline, Static

from .configs import InitConfig
from .const import ValidButtons, ValidModes, ValidNav, ValidSettings
from .engine import Engine
from .functionalities import MFunctionality, SFunctionality, init_nav


class KeysUI(Static):

    def __init__(
        self,
        sequencer: Engine,
    ):
        super().__init__()
        self.internal_config = InitConfig()
        self.sequencer = sequencer
        self.pos_top_label = Label("")
        self.data_vis_top = Sparkline(data=[0] * self.internal_config.n_steps)
        self.pos_bottom_label = Label("")
        self.data_vis_bottom = Sparkline(data=[0] * self.internal_config.n_steps)
        self.navigation_ui: Optional[NavigationUI] = None
        self.update_all()

    def update_top(self) -> None:
        show_as = self.sequencer.settings[ValidSettings.VIEW_FUNCTION].get_value()
        if self.sequencer.settings[ValidSettings.COPY].get_ind() == 1:
            show_as = "To"
        midi, part, step, channel, valid_mode = self.sequencer.get_current_v_pos()
        data = []
        vis_index_1, vis_index_2 = self.sequencer.get_current_v_step_mode(
            valid_mode=valid_mode
        ).get_vis_ind()
        for step in range(1, self.internal_config.n_steps + 1):
            if vis_index_1 >= len(self.sequencer.sequences[midi][part][step][channel][valid_mode]):
                vis_index_1 = 0
            if vis_index_2 >= len(
                self.sequencer.sequences[midi][part][step][channel][valid_mode][vis_index_1]
            ):
                vis_index_2 = 0
            data.append(
                self.sequencer.sequences[midi][part][step][channel][valid_mode][vis_index_1][
                    vis_index_2
                ]
            )
        self.data_vis_top.data = data
        step = int(self.sequencer.settings[ValidSettings.V_STEP].get_value())
        pos_label = f"{show_as}|M{midi}|C{channel}|P{part:02}|{valid_mode.value}|S{step:02}|"
        self.pos_top_label.update(pos_label)

    def update_bottom(self) -> None:
        show_as = "Edit"
        if self.sequencer.settings[ValidSettings.COPY].get_ind() == 1:
            show_as = "From"
        midi, part, step, channel, valid_mode = self.sequencer.get_current_e_pos()
        data = []
        vis_index_1, vis_index_2 = self.sequencer.get_current_e_step_mode(
            valid_mode=valid_mode
        ).get_vis_ind()
        for step in range(1, self.internal_config.n_steps + 1):
            data.append(
                self.sequencer.sequences[midi][part][step][channel][valid_mode][vis_index_1][
                    vis_index_2
                ]
            )
        self.data_vis_bottom.data = data
        step = int(self.sequencer.settings[ValidSettings.V_STEP].get_value())
        pos_label = f"{show_as}|M{midi}|C{channel}|P{part:02}|{valid_mode.value}|S{step:02}|"
        self.pos_bottom_label.update(pos_label)

    def compose(self) -> ComposeResult:
        yield self.pos_top_label
        yield self.data_vis_top
        yield self.pos_bottom_label
        yield self.data_vis_bottom

    def update_all(self) -> None:
        self.update_top()
        self.update_bottom()

    def config_mode(self, key_ind: int) -> MFunctionality:
        valid_mode = ValidModes(str(self.sequencer.settings[ValidSettings.E_MODE].get_value()))
        mode = self.sequencer.modes[valid_mode]
        main_label = mode.get_vis_label()
        return (
            mode.new_with_off(off=main_label, ind=key_ind, exe=None)
            .new_with_off(off="Length", ind=0, exe=0)
            .new_with_off(off="Velocity", ind=0, exe=0)
        )

    def key_1(self):
        mode = self.config_mode(key_ind=0)
        self.sequencer.send_mode(mode=mode)
        self.update_all()

    def key_2(self):
        mode = self.config_mode(key_ind=1)
        self.sequencer.send_mode(mode=mode)
        self.update_all()
        if self.navigation_ui is not None:
            self.navigation_ui.update_all()

    def key_3(self):
        mode = self.config_mode(key_ind=2)
        self.sequencer.send_mode(mode=mode)
        self.update_all()
        if self.navigation_ui is not None:
            self.navigation_ui.update_all()

    def key_4(self):
        mode = self.config_mode(key_ind=3)
        self.sequencer.send_mode(mode=mode)
        self.update_all()
        if self.navigation_ui is not None:
            self.navigation_ui.update_all()

    def key_5(self):
        mode = self.config_mode(key_ind=4)
        self.sequencer.send_mode(mode=mode)
        self.update_all()
        if self.navigation_ui is not None:
            self.navigation_ui.update_all()

    def key_6(self):
        mode = self.config_mode(key_ind=5)
        self.sequencer.send_mode(mode=mode)
        self.update_all()
        if self.navigation_ui is not None:
            self.navigation_ui.update_all()

    def key_7(self):
        mode = self.config_mode(key_ind=6)
        self.sequencer.send_mode(mode=mode)
        self.update_all()
        if self.navigation_ui is not None:
            self.navigation_ui.update_all()

    def key_8(self):
        mode = self.config_mode(key_ind=7)
        self.sequencer.send_mode(mode=mode)
        main_label = mode.get_vis_label()
        mode_value = mode.get_single_value_by_lab(exe=0, lab=main_label)
        if mode_value == ValidButtons.NEXT:
            self.sequencer.get_current_proto_mode().update_offsets_with_lab(
                lab=main_label, by=self.internal_config.n_buttons
            )
            if self.navigation_ui is not None:
                self.navigation_ui.update_all()
        self.update_all()
        if self.navigation_ui is not None:
            self.navigation_ui.update_all()


class NavigationUI(Static):

    def __init__(
        self,
        sequencer: Engine,
    ):
        super().__init__()
        self.internal_config = InitConfig()
        self.sequencer = sequencer
        self.settings_vis = Label("")
        self.nav_vis = Label("")
        self.keys_vis = Label("")
        self.valid_nav: List[ValidNav] = [
            ValidNav.RECORD,
            ValidNav.COPY,
            ValidNav.VIEW,
            ValidNav.PLAY,
            ValidNav.TEMPO,
        ]
        self.nav_id = 0
        self.navigation = init_nav()
        self.keys_ui: Optional[KeysUI] = None
        self.nav_action: Dict[ValidButtons, Callable] = self.create_nav_actions()
        self.update_all()

    def compose(self) -> ComposeResult:
        yield self.settings_vis
        yield self.nav_vis
        yield self.keys_vis

    def create_nav_actions(self) -> Dict[ValidButtons, Callable]:
        nav_actions: Dict[ValidButtons, Callable] = dict()
        nav_actions[ValidButtons.EMPTY] = lambda: None
        nav_actions[ValidButtons.OPT_DOWN] = self.opt_down
        nav_actions[ValidButtons.OPT_UP] = self.opt_up
        nav_actions[ValidButtons.REC_ON] = self.record_on
        nav_actions[ValidButtons.REC_OFF] = self.record_off
        nav_actions[ValidButtons.VIEW_ON] = self.view_on
        nav_actions[ValidButtons.VIEW_ONLY] = self.view_only
        nav_actions[ValidButtons.VIEW_REC] = self.view_rec
        nav_actions[ValidButtons.VIEW_PLAY] = self.view_play
        nav_actions[ValidButtons.VIEW_OFF] = self.view_off
        nav_actions[ValidButtons.PLAY_ON] = self.play_on
        nav_actions[ValidButtons.PLAY_OFF] = self.play_off
        nav_actions[ValidButtons.MIDI] = self.next_midi
        nav_actions[ValidButtons.CHANNEL] = self.next_channel
        nav_actions[ValidButtons.PART] = self.next_part
        nav_actions[ValidButtons.MODE] = self.next_mode
        nav_actions[ValidButtons.DELETE] = self.delete_note
        nav_actions[ValidButtons.TEMPO_UP] = self.tempo_up
        nav_actions[ValidButtons.TEMPO_DOWN] = self.tempo_down
        nav_actions[ValidButtons.SKIP] = self.skip_step
        nav_actions[ValidButtons.COPY_ON] = self.copy_on
        nav_actions[ValidButtons.COPY_OFF] = self.copy_off
        nav_actions[ValidButtons.C_RANDOM] = self.copy_random
        nav_actions[ValidButtons.C_REVERSE] = self.copy_reverse
        nav_actions[ValidButtons.C_AS_IS] = self.copy_as_is
        nav_actions[ValidButtons.LENGTH] = self.next_length
        nav_actions[ValidButtons.VELOCITY] = self.next_velocity
        nav_actions[ValidButtons.PLAY_PART] = self.play_part
        nav_actions[ValidButtons.PLAY_PARTS] = self.play_parts
        nav_actions[ValidButtons.PLAY_ALL] = self.play_all
        return nav_actions

    def play_part(self) -> None:
        view = self.config_setting(ValidSettings.PLAY_FUNCTION, str(ValidButtons.PLAY_PARTS.value))
        self.sequencer.send_setting(view)

    def play_parts(self) -> None:
        view = self.config_setting(ValidSettings.PLAY_FUNCTION, str(ValidButtons.PLAY_PARTS.value))
        self.sequencer.send_setting(view)

    def play_all(self) -> None:
        view = self.config_setting(ValidSettings.PLAY_FUNCTION, str(ValidButtons.PLAY_ALL.value))
        self.sequencer.send_setting(view)

    def opt_up(self) -> None:
        self.nav_id += 1
        if self.nav_id >= len(self.valid_nav):
            self.nav_id = 0

    def opt_down(self) -> None:
        self.nav_id -= 1
        if self.nav_id < 0:
            self.nav_id = len(self.valid_nav) - 1

    def tempo_up(self) -> None:
        self.change_setting(valid_setting=ValidSettings.TEMPO, direction=1)
        self.sequencer.send_setting(setting=self.sequencer.settings[ValidSettings.TEMPO])

    def tempo_down(self) -> None:
        self.change_setting(valid_setting=ValidSettings.TEMPO, direction=-1)
        self.sequencer.send_setting(setting=self.sequencer.settings[ValidSettings.TEMPO])

    def delete_note(self) -> None:
        self.sequencer.send_delete()

    def skip_step(self) -> None:
        self.sequencer.send_next_step()

    def next_midi(self) -> None:
        setting = self.next_any(ValidSettings.E_MIDI_O)
        self.sequencer.send_setting(setting=setting)
        self.sequencer.send_reset_step()

    def next_channel(self) -> None:
        setting = self.next_any(ValidSettings.E_CHANNEL)
        self.sequencer.send_setting(setting=setting)
        self.sequencer.send_reset_step()

    def next_part(self) -> None:
        setting = self.next_any(ValidSettings.E_PART)
        self.sequencer.send_setting(setting=setting)
        self.sequencer.send_reset_step()

    def next_mode(self) -> None:
        setting = self.next_any(ValidSettings.E_MODE)
        self.sequencer.send_setting(setting=setting)
        self.sequencer.send_reset_step()

    def next_length(self) -> MFunctionality:
        return self.sequencer.get_current_proto_mode().update_offsets_with_lab(lab="Length", by=1)

    def next_velocity(self) -> MFunctionality:
        return self.sequencer.get_current_proto_mode().update_offsets_with_lab(lab="Velocity", by=1)

    def record_on(self) -> None:
        self.navigate(direction=1)
        record = self.config_setting(ValidSettings.RECORD, "On")
        self.sequencer.send_setting(record)

    def record_off(self) -> None:
        self.sequencer.send_reset_step()
        self.navigate(direction=-1)
        record = self.config_setting(ValidSettings.RECORD, "Off")
        self.sequencer.send_setting(record)

    def view_on(self) -> None:
        self.sequencer.send_reset_step()
        self.navigate(direction=1)
        view = self.config_setting(ValidSettings.VIEW_SHOW, "On")
        self.sequencer.send_setting(view)

    def view_only(self) -> None:
        self.sequencer.send_reset_step()
        view = self.config_setting(ValidSettings.VIEW_FUNCTION, str(ValidButtons.VIEW_ONLY.value))
        self.sequencer.send_setting(view)

    def view_rec(self) -> None:
        self.sequencer.send_reset_step()
        view = self.config_setting(ValidSettings.VIEW_FUNCTION, str(ValidButtons.VIEW_REC.value))
        self.sequencer.send_setting(view)

    def view_play(self) -> None:
        self.sequencer.send_reset_step()
        view_fun = self.config_setting(
            ValidSettings.VIEW_FUNCTION, str(ValidButtons.VIEW_PLAY.value)
        )
        self.sequencer.send_setting(view_fun)

    def view_off(self) -> None:
        self.sequencer.send_reset_step()
        self.navigate(direction=-1)
        view_show = self.config_setting(ValidSettings.VIEW_SHOW, "Off")
        self.sequencer.send_setting(view_show)

    def copy_on(self) -> None:
        self.sequencer.send_reset_step()
        self.navigate(direction=1)
        view = self.config_setting(ValidSettings.COPY, "On")
        self.sequencer.send_setting(view)

    def copy_off(self) -> None:
        self.sequencer.send_reset_step()
        self.navigate(direction=-1)
        view = self.config_setting(ValidSettings.COPY, "Off")
        self.sequencer.send_setting(view)

    def copy_random(self) -> None:
        f_midi, f_part, f_step, f_channel, f_mode = self.sequencer.get_current_e_pos()
        self.sequencer.send_copy(
            f_midi=f_midi,
            f_channel=f_channel,
            f_part=f_part,
            f_mode=f_mode,
            button=ValidButtons.C_RANDOM,
        )
        if self.keys_ui is not None:
            self.keys_ui.update_all()

    def copy_reverse(self) -> None:
        f_midi, f_part, f_step, f_channel, f_mode = self.sequencer.get_current_e_pos()
        self.sequencer.send_copy(
            f_midi=f_midi,
            f_channel=f_channel,
            f_part=f_part,
            f_mode=f_mode,
            button=ValidButtons.C_REVERSE,
        )
        if self.keys_ui is not None:
            self.keys_ui.update_all()

    def copy_as_is(self) -> None:
        f_midi, f_part, f_step, f_channel, f_mode = self.sequencer.get_current_e_pos()
        self.sequencer.send_copy(
            f_midi=f_midi,
            f_channel=f_channel,
            f_part=f_part,
            f_mode=f_mode,
            button=ValidButtons.C_AS_IS,
        )
        if self.keys_ui is not None:
            self.keys_ui.update_all()

    def play_on(self) -> None:
        self.navigate(direction=1)
        play = self.config_setting(ValidSettings.PLAY_SHOW, "On")
        self.sequencer.send_setting(play)

    def play_off(self) -> None:
        self.sequencer.stop_play()
        self.navigate(direction=-1)
        play = self.config_setting(ValidSettings.PLAY_SHOW, "Off")
        self.sequencer.send_setting(play)

    def next_any(self, valid_setting: ValidSettings) -> SFunctionality:
        return self.sequencer.settings[valid_setting].next_ind()

    def config_setting(self, valid_setting: ValidSettings, setting_value: str) -> SFunctionality:
        return self.sequencer.settings[valid_setting].set_value(setting_value)

    def update_all(self) -> None:
        self.update_settings_vis()
        self.update_nav_vis()
        self.update_keys_vis()

    def update_nav_vis(self) -> None:
        name, buttons = self.get_current_nav()
        text = "|"
        for button in buttons:
            text += f"{button[0:5]:>5}|"
        self.nav_vis.update(text)

    def update_keys_vis(self) -> None:
        mode = self.sequencer.get_current_new_mode()
        text = ""
        if "Length" in mode.get_labels():
            text += f"L:{mode.get_single_value_by_off(off='Length', ind=0)},"
        if "Velocity" in mode.get_labels():
            text += f"V:{mode.get_single_value_by_off(off='Velocity', ind=0)}|"
        vis_label = mode.get_vis_label()
        for j in range(self.internal_config.n_buttons):
            text += f"{mode.get_single_value_by_off(off=vis_label, ind=j)}|"
        self.keys_vis.update(text)

    def update_settings_vis(self) -> None:
        tempo_val = self.sequencer.settings[ValidSettings.TEMPO].get_value()
        all_labels, all_values = self.sequencer.get_sound_properties()
        text = f"|Temp:{int(tempo_val):03}|"
        for i in range(len(all_labels)):
            text += f"{all_labels[i][0:4]:>4}:{all_values[i]}|"
        self.settings_vis.update(text)

    def navigate(self, direction: int) -> None:
        current_nav = self.valid_nav[self.nav_id]
        self.navigation[current_nav].update_with_dir(direction=direction)

    def change_setting(self, valid_setting: ValidSettings, direction: int) -> SFunctionality:
        return self.sequencer.settings[valid_setting].change(direction=direction)

    def get_current_nav(self) -> Tuple[str, List[ValidButtons]]:
        current_nav = self.valid_nav[self.nav_id]
        navigation = self.navigation[current_nav]
        buttons = navigation.get_buttons(
            interval=self.internal_config.n_buttons,
        )
        return navigation.name, buttons

    def nav_1(self) -> None:
        button = self.get_current_nav()[1][0]
        self.nav_action[button]()
        self.update_all()
        if self.keys_ui is not None:
            self.keys_ui.update_all()

    def nav_2(self) -> None:
        button = self.get_current_nav()[1][1]
        self.nav_action[button]()
        self.update_all()
        if self.keys_ui is not None:
            self.keys_ui.update_all()

    def nav_3(self) -> None:
        button = self.get_current_nav()[1][2]
        self.nav_action[button]()
        self.update_all()
        if self.keys_ui is not None:
            self.keys_ui.update_all()

    def nav_4(self) -> None:
        button = self.get_current_nav()[1][3]
        self.nav_action[button]()
        self.update_all()
        if self.keys_ui is not None:
            self.keys_ui.update_all()

    def nav_5(self) -> None:
        button = self.get_current_nav()[1][4]
        self.nav_action[button]()
        self.update_all()
        if self.keys_ui is not None:
            self.keys_ui.update_all()

    def nav_6(self) -> None:
        button = self.get_current_nav()[1][5]
        self.nav_action[button]()
        self.update_all()
        if self.keys_ui is not None:
            self.keys_ui.update_all()

    def nav_7(self) -> None:
        button = self.get_current_nav()[1][6]
        self.nav_action[button]()
        self.update_all()
        if self.keys_ui is not None:
            self.keys_ui.update_all()

    def nav_8(self) -> None:
        button = self.get_current_nav()[1][7]
        self.nav_action[button]()
        self.update_all()
        if self.keys_ui is not None:
            self.keys_ui.update_all()
