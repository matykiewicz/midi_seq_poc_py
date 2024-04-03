import time

import pytest
from textual.pilot import Pilot

from midi_seq_txt.app import MSApp
from midi_seq_txt.cli import main


@pytest.mark.asyncio
async def test_record_and_scale(command_line_args):
    import midi_seq_txt.sequencer

    setattr(midi_seq_txt.sequencer, "DEBUG", True)
    ms_app: MSApp = main()
    pilot: Pilot
    async with ms_app.run_test() as pilot:  # noqa
        time.sleep(0.01)
        await pilot.press("9")  # next mode (Vo2)
        time.sleep(0.01)
        await pilot.press("9")  # next mode (Scale)
        time.sleep(0.01)
        await pilot.press("c")  # record on
        time.sleep(0.01)
        await pilot.press("l")  # next keys
        time.sleep(0.01)
        await pilot.press("e")  # key 1
        time.sleep(0.01)


@pytest.mark.asyncio
async def test_record_and_copy(command_line_args):
    import midi_seq_txt.sequencer

    setattr(midi_seq_txt.sequencer, "DEBUG", True)
    ms_app: MSApp = main()
    pilot: Pilot
    async with ms_app.run_test() as pilot:  # noqa
        await pilot.press("a")  # tempo
        time.sleep(0.01)
        await pilot.press("d")  # tempo +
        time.sleep(0.01)
        await pilot.press("d")  # tempo +
        time.sleep(0.01)
        await pilot.press("d")  # tempo +
        time.sleep(0.01)
        await pilot.press("d")  # tempo +
        time.sleep(0.01)
        await pilot.press("b")  # rec
        time.sleep(0.01)
        await pilot.press("l")  # next keys
        time.sleep(0.01)
        await pilot.press("d")  # skip step
        time.sleep(0.01)
        await pilot.press("c")  # record on
        time.sleep(0.01)
        await pilot.press("e")  # key 1
        time.sleep(0.01)
        await pilot.press("f")  # key 2
        time.sleep(0.01)
        await pilot.press("d")  # delete step
        time.sleep(0.01)
        await pilot.press("7")  # part +
        time.sleep(0.01)
        await pilot.press("b")  # next length
        time.sleep(0.01)
        await pilot.press("e")  # key 1
        time.sleep(0.01)
        await pilot.press("d")  # delete step
        time.sleep(0.01)
        await pilot.press("d")  # delete step
        time.sleep(0.01)
        await pilot.press("f")  # key 2
        time.sleep(0.01)
        await pilot.press("d")  # delete step
        time.sleep(0.01)
        await pilot.press("g")  # key 3
        time.sleep(0.01)
        await pilot.press("l")  # next keys
        time.sleep(0.01)
        await pilot.press("a")  # exit record
        time.sleep(0.01)
        await pilot.press("b")  # copy
        time.sleep(0.01)
        await pilot.press("d")  # empty
        time.sleep(0.01)
        await pilot.press("c")  # copy on
        time.sleep(0.01)
        await pilot.press("9")  # next mode
        time.sleep(0.01)
        await pilot.press("d")  # copy as is
        time.sleep(0.01)
        await pilot.press("b")  # copy random
        time.sleep(0.01)
        await pilot.press("c")  # copy reverse
        time.sleep(0.01)
        await pilot.press("a")  # exit copy
        time.sleep(0.01)
        await pilot.press("b")  # view
        time.sleep(0.01)
        await pilot.press("b")  # play
        time.sleep(0.01)
        await pilot.press("c")  # play on
        time.sleep(0.01)
        await pilot.press("d")  # play all
        time.sleep(0.01)
    time.sleep(1000.01)
    ms_app.sequencer.process.kill()


@pytest.mark.asyncio
async def test_tempo(command_line_args):
    import midi_seq_txt.sequencer

    setattr(midi_seq_txt.sequencer, "DEBUG", False)
    ms_app: MSApp = main()
    pilot: Pilot
    async with ms_app.run_test() as pilot:  # noqa
        await pilot.press("b")  # copy
        time.sleep(0.01)
        await pilot.press("b")  # view
        time.sleep(0.01)
        await pilot.press("b")  # play
        time.sleep(0.01)
        await pilot.press("b")  # tempo
        time.sleep(0.01)
        await pilot.press("d")  # tempo up
        time.sleep(0.01)
        await pilot.press("c")  # tempo down
        time.sleep(0.01)
    ms_app.sequencer.process.kill()


@pytest.mark.asyncio
async def test_view(command_line_args):
    import midi_seq_txt.sequencer

    setattr(midi_seq_txt.sequencer, "DEBUG", False)
    ms_app: MSApp = main()
    pilot: Pilot
    async with ms_app.run_test() as pilot:  # noqa
        await pilot.press("b")  # copy
        time.sleep(0.01)
        await pilot.press("b")  # view
        time.sleep(0.01)
        await pilot.press("c")  # view on
        time.sleep(0.01)
        await pilot.press("c")  # rec view
        time.sleep(0.01)
        await pilot.press("d")  # play view
        time.sleep(0.01)
        await pilot.press("a")  # view off
    ms_app.sequencer.process.kill()


@pytest.mark.asyncio
async def test_buttons(command_line_args):
    import midi_seq_txt.sequencer

    setattr(midi_seq_txt.sequencer, "DEBUG", False)
    ms_app: MSApp = main()
    pilot: Pilot
    async with ms_app.run_test() as pilot:  # noqa
        for binding in ms_app.BINDINGS:
            if isinstance(binding, tuple):
                await pilot.press(binding[0])  # play view
                time.sleep(0.01)
    ms_app.sequencer.process.kill()
