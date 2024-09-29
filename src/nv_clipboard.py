"""Plugin template for novelibre.

Requires Python 3.6+
Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/nv_clipboard
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
from pathlib import Path
from tkinter import ttk
import webbrowser

from nvclipboardlib.nvclipboard_globals import _
from nvclipboardlib.clipboard_manager import ClipboardManager
from nvclipboardlib.platform.platform_settings import KEYS
from nvlib.plugin.plugin_base import PluginBase
import tkinter as tk


class Plugin(PluginBase):
    """Clipboard plugin class.
    
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
    API_VERSION = '4.11'
    DESCRIPTION = 'A clipboard plugin'
    URL = 'https://github.com/peter88213/nv_clipboard'
    _HELP_URL = f'https://peter88213.github.io/{_("nvhelp-en")}/nv_clipboard/'

    def disable_menu(self):
        """Disable toolbar buttons when no project is open.
        
        Overrides the superclass method.
        """
        # self._cut.disable()
        self._copyButton.disable()
        self._pasteButton.disable()

    def enable_menu(self):
        """Enable toolbar buttons when a project is open.
        
        Overrides the superclass method.
        """
        # self._cut.enable()
        self._copyButton.enable()
        self._pasteButton.enable()

    def install(self, model, view, controller, prefs=None):
        """Install the plugin.
        
        Positional arguments:
            model -- reference to the main model instance of the application.
            view -- reference to the main view instance of the application.
            controller -- reference to the main controller instance of the application.

        Optional arguments:
            prefs -- deprecated. Please use controller.get_preferences() instead.
        
        Overrides the superclass method.
        """

        # Add an entry to the Help menu.
        view.helpMenu.add_command(label=_('Clipboard Online help'), command=lambda: webbrowser.open(self._HELP_URL))

        # Set up the clipboard manager.
        clipboardManager = ClipboardManager(model, view, controller)

        # Bind Keyboard events.
        view.tv.tree.bind(KEYS.COPY[0], clipboardManager._copy_element)
        view.tv.tree.bind(KEYS.PASTE[0], clipboardManager._paste_element)

        # Configure the toolbar.

        # Get the icons.
        prefs = controller.get_preferences()
        if prefs.get('large_icons', False):
            size = 24
        else:
            size = 16
        try:
            homeDir = str(Path.home()).replace('\\', '/')
            iconPath = f'{homeDir}/.novx/icons/{size}'
        except:
            iconPath = None
        try:
            copyIcon = tk.PhotoImage(file=f'{iconPath}/copy.png')
        except:
            copyIcon = None
        try:
            pasteIcon = tk.PhotoImage(file=f'{iconPath}/paste.png')
        except:
            pasteIcon = None

        # Put a Separator on the toolbar.
        tk.Frame(view.toolbar.buttonBar, bg='light gray', width=1).pack(side='left', fill='y', padx=4)

        # Put a "Copy" button on the toolbar.
        self._copyButton = ttk.Button(
            view.toolbar.buttonBar,
            text=f"{_('Copy')} ({KEYS.COPY[1]})",
            image=copyIcon,
            command=clipboardManager._copy_element
            )
        self._copyButton.pack(side='left')
        self._copyButton.image = copyIcon

        # Put a "Paste" button on the toolbar.
        self._pasteButton = ttk.Button(
            view.toolbar.buttonBar,
            text=f"{_('Paste')} ({KEYS.PASTE[1]})",
            image=pasteIcon,
            command=clipboardManager._paste_element
            )
        self._pasteButton.pack(side='left')
        self._pasteButton.image = pasteIcon

        # Initialize tooltips.
        if not prefs['enable_hovertips']:
            return

        try:
            from idlelib.tooltip import Hovertip
        except ModuleNotFoundError:
            return

        Hovertip(self._copyButton, self._copyButton['text'])
        Hovertip(self._pasteButton, self._pasteButton['text'])

    def lock(self):
        """Inhibit changes on the model.
        
        Overrides the superclass method.
        """
        # self._cutButton.disable()
        self._pasteButton.config(state='disabled')

    def unlock(self):
        """Enable changes on the model.
        
        Overrides the superclass method.
        """
        # self._cut.enable()
        self._pasteButton.config(state='normal')
