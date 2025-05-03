# flood_fill.py
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

from gi.repository import GObject

from .tool import Tool

from gettext import gettext as _


class Fill(Tool):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._active = False

        self.canvas.click_gesture.connect("pressed", self.on_click_pressed)
        self.canvas.click_gesture.connect("released", self.on_click_released)
        self.canvas.click_gesture.connect("stopped", self.on_click_stopped)

        self.start_x = 0
        self.start_y = 0

        self.x_mul = 12
        self.y_mul = 24

        self.end_x = 0
        self.end_y = 0

        self._size = 1

    @GObject.Property(type=bool, default=False)
    def active(self):
        return self._active

    @active.setter
    def active(self, value):
        self._active = value
        self.notify('active')

    def on_click_pressed(self, click, arg, x, y):
        if not self._active:
            return

        x_char = int(x / self.x_mul)
        y_char = int(y / self.y_mul)

        self.canvas.add_undo_action(_("Fill"))

        button = click.get_current_button()

        if button == 1:
            flood_fill(
                self.canvas, x_char, y_char, self.canvas.get_selected_char())
        elif button == 3:
            flood_fill(
                self.canvas, x_char, y_char, self.canvas.get_unselected_char())

        self.canvas.update()

    def on_click_stopped(self, click):
        if not self._active:
            return
        pass

    def on_click_released(self, click, arg, x, y):
        if not self._active:
            return
        pass


def flood_fill(canvas, start_x, start_y, replacement_char):
    target_char = canvas.get_char_at(start_x, start_y)

    if target_char == replacement_char:
        return

    rows, cols = canvas.get_canvas_size()

    stack = [(start_x, start_y)]

    while stack:
        x, y = stack.pop()

        if canvas.get_char_at(x, y) == target_char:
            canvas.set_char_at(x, y, replacement_char, True)

            if x > 0:
                stack.append((x - 1, y))
            if x < rows - 1:
                stack.append((x + 1, y))
            if y > 0:
                stack.append((x, y - 1))
            if y < cols - 1:
                stack.append((x, y + 1))
