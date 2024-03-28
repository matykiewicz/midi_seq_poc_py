import argparse

from midi_seq_txt.app import MSApp


def main(blocking: bool = True) -> MSApp:
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    ui = MSApp(args)
    if blocking:
        ui.run()
    return ui


if __name__ == "__main__":
    main(blocking=True)
