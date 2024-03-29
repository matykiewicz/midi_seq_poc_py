import time

import pytest
from textual.pilot import Pilot

from midi_seq_txt.cli import main
from midi_seq_txt.ui import UI


@pytest.mark.asyncio
async def test_ui(command_line_args):
    ui: UI = main(blocking=False)
    pilot: Pilot
    async with ui.run_test() as pilot:
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
        await pilot.press("b")  # view
        time.sleep(1)
        await pilot.press("b")  # play
        time.sleep(1)
        await pilot.press("b")  # tempo
        time.sleep(1)
        await pilot.press("d")  # tempo up
        time.sleep(1)
        await pilot.press("e")  # key 1
        time.sleep(1)
        await pilot.press("f")  # key 2
        time.sleep(1)
        await pilot.press("a")  # record off
        time.sleep(1)
        await pilot.press("b")  # option+
        time.sleep(1)
        await pilot.press("c")  # view on
        time.sleep(1)
        await pilot.press("7")  # part +
        time.sleep(1)
        await pilot.press("c")
        time.sleep(1)
        await pilot.press("d")
        time.sleep(1)
        await pilot.press("g")
        time.sleep(1)
    ui.sequencer.process.kill()
