import argparse

from midi_seq_txt.ui import UI


def main(blocking: bool = False) -> UI:
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    ui = UI(args)
    if blocking:
        ui.run()
    return ui


if __name__ == "__main__":
    main(blocking=True)
