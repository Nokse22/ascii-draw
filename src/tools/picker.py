# picker.py
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

from .tool import Tool


class Picker(Tool):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.canvas.click_gesture.connect("pressed", self.on_click_pressed)
        self.canvas.click_gesture.connect("released", self.on_click_released)
        self.canvas.click_gesture.connect("stopped", self.on_click_stopped)

        self.flip = False

        self.x_mul = 12
        self.y_mul = 24

    def on_click_pressed(self, click, arg, x, y):
        if not self._active:
            return

        if self.flip:
            if self.drawing_area_width == 0:
                self.update_area_width()
            x = self.drawing_area_width - x
        x_char = int(x / self.x_mul)
        y_char = int(y / self.y_mul)

        char = self.canvas.get_char_at(x_char, y_char)
        self.canvas.set_selected_char(char)

    def on_click_stopped(self, click):
        if not self._active:
            return
        pass

    def on_click_released(self, click, arg, x, y):
        if not self._active:
            return
        pass
