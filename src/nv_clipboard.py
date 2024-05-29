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
import gettext
import locale
import os
from pathlib import Path
import sys
from tkinter import ttk
import webbrowser
from xml.etree import ElementTree as ET

from novxlib.novx_globals import CHAPTER_PREFIX
from novxlib.novx_globals import CHARACTER_PREFIX
from novxlib.novx_globals import ITEM_PREFIX
from novxlib.novx_globals import LOCATION_PREFIX
from novxlib.novx_globals import PLOT_LINE_PREFIX
from novxlib.novx_globals import PLOT_POINT_PREFIX
from novxlib.novx_globals import PRJ_NOTE_PREFIX
from novxlib.novx_globals import SECTION_PREFIX
import tkinter as tk

# Initialize localization.
LOCALE_PATH = f'{os.path.dirname(sys.argv[0])}/locale/'
try:
    CURRENT_LANGUAGE = locale.getlocale()[0][:2]
except:
    # Fallback for old Windows versions.
    CURRENT_LANGUAGE = locale.getdefaultlocale()[0][:2]
try:
    t = gettext.translation('nv_clipboard', LOCALE_PATH, languages=[CURRENT_LANGUAGE])
    _ = t.gettext
except:

    def _(message):
        return message


class Plugin:
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
    API_VERSION = '4.3'
    DESCRIPTION = 'A clipboard plugin'
    URL = 'https://github.com/peter88213/nv_clipboard'
    _HELP_URL = f'https://peter88213.github.io/{_("nvhelp-en")}/nv_clipboard/'

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
        self._ui.helpMenu.add_command(label=_('Clipboard Online help'), command=lambda: webbrowser.open(self._HELP_URL))

        # Key bindings
        self._ui.tv.tree.bind('<Control-x>', self._cut_element)
        self._ui.tv.tree.bind('<Control-c>', self._copy_element)
        self._ui.tv.tree.bind('<Control-v>', self._paste_element)

        self._add_toolbar_buttons()

    def disable_menu(self):
        """Disable toolbar buttons when no project is open."""
        self._cutButton.config(state='disabled')
        self._copyButton.config(state='disabled')
        self._pasteButton.config(state='disabled')

    def enable_menu(self):
        """Enable toolbar buttons when a project is open."""
        self._cutButton.config(state='normal')
        self._copyButton.config(state='normal')
        self._pasteButton.config(state='normal')

    def _add_toolbar_buttons(self):
        prefs = self._ctrl.get_preferences()

        # Get the icons.
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

        # Separator.
        tk.Frame(self._ui.toolbar.buttonBar, bg='light gray', width=1).pack(side='left', fill='y', padx=4)

        # "Cut" button.
        self._cutButton = ttk.Button(
            self._ui.toolbar.buttonBar,
            text=_('Cut'),
            image=cutIcon,
            command=self._cut_element
            )
        self._cutButton.pack(side='left')
        self._cutButton.image = cutIcon

        # "Copy" button.
        self._copyButton = ttk.Button(
            self._ui.toolbar.buttonBar,
            text=_('Copy'),
            image=copyIcon,
            command=self._copy_element
            )
        self._copyButton.pack(side='left')
        self._copyButton.image = copyIcon

        # "Paste" button.
        self._pasteButton = ttk.Button(
            self._ui.toolbar.buttonBar,
            text=_('Paste'),
            image=pasteIcon,
            command=self._paste_element
            )
        self._pasteButton.pack(side='left')
        self._pasteButton.image = pasteIcon

    def _cut_element(self, event=None, elemPrefix=None):
        if self._ctrl.check_lock():
            return

        try:
            node = self._ui.tv.tree.selection()[0]
        except:
            return

        if self._copy_element(elemPrefix) is None:
            return

        if self._ui.tv.tree.prev(node):
            self._ui.tv.go_to_node(self._ui.tv.tree.prev(node))
        else:
            self._ui.tv.go_to_node(self._ui.tv.tree.parent(node))
        self._mdl.delete_element(node)
        return 'break'

    def _copy_element(self, event=None, elemPrefix=None):
        try:
            node = self._ui.tv.tree.selection()[0]
        except:
            return

        nodePrefix = node[:2]
        if elemPrefix is not None:
            if nodePrefix != elemPrefix:
                return

        elementContainers = {
            CHAPTER_PREFIX: self._mdl.novel.chapters,
            SECTION_PREFIX: self._mdl.novel.sections,
            PLOT_LINE_PREFIX: self._mdl.novel.plotLines,
            PLOT_POINT_PREFIX: self._mdl.novel.plotPoints,
            CHARACTER_PREFIX: self._mdl.novel.characters,
            LOCATION_PREFIX: self._mdl.novel.locations,
            ITEM_PREFIX: self._mdl.novel.items,
            PRJ_NOTE_PREFIX: self._mdl.novel.projectNotes
        }
        if not nodePrefix in elementContainers:
            return

        elem = elementContainers[nodePrefix][node]
        xmlElement = ET.Element(nodePrefix)
        elem.to_xml(xmlElement)
        self._remove_references(xmlElement)
        text = ET.tostring(xmlElement)
        # no utf-8 encoding here, because the text is escaped
        self._ui.root.clipboard_clear()
        self._ui.root.clipboard_append(text)
        self._ui.root.update()
        return 'break'

    def _paste_element(self, event=None, elemPrefix=None):
        if self._ctrl.check_lock():
            return

        try:
            node = self._ui.tv.tree.selection()[0]
        except:
            return

        try:
            text = self._ui.root.clipboard_get()
            xmlElement = ET.fromstring(text)
        except:
            return

        nodePrefix = xmlElement.tag
        if elemPrefix is not None:
            if nodePrefix != elemPrefix:
                return

        if nodePrefix == SECTION_PREFIX:
            typeStr = xmlElement.get('type', 0)
            if int(typeStr) > 1:
                elemCreator = self._mdl.add_stage
            else:
                elemCreator = self._mdl.add_section
            elemContainer = self._mdl.novel.sections
        else:
            elementControls = {
                CHAPTER_PREFIX: (self._mdl.add_chapter, self._mdl.novel.chapters),
                PLOT_LINE_PREFIX: (self._mdl.add_plot_line, self._mdl.novel.plotLines),
                PLOT_POINT_PREFIX: (self._mdl.add_plot_point, self._mdl.novel.plotPoints),
                CHARACTER_PREFIX: (self._mdl.add_character, self._mdl.novel.characters),
                LOCATION_PREFIX: (self._mdl.add_location, self._mdl.novel.locations),
                ITEM_PREFIX: (self._mdl.add_item, self._mdl.novel.items),
                PRJ_NOTE_PREFIX: (self._mdl.add_project_note, self._mdl.novel.projectNotes)
            }
            if not nodePrefix in elementControls:
                return

            elemCreator, elemContainer = elementControls[nodePrefix]

        newNode = elemCreator(targetNode=node)
        if not newNode:
            return

        elemContainer[newNode].from_xml(xmlElement)
        self._ctrl.refresh_views()
        self._ui.tv.go_to_node(newNode)
        return 'break'

    def _remove_references(self, xmlElement):
        references = [
            'Characters',
            'Locations',
            'Items',
            'PlotlineNotes',
            'Sections',
            'Section',
        ]
        for ref in references:
            for xmlRef in xmlElement.findall(ref):
                xmlElement.remove(xmlRef)
