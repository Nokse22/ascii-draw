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

import threading
import math
import pyfiglet
import unicodedata
import emoji
import os

class Tool():
    def __init__(self, _drawing_area, _preview_grid, _draw_grid):
        self.drawing_area = _drawing_area
        self.preview_grid = _preview_grid
        self.draw_grid = _draw_grid

        # self.active = GObject.Property(type=bool, default=False, flags=GObject.ParamFlags.READWRITE)

    def get_chars_coords(x_coord: float, y_coord: float) -> (int, int):
        if self.flip:
            end_x = - end_x
        start_x_char = x_coord // self.x_mul
        start_y_char = y_coord // self.y_mul

        width = int((end_x + x_coord) // self.x_mul - start_x_char)
        height = int((end_y + y_coord) // self.y_mul - start_y_char)

        self.end_x = width * self.x_mul
        self.end_y = height * self.y_mul
