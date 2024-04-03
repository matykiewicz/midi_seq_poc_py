import argparse

from midi_seq_txt.app import MSApp
from midi_seq_txt.presets import write_all_presets


def main() -> MSApp:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--command",
        "-c",
        choices=["app", "presets", "headless"],
        help="Main command to run (default: %(default)s)",
        default="headless",
    )
    parser.add_argument(
        "--dir",
        "-d",
        type=str,
        help="This software working directory (default: %(default)s)",
        default="./presets",
    )
    args = parser.parse_args()
    ui = MSApp(args)
    if args.command == "app":
        ui.run()
    elif args.command == "presets":
        write_all_presets(args)
        ui.sequencer.process.kill()
    return ui
