# line.py
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

class Line(GObject.GObject):
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

        self.flip = False
        self.start_x = 0
        self.start_y = 0

        self.x_mul = 12
        self.y_mul = 24

        self.end_x = 0
        self.end_y = 0

        self.prev_x = 0
        self.prev_y = 0

        self.prev_line_pos = [0,0]
        self.line_direction = [0,0]

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

        self.canvas.clear_preview()
        if width < 0:
            width -= 1
        else:
            width += 1
        if height < 0:
            height -= 1
        else:
            height += 1
        # if self.prev_line_pos != [self.start_x + width, self.start_y + height]:
        self.line_direction = self.normalize_vector([end_x - self.prev_line_pos[0], end_y - self.prev_line_pos[1]])
        self.line_direction = [abs(self.line_direction[0]), abs(self.line_direction[1])]
        self.draw_line(start_x_char, start_y_char, width, height, False)

        self.prev_line_pos = [end_x, end_y]

        print(self.line_direction)

    def on_drag_end(self, gesture, delta_x, delta_y):
        if not self._active: return

        self.canvas.clear_preview()

        if self.flip:
            delta_x = - delta_x
        start_x_char = self.start_x // self.x_mul
        start_y_char = self.start_y // self.y_mul
        width = int((delta_x + self.start_x) // self.x_mul - start_x_char)
        height = int((delta_y + self.start_y) // self.y_mul - start_y_char)

        self.prev_x = 0
        self.prev_y = 0

        self.canvas.add_undo_action("Line")
        if width < 0:
            width -= 1
        else:
            width += 1
        if height < 0:
            height -= 1
        else:
            height += 1
        self.draw_line(start_x_char, start_y_char, width, height, True)

    def on_click_pressed(self, click, arg, x, y):
        if not self._active: return
        pass

    def on_click_stopped(self, click):
        if not self._active: return
        pass

    def on_click_released(self, click, arg, x, y):
        if not self._active: return
        pass

    def draw_line(self, start_x_char, start_y_char, width, height, draw):
        end_vertical = self.canvas.left_vertical()
        start_vertical = self.canvas.right_vertical()
        end_horizontal = self.canvas.top_horizontal()
        start_horizontal = self.canvas.bottom_horizontal()

        arrow = False

        if width > 0 and height > 0:
            if self.line_direction == [1, 0]:
                self.canvas.horizontal_line(start_y_char + height - 1, start_x_char + 1, width - 1, start_horizontal, draw)
                if height > 1:
                    self.canvas.vertical_line(start_x_char, start_y_char, height - 1, end_vertical, draw)
                if height != 1:
                    self.canvas.set_char_at(start_x_char, start_y_char + height - 1, self.canvas.bottom_left(), draw)
                if arrow:
                    self.canvas.set_char_at(start_x_char + width - 1, start_y_char + height - 1, self.canvas.right_arrow(), draw)
            else:
                self.canvas.horizontal_line(start_y_char, start_x_char, width - 1, end_horizontal, draw)
                if height > 1:
                    self.canvas.vertical_line(start_x_char + width - 1, start_y_char + 1, height - 1, start_vertical, draw)
                if width != 1 and height != 1:
                    self.canvas.set_char_at(start_x_char + width - 1, start_y_char, self.canvas.top_right(), draw)
                if arrow:
                    self.canvas.set_char_at(start_x_char + width - 1, start_y_char + height - 1, self.canvas.down_arrow(), draw)
        elif width > 0 and height < 0:
            if self.line_direction == [1, 0]:
                self.canvas.horizontal_line(start_y_char + height + 1, start_x_char + 1, width - 1, end_horizontal, draw)
                if height < 1:
                    self.canvas.vertical_line(start_x_char, start_y_char + 1, height + 1, end_vertical, draw)
                if width != 1 and height != 1:
                    self.canvas.set_char_at(start_x_char, start_y_char + height + 1, self.canvas.top_left(), draw)
                if arrow:
                    self.canvas.set_char_at(start_x_char + width - 1, start_y_char + height + 1, self.canvas.right_arrow(), draw)
            else:
                self.canvas.horizontal_line(start_y_char, start_x_char, width - 1, start_horizontal, draw)
                if height < 1:
                    self.canvas.vertical_line(start_x_char + width - 1, start_y_char, height + 1, start_vertical, draw)
                if width != 1 and height != 1:
                    self.canvas.set_char_at(start_x_char + width - 1, start_y_char, self.canvas.bottom_right(), draw)
                if arrow:
                    self.canvas.set_char_at(start_x_char + width - 1, start_y_char + height + 1, self.canvas.up_arrow(), draw)
        elif width < 0 and height > 0:
            if self.line_direction == [1, 0]:
                self.canvas.horizontal_line(start_y_char + height - 1, start_x_char, width + 1, start_horizontal, draw)
                if height > 1:
                    self.canvas.vertical_line(start_x_char, start_y_char, height - 1, start_vertical, draw)
                if width != 1 and height != 1:
                    self.canvas.set_char_at(start_x_char, start_y_char + height - 1, self.canvas.bottom_right(), draw)
                if arrow:
                    self.canvas.set_char_at(start_x_char + width + 1, start_y_char + height - 1, self.canvas.left_arrow(), draw)
            else:
                self.canvas.horizontal_line(start_y_char, start_x_char + 1, width + 1, end_horizontal, draw)
                if height > 1:
                    self.canvas.vertical_line(start_x_char + width + 1, start_y_char + 1, height - 1, end_vertical, draw)
                if width != 1 and height != 1:
                    self.canvas.set_char_at(start_x_char + width + 1, start_y_char, self.canvas.top_left(), draw)
                if arrow:
                    self.set_char_at(start_x_char + width + 1, start_y_char + height - 1, self.canvas.down_arrow(), draw)
        elif width < 0 and height < 0:
            if self.line_direction == [1, 0]:
                self.canvas.horizontal_line(start_y_char + height + 1, start_x_char, width + 1, end_horizontal, draw)
                if height < 1:
                    self.canvas.vertical_line(start_x_char, start_y_char + 1, height + 1, start_vertical, draw)
                if width != 1 and height != 1:
                    self.canvas.set_char_at(start_x_char, start_y_char + height + 1, self.canvas.top_right(), draw)
                if arrow:
                    self.canvas.set_char_at(start_x_char + width + 1, start_y_char + height + 1, self.canvas.left_arrow(), draw)
            else:
                self.canvas.horizontal_line(start_y_char, start_x_char + 1, width + 1, start_horizontal, draw)
                if height < 1:
                    self.canvas.vertical_line(start_x_char + width + 1, start_y_char, height + 1, end_vertical, draw)
                if width != 1 and height != 1:
                    self.canvas.set_char_at(start_x_char + width + 1, start_y_char, self.canvas.bottom_left(), draw)
                if arrow:
                    self.canvas.set_char_at(start_x_char + width + 1, start_y_char + height + 1, self.canvas.up_arrow(), draw)

        if width == 1 and height < 0:
            self.canvas.set_char_at(start_x_char, start_y_char, self.canvas.left_vertical(), draw)
        elif width == 1 and height > 0:
            self.canvas.set_char_at(start_x_char, start_y_char, self.canvas.right_vertical(), draw)
        elif height == 1:
            self.canvas.set_char_at(start_x_char, start_y_char, self.canvas.bottom_horizontal(), draw)

    def normalize_vector(self, vector):
        magnitude = math.sqrt(vector[0]**2 + vector[1]**2)
        if magnitude == 0:
            return [0, 0]
        normalized = [round(vector[0] / magnitude), round(vector[1] / magnitude)]
        return normalized
