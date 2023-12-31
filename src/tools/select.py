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

        self.dragging_delta_char_x = 0
        self.dragging_delta_char_y = 0

        self.selection_start_x_char = 0
        self.selection_start_y_char = 0

        self.selection_delta_char_x = 0
        self.selection_delta_char_y = 0

        self.has_selection = False
        self.is_dragging = False

        self.moved_text: str = ''

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

    def on_drag_begin(self, gesture, this_x, this_y):
        if not self._active: return

        this_x_char = this_x // self.x_mul
        this_y_char = this_y // self.y_mul

#         print(f"""here: {this_x_char}, {this_y_char}
# selection start: {self.selection_start_x_char}, {self.selection_start_y_char}
# selection size: {self.selection_delta_char_x}, {self.selection_delta_char_y}
# dragging: {self.dragging_delta_char_x}, {self.dragging_delta_char_y}""")

        if (this_x_char > (self.selection_start_x_char + self.dragging_delta_char_x)
                and this_x_char < (self.selection_start_x_char + self.selection_delta_char_x + self.dragging_delta_char_x)
                and this_y_char > (self.selection_start_y_char + self.dragging_delta_char_y)
                and this_y_char < (self.selection_start_y_char + self.selection_delta_char_y + self.dragging_delta_char_x)):
            self.is_dragging = True

            for y in range(1, int(self.selection_delta_char_y)):
                for x in range(1, int(self.selection_delta_char_x)):
                    # print(self.canvas.get_char_at(self.selection_start_x_char + x, self.selection_start_y_char + y))
                    self.moved_text += self.canvas.get_char_at(self.selection_start_x_char + x, self.selection_start_y_char + y) or " "
                self.moved_text += '\n'

            print(self.moved_text)

            # Delete selection
            for y in range(1, int(self.selection_delta_char_y)):
                for x in range(1, int(self.selection_delta_char_x)):
                    self.canvas.set_char_at(self.selection_start_x_char + x, self.selection_start_y_char + y, ' ', True)
        else:
            print("new selection")
            self.selection_start_x_char = this_x // self.x_mul
            self.selection_start_y_char = this_y // self.y_mul

            self.drag_start_x = this_x # used to fix drag alignment
            self.drag_start_y = this_y # used to fix drag alignment

            self.is_dragging = False

            # print(f"{this_y} is {self.selection_start_y_char} chars {this_y / self.y_mul}")

    def on_drag_follow(self, gesture, delta_x, delta_y):
        if not self._active: return
        if self.flip:
            delta_x = - delta_x

        if self.is_dragging:
            self.dragging_delta_char_x = (self.drag_start_x + delta_x) // self.x_mul - self.drag_start_x // self.x_mul
            self.dragging_delta_char_y = (self.drag_start_y + delta_y) // self.y_mul - self.drag_start_y // self.y_mul

            self.canvas.clear_preview()
            self.canvas.draw_text(self.selection_start_x_char + self.dragging_delta_char_x + 1,
                            self.selection_start_y_char + self.dragging_delta_char_y + 1, self.moved_text, False, False)

        else:
            self.selection_delta_char_x = (self.drag_start_x + delta_x) // self.x_mul - self.drag_start_x // self.x_mul
            self.selection_delta_char_y = (self.drag_start_y + delta_y) // self.y_mul - self.drag_start_y // self.y_mul

        self.canvas.drawing_area.queue_draw()

    def on_drag_end(self, gesture, delta_x, delta_y):
        if not self._active: return

        if self.flip:
            delta_x = - delta_x

        if self.is_dragging:
            self.selection_start_x_char += self.dragging_delta_char_x
            self.selection_start_y_char += self.dragging_delta_char_y
            self.is_dragging = False

            self.canvas.clear_preview()
            self.canvas.draw_text(self.selection_start_x_char + 1, self.selection_start_y_char + 1, self.moved_text, True, True)
            self.moved_text = ''
            self.dragging_delta_char_x = 0
            self.dragging_delta_char_y = 0

        self.has_selection = True

    def on_click_pressed(self, click, arg, x, y):
        if not self._active: return

        print("pressed")

        return

        self.drag_start_x = 0
        self.drag_start_y = 0

        self.dragging_delta_char_x = 0
        self.dragging_delta_char_y = 0

        self.selection_start_x_char = 0
        self.selection_start_y_char = 0

        self.selection_delta_char_x = 0
        self.selection_delta_char_y = 0

        self.has_selection = False
        self.is_dragging = False

        self.canvas.drawing_area.queue_draw()

        print("clicked")

    def on_click_stopped(self, click):
        if not self._active: return
        print("stopped")

    def on_click_released(self, click, arg, x, y):
        if not self._active: return
        print("released")

    def drawing_function(self, area, cr, width, height, data):
        cr.save()
        cr.set_source_rgb(0.208, 0.518, 0.894)
        cr.rectangle(self.selection_start_x_char * self.x_mul + self.x_mul/2 + self.dragging_delta_char_x * self.x_mul,
                            self.selection_start_y_char * self.y_mul + self.y_mul/2 + self.dragging_delta_char_y * self.y_mul,
                            self.selection_delta_char_x * self.x_mul,
                            self.selection_delta_char_y * self.y_mul)
        cr.stroke()
        cr.restore()
