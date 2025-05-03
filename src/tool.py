# tool.py
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

from gi.repository import GObject


class Tool():
    def __init__(self, _drawing_area, _drag_gesture, _click_gesture):
        self.drawing_area = _drawing_area
        self.drag_gesture = _drag_gesture
        self.click_gesture = _click_gesture

        self.active = GObject.Property(
            type=bool, default=False, flags=GObject.ParamFlags.READWRITE)

    def on_drag_begin(self, gesture, start_x, start_y):
        pass

    def on_drag_follow(self, gesture, delta_x, delta_y):
        pass

    def on_drag_end(self, gesture, delta_x, delta_y):
        pass

    def on_click_pressed(self, click, arg, x, y):
        pass

    def on_click_stopped(self, click, arg, x, y):
        pass

    def on_click_released(self, click, arg, x, y):
        pass
