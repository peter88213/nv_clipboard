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
        if self._mdl.prjFile is None:
            return

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
        if self._mdl.prjFile is None:
            return

        try:
            node = self._ui.tv.tree.selection()[0]
        except:
            return

        nodePrefix = node[:2]
        if elemPrefix is not None:
            if nodePrefix != elemPrefix:
                return

        elementContainers = {
            CHAPTER_PREFIX: (self._mdl.novel.chapters, 'CHAPTER'),
            SECTION_PREFIX: (self._mdl.novel.sections, 'SECTION'),
            PLOT_LINE_PREFIX: (self._mdl.novel.plotLines, 'ARC'),
            PLOT_POINT_PREFIX: (self._mdl.novel.plotPoints, 'POINT'),
            CHARACTER_PREFIX: (self._mdl.novel.characters, 'CHARACTER'),
            LOCATION_PREFIX: (self._mdl.novel.locations, 'LOCATION'),
            ITEM_PREFIX: (self._mdl.novel.items, 'ITEM'),
            PRJ_NOTE_PREFIX: (self._mdl.novel.projectNotes, 'PROJECTNOTE')
        }
        if not nodePrefix in elementContainers:
            return

        elementContainer, xmlTag = elementContainers[nodePrefix]
        element = elementContainer[node]
        xmlElement = ET.Element(xmlTag)
        element.to_xml(xmlElement)
        self._remove_references(xmlElement)

        # Get children, if any.
        if nodePrefix == CHAPTER_PREFIX:
            for scId in self._mdl.novel.tree.get_children(node):
                xmlSection = ET.SubElement(xmlElement, 'SECTION')
                self._mdl.novel.sections[scId].to_xml(xmlSection)
                self._remove_references(xmlSection)
        elif nodePrefix == PLOT_LINE_PREFIX:
            for ppId in self._mdl.novel.tree.get_children(node):
                xmlPlotPoint = ET.SubElement(xmlElement, 'POINT')
                self._mdl.novel.plotPoints[ppId].to_xml(xmlPlotPoint)
                self._remove_references(xmlPlotPoint)

        text = ET.tostring(xmlElement)
        # no utf-8 encoding here, because the text is escaped
        self._ui.root.clipboard_clear()
        self._ui.root.clipboard_append(text)
        self._ui.root.update()
        return 'break'

    def _paste_element(self, event=None, elemPrefix=None):
        if self._mdl.prjFile is None:
            return

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

        prefixes = {
            'CHAPTER': CHAPTER_PREFIX,
            'SECTION': SECTION_PREFIX,
            'ARC': PLOT_LINE_PREFIX,
            'POINT': PLOT_POINT_PREFIX,
            'CHARACTER': CHARACTER_PREFIX,
            'LOCATION': LOCATION_PREFIX,
            'ITEM': ITEM_PREFIX,
            'PROJECTNOTE': PRJ_NOTE_PREFIX
        }
        nodePrefix = prefixes.get(xmlElement.tag, None)
        if nodePrefix is None:
            return

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

        elemId = elemCreator(targetNode=node)
        if not elemId:
            return

        elemContainer[elemId].from_xml(xmlElement)

        # Get children, if any.
        if nodePrefix == CHAPTER_PREFIX:
            for xmlSection in xmlElement.iterfind('SECTION'):
                typeStr = xmlSection.get('type', 0)
                if int(typeStr) > 1:
                    scId = self._mdl.add_stage(targetNode=elemId)
                else:
                    scId = self._mdl.add_section(targetNode=elemId)
                self._mdl.novel.sections[scId].from_xml(xmlSection)
        elif nodePrefix == PLOT_LINE_PREFIX:
            for xmlPoint in xmlElement.iterfind('POINT'):
                ppId = self._mdl.add_plot_point(targetNode=elemId)
                self._mdl.novel.plotPoints[ppId].from_xml(xmlPoint)

        self._ctrl.refresh_views()
        self._ui.tv.go_to_node(elemId)
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
