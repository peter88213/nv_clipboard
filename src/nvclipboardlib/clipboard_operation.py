"""Provide a class for a clipboard operation.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/nv_clipboard
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
from tkinter import ttk


class ClipboardOperation:

    def __init__(self, view, text, icon, shortcut, command):
        self._ui = view
        self._toolbarButton = ttk.Button(
            self._ui.toolbar.buttonBar,
            text=text,
            image=icon,
            command=command
            )
        self._toolbarButton.pack(side='left')
        self._toolbarButton.image = icon

        self._ui.tv.tree.bind(shortcut, command)

    def disable(self):
        self._toolbarButton.config(state='disabled')

    def enable(self):
        self._toolbarButton.config(state='normal')
