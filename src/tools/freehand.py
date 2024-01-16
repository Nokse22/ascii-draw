# freehand.py
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

class Freehand(GObject.GObject):
    def __init__(self, _canvas, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.canvas = _canvas

        self._active = False

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

        self._size = 1
        self._char = '#'

        self.brush_sizes = [
                [[0,0] ],
                [[0,0],[-1,0],[1,0] ],
                [[0,0],[-1,0],[1,0],[0,1],[0,-1] ],
                [[0,0],[-1,0],[1,0],[0,1],[0,-1],[-2,0],[2,0] ],
                [[0,0],[-1,0],[1,0],[0,1],[0,-1],[-2,0],[2,0],[1,1],[-1,-1],[-1,1],[1,-1], ],
                [[0,0],[-1,0],[1,0],[0,1],[0,-1],[-2,0],[2,0],[1,1],[-1,-1],[-1,1],[1,-1],[-2,1],[2,1],[-2,-1],[2,-1], ],
                [[0,0],[-1,0],[1,0],[0,1],[0,-1],[-2,0],[2,0],[1,1],[-1,-1],[-1,1],[1,-1],[-2,1],[2,1],[-2,-1],[2,-1],[0,2],[0,-2],[-3,0],[3,0], ],
                [[0,0],[-1,0],[1,0],[0,1],[0,-1],[-2,0],[2,0],[1,1],[-1,-1],[-1,1],[1,-1],[-2,1],[2,1],[-2,-1],[2,-1],[0,2],[0,-2],[-3,0],[3,0],[1,2],[1,-2],[-1,-2],[-1,2], ],
                ]

    @GObject.Property(type=bool, default=False)
    def active(self):
        return self._active

    @active.setter
    def active(self, value):
        self._active = value
        self.notify('active')

    @GObject.Property(type=int, default=1)
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = value
        self.notify('size')

    def on_drag_begin(self, gesture, start_x, start_y):
        if not self._active: return
        self.start_x = start_x
        self.start_y = start_y

        self.canvas.add_undo_action(_("Freehand"))

    def on_drag_follow(self, gesture, end_x, end_y):
        if not self._active: return

        button = gesture.get_current_button()

        start_x_char = self.start_x // self.x_mul
        start_y_char = self.start_y // self.y_mul

        width = int((end_x + self.start_x) // self.x_mul - start_x_char)
        height = int((end_y + self.start_y) // self.y_mul - start_y_char)

        self.end_x = width * self.x_mul
        self.end_y = height * self.y_mul

        x_coord = (self.start_x + self.end_x)//self.x_mul
        y_coord = (self.start_y + self.end_y)//self.y_mul
        for delta in self.brush_sizes[int(self._size - 1)]:
            if button == 1: self.canvas.draw_at(x_coord + delta[0], y_coord + delta[1])
            elif button == 3: self.canvas.draw_inverted_at(x_coord + delta[0], y_coord + delta[1])
        self.canvas.update()

    def on_drag_end(self, gesture, delta_x, delta_y):
        if not self._active: return
        pass

    def on_click_pressed(self, click, arg, x, y):
        if not self._active: return
        pass

    def on_click_stopped(self, click):
        if not self._active: return
        pass

    def on_click_released(self, click, arg, x, y):
        if not self._active: return
        pass
