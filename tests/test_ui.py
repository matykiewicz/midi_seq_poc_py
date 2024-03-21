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
        await pilot.press("c")
        time.sleep(1)
        await pilot.press("d")
        time.sleep(1)
        await pilot.press("e")
        time.sleep(1)
        await pilot.press("f")
        time.sleep(1)
        await pilot.press("c")
        time.sleep(1)
        await pilot.press("d")
        time.sleep(1)
        await pilot.press("g")
        time.sleep(1)
    for midi in ui.midis.keys():
        ui.midis[midi].process.kill()
