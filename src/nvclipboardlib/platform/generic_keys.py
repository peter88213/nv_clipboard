"""Provide a class with key definitions.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/nv_clipboard
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
from nvclipboardlib.nvclipboard_globals import _


class GenericKeys:

    COPY = ('<Control-c>', f'{_("Ctrl")}-C')
    CUT = ('<Control-x>', f'{_("Ctrl")}-X')
    PASTE = ('<Control-v>', f'{_("Ctrl")}-V')
