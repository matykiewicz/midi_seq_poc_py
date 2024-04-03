import sys
from typing import List

import pytest


@pytest.fixture
def command_line_args(tmpdir) -> List[str]:
    sys.argv = [__file__]
    sys.argv.append("-d")
    sys.argv.append(str(tmpdir))
    return sys.argv
