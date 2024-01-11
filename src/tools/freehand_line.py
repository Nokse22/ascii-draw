# text.py
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

import math

class FreehandLine(GObject.GObject):
    def __init__(self, _canvas, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.canvas = _canvas

        self._active = False
        self._style = 0

        self.canvas.drag_gesture.connect("drag-begin", self.on_drag_begin)
        self.canvas.drag_gesture.connect("drag-update", self.on_drag_follow)
        self.canvas.drag_gesture.connect("drag-end", self.on_drag_end)

        self.flip = False
        self.start_x = 0
        self.start_y = 0

        self.x_mul = 12
        self.y_mul = 24

        self.end_x = 0
        self.end_y = 0

        self.prev_char = ""
        self.prev_char_pos = []
        self.prev_pos = []

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

    def on_drag_begin(self, gesture, start_x, start_y):
        if not self._active: return
        self.start_x = start_x
        self.start_y = start_y

        if self.flip:
            if self.drawing_area_width == 0:
                self.update_area_width()
            self.start_x = self.drawing_area_width - self.start_x

        start_x_char = self.start_x // self.x_mul
        start_y_char = self.start_y // self.y_mul

        self.canvas.add_undo_action("Freehand Line")
        self.prev_char_pos = [start_x_char, start_y_char]

    def on_drag_follow(self, gesture, end_x, end_y):
        if not self._active: return
        if self.flip:
            end_x = - end_x
        start_x_char = self.start_x // self.x_mul
        start_y_char = self.start_y // self.y_mul

        width = int((end_x + self.start_x) // self.x_mul - start_x_char)
        height = int((end_y + self.start_y) // self.y_mul - start_y_char)

        self.end_x = width * self.x_mul
        self.end_y = height * self.y_mul

        self.draw_free_line(start_x_char + width, start_y_char + height)

    def on_drag_end(self, gesture, delta_x, delta_y):
        if not self._active: return

        self.prev_char = ""
        self.prev_char_pos = []
        self.prev_pos = []

    def draw_free_line(self, new_x, new_y):
        pos = [new_x, new_y]
        if self.prev_pos == [] or pos == self.prev_pos:
            self.prev_pos = [new_x, new_y]
            return
        pos = [new_x, new_y]
        direction = [int(pos[0] - self.prev_pos[0]), int(pos[1] - self.prev_pos[1])]
        dir2 = direction
        direction = self.normalize_vector(direction)
        prev_direction = [int(self.prev_pos[0] - self.prev_char_pos[0]),
                                    int(self.prev_pos[1] - self.prev_char_pos[1])]

        if direction == [1, 0] or direction == [-1, 0]:
            self.canvas.set_char_at(new_x, new_y, self.canvas.bottom_horizontal(), True)
        elif direction == [0, 1] or direction == [0, -1]:
            self.canvas.set_char_at(new_x, new_y, self.canvas.right_vertical(), True)

        # ["─", "─", "│", "│", "┌", "┐", "┘","└", "┼", "├", "┤", "┴","┬", "▲", "▼", "►", "◄"],

        if direction == [1, 0]:
            if dir2 != direction:
                self.canvas.horizontal_line(new_y, new_x - dir2[0], dir2[0], self.canvas.bottom_horizontal(), True)
            if prev_direction == [0, -1]:
                self.canvas.set_char_at(self.prev_pos[0], self.prev_pos[1], self.canvas.top_left(), True)
            elif prev_direction == [0, 1]:
                self.canvas.set_char_at(self.prev_pos[0], self.prev_pos[1], self.canvas.bottom_left(), True)
            else:
                self.canvas.set_char_at(self.prev_pos[0], self.prev_pos[1], self.canvas.bottom_horizontal(), True)
        elif direction == [-1, 0]:
            if prev_direction == [0, -1]:
                self.canvas.set_char_at(self.prev_pos[0], self.prev_pos[1], self.canvas.top_right(), True)
            elif prev_direction == [0, 1]:
                self.canvas.set_char_at(self.prev_pos[0], self.prev_pos[1], self.canvas.bottom_right(), True)
            else:
                self.canvas.set_char_at(self.prev_pos[0], self.prev_pos[1], self.canvas.bottom_horizontal(), True)

        if direction == [0, -1]:
            if prev_direction == [1, 0]:
                self.canvas.set_char_at(self.prev_pos[0], self.prev_pos[1], self.canvas.bottom_right(), True)
            elif prev_direction == [-1, 0]:
                self.canvas.set_char_at(self.prev_pos[0], self.prev_pos[1], self.canvas.bottom_left(), True)
            else:
                self.canvas.set_char_at(self.prev_pos[0], self.prev_pos[1], self.canvas.right_vertical(), True)
        elif direction == [0, 1]:
            if prev_direction == [1, 0]:
                self.canvas.set_char_at(self.prev_pos[0], self.prev_pos[1], self.canvas.top_right(), True)
            elif prev_direction == [-1, 0]:
                self.canvas.set_char_at(self.prev_pos[0], self.prev_pos[1], self.canvas.top_left(), True)
            else:
                self.canvas.set_char_at(self.prev_pos[0], self.prev_pos[1], self.canvas.right_vertical(), True)

        self.prev_char_pos = [self.prev_pos[0], self.prev_pos[1]]
        self.prev_pos = [new_x, new_y]

    def normalize_vector(self, vector):
        magnitude = math.sqrt(vector[0]**2 + vector[1]**2)
        if magnitude == 0:
            return [0, 0]  # Avoid division by zero
        normalized = [round(vector[0] / magnitude), round(vector[1] / magnitude)]
        return normalized
