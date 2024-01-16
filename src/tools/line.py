# arrow.py
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
        self._arrow = False
        self._line_type = 0

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

        self.end_x = 0
        self.end_y = 0

        self.prev_x = 0
        self.prev_y = 0

        self.prev_line_pos = [0,0]
        self.line_direction = [0,0]

        self.prev_char = ""
        self.prev_prev_pos = [0,0]
        self.prev_pos = [0,0]

    @GObject.Property(type=bool, default=False)
    def active(self):
        return self._active

    @active.setter
    def active(self, value):
        self._active = value
        self.notify('active')

        # if value:
        #     self.canvas.drawing_area.set_draw_func(self.drawing_function, None)

    @GObject.Property(type=bool, default=False)
    def arrow(self):
        return self._arrow

    @arrow.setter
    def arrow(self, value):
        self._arrow = value
        self.notify('arrow')

    @GObject.Property(type=int, default=0)
    def line_type(self):
        return self._line_type

    @line_type.setter
    def line_type(self, value):
        self._line_type = value
        self.notify('line_type')

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
        if self._line_type == 2:
            self.canvas.add_undo_action(_("Freehand Line"))
            start_x_char = start_x // self.x_mul
            start_y_char = start_y // self.y_mul
            self.prev_prev_pos = [start_x_char, start_y_char]
            self.prev_pos = [start_x_char, start_y_char]

    def on_drag_follow(self, gesture, end_x, end_y):
        if not self._active: return

        start_x_char = self.start_x // self.x_mul
        start_y_char = self.start_y // self.y_mul

        width = int((end_x + self.start_x) // self.x_mul - start_x_char)
        height = int((end_y + self.start_y) // self.y_mul - start_y_char)

        self.end_x = width * self.x_mul
        self.end_y = height * self.y_mul

        self.canvas.clear_preview()
        self.line_direction = self.normalize_vector([end_x - self.prev_line_pos[0], end_y - self.prev_line_pos[1]])
        # self.line_direction = [abs(self.line_direction[0]), abs(self.line_direction[1])]

        # print(width, height)

        if self._line_type == 0:
            self.draw_line(start_x_char, start_y_char, width, height, self.line_direction, False)
        elif self._line_type == 1:
            self.draw_step_line(start_x_char, start_y_char, width, height, False)
        elif self._line_type == 2:
            if [int(start_x_char + width), int(start_y_char + height)] != self.prev_pos:
                self.draw_free_line(start_x_char + width, start_y_char + height, self.prev_pos[0], self.prev_pos[1], self.prev_prev_pos[0], self.prev_prev_pos[1], True)
                self.prev_prev_pos = [self.prev_pos[0], self.prev_pos[1]]
                self.prev_pos = [start_x_char + width, start_y_char + height]
                self.canvas.update()

        self.prev_line_pos = [end_x, end_y]

        self.canvas.drawing_area.queue_draw()

    def on_drag_end(self, gesture, delta_x, delta_y):
        if not self._active: return

        self.canvas.clear_preview()

        start_x_char = self.start_x // self.x_mul
        start_y_char = self.start_y // self.y_mul
        width = int((delta_x + self.start_x) // self.x_mul - start_x_char)
        height = int((delta_y + self.start_y) // self.y_mul - start_y_char)

        self.prev_x = 0
        self.prev_y = 0

        if self._line_type == 0:
            self.canvas.add_undo_action(_("Cartesian Line"))
            self.draw_line(start_x_char, start_y_char, width, height, self.line_direction, True)
        elif self._line_type == 1:
            self.canvas.add_undo_action(_("Step Line"))
            self.draw_step_line(start_x_char, start_y_char, width, height, True)
        elif self._line_type == 2:
            self.prev_char = ""
            self.prev_prev_pos = [0,0]
            self.prev_pos = [0,0]

        self.canvas.update()

    def on_click_pressed(self, click, arg, x, y):
        if not self._active: return
        pass

    def on_click_stopped(self, click):
        if not self._active: return
        pass

    def on_click_released(self, click, arg, x, y):
        if not self._active: return
        pass

    def draw_step_line(self, start_x, start_y, width, height, draw):
        line = self.calculate_step_line(start_x, start_y, width, height)

        for i in range(len(line) - 2):
            self.draw_free_line(line[i + 2][0], line[i + 2][1], line[i + 1][0], line[i + 1][1], line[i][0], line[i][1], draw)

        if self._arrow:
            if abs(width) < (abs(height)*2):
                if height > 0:
                    char = self.canvas.down_arrow()
                else:
                    char = self.canvas.up_arrow()
            else:
                if width > 0:
                    char = self.canvas.right_arrow()
                else:
                    char = self.canvas.left_arrow()
            self.canvas.set_char_at(line[len(line) - 1][0], line[len(line) - 1][1], char, draw)

    def calculate_step_line(self, start_x, start_y, width, height):
        coordinates = []

        end_x = start_x + width
        end_y = start_y + height

        delta_x = abs(end_x - start_x)
        delta_y = abs(end_y - start_y)

        step_x = 1 if start_x < end_x else -1
        step_y = 1 if start_y < end_y else -1

        error = delta_x - delta_y

        coordinates.append([start_x, start_y])

        index = 0

        while True:
            if start_x == end_x and start_y == end_y:
                break

            error_2 = 2 * error

            if error_2 > -delta_y:
                error -= delta_y
                start_x += step_x

            if error_2 < delta_x:
                error += delta_x
                start_y += step_y

            if abs(start_x - coordinates[index][0]) == 1 and abs(start_y - coordinates[index][1]) == 1:
                coordinates.append([start_x, coordinates[index][1]])
                index += 1

            coordinates.append([start_x, start_y])
            index += 1

        return coordinates

    def draw_line(self, start_x_char, start_y_char, width, height, direction: list[int], draw):
        end_vertical = self.canvas.left_vertical()
        start_vertical = self.canvas.right_vertical()
        end_horizontal = self.canvas.top_horizontal()
        start_horizontal = self.canvas.bottom_horizontal()

        if width > 0 and height > 0:
            if abs(direction[0]) == 1: # FIXED
                self.canvas.horizontal_line(start_y_char + height, start_x_char + 1, width, start_horizontal, draw)
                self.canvas.vertical_line(start_x_char, start_y_char, height, end_vertical, draw)
                self.canvas.set_char_at(start_x_char, start_y_char + height, self.canvas.bottom_left(), draw)
                if self._arrow:
                    self.canvas.set_char_at(start_x_char + width, start_y_char + height, self.canvas.right_arrow(), draw)
            else: # FIXED
                self.canvas.horizontal_line(start_y_char, start_x_char, width, end_horizontal, draw)
                self.canvas.vertical_line(start_x_char + width, start_y_char + 1, height, start_vertical, draw)
                self.canvas.set_char_at(start_x_char + width, start_y_char, self.canvas.top_right(), draw)
                if self._arrow:
                    self.canvas.set_char_at(start_x_char + width, start_y_char + height, self.canvas.down_arrow(), draw)
        elif width > 0 and height < 0:
            if abs(direction[0]) == 1: # FIXED
                self.canvas.horizontal_line(start_y_char + height, start_x_char + 1, width, end_horizontal, draw)
                self.canvas.vertical_line(start_x_char, start_y_char + 1, height, end_vertical, draw)
                self.canvas.set_char_at(start_x_char, start_y_char + height, self.canvas.top_left(), draw)
                if self._arrow:
                    self.canvas.set_char_at(start_x_char + width, start_y_char + height, self.canvas.right_arrow(), draw)
            else: # FIXED
                self.canvas.horizontal_line(start_y_char, start_x_char, width, start_horizontal, draw)
                self.canvas.vertical_line(start_x_char + width, start_y_char, height, start_vertical, draw)
                self.canvas.set_char_at(start_x_char + width, start_y_char, self.canvas.bottom_right(), draw)
                if self._arrow:
                    self.canvas.set_char_at(start_x_char + width, start_y_char + height, self.canvas.up_arrow(), draw)
        elif width < 0 and height > 0:
            if abs(direction[0]) == 1: # FIXED
                self.canvas.horizontal_line(start_y_char + height, start_x_char, width, start_horizontal, draw)
                self.canvas.vertical_line(start_x_char, start_y_char, height, start_vertical, draw)
                self.canvas.set_char_at(start_x_char, start_y_char + height, self.canvas.bottom_right(), draw)
                if self._arrow:
                    self.canvas.set_char_at(start_x_char + width, start_y_char + height, self.canvas.left_arrow(), draw)
            else: # FIXED
                self.canvas.horizontal_line(start_y_char, start_x_char + 1, width, end_horizontal, draw)
                self.canvas.vertical_line(start_x_char + width, start_y_char, height + 1, end_vertical, draw)
                self.canvas.set_char_at(start_x_char + width, start_y_char, self.canvas.top_left(), draw)
                if self._arrow:
                    self.canvas.set_char_at(start_x_char + width, start_y_char + height, self.canvas.down_arrow(), draw)
        elif width < 0 and height < 0:
            if abs(direction[0]) == 1: # FIXED
                self.canvas.horizontal_line(start_y_char + height, start_x_char, width, end_horizontal, draw)
                self.canvas.vertical_line(start_x_char, start_y_char + 1, height, start_vertical, draw)
                self.canvas.set_char_at(start_x_char, start_y_char + height, self.canvas.top_right(), draw)
                if self._arrow:
                    self.canvas.set_char_at(start_x_char + width, start_y_char + height, self.canvas.left_arrow(), draw)
            else: # FIXED
                self.canvas.horizontal_line(start_y_char, start_x_char + 1, width, start_horizontal, draw)
                self.canvas.vertical_line(start_x_char + width, start_y_char, height, end_vertical, draw)
                self.canvas.set_char_at(start_x_char + width, start_y_char, self.canvas.bottom_left(), draw)
                if self._arrow:
                    self.canvas.set_char_at(start_x_char + width, start_y_char + height, self.canvas.up_arrow(), draw)

        if width == 0 and height == 0:
            if abs(direction[0]) == 1:
                self.canvas.set_char_at(start_x_char + width, start_y_char, end_horizontal, draw)
            else:
                self.canvas.set_char_at(start_x_char + width, start_y_char, end_vertical, draw)
        elif width == 0:
            if height < 0:
                self.canvas.vertical_line(start_x_char, start_y_char + 1, height - 1, end_vertical, draw)
                if self._arrow:
                    self.canvas.set_char_at(start_x_char, start_y_char + height, self.canvas.up_arrow(), draw)
            else:
                self.canvas.vertical_line(start_x_char, start_y_char, height + 1, end_vertical, draw)
                if self._arrow:
                    self.canvas.set_char_at(start_x_char, start_y_char + height, self.canvas.down_arrow(), draw)

        elif height == 0:
            if width < 0:
                self.canvas.horizontal_line(start_y_char, start_x_char + 1, width - 1, start_horizontal, draw)
                if self._arrow:
                    self.canvas.set_char_at(start_x_char + width, start_y_char, self.canvas.left_arrow(), draw)
            else:
                self.canvas.horizontal_line(start_y_char, start_x_char, width + 1, start_horizontal, draw)
                if self._arrow:
                    self.canvas.set_char_at(start_x_char + width, start_y_char, self.canvas.right_arrow(), draw)

    def normalize_vector(self, vector):
        magnitude = math.sqrt(vector[0]**2 + vector[1]**2)
        if magnitude == 0:
            return [0, 0]
        normalized = [round(vector[0] / magnitude), round(vector[1] / magnitude)]
        return normalized

    def draw_free_line(self, new_x, new_y, old_x, old_y, old_old_x, old_old_y, draw):
        pos = [new_x, new_y]
        prev_pos = [old_x, old_y]
        prev_prev_pos = [old_old_x, old_old_y]

        if prev_pos == [] or pos == prev_pos:
            return
        direction = [int(pos[0] - prev_pos[0]), int(pos[1] - prev_pos[1])]
        dir2 = direction
        direction = self.normalize_vector(direction)
        prev_direction = [int(prev_pos[0] - prev_prev_pos[0]),
                                    int(prev_pos[1] - prev_prev_pos[1])]

        if direction == [1, 0] or direction == [-1, 0]:
            self.canvas.set_char_at(new_x, new_y, self.canvas.bottom_horizontal(), draw)
        elif direction == [0, 1] or direction == [0, -1]:
            self.canvas.set_char_at(new_x, new_y, self.canvas.right_vertical(), draw)

        if direction == [1, 0]:
            if dir2 != direction:
                self.canvas.horizontal_line(new_y, new_x - dir2[0], dir2[0], self.canvas.bottom_horizontal(), draw)
            if prev_direction == [0, -1]:
                self.canvas.set_char_at(prev_pos[0], prev_pos[1], self.canvas.top_left(), draw)
            elif prev_direction == [0, 1]:
                self.canvas.set_char_at(prev_pos[0], prev_pos[1], self.canvas.bottom_left(), draw)
            else:
                self.canvas.set_char_at(prev_pos[0], prev_pos[1], self.canvas.bottom_horizontal(), draw)
        elif direction == [-1, 0]:
            if prev_direction == [0, -1]:
                self.canvas.set_char_at(prev_pos[0], prev_pos[1], self.canvas.top_right(), draw)
            elif prev_direction == [0, 1]:
                self.canvas.set_char_at(prev_pos[0], prev_pos[1], self.canvas.bottom_right(), draw)
            else:
                self.canvas.set_char_at(prev_pos[0], prev_pos[1], self.canvas.bottom_horizontal(), draw)
        elif direction == [0, -1]:
            if prev_direction == [1, 0]:
                self.canvas.set_char_at(prev_pos[0], prev_pos[1], self.canvas.bottom_right(), draw)
            elif prev_direction == [-1, 0]:
                self.canvas.set_char_at(prev_pos[0], prev_pos[1], self.canvas.bottom_left(), draw)
            else:
                self.canvas.set_char_at(prev_pos[0], prev_pos[1], self.canvas.right_vertical(), draw)
        elif direction == [0, 1]:
            if prev_direction == [1, 0]:
                self.canvas.set_char_at(prev_pos[0], prev_pos[1], self.canvas.top_right(), draw)
            elif prev_direction == [-1, 0]:
                self.canvas.set_char_at(prev_pos[0], prev_pos[1], self.canvas.top_left(), draw)
            else:
                self.canvas.set_char_at(prev_pos[0], prev_pos[1], self.canvas.right_vertical(), draw)
