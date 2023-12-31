# select.py
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

import numpy as np

class Select(GObject.GObject):
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

        self.x_mul = 12
        self.y_mul = 24

        self.drag_start_x = 0
        self.drag_start_y = 0

        self.delta_x = 0
        self.delta_y = 0

        self.prev_x = 0
        self.prev_y = 0

        self.has_selection = False
        self.is_dragging = False

        self.selection_start_x_char = 0
        self.selection_start_y_char = 0

        self.start_x_char = 0
        self.start_y_char = 0

        self.selection_width = 0
        self.selection_height = 0

    @GObject.Property(type=bool, default=False)
    def active(self):
        return self._active

    @active.setter
    def active(self, value):
        self._active = value
        self.notify('active')

        if value:
            self.canvas.drawing_area.set_draw_func(self.drawing_function, None)

    @GObject.Property(type=str, default='#')
    def style(self):
        return self._style

    @style.setter
    def style(self, value):
        self._style = value
        self.notify('style')

    def on_drag_begin(self, gesture, start_x, start_y):
        if not self._active: return

        print(f"coords: {start_x}, {start_y}")

        if self.has_selection and start_x > self.drag_start_x and start_x < self.delta_x and start_y > self.drag_start_y and start_y < self.delta_y:
            print("dragging selection")
            self.is_dragging = True
        else:
            self.start_x_char = (start_x // self.x_mul) * self.x_mul
            self.start_y_char = (start_y // self.y_mul) * self.y_mul

    def on_drag_follow(self, gesture, delta_x, delta_y):
        if not self._active: return
        if self.flip:
            delta_x = - delta_x
        start_x_char = self.drag_start_x // self.x_mul
        start_y_char = self.drag_start_y // self.y_mul

        width = int((delta_x + self.drag_start_x) // self.x_mul - start_x_char)
        height = int((delta_y + self.drag_start_y) // self.y_mul - start_y_char)

        self.delta_x = width * self.x_mul
        self.delta_y = height * self.y_mul

        if self.is_dragging:
            self.selection_start_x_char = self.start_x_char + self.delta_x
            self.selection_start_y_char = self.start_y_char + self.delta_y
        else:
            self.selection_width = self.delta_x
            self.selection_height = self.delta_y

        self.canvas.drawing_area.queue_draw()

    def on_drag_end(self, gesture, delta_x, delta_y):
        if not self._active: return

        if self.flip:
            delta_x = - delta_x
        start_x_char = self.drag_start_x // self.x_mul
        start_y_char = self.drag_start_y // self.y_mul

        width = int((delta_x + self.drag_start_x) // self.x_mul - start_x_char)
        height = int((delta_y + self.drag_start_y) // self.y_mul - start_y_char)

        self.start_x_char = start_x_char
        self.start_y_char = start_y_char

        self.delta_x = width * self.x_mul
        self.delta_y = height * self.y_mul

        if not self.is_dragging:
            self.selection_width = self.delta_x
            self.selection_height = self.delta_y

        self.has_selection = True

    def on_click_pressed(self, click, arg, x, y):
        if not self._active: return
        pass

    def on_click_stopped(self, click):
        if not self._active: return
        pass

    def on_click_released(self, click, arg, x, y):
        if not self._active: return

        # self.has_selection = False

        # print("unselected")

    def drawing_function(self, area, cr, width, height, data):
        cr.save()
        cr.set_source_rgb(0.208, 0.518, 0.894)
        cr.rectangle(self.selection_start_x_char + self.x_mul/2,
                            self.selection_start_y_char + self.y_mul/2,
                            self.selection_width, self.selection_height)
        cr.stroke()
        cr.restore()
