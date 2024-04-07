from argparse import Namespace

from textual.app import App, ComposeResult
from textual.widgets import Footer

from .engine import Engine
from .ui import KeysUI, NavigationUI


class MSApp(App):

    CSS_PATH = "app.tcss"
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
        self.sequencer = Engine(loc=args.dir)
        self.sequencer.detach()
        self.sequencer.init_data()
        self.keys_ui = KeysUI(sequencer=self.sequencer, loc=args.dir)
        self.navigation_ui = NavigationUI(sequencer=self.sequencer, loc=args.dir)
        self.navigation_ui.keys_ui = self.keys_ui
        self.keys_ui.navigation_ui = self.navigation_ui

    def compose(self) -> ComposeResult:
        yield self.keys_ui
        yield self.navigation_ui
        yield Footer()

    def action_nav_1(self) -> None:
        self.navigation_ui.nav_1()

    def action_nav_2(self) -> None:
        self.navigation_ui.nav_2()

    def action_nav_3(self) -> None:
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
