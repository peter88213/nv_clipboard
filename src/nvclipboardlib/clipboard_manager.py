"""Provide a class to manage the novelibre tree view clipboard transfer.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/nv_clipboard
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
from xml.etree import ElementTree as ET

from novxlib.novx_globals import CHAPTER_PREFIX
from novxlib.novx_globals import CHARACTER_PREFIX
from novxlib.novx_globals import ITEM_PREFIX
from novxlib.novx_globals import LOCATION_PREFIX
from novxlib.novx_globals import PLOT_LINE_PREFIX
from novxlib.novx_globals import PLOT_POINT_PREFIX
from novxlib.novx_globals import PRJ_NOTE_PREFIX
from novxlib.novx_globals import SECTION_PREFIX


class ClipboardManager:

    def __init__(self, model, view, controller):
        self._mdl = model
        self._ui = view
        self._ctrl = controller

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
