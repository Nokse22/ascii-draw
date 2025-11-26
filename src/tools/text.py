# text.py
#
# Copyright 2023-2025 Nokse
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Gtk
from gi.repository import GObject

import pyfiglet
import emoji

from .tool import Tool


class Text(Tool):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style = 0

        self.canvas.drag_gesture.connect("drag-begin", self.on_drag_begin)
        self.canvas.drag_gesture.connect("drag-update", self.on_drag_follow)
        self.canvas.drag_gesture.connect("drag-end", self.on_drag_end)

        self.canvas.click_gesture.connect("pressed", self.on_click_pressed)

        builder = Gtk.Builder.new_from_resource("/io/github/nokse22/asciidraw/ui/text_sidebar.ui")
        self._sidebar = builder.get_object("text_stack_page")
        self.text_entry_buffer = builder.get_object("text_entry_buffer")
        self.enter_button = builder.get_object("enter_button")
        self.transparent_check = builder.get_object("transparent_check")
        self.vertical_check = builder.get_object("vertical_check")
        self.text_sidebar_stack = builder.get_object("text_sidebar_stack")

        self.font_button = builder.get_object("font_button")
        self.font_box = builder.get_object("font_box")
        self.font_cancel_button = builder.get_object("font_cancel_button")
        self.font_select_button = builder.get_object("font_select_button")

        self.font_list = [
            "Normal", "3x5", "avatar", "big", "bell", "briteb",
            "bubble", "bulbhead", "chunky", "contessa", "computer",
            "crawford", "cricket", "cursive", "cyberlarge", "cybermedium",
            "cybersmall", "digital", "doom", "double", "drpepper",
            "eftifont", "eftirobot", "eftitalic", "eftiwall", "eftiwater",
            "fourtops", "fuzzy", "gothic", "graceful", "graffiti", "invita",
            "italic", "lcd", "letters", "linux", "lockergnome", "madrid",
            "maxfour", "mike", "mini", "morse", "ogre", "puffy", "rectangles",
            "rowancap", "script", "serifcap", "shadow", "shimrod", "short",
            "slant", "slide", "slscript", "small", "smisome1", "smkeyboard",
            "smscript", "smshadow", "smslant", "speed", "stacey", "weird",
            "stampatello", "standard", "stop", "straight", "thin", "wavy",
            "threepoint", "times", "tombstone", "tinker-toy", "twopoint"
        ]

        self.selected_font = "Normal"

        for font in self.font_list:
            if font == "Normal":
                text = "font 123"
            else:
                text = pyfiglet.figlet_format("font 123", font=font)
            font_text_view = Gtk.Label(css_classes=["font-preview"], name=font)

            font_text_view.set_label(text)
            self.font_box.append(font_text_view)

        self.start_x = 0
        self.start_y = 0

        self.x_mul = 12
        self.y_mul = 24

        self.text_x = 0
        self.text_y = 0

        self.drag_x = 0
        self.drag_y = 0

        self.drag_start_x = 0
        self.drag_start_y = 0

        self._text = ''

        self.selected_font = "Normal"

        self._transparent = False

        self.previous_font = self.font_box.get_first_child()

        self.font_box.select_row(self.previous_font)

        self.insert_text_signal = self.text_entry_buffer.connect("insert-text", self.on_text_inserted)
        self.text_entry_buffer.connect_after("changed", self.preview_text)
        self.enter_button.connect("activated", self.insert_text)
        self.text_entry_buffer.bind_property("text", self, "text")
        self.transparent_check.bind_property("active", self, "transparent")
        self.vertical_check.connect("notify::active", self.preview_text)

        self.font_button.connect("clicked", self.show_font_selection)
        self.font_box.connect("row-selected", self.font_row_selected)
        self.font_cancel_button.connect("clicked", self.cancel_font_selection)
        self.font_select_button.connect("clicked", self.select_font_selection)

        self._sidebar.bind_property("visible", self, "active")

    def set_selected_font(self, value):
        self.selected_font = value

    def get_sidebar(self):
        return self.sidebar

    @GObject.Property(type=str, default='#')
    def style(self):
        return self._style

    @style.setter
    def style(self, value):
        self._style = value
        self.notify('style')

    @GObject.Property(type=bool, default=False)
    def transparent(self):
        return self._transparent

    @transparent.setter
    def transparent(self, value):
        self._transparent = value
        self.notify('transparent')

    @GObject.Property(type=str, default='')
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        self.notify('text')

    def on_drag_begin(self, gesture, start_x, start_y):
        if not self._active: return

        self.drag_start_x = start_x
        self.drag_start_y = start_y

    def on_drag_follow(self, gesture, x, y):
        if not self._active: return

        self.drag_x = int((x + self.drag_start_x) // self.x_mul - self.drag_start_x// self.x_mul)
        self.drag_y = int((y + self.drag_start_y) // self.y_mul - self.drag_start_y// self.y_mul)

        self.canvas.clear_preview()
        self.preview_text()

    def on_drag_end(self, gesture, delta_x, delta_y):
        if not self._active: return

        self.text_x += self.drag_x
        self.text_y += self.drag_y

        self.drag_x = 0
        self.drag_y = 0

    def on_click_pressed(self, click, arg, x, y):
        if not self._active: return

        self.text_x = int(x / self.x_mul)
        self.text_y = int(y / self.y_mul)

        self.canvas.clear_preview()
        self.preview_text()

    def insert_text(self, *args):
        self.canvas.add_undo_action(_("Text"))
        self.canvas.clear_preview()

        text = self._text
        if self.vertical_check.get_active():
            text = "\n".join(text)
        if self.selected_font != "Normal":
            text = pyfiglet.figlet_format(text, font=self.selected_font)

        self.canvas.draw_text(self.text_x + self.drag_x, self.text_y + self.drag_y, text, self._transparent, True)
        self.canvas.update()

    def preview_text(self, *args):
        self.canvas.clear_preview()

        text = self._text
        if self.vertical_check.get_active():
            text = "\n".join(text)
        if self.selected_font != "Normal":
            text = pyfiglet.figlet_format(text, font=self.selected_font)

        self.canvas.draw_text(self.text_x + self.drag_x, self.text_y + self.drag_y, text, self._transparent, False)

        self.canvas.update_preview()

    def font_row_selected(self, list_box, row):
        self.set_selected_font(list_box.get_selected_row().get_child().get_name())
        self.preview_text()

    def on_text_inserted(self, buffer, loc, text, length):
        self.text_entry_buffer.handler_block(self.insert_text_signal)

        filtered = emoji.replace_emoji(text, replace="")

        if filtered != text:
            buffer.stop_emission("insert-text")

            mark = buffer.create_mark(None, loc, left_gravity=True)
            iter_at_mark = buffer.get_iter_at_mark(mark)

            buffer.insert(iter_at_mark, filtered)

            buffer.delete_mark(mark)

        self.text_entry_buffer.handler_unblock(self.insert_text_signal)

    def show_font_selection(self, *args):
        self.text_sidebar_stack.set_visible_child_name("font_chooser")

        self.previous_font = self.font_box.get_selected_row()

    def cancel_font_selection(self, *args):
        self.text_sidebar_stack.set_visible_child_name("main_sidebar")

        self.font_box.select_row(self.previous_font)

    def select_font_selection(self, *args):
        self.text_sidebar_stack.set_visible_child_name("main_sidebar")
