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

class Tree(GObject.GObject):
    def __init__(self, _canvas, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.canvas = _canvas

        self._active = False
        self._style = 0

        self.canvas.drag_gesture.connect("drag-begin", self.on_drag_begin)
        self.canvas.drag_gesture.connect("drag-update", self.on_drag_follow)
        self.canvas.drag_gesture.connect("drag-end", self.on_drag_end)

        self.canvas.click_gesture.connect("pressed", self.on_click_pressed)
        self.canvas.click_gesture.connect("released", self.on_click_released)
        self.canvas.click_gesture.connect("stopped", self.on_click_stopped)

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

    def set_selected_font(self, value):
        self.selected_font = value

    @GObject.Property(type=bool, default=False)
    def active(self):
        return self._active

    @active.setter
    def active(self, value):
        self._active = value
        self.notify('active')

    @GObject.Property(type=str, default='#')
    def style(self):
        return self._style

    @style.setter
    def style(self, value):
        self._style = value
        self.notify('style')

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

    def on_drag_follow(self, gesture, x, y):
        if not self._active: return

        x_char = int(x / self.x_mul)
        y_char = int(y / self.y_mul)

        self.drag_x = x_char
        self.drag_y = y_char

        self.canvas.clear_preview()
        self.preview_tree()

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
        self.preview_tree()

    def on_click_stopped(self, click):
        if not self._active: return
        pass

    def on_click_released(self, click, arg, x, y):
        if not self._active: return
        pass

    def preview_tree(self):
        self.canvas.clear_preview()
        self.draw_tree(self.tree_x + self.drag_x, self.tree_y + self.drag_y, False)
        self.canvas.update_preview()

    def insert_tree(self):
        self.canvas.clear_preview()
        self.draw_tree(self.tree_x, self.tree_y, True)
        self.canvas.update()

    def draw_tree(self, start_x, start_y, draw):
        lines = self._text.split("\n")
        processed_lines = []
        current_indent = 0
        leading_spaces = []
        indent_level = 0
        # print("------tree------")
        for index, line in enumerate(lines):
            # print("------line------")
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
                                # print(f"the indent is {processed_lines[i - line_number][0]} was {indent_level}")
                                indent_level = processed_lines[i - line_number][0]
                                previos_spaces = leading_spaces[i]
            current_indent = indent_level
            leading_spaces.append(indent_space)
            processed_lines.append([indent_level, stripped_line])

        tree_structure = ""

        y = self.tree_y
        for index, (indent, text) in enumerate(processed_lines):
            x = self.tree_x + (indent) * 4
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
