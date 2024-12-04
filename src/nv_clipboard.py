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

from nvclipboard.clipboard_manager import ClipboardManager
from nvclipboard.nvclipboard_locale import _
from nvclipboard.platform.platform_settings import KEYS
from nvlib.controller.plugin.plugin_base import PluginBase
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
    API_VERSION = '5.0'
    DESCRIPTION = 'A clipboard plugin'
    URL = 'https://github.com/peter88213/nv_clipboard'
    HELP_URL = f'{_("https://peter88213.github.io/nvhelp-en")}/nv_clipboard/'

    def cut_element(self):
        self.clipboardManager.cut_element()

    def copy_element(self):
        self.clipboardManager.copy_element()

    def disable_menu(self):
        """Disable toolbar buttons when no project is open.
        
        Overrides the superclass method.
        """
        self.cutButton.config(state='disabled')
        self.copyButton.config(state='disabled')
        self.pasteButton.config(state='disabled')

    def enable_menu(self):
        """Enable toolbar buttons when a project is open.
        
        Overrides the superclass method.
        """
        self.cutButton.config(state='normal')
        self.copyButton.config(state='normal')
        self.pasteButton.config(state='normal')

    def install(self, model, view, controller):
        """Install the plugin.
        
        Positional arguments:
            model -- reference to the main model instance of the application.
            view -- reference to the main view instance of the application.
            controller -- reference to the main controller instance of the application.

        Optional arguments:
            prefs -- deprecated. Please use controller.get_preferences() instead.
        
        Extends the superclass method.
        """
        super().install(model, view, controller)

        # Add an entry to the Help menu.
        self._ui.helpMenu.add_command(label=_('Clipboard Online help'), command=self.open_help_page)

        # Set up the clipboard manager.
        self.clipboardManager = ClipboardManager(model, view, controller)

        # Bind Keyboard events.
        self._ui.tv.tree.bind(KEYS.CUT[0], self.cut_element)
        self._ui.tv.tree.bind(KEYS.COPY[0], self.copy_element)
        self._ui.tv.tree.bind(KEYS.PASTE[0], self.paste_element)

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
            cutIcon = tk.PhotoImage(file=f'{iconPath}/cut.png')
        except:
            cutIcon = None
        try:
            copyIcon = tk.PhotoImage(file=f'{iconPath}/copy.png')
        except:
            copyIcon = None
        try:
            pasteIcon = tk.PhotoImage(file=f'{iconPath}/paste.png')
        except:
            pasteIcon = None

        # Put a Separator on the toolbar.
        tk.Frame(self._ui.toolbar.buttonBar, bg='light gray', width=1).pack(side='left', fill='y', padx=4)

        # Put a "Cut" button on the toolbar.
        self.cutButton = ttk.Button(
            self._ui.toolbar.buttonBar,
            text=f"{_('Cut')} ({KEYS.CUT[1]})",
            image=cutIcon,
            command=self.cut_element
            )
        self.cutButton.pack(side='left')
        self.cutButton.image = cutIcon

        # Put a "Copy" button on the toolbar.
        self.copyButton = ttk.Button(
            self._ui.toolbar.buttonBar,
            text=f"{_('Copy')} ({KEYS.COPY[1]})",
            image=copyIcon,
            command=self.copy_element
            )
        self.copyButton.pack(side='left')
        self.copyButton.image = copyIcon

        # Put a "Paste" button on the toolbar.
        self.pasteButton = ttk.Button(
            self._ui.toolbar.buttonBar,
            text=f"{_('Paste')} ({KEYS.PASTE[1]})",
            image=pasteIcon,
            command=self.paste_element
            )
        self.pasteButton.pack(side='left')
        self.pasteButton.image = pasteIcon

        # Initialize tooltips.
        if not prefs['enable_hovertips']:
            return

        try:
            from idlelib.tooltip import Hovertip
        except ModuleNotFoundError:
            return

        Hovertip(self.cutButton, self.cutButton['text'])
        Hovertip(self.copyButton, self.copyButton['text'])
        Hovertip(self.pasteButton, self.pasteButton['text'])

    def lock(self):
        """Inhibit changes on the model.
        
        Overrides the superclass method.
        """
        self.cutButton.config(state='disabled')
        self.pasteButton.config(state='disabled')

    def on_close(self):
        """Actions to be performed when a project is closed."""
        self.disable_menu()

    def open_help_page(self):
        webbrowser.open(self.HELP_URL)

    def paste_element(self):
        self.clipboardManager.paste_element()

    def unlock(self):
        """Enable changes on the model.
        
        Overrides the superclass method.
        """
        self.cutButton.config(state='normal')
        self.pasteButton.config(state='normal')

