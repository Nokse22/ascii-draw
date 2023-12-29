# drawing_canvas.py
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

class Canvas():
    def __init__(self):
        self.drawing_area = Gtk.DrawingArea()

        self.drag_gesture = Gtk.GestureDrag()
        self.drag_gesture.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.drawing_area.add_controller(self.drag_gesture)

        self.click_gesture = Gtk.GestureClick()
        self.click_gesture.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.drawing_area.add_controller(self.click_gesture)

        self.draw_grid = Gtk.Grid()
        self.preview_grid = Gtk.Grid()

        overlay = Gtk.Overlay()
        overlay.set_child(self.draw_grid)
        overlay.add_overlay(self.drawing_area)
        overlay.add_overlay(self.preview_grid)

        self.x_mul = 12
        self.y_mul = 24

        self.canvas_width = 50
        self.canvas_height = 25

        for y in range(self.canvas_height):
            for x in range(self.canvas_width):
                self.draw_grid.attach(Gtk.Inscription(nat_chars=0, nat_lines=0,
                        min_chars=0, min_lines=0, css_classes=["ascii"],
                        width_request=self.x_mul, height_request=self.y_mul), x, y, 1, 1)
                self.preview_grid.attach(Gtk.Inscription(nat_chars=0,
                        nat_lines=0, min_chars=0, min_lines=0,
                        css_classes=["ascii"], width_request=self.x_mul,
                        height_request=self.y_mul), x, y, 1, 1)

        self.active = GObject.Property(type=bool, default=False, flags=GObject.ParamFlags.READWRITE)

        self.flip = False

        self.x_mul = 12
        self.y_mul = 24

    def draw_char(self, x_coord, y_coord):
        for delta in self.brush_sizes[int(self.brush_size - 1)]:
            child = self.grid.get_child_at(x_coord + delta[0], y_coord + delta[1])
            if child:
                if child.get_text() == self.free_char:
                    continue
                self.undo_changes[0].add_change(x_coord + delta[0], y_coord + delta[1], child.get_text())
                child.set_text(self.free_char)
