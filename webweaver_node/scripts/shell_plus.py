#!/bin/env python3

import IPython
from traitlets.config import Config


c = Config()
c.InteractiveShellApp.exec_lines = [
    'from shell_plus_config import init',
    'ipython = get_ipython()',
    'await init(ipython.user_ns)'
]

IPython.start_ipython(argv=[], config=c)