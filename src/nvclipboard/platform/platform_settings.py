"""Provide platform specific key definitions for the nv_clipboard plugin.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/nv_clipboard
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
import platform

from nvclipboard.platform.generic_keys import GenericKeys
from nvclipboard.platform.mac_keys import MacKeys

if platform.system() == 'Windows':
    PLATFORM = 'win'
    KEYS = GenericKeys()
elif platform.system() in ('Linux', 'FreeBSD'):
    PLATFORM = 'ix'
    KEYS = GenericKeys()
elif platform.system() == 'Darwin':
    PLATFORM = 'mac'
    KEYS = MacKeys()
else:
    PLATFORM = ''
    KEYS = GenericKeys()
