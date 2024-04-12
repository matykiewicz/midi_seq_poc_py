from typing import Callable, Dict, List, Optional, Tuple

from textual.app import ComposeResult
from textual.widgets import Label, Sparkline, Static

from .configs import InitConfig
from .const import ValidButtons, ValidNav, ValidSettings
from .engine import Engine
from .functionalities import MOutFunctionality, SFunctionality
from .init import create_notes, init_nav
from .presets import write_preset_type


class KeysUI(Static):

    def __init__(
        self,
        sequencer: Engine,
        loc: str,
    ):
        super().__init__()
        self.loc = loc
        self.internal_config = InitConfig()
        self.sequencer = sequencer
        self.pos_top_label = Label("")
        self.data_vis_top = Sparkline(data=[0] * self.internal_config.n_steps)
        self.pos_bottom_label = Label("")
        self.data_vis_bottom = Sparkline(data=[0] * self.internal_config.n_steps)
        self.mappings_label = Label("")
        self.mappings_label.add_class("mappings")
        self.navigation_ui: Optional[NavigationUI] = None
        self.seq_step: int = 1
        self.update_all()

    def update_top(self) -> None:
        if not self.sequencer.current_step_id.empty():
            self.seq_step = self.sequencer.current_step_id.get()
        show_as = self.sequencer.settings[ValidSettings.VIEW_FUNCTION].get_value()
        if self.sequencer.settings[ValidSettings.COPY].get_ind() == 1:
            show_as = "To"
        midi, channel, part, step, valid_out_mode = self.sequencer.get_current_v_pos()
        data = []
        vis_index_1, vis_index_2 = self.sequencer.get_current_v_step_out_mode(
            valid_out_mode=valid_out_mode
        ).get_vis_ind()
        for step in range(1, self.internal_config.n_steps + 1):
            if vis_index_1 >= len(
                self.sequencer.sequences.data[midi][channel][part][step][valid_out_mode]
            ):
                vis_index_1 = 0
            if vis_index_2 >= len(
                self.sequencer.sequences.data[midi][channel][part][step][valid_out_mode][
                    vis_index_1
                ]
            ):
                vis_index_2 = 0
            data.append(
                self.sequencer.sequences.data[midi][channel][part][step][valid_out_mode][
                    vis_index_1
                ][vis_index_2]
            )
        self.data_vis_top.data = data
        step = int(self.sequencer.settings[ValidSettings.V_STEP].get_value())
        pos_label = (
            f"{show_as}|M{midi}|C{channel}|P{part:02}|S{step:02}|"
            f"{valid_out_mode}|{self.seq_step:02}"
        )
        self.pos_top_label.update(pos_label)

    def update_bottom(self) -> None:
        if not self.sequencer.current_step_id.empty():
            self.seq_step = self.sequencer.current_step_id.get()
        show_as = "Edit"
        if self.sequencer.settings[ValidSettings.COPY].get_ind() == 1:
            show_as = "From"
        midi, channel, part, step, valid_out_mode = self.sequencer.get_current_e_pos()
        data = []
        vis_index_1, vis_index_2 = self.sequencer.get_current_e_step_out_mode(
            valid_out_mode=valid_out_mode
        ).get_vis_ind()
        for step in range(1, self.internal_config.n_steps + 1):
            data.append(
                self.sequencer.sequences.data[midi][channel][part][step][valid_out_mode][
                    vis_index_1
                ][vis_index_2]
            )
        self.data_vis_bottom.data = data
        step = int(self.sequencer.settings[ValidSettings.E_STEP].get_value())
        pos_label = (
            f"{show_as}|M{midi}|C{channel}|P{part:02}|S{step:02}|"
            f"{valid_out_mode}|{self.seq_step:02}"
        )
        self.pos_bottom_label.update(pos_label)

    def update_mappings(self) -> None:
        text = ""
        edit_conn = self.sequencer.settings[ValidSettings.MAP_E_CONN].get_value()
        edit_on = (
            self.sequencer.settings[ValidSettings.PRESETS].get_value()
            == ValidButtons.PRESETS_E_MAP_ON
        )
        for i, conn in enumerate(self.sequencer.mappings.conns):
            out_in = "out" if conn.is_out else "in"
            port_id = self.sequencer.midi_id_to_port_id(conn.midi_id)
            cur_edit = "!" if edit_on and i == edit_conn else " "
            text += (
                f"{cur_edit} {out_in}:{conn.midi_id} -> N:'{conn.port_name}' C:{conn.channel} "
                f"I:{conn.instruments} -> {port_id if port_id > -1 else 'off'}\n"
            )

        text = text[:-1]
        self.mappings_label.update(text)

    def compose(self) -> ComposeResult:
        yield self.pos_top_label
        yield self.data_vis_top
        yield self.pos_bottom_label
        yield self.data_vis_bottom
        yield self.mappings_label

    def update_all(self) -> None:
        self.update_top()
        self.update_bottom()
        self.update_mappings()

    def config_out_mode(self, key_ind: int) -> MOutFunctionality:
        valid_out_mode = str(self.sequencer.settings[ValidSettings.E_O_MODE].get_value())
        out_mode = self.sequencer.out_modes[valid_out_mode]
        main_label = out_mode.get_vis_label()
        return (
            out_mode.new_with_lab(lab=main_label, sub_ind=key_ind, exe=None)
            .new_with_lab(lab="Length", sub_ind=0, exe=0)
            .new_with_lab(lab="Velocity", sub_ind=0, exe=0)
        )

    def key_1(self):
        out_mode = self.config_out_mode(key_ind=0)
        self.sequencer.send_out_mode(out_mode=out_mode)
        self.update_all()
        if self.navigation_ui is not None:
            self.navigation_ui.update_all()

    def key_2(self):
        out_mode = self.config_out_mode(key_ind=1)
        self.sequencer.send_out_mode(out_mode=out_mode)
        main_label = out_mode.get_vis_label()
        out_mode_value = out_mode.get_single_value_by_lab(exe=0, lab=main_label)
        if out_mode_value == ValidButtons.NEXT:
            self.sequencer.get_current_proto_mode().update_offsets_with_lab(
                lab=main_label, by=self.internal_config.n_buttons
            )
        self.update_all()
        if self.navigation_ui is not None:
            self.navigation_ui.update_all()

    def key_3(self):
        out_mode = self.config_out_mode(key_ind=2)
        self.sequencer.send_out_mode(out_mode=out_mode)
        main_label = out_mode.get_vis_label()
        out_mode_value = out_mode.get_single_value_by_lab(exe=0, lab=main_label)
        if out_mode_value == ValidButtons.NEXT:
            self.sequencer.get_current_proto_mode().update_offsets_with_lab(
                lab=main_label, by=self.internal_config.n_buttons
            )
        self.update_all()
        if self.navigation_ui is not None:
            self.navigation_ui.update_all()

    def key_4(self):
        out_mode = self.config_out_mode(key_ind=3)
        self.sequencer.send_out_mode(out_mode=out_mode)
        main_label = out_mode.get_vis_label()
        out_mode_value = out_mode.get_single_value_by_lab(exe=0, lab=main_label)
        if out_mode_value == ValidButtons.NEXT:
            self.sequencer.get_current_proto_mode().update_offsets_with_lab(
                lab=main_label, by=self.internal_config.n_buttons
            )
        self.update_all()
        if self.navigation_ui is not None:
            self.navigation_ui.update_all()

    def key_5(self):
        out_mode = self.config_out_mode(key_ind=4)
        self.sequencer.send_out_mode(out_mode=out_mode)
        main_label = out_mode.get_vis_label()
        out_mode_value = out_mode.get_single_value_by_lab(exe=0, lab=main_label)
        if out_mode_value == ValidButtons.NEXT:
            self.sequencer.get_current_proto_mode().update_offsets_with_lab(
                lab=main_label, by=self.internal_config.n_buttons
            )
        self.update_all()
        if self.navigation_ui is not None:
            self.navigation_ui.update_all()

    def key_6(self):
        out_mode = self.config_out_mode(key_ind=5)
        self.sequencer.send_out_mode(out_mode=out_mode)
        main_label = out_mode.get_vis_label()
        out_mode_value = out_mode.get_single_value_by_lab(exe=0, lab=main_label)
        if out_mode_value == ValidButtons.NEXT:
            self.sequencer.get_current_proto_mode().update_offsets_with_lab(
                lab=main_label, by=self.internal_config.n_buttons
            )
        self.update_all()
        if self.navigation_ui is not None:
            self.navigation_ui.update_all()

    def key_7(self):
        out_mode = self.config_out_mode(key_ind=6)
        self.sequencer.send_out_mode(out_mode=out_mode)
        main_label = out_mode.get_vis_label()
        out_mode_value = out_mode.get_single_value_by_lab(exe=0, lab=main_label)
        if out_mode_value == ValidButtons.NEXT:
            self.sequencer.get_current_proto_mode().update_offsets_with_lab(
                lab=main_label, by=self.internal_config.n_buttons
            )
        self.update_all()
        if self.navigation_ui is not None:
            self.navigation_ui.update_all()

    def key_8(self):
        out_mode = self.config_out_mode(key_ind=7)
        self.sequencer.send_out_mode(out_mode=out_mode)
        main_label = out_mode.get_vis_label()
        out_mode_value = out_mode.get_single_value_by_lab(exe=0, lab=main_label)
        if out_mode_value == ValidButtons.NEXT:
            self.sequencer.get_current_proto_mode().update_offsets_with_lab(
                lab=main_label, by=self.internal_config.n_buttons
            )
        self.update_all()
        if self.navigation_ui is not None:
            self.navigation_ui.update_all()


class NavigationUI(Static):

    def __init__(
        self,
        sequencer: Engine,
        loc: str,
    ):
        super().__init__()
        self.loc = loc
        self.internal_config = InitConfig()
        self.sequencer = sequencer
        self.settings_vis = Label("")
        self.name_vis = Label("")
        self.nav_vis = Label("")
        self.keys_vis = Label("")
        self.valid_nav: List[ValidNav] = [
            ValidNav.RECORD,
            ValidNav.COPY,
            ValidNav.VIEW,
            ValidNav.PLAY,
            ValidNav.TEMPO,
            ValidNav.PRESETS,
        ]
        self.nav_id = 0
        self.navigation = init_nav()
        self.keys_ui: Optional[KeysUI] = None
        self.nav_action: Dict[ValidButtons, Callable] = self.create_nav_actions()
        self.update_all()

    def compose(self) -> ComposeResult:
        yield self.name_vis
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
        nav_actions[ValidButtons.O_MODE] = self.next_out_mode
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
        nav_actions[ValidButtons.SCALE] = self.next_scale
        nav_actions[ValidButtons.PLAY_PART] = self.play_part
        nav_actions[ValidButtons.PLAY_PARTS] = self.play_parts
        nav_actions[ValidButtons.PLAY_ALL] = self.play_all
        nav_actions[ValidButtons.PRESETS_OFF_MUSIC] = self.presets_off_music
        nav_actions[ValidButtons.PRESETS_OFF_MAP] = self.presets_off_map
        nav_actions[ValidButtons.PRESETS_ON_MUSIC] = self.presets_on_music
        nav_actions[ValidButtons.PRESETS_ON_MAP] = self.presets_on_map
        nav_actions[ValidButtons.PRESETS_N_MUSIC] = self.next_music_name
        nav_actions[ValidButtons.PRESETS_N_MAP] = self.next_map_name
        nav_actions[ValidButtons.PRESETS_L_MUSIC] = self.load_music
        nav_actions[ValidButtons.PRESETS_L_MAP] = self.load_map
        nav_actions[ValidButtons.PRESETS_S_MUSIC] = self.save_music
        nav_actions[ValidButtons.PRESETS_S_MAP] = self.save_map
        nav_actions[ValidButtons.PRESETS_E_MAP_ON] = self.edit_map_on
        nav_actions[ValidButtons.PRESETS_E_MAP_OFF] = self.edit_map_off
        nav_actions[ValidButtons.PRESETS_E_MAP_N_CONN] = self.edit_next_conn
        nav_actions[ValidButtons.PRESETS_E_MAP_N_MIDI] = self.edit_next_midi
        nav_actions[ValidButtons.PRESETS_E_MAP_N_DIR] = self.edit_next_dir
        nav_actions[ValidButtons.PRESETS_E_MAP_N_CH] = self.edit_next_channel
        nav_actions[ValidButtons.PRESETS_E_MAP_N_PNAME] = self.edit_next_port_name
        nav_actions[ValidButtons.PRESETS_E_MAP_N_INSTR_1] = self.edit_next_instr_1
        nav_actions[ValidButtons.PRESETS_E_MAP_N_INSTR_2] = self.edit_next_instr_2
        return nav_actions

    def presets_on_music(self) -> None:
        self.navigate(direction=1)
        presets = self.config_setting(
            ValidSettings.PRESETS, str(ValidButtons.PRESETS_ON_MUSIC.value)
        )
        self.sequencer.send_setting(presets)

    def presets_on_map(self) -> None:
        self.navigate(direction=2)
        presets = self.config_setting(ValidSettings.PRESETS, str(ValidButtons.PRESETS_ON_MAP.value))
        self.sequencer.send_setting(presets)

    def presets_off_music(self) -> None:
        self.navigate(direction=-1)
        presets = self.config_setting(
            ValidSettings.PRESETS, str(ValidButtons.PRESETS_OFF_MUSIC.value)
        )
        self.sequencer.send_setting(presets)

    def presets_off_map(self) -> None:
        self.navigate(direction=-2)
        presets = self.config_setting(
            ValidSettings.PRESETS, str(ValidButtons.PRESETS_OFF_MAP.value)
        )
        self.sequencer.send_setting(presets)

    def load_music(self) -> None:
        presets = self.config_setting(
            ValidSettings.PRESETS, str(ValidButtons.PRESETS_L_MUSIC.value)
        )
        self.sequencer.send_setting(presets)

    def save_music(self) -> None:
        music_name = str(self.sequencer.settings[ValidSettings.MUS_NAME].get_value())
        self.sequencer.sequences.name = music_name
        write_preset_type(preset=self.sequencer.sequences, loc=self.loc)
        presets = self.config_setting(
            ValidSettings.PRESETS, str(ValidButtons.PRESETS_S_MUSIC.value)
        )
        self.sequencer.send_setting(presets)

    def load_map(self) -> None:
        presets = self.config_setting(ValidSettings.PRESETS, str(ValidButtons.PRESETS_L_MAP.value))
        self.sequencer.send_setting(presets)

    def save_map(self) -> None:
        map_name = str(self.sequencer.settings[ValidSettings.MAP_NAME].get_value())
        self.sequencer.mappings.name = map_name
        write_preset_type(preset=self.sequencer.mappings, loc=self.loc)
        presets = self.config_setting(ValidSettings.PRESETS, str(ValidButtons.PRESETS_S_MAP.value))
        self.sequencer.send_setting(presets)

    def edit_map_on(self) -> None:
        self.navigate(direction=1)
        presets = self.config_setting(
            ValidSettings.PRESETS, str(ValidButtons.PRESETS_E_MAP_ON.value)
        )
        self.sequencer.send_setting(presets)

    def edit_map_off(self) -> None:
        self.navigate(direction=-1)
        presets = self.config_setting(
            ValidSettings.PRESETS, str(ValidButtons.PRESETS_E_MAP_OFF.value)
        )
        self.sequencer.send_setting(presets)

    def edit_next_conn(self) -> None:
        self.change_setting(valid_setting=ValidSettings.MAP_E_CONN, direction=1)
        self.sequencer.send_setting(setting=self.sequencer.settings[ValidSettings.MAP_E_CONN])

    def edit_next_midi(self) -> None:
        self.change_setting(valid_setting=ValidSettings.MAP_E_MIDI, direction=1)
        self.sequencer.send_setting(setting=self.sequencer.settings[ValidSettings.MAP_E_MIDI])

    def edit_next_dir(self) -> None:
        self.change_setting(valid_setting=ValidSettings.MAP_E_DIR, direction=1)
        self.sequencer.send_setting(setting=self.sequencer.settings[ValidSettings.MAP_E_DIR])

    def edit_next_channel(self) -> None:
        self.change_setting(valid_setting=ValidSettings.MAP_E_CH, direction=1)
        self.sequencer.send_setting(setting=self.sequencer.settings[ValidSettings.MAP_E_CH])

    def edit_next_port_name(self) -> None:
        self.change_setting(valid_setting=ValidSettings.MAP_E_PNAME, direction=1)
        self.sequencer.send_setting(setting=self.sequencer.settings[ValidSettings.MAP_E_PNAME])

    def edit_next_instr_1(self) -> None:
        self.change_setting(valid_setting=ValidSettings.MAP_E_INSTR_1, direction=1)
        self.sequencer.send_setting(setting=self.sequencer.settings[ValidSettings.MAP_E_INSTR_1])

    def edit_next_instr_2(self) -> None:
        self.change_setting(valid_setting=ValidSettings.MAP_E_INSTR_2, direction=1)
        self.sequencer.send_setting(setting=self.sequencer.settings[ValidSettings.MAP_E_INSTR_2])

    def next_music_name(self) -> None:
        self.change_setting(valid_setting=ValidSettings.MUS_NAME, direction=1)
        self.sequencer.send_setting(setting=self.sequencer.settings[ValidSettings.MUS_NAME])

    def next_map_name(self) -> None:
        self.change_setting(valid_setting=ValidSettings.MAP_NAME, direction=1)
        self.sequencer.send_setting(setting=self.sequencer.settings[ValidSettings.MAP_NAME])

    def play_part(self) -> None:
        play = self.config_setting(ValidSettings.PLAY_FUNCTION, str(ValidButtons.PLAY_PARTS.value))
        self.sequencer.send_setting(play)

    def play_parts(self) -> None:
        play = self.config_setting(ValidSettings.PLAY_FUNCTION, str(ValidButtons.PLAY_PARTS.value))
        self.sequencer.send_setting(play)

    def play_all(self) -> None:
        play = self.config_setting(ValidSettings.PLAY_FUNCTION, str(ValidButtons.PLAY_ALL.value))
        self.sequencer.send_setting(play)

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
        if (
            self.sequencer.settings[ValidSettings.VIEW_SHOW].get_ind() == 1
            or self.sequencer.settings[ValidSettings.COPY].get_ind()
        ):
            setting = self.next_v_pos(ValidSettings.V_MIDI_O)
        else:
            setting = self.next_e_pos(ValidSettings.E_MIDI_O)
        self.sequencer.send_setting(setting=setting)
        self.sequencer.send_reset_step()

    def next_channel(self) -> None:
        if (
            self.sequencer.settings[ValidSettings.VIEW_SHOW].get_ind() == 1
            or self.sequencer.settings[ValidSettings.COPY].get_ind()
        ):
            setting = self.next_v_pos(ValidSettings.V_CHANNEL)
        else:
            setting = self.next_e_pos(ValidSettings.E_CHANNEL)
        self.sequencer.send_setting(setting=setting)
        self.sequencer.send_reset_step()

    def next_part(self) -> None:
        if (
            self.sequencer.settings[ValidSettings.VIEW_SHOW].get_ind() == 1
            or self.sequencer.settings[ValidSettings.COPY].get_ind()
        ):
            setting = self.next_v_pos(ValidSettings.V_PART)
        else:
            setting = self.next_e_pos(ValidSettings.E_PART)
        self.sequencer.send_setting(setting=setting)
        self.sequencer.send_reset_step()

    def next_out_mode(self) -> None:
        if (
            self.sequencer.settings[ValidSettings.VIEW_SHOW].get_ind() == 1
            or self.sequencer.settings[ValidSettings.COPY].get_ind()
        ):
            setting = self.next_v_pos(ValidSettings.V_O_MODE)
        else:
            setting = self.next_e_pos(ValidSettings.E_O_MODE)
        self.sequencer.send_setting(setting=setting)
        self.sequencer.send_reset_step()

    def next_length(self) -> MOutFunctionality:
        return self.sequencer.get_current_proto_mode().update_offsets_with_lab(lab="Length", by=1)

    def next_velocity(self) -> MOutFunctionality:
        return self.sequencer.get_current_proto_mode().update_offsets_with_lab(lab="Velocity", by=1)

    def next_scale(self) -> MOutFunctionality:
        out_mode = self.sequencer.get_current_proto_mode().update_offsets_with_lab(
            lab="Scale", by=1
        )
        scale = out_mode.get_single_value_by_off(off="Scale", ind=0)
        out_mode = self.sequencer.get_current_proto_mode().set_data_with_lab(
            lab="Note", data=create_notes(scale=scale)
        )
        return out_mode

    def record_on(self) -> None:
        self.navigate(direction=1)
        record = self.config_setting(ValidSettings.RECORD, ValidButtons.ON)
        self.sequencer.send_setting(record)

    def record_off(self) -> None:
        self.sequencer.send_reset_step()
        self.navigate(direction=-1)
        record = self.config_setting(ValidSettings.RECORD, ValidButtons.OFF)
        self.sequencer.send_setting(record)

    def view_on(self) -> None:
        self.sequencer.send_reset_step()
        self.navigate(direction=1)
        view = self.config_setting(ValidSettings.VIEW_SHOW, ValidButtons.ON)
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
        view_show = self.config_setting(ValidSettings.VIEW_SHOW, ValidButtons.OFF)
        self.sequencer.send_setting(view_show)

    def copy_on(self) -> None:
        self.sequencer.send_reset_step()
        self.navigate(direction=1)
        view = self.config_setting(ValidSettings.COPY, ValidButtons.ON)
        self.sequencer.send_setting(view)

    def copy_off(self) -> None:
        self.sequencer.send_reset_step()
        self.navigate(direction=-1)
        view = self.config_setting(ValidSettings.COPY, ValidButtons.OFF)
        self.sequencer.send_setting(view)

    def copy_random(self) -> None:
        f_midi, f_channel, f_part, f_step, f_out_mode = self.sequencer.get_current_e_pos()
        self.sequencer.send_copy(
            f_midi=f_midi,
            f_channel=f_channel,
            f_part=f_part,
            f_out_mode=f_out_mode,
            button=ValidButtons.C_RANDOM,
        )
        if self.keys_ui is not None:
            self.keys_ui.update_all()

    def copy_reverse(self) -> None:
        f_midi, f_channel, f_part, f_step, f_out_mode = self.sequencer.get_current_e_pos()
        self.sequencer.send_copy(
            f_midi=f_midi,
            f_channel=f_channel,
            f_part=f_part,
            f_out_mode=f_out_mode,
            button=ValidButtons.C_REVERSE,
        )
        if self.keys_ui is not None:
            self.keys_ui.update_all()

    def copy_as_is(self) -> None:
        f_midi, f_channel, f_part, f_step, f_out_mode = self.sequencer.get_current_e_pos()
        self.sequencer.send_copy(
            f_midi=f_midi,
            f_channel=f_channel,
            f_part=f_part,
            f_out_mode=f_out_mode,
            button=ValidButtons.C_AS_IS,
        )
        if self.keys_ui is not None:
            self.keys_ui.update_all()

    def play_on(self) -> None:
        self.navigate(direction=1)
        play = self.config_setting(ValidSettings.PLAY_SHOW, ValidButtons.ON)
        self.sequencer.send_setting(play)

    def play_off(self) -> None:
        self.navigate(direction=-1)
        play_fun = self.config_setting(ValidSettings.PLAY_FUNCTION, ValidButtons.NA)
        self.sequencer.send_setting(play_fun)
        play_show = self.config_setting(ValidSettings.PLAY_SHOW, ValidButtons.OFF)
        self.sequencer.send_setting(play_show)

    def next_e_pos(self, valid_setting: ValidSettings) -> SFunctionality:
        next_setting = self.sequencer.next_e_pos(valid_setting=valid_setting)
        if next_setting is not None:
            return next_setting
        else:
            raise ValueError("Next position was not found")

    def next_v_pos(self, valid_setting: ValidSettings) -> SFunctionality:
        next_setting = self.sequencer.next_v_pos(valid_setting=valid_setting)
        if next_setting is not None:
            return next_setting
        else:
            raise ValueError("Next position was not found")

    def config_setting(self, valid_setting: ValidSettings, setting_value: str) -> SFunctionality:
        return self.sequencer.settings[valid_setting].set_value(setting_value)

    def update_all(self) -> None:
        self.update_name_vis()
        self.update_settings_vis()
        self.update_nav_vis()
        self.update_keys_vis()

    def update_nav_vis(self) -> None:
        name, buttons = self.get_current_nav()
        text = "|"
        for button in buttons:
            text += f"{button[0:5]:>5}|"
        self.nav_vis.update(text)

    def update_name_vis(self) -> None:
        text = "|"
        setting = self.sequencer.settings[ValidSettings.PRESETS]
        mus_edit = self.sequencer.settings[ValidSettings.RECORD].get_value() == ValidButtons.ON
        map_edit = (
            self.sequencer.settings[ValidSettings.PRESETS].get_value()
            == ValidButtons.PRESETS_E_MAP_ON
        )
        mus_loaded_edit = "!" if mus_edit else "*"
        map_loaded_edit = "!" if map_edit else "*"
        loaded_map_name = self.sequencer.mappings.name
        loaded_mus_name = self.sequencer.sequences.name
        current_mus_name = self.sequencer.settings[ValidSettings.MUS_NAME].get_value()
        current_map_name = self.sequencer.settings[ValidSettings.MAP_NAME].get_value()
        mus_loaded_edit = mus_loaded_edit if current_mus_name == loaded_mus_name else " "
        map_loaded_edit = map_loaded_edit if current_map_name == loaded_map_name else " "
        if setting.get_value() in [
            ValidButtons.PRESETS_OFF_MUSIC,
            ValidButtons.PRESETS_ON_MUSIC,
            ValidButtons.PRESETS_S_MUSIC,
            ValidButtons.PRESETS_L_MUSIC,
        ]:
            text += f"{mus_loaded_edit}Mus: {current_mus_name}|"
        elif setting.get_value() in [
            ValidButtons.PRESETS_ON_MAP,
            ValidButtons.PRESETS_OFF_MAP,
            ValidButtons.PRESETS_L_MAP,
            ValidButtons.PRESETS_S_MAP,
            ValidButtons.PRESETS_E_MAP_ON,
            ValidButtons.PRESETS_E_MAP_OFF,
        ]:
            text += f"{mus_loaded_edit}Map: {current_map_name}|"
        else:
            text += "___: ___ |"
        self.name_vis.update(text)

    def update_keys_vis(self) -> None:
        out_mode = self.sequencer.get_current_new_out_mode()
        text = "|"
        if "Length" in out_mode.get_labels():
            text += f"L:{out_mode.get_single_value_by_off(off='Length', ind=0)},"
        if "Velocity" in out_mode.get_labels():
            text += f"V:{out_mode.get_single_value_by_off(off='Velocity', ind=0)},"
        if "Scale" in out_mode.get_labels():
            text += f"S:{out_mode.get_single_value_by_off(off='Scale', ind=0)}|"
        vis_label = out_mode.get_vis_label()
        for j in range(self.internal_config.n_buttons):
            text += f"{out_mode.get_single_value_by_off(off=vis_label, ind=j)}|"
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
