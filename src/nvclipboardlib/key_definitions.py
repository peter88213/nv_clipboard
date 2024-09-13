"""Provide platform specific key definitions for the nv_clipboard plugin.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/nv_clipboard
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
from nvclipboardlib.nvclipboard_globals import PLATFORM
from nvclipboardlib.generic_keys import GenericKeys
from nvclipboardlib.mac_keys import MacKeys

if PLATFORM == 'win':
    KEYS = GenericKeys()
elif PLATFORM == 'ix':
    KEYS = GenericKeys()
elif PLATFORM == 'mac':
    KEYS = MacKeys()
else:
    KEYS = GenericKeys()
