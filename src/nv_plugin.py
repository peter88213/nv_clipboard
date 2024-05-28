"""Plugin template for novelibre.

Requires Python 3.6+
Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/nv_plugin
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
"""
import sys
import os
import tkinter as tk
import locale
import gettext
import webbrowser
from nvlib.plugin.plugin_base import PluginBase

# Initialize localization.
LOCALE_PATH = f'{os.path.dirname(sys.argv[0])}/locale/'
try:
    CURRENT_LANGUAGE = locale.getlocale()[0][:2]
except:
    # Fallback for old Windows versions.
    CURRENT_LANGUAGE = locale.getdefaultlocale()[0][:2]
try:
    t = gettext.translation('nv_plugin', LOCALE_PATH, languages=[CURRENT_LANGUAGE])
    _ = t.gettext
except:

    def _(message):
        return message


class Plugin(PluginBase):
    """Template plugin class.
    
    Public class constants:
        VERSION: str -- Version string.
        API_VERSION: str -- API compatibility indicator.
        DESCRIPTION: str -- Description to be diplayed in the novelibre plugin list.
        URL: str -- Plugin project homepage URL.

    Public instance variables:
        filePath: str -- Location of the installed plugin.
        isActive: Boolean -- Acceptance flag.
        isRejected: Boolean --  Rejection flag.
    """
    VERSION = '@release'
    API_VERSION = '4.0'
    DESCRIPTION = 'Plugin template'
    URL = 'https://github.com/peter88213/nv_plugin'
    _HELP_URL = f'https://peter88213.github.io/{_("nvhelp-en")}/nv_plugin/usage'

    def install(self, model, view, controller, prefs):
        """Install the plugin.
        
        Positional arguments:
            model -- reference to the main model instance of the application.
            view -- reference to the main view instance of the application.
            controller -- reference to the main controller instance of the application.
            prefs -- reference to the application's global dictionary with settings and options.
        """
        self._mdl = model
        self._ui = view
        self._ctrl = controller

        # Add an entry to the Help menu.
        self._ui.helpMenu.add_command(label=_('nv_plugin Online help'), command=lambda: webbrowser.open(self._HELP_URL))

