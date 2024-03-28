import time

import pytest
from textual.pilot import Pilot

from midi_seq_txt.app import MSApp
from midi_seq_txt.cli import main


@pytest.mark.asyncio
async def test_record_and_copy(command_line_args):
    ms_app: MSApp = main(blocking=False)
    pilot: Pilot
    async with ms_app.run_test() as pilot:  # noqa
        time.sleep(1)
        await pilot.press("l")  # next keys
        time.sleep(1)
        await pilot.press("c")  # record on
        time.sleep(1)
        await pilot.press("d")  # delete step
        time.sleep(1)
        await pilot.press("7")  # part +
        time.sleep(1)
        await pilot.press("b")  # next length
        time.sleep(1)
        await pilot.press("e")  # key 1
        time.sleep(1)
        await pilot.press("f")  # key 2
        time.sleep(1)
        await pilot.press("l")  # next keys
        time.sleep(1)
        await pilot.press("a")  # exit record
        time.sleep(1)
        await pilot.press("b")  # copy
        time.sleep(1)
        await pilot.press("c")  # copy on
        time.sleep(1)
        await pilot.press("9")  # next mode
        time.sleep(1)
        await pilot.press("d")  # copy as is
        time.sleep(1)
    ms_app.sequencer.process.kill()


@pytest.mark.asyncio
async def test_tempo(command_line_args):
    ms_app: MSApp = main(blocking=False)
    pilot: Pilot
    async with ms_app.run_test() as pilot:  # noqa
        await pilot.press("b")  # copy
        time.sleep(1)
        await pilot.press("b")  # view
        time.sleep(1)
        await pilot.press("b")  # play
        time.sleep(1)
        await pilot.press("b")  # tempo
        time.sleep(1)
        await pilot.press("d")  # tempo up
        time.sleep(1)
        await pilot.press("c")  # tempo down
        time.sleep(1)
    ms_app.sequencer.process.kill()


@pytest.mark.asyncio
async def test_view(command_line_args):
    ms_app: MSApp = main(blocking=False)
    pilot: Pilot
    async with ms_app.run_test() as pilot:  # noqa
        await pilot.press("b")  # copy
        time.sleep(1)
        await pilot.press("b")  # view
        time.sleep(1)
        await pilot.press("c")  # view on
        time.sleep(1)
        await pilot.press("c")  # rec view
        time.sleep(1)
        await pilot.press("a")  # view off
    ms_app.sequencer.process.kill()
