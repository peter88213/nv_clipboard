"""Provide a class with key definitions for the Mac OS.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/nv_clipboard
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
from nvclipboardlib.platform.generic_keys import GenericKeys


class MacKeys(GenericKeys):

    COPY = ('<Command-c>', 'Cmd-C')
    CUT = ('<Command-x>', 'Cmd-X')
    PASTE = ('<Command-v>', 'Cmd-V')
