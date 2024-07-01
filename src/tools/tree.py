# tree.py
#
# Copyright 2023 Nokse
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

from gi.repository import Adw
from gi.repository import Gtk
from gi.repository import Gdk, Gio, GObject

import pyfiglet
import emoji

from .tool import Tool

class Tree(Tool):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.canvas.drag_gesture.connect("drag-begin", self.on_drag_begin)
        self.canvas.drag_gesture.connect("drag-update", self.on_drag_follow)
        self.canvas.drag_gesture.connect("drag-end", self.on_drag_end)

        self.canvas.click_gesture.connect("pressed", self.on_click_pressed)
        self.canvas.click_gesture.connect("released", self.on_click_released)
        self.canvas.click_gesture.connect("stopped", self.on_click_stopped)

        builder = Gtk.Builder.new_from_resource("/io/github/nokse22/asciidraw/ui/tree_sidebar.ui")
        self._sidebar = builder.get_object("tree_stack_page")
        self.text_entry_buffer = builder.get_object("text_entry_buffer")
        self.enter_button = builder.get_object("enter_button")

        self.start_x = 0
        self.start_y = 0

        self.x_mul = 12
        self.y_mul = 24

        self.tree_x = 0
        self.tree_y = 0

        self.drag_x = 0
        self.drag_y = 0

        self._text = ""

        self.selected_font = "Normal"

        self._transparent = False

        self.text_entry_buffer.connect_after("insert-text", self.on_text_inserted)
        self.text_entry_buffer.connect("changed", self.preview)
        self.enter_button.connect("clicked", self.insert)
        self.text_entry_buffer.bind_property("text", self, "text")

    def set_selected_font(self, value):
        self.selected_font = value

    @GObject.Property(type=str, default="")
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        self.notify('text')

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
        self.preview()

    def on_drag_end(self, gesture, delta_x, delta_y):
        if not self._active: return

        self.tree_x += self.drag_x
        self.tree_y += self.drag_y

        self.drag_x = 0
        self.drag_y = 0

    def on_click_pressed(self, click, arg, x, y):
        if not self._active: return

        x_char = int(x / self.x_mul)
        y_char = int(y / self.y_mul)

        self.tree_x = x_char
        self.tree_y = y_char

        self.canvas.clear_preview()
        self.preview()

    def on_click_stopped(self, click):
        if not self._active: return
        pass

    def on_click_released(self, click, arg, x, y):
        if not self._active: return
        pass

    def preview(self, *args):
        if not self._active: return
        self.canvas.clear_preview()
        self.draw_tree(self.tree_x + self.drag_x, self.tree_y + self.drag_y, False)
        self.canvas.update_preview()

    def insert(self, *args):
        self.canvas.add_undo_action(_("Tree"))
        self.canvas.clear_preview()
        self.draw_tree(self.tree_x, self.tree_y, True)
        self.canvas.update()

    def draw_tree(self, tree_x, tree_y, draw):
        lines = self._text.split("\n")
        processed_lines = []
        current_indent = 0
        leading_spaces = []
        indent_level = 0
        for index, line in enumerate(lines):
            stripped_line = line.lstrip(' ')  # Remove leading underscores
            indent_space = len(line) - len(stripped_line)
            line_number = len(leading_spaces)
            if line_number > 0:
                if indent_space > leading_spaces[-1]:
                    indent_level = current_indent + 1
                elif indent_space == leading_spaces[-1]:
                    indent_level = current_indent
                else:
                    previos_spaces = 0
                    indent_level = current_indent - 1
                    for i in range(line_number - 1, 0, -1):
                        # print(indent_level, indent_space, leading_spaces[i])
                        if i != 0:
                            leading_spaces[i] #previous spaces
                            indent_space # current spaces
                            if leading_spaces[i] < indent_space:
                                break
                            if leading_spaces[i] < previos_spaces:
                                indent_level -= 1
                                previos_spaces = leading_spaces[i]
                            elif leading_spaces[i] > previos_spaces:
                                indent_level = processed_lines[i - line_number][0]
                                previos_spaces = leading_spaces[i]
            current_indent = indent_level
            leading_spaces.append(indent_space)
            processed_lines.append([indent_level, stripped_line])

        tree_structure = ""

        y = tree_y
        for index, (indent, text) in enumerate(processed_lines):
            x = tree_x + (indent) * 4
            self.canvas.draw_text(x, y, text, False, draw)
            if indent != 0:
                self.canvas.set_char_at(x - 1, y, " ", draw)
                self.canvas.set_char_at(x - 2, y, self.canvas.bottom_horizontal(), draw)
                self.canvas.set_char_at(x - 3, y, self.canvas.bottom_horizontal(), draw)
                self.canvas.set_char_at(x - 4, y, self.canvas.bottom_left(), draw)

                prev_index = index - 1
                while processed_lines[prev_index][0] != processed_lines[index][0] - 1:
                    if prev_index < 0:
                        break
                    if processed_lines[prev_index][0] == processed_lines[index][0]:
                        self.canvas.set_char_at(x - 4, y - (index - prev_index), self.canvas.right_intersect(), draw)
                    else:
                        self.canvas.set_char_at(x - 4, y - (index - prev_index), self.canvas.left_vertical(), draw)
                    prev_index -= 1
            y += 1

    def on_text_inserted(self, buffer, loc, text, length):
        if emoji.is_emoji(text):
            start_iter = loc.copy()
            start_iter.backward_char()
            buffer.delete(start_iter ,loc)
            buffer.insert(start_iter, "X")
            return
        spaces = 0
        if text == "\n":
            start_iter = loc.copy()
            start_iter.backward_char()
            start_iter.set_line_offset(0)
            end_iter = start_iter.copy()
            start_iter.backward_char()
            while not end_iter.ends_line():
                start_iter.forward_char()
                end_iter.forward_char()
                char = buffer.get_text(start_iter, end_iter, False)
                if char != " ":
                    break
                spaces += 1
            indentation = " " * spaces
            buffer.insert(loc, f"{indentation}")
        elif text == "\t":
            start_iter = loc.copy()
            start_iter.backward_char()
            buffer.delete(start_iter ,loc)
            buffer.insert(start_iter, " ")

        self.preview()
