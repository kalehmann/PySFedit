#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2018 by Karsten Lehmann <mail@kalehmann.de>
#
#    This file is part of PySFedit.
#
#    PySFedit is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    PySFedit is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    long with PySFedit. If not, see <http://www.gnu.org/licenses/>.

"""
This module provides a dialog for editing unicode descriptions of glyphs
in a pc screen font.
"""

import re
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

from . import psflib

class TextRow(Gtk.ListBoxRow):
    TYPE_SINGLE_VALUE = 0
    TYPE_SEQUENCE = 1
    """A simple row for a list box containing text.a

    Args:
        text (str): The text the row should contain
        _type (int): The type of the content of the row. Whether
                 it is a single unicode value or a sequence
                 of unicode values.
        index (int): The index of the content of the row in the
                 unicode description
    """
    def __init__(self, payload):
        Gtk.ListBoxRow.__init__(self)
        self.box = Gtk.Box()
        self.add(self.box)

        self.payload = payload
        self.label = Gtk.Label(label=str(payload))
        self.box.pack_start(self.label, True, True, 0)

    def update_label(self):
        self.label.set_text(str(self.payload))


class EditUnicodeDescriptionDialog(Gtk.Dialog):

    REGEX_VALUES_FULL = re.compile(r"^(\\u[a-fA-F0-9]{4}(,\s*)*)*$")
    REGEX_VALUES = re.compile(r"(\\u(?P<value>[a-fA-F0-9]{4}))")

    PAGE_HR = 0
    PAGE_VALUES = 1
    """
    A dialog for editing unicode descriptions.

    This dialog allows the user to enter unicode values for an  glyph.
    Optionally the input of unicode sequences can be enable by calling
    set_allow_entering_sequences(True) on the context.

    Args:
        parent (Gtk.Window): The toplevel gtk window
        description (psflib.UnicodeDescription): The unicode description
            to edit
        context (GlyphSelectorContext): The context of the parent glyph
            selector
    """
    def __init__(self, parent, description, context):
        Gtk.Dialog.__init__(self, transient_for=parent)
        self.set_default_size(200,200)
        self.set_title(_("Edit unicode description"))
        self.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.OK, Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL)
        self.connect("response", self.__on_response)

        self.description = psflib.UnicodeDescription()
        self.old_description = description
        self.__copy_desc(description, self.description)

        self.context = context

        box = Gtk.Box()
        self.get_content_area().pack_start(box, True, True, 0)

        descriptions_wrapper = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL)
        box_buttons = Gtk.Box()
        descriptions_wrapper.pack_start(box_buttons, False, False, 0)
        # Button add
        self.btn_add = Gtk.Button.new_from_icon_name(
            'list-add', Gtk.IconSize.BUTTON)
        self.btn_add.connect("clicked", self.__on_btn_add_clicked)
        box_buttons.pack_start(self.btn_add, False, False, 0)
        # Button remove
        self.btn_remove = Gtk.Button.new_from_icon_name(
            'list-remove', Gtk.IconSize.BUTTON)
        self.btn_remove.connect("clicked", self.__on_btn_remove_clicked)
        self.btn_remove.set_sensitive(
            bool(len(description.unicode_values)) or
            bool(len(description.sequences))
        )
        box_buttons.pack_start(self.btn_remove, False, False, 0)
        # Button up
        self.btn_up = Gtk.Button.new_from_icon_name(
            'go-up', Gtk.IconSize.BUTTON)
        self.btn_up.connect("clicked", self.__on_btn_up_clicked)
        box_buttons.pack_start(self.btn_up, False, False, 0)
        # Button down
        self.btn_down = Gtk.Button.new_from_icon_name(
            'go-down', Gtk.IconSize.BUTTON)
        self.btn_down.connect("clicked", self.__on_btn_down_clicked)
        box_buttons.pack_start(self.btn_down, False, False, 0)
        # Listbox with all descriptions
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_min_content_width(100)
        self.lb_descriptions = Gtk.ListBox()
        self.lb_descriptions.set_selection_mode(
            Gtk.SelectionMode.SINGLE)
        self.lb_descriptions.connect('row-selected',
            self.__on_row_selected)
        scrolled_window.add(self.lb_descriptions)
        descriptions_wrapper.pack_start(scrolled_window, True, True, 0)
        box.pack_start(descriptions_wrapper, False, False, 0)

        values = self.description.unicode_values
        sequences = self.description.sequences
        for value in values:
            row = TextRow(value)
            self.lb_descriptions.add(row)
        for sequence in sequences:
            row = TextRow(sequence)
            self.lb_descriptions.add(row)

        editor_wrapper = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.pack_end(editor_wrapper, True, True, 2)
        self.nb_editor = Gtk.Notebook()
        editor_wrapper.pack_start(self.nb_editor, True, True, 0)
        page_hr = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        # Entry for human readable input
        self.entry_unicode = Gtk.Entry()
        self.entry_unicode.set_sensitive(bool(
            self.lb_descriptions.get_children()))
        page_hr.pack_start(self.entry_unicode, True, True, 0)
        self.nb_editor.append_page(
            page_hr,
            Gtk.Label.new_with_mnemonic(_("_Human readable")))

        page_values = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        # Entry for values
        self.entry_values = Gtk.Entry()
        self.entry_values.set_sensitive(bool(
            self.lb_descriptions.get_children()))
        page_values.pack_start(self.entry_values, True, True, 0)
        self.nb_editor.append_page(
            page_values,
            Gtk.Label.new_with_mnemonic(_("_Values")))
        # Label for error in user input
        self.label_error = Gtk.Label()
        editor_wrapper.pack_start(self.label_error, True, True, 0)
        # Button for saving
        self.btn_save = Gtk.Button.new_with_label(_("Save"))
        self.btn_save.set_image(Gtk.Image.new_from_icon_name(
            'document-save', Gtk.IconSize.BUTTON))
        self.btn_save.set_always_show_image(True)
        self.btn_save.connect("clicked", self.__on_btn_save_clicked)
        editor_wrapper.pack_start(self.btn_save, True, True, 0)

        # Select the first row
        if description.unicode_values:
            first_row = self.lb_descriptions.get_row_at_index(0)
            self.lb_descriptions.select_row(first_row)

        self.nb_editor.connect('switch-page',
            self.__on_nb_editor_switch_page)

        self.show_all()

    def __copy_desc(self, first, second):
        values = first.codepoints
        seqs = first.seq_codepoints

        second.unicode_values = [psflib.UnicodeValue(v) for v in values]
        second.sequences = [psflib.UnicodeSequence(s) for s in seqs]

    def __update_description(self, row, user_input):
        """Update a value or sequence of the unicode description.

        Args:
            old: A string/integer or list containg the unicode value or
                sequence to replace
            new: A string/integer or list containg the new unicode value
                or sequence
        """
        payload = row.payload
        if type(payload) == psflib.UnicodeValue:
            if isinstance(user_input, str):
                payload.value = ord(user_input)
            elif isinstance(user_input, int):
                payload.value = user_input
            elif len(user_input) == 1:
                payload.value = user_input[0]
            else:
                self.description.unicode_values.remove(payload)
                payload = psflib.UnicodeSequence([psflib.UnicodeValue(v) for v in user_input])
                row.payload = payload
                self.description.add_sequence(payload)
            row.update_label()
            return

        if not isinstance(user_input, (int, str)) and len(user_input) > 1:
            payload.values = [psflib.UnicodeValue(v) for v in user_input]
            row.update_label()

            return

        self.description.sequences.remove(payload)
        payload = psflib.UnicodeValue(0)
        row.payload = payload

        if isinstance(user_input, str):
            payload.value = ord(user_input)
        elif isinstance(user_input, int):
            payload.value = user_input
        else:
            payload.value = user_input[0]
        row.update_label()
        self.description.add_unicode_value(payload.value)

    def __on_btn_save_clicked(self, button):
        """Gets called when the user clicks the button to save an
        entered unicode value or sequence.

        Args:
            button (Gtk.Button): The save button
        """
        row = self.lb_descriptions.get_selected_row()

        if not row:

            return

        if (self.nb_editor.get_current_page() == self.PAGE_HR):
            user_input = self.entry_unicode.get_text()
            if len(user_input) == 1:
                self.label_error.set_markup('')
                self.__update_description(row, user_input)
                self.entry_values.set_text('\\u%04x' % ord(user_input))

                return
            self.label_error.set_markup(
                '<span fgcolor="#FF0000">' +
                _('Error, must be a single letter') +
                '</span>'
            )

            return

        if self.nb_editor.get_current_page() == self.PAGE_VALUES:
            user_input = self.entry_values.get_text()
            if None == self.REGEX_VALUES_FULL.match(user_input):
                self.label_error.set_markup(
                    '<span fgcolor="#FF0000">' +
                    _('Error, can not parse unicode values') +
                    '</span>'
                )

                return

            values = [int(m[1], 16)
                for m in self.REGEX_VALUES.findall(user_input)]

            if (len(values) > 1 and
                not self.context.get_allow_entering_sequences()):

                self.label_error.set_markup(
                    '<span fgcolor="#FF0000">' +
                    _('Error, entering sequences is not enabled') +
                    '</span>'
                )

                return

            self.label_error.set_markup('')
            self.__update_description(row, values)
            row = self.lb_descriptions.get_selected_row()
            hr = psflib.get_str_form_unicode_sequence(values)
            self.entry_unicode.set_text(hr)

    def __on_btn_add_clicked(self, button):
        """This method gets called, when the user clicks the button
        for adding a new unicode description.

        Args:
            button (Gtk.Button): The add button
        """
        values = []
        for value in self.description.unicode_values:
            values.append(int(value))

        i = 0
        while i in values:
            i += 1
        value = psflib.UnicodeValue(i)
        self.description.add_unicode_value(value)
        row = TextRow(value)
        self.lb_descriptions.add(row)
        self.lb_descriptions.show_all()
        self.lb_descriptions.select_row(row)
        self.entry_unicode.set_sensitive(True)
        self.entry_values.set_sensitive(True)

        self.btn_remove.set_sensitive(True)

    def __on_btn_remove_clicked(self, button):
        """This method gets called, when the user clicks the button for
        removing an unicode description.

        Args:
            button (Gtk.Button): The remove button
        """
        row = self.lb_descriptions.get_selected_row()
        if not row:
            return

        index = row.get_index()
        if index > 0:
            next_row = self.lb_descriptions.get_row_at_index(index - 1)
        elif len(self.lb_descriptions.get_children()) > 1:
            # The row that will be deleted is the first row. Select the
            # second row.
            next_row = self.lb_descriptions.get_row_at_index(1)

        self.__remove_current_values()
        row.destroy()
        self.lb_descriptions.select_row(next_row)

        if not self.lb_descriptions.get_children():
            self.entry_unicode.set_text('')
            self.entry_unicode.set_sensitive(False)
            self.entry_values.set_text('')
            self.entry_values.set_sensitive(False)
            button.set_sensitive(False)

    def __on_btn_up_clicked(self, btn):
        """Gets called when the user clicks the button for moving an unicode
        description up.

        Args:
            button (Gtk.Button): The up button
        """
        row = self.lb_descriptions.get_selected_row()
        if not row:
            return

        index = row.get_index()
        if index < 1:
            return

        previous_row = self.lb_descriptions.get_row_at_index(index - 1)
        self.lb_descriptions.remove(previous_row)
        self.lb_descriptions.insert(previous_row, index)


    def __on_btn_down_clicked(self, btn):
        """Gets called when the user clicks the button for moving an unicode
        description down.

        Args:
            button (Gtk.Button): The down button
        """
        row = self.lb_descriptions.get_selected_row()
        if not row:
            return

        index = row.get_index()
        if index + 1 >= len(self.lb_descriptions.get_children()):
            return

        next_row = self.lb_descriptions.get_row_at_index(index + 1)
        self.lb_descriptions.remove(next_row)
        self.lb_descriptions.insert(next_row, index)


    def __on_nb_editor_switch_page(self, notebook, page, page_num):
        """This method gets called, when the user changes the page in
        the editor notebook.

        Args:
            notebook (Gtk.Notebook): The editor notebook
            page (Gtk.Widget): The newly selected page
            page_num (int): The index of the newly selected page
        """
        row = self.lb_descriptions.get_selected_row()
        self.__on_row_selected(self.lb_descriptions, row)

    def __remove_current_values(self):
        """Remove the unicode value/sequence referenced by the currently
        selected row.
        """
        row = self.lb_descriptions.get_selected_row()

        if not row:

            return
        payload= row.payload

        if type(payload) == psflib.UnicodeValue:
            self.description.unicode_values.remove(payload)
            return

        self.description.sequences.remove(payload)

    def __on_row_selected(self, listbox, row):
        """This method gets called when the selected row in the listbox
        with the descriptions changes.

        Args:
            listbox (Gtk.ListBox): The listbox with the descriptions
            row (Gtk.ListBoxRow): The newly selected row
        """
        if not row:
            return

        payload = row.payload
        values = ([int(payload)]
                    if type(payload) == psflib.UnicodeValue
                    else [int(v) for v in payload.values])
        v = ''
        for value in values:
            v += '\\u%04x, ' % value
        v = v[:-2] # Remove trailing comma

        self.entry_unicode.set_text(str(payload))
        self.entry_values.set_text(v)
        self.label_error.set_markup('')

    def __on_response(self, dialog, response_id):
        """This method gets called, when this dialog gets submited.

        Args:
            dialog (EditUnicodeDescriptionDialog): this dialog
            response_id: The id of the response type, see
                Gtk.ResponseTypes
        """
        if response_id != Gtk.ResponseType.OK:
            return

        self.__copy_desc(self.description, self.old_description)
