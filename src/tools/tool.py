# tool.py
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

from gi.repository import GObject


class Tool(GObject.GObject):
    def __init__(self, _canvas, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.canvas = _canvas
        self._active = False
        self._style = 0
        self._sidebar = None
        self._stack_page = None

        self.brush_sizes = [
            [[0, 0]],
            [[0, 0], [-1, 0], [1, 0]],
            [[0, 0], [-1, 0], [1, 0], [0, 1], [0, -1]],
            [[0, 0], [-1, 0], [1, 0], [0, 1], [0, -1], [-2, 0], [2, 0]],
            [[0, 0], [-1, 0], [1, 0], [0, 1], [0, -1], [-2, 0], [2, 0], [1, 1],
                [-1, -1], [-1, 1], [1, -1]],
            [[0, 0], [-1, 0], [1, 0], [0, 1], [0, -1], [-2, 0], [2, 0], [1, 1],
                [-1, -1], [-1, 1], [1, -1], [-2, 1], [2, 1], [-2, -1],
                [2, -1]],
            [[0, 0], [-1, 0], [1, 0], [0, 1], [0, -1], [-2, 0], [2, 0], [1, 1],
                [-1, -1], [-1, 1], [1, -1], [-2, 1], [2, 1], [-2, -1], [2, -1],
                [0, 2], [0, -2], [-3, 0], [3, 0]],
            [[0, 0], [-1, 0], [1, 0], [0, 1], [0, -1], [-2, 0], [2, 0], [1, 1],
                [-1, -1], [-1, 1], [1, -1], [-2, 1], [2, 1], [-2, -1], [2, -1],
                [0, 2], [0, -2], [-3, 0], [3, 0], [1, 2], [1, -2], [-1, -2],
                [-1, 2]],
        ]

    @GObject.Property(type=bool, default=False)
    def active(self):
        return self._active

    @active.setter
    def active(self, value):
        self._active = value
        if self._stack_page:
            self._stack_page.set_visible(value)
        self.notify('active')

        self.on_active_changed(value)

    @GObject.Property(type=str, default='#')
    def style(self):
        return self._style

    @style.setter
    def style(self, value):
        self._style = value
        self.notify('style')

    def on_active_changed(self, value):
        pass

    def add_sidebar_to(self, stack):
        if self._sidebar is None:
            print("Missing sidebar")
            return
        stack_page = stack.add(self._sidebar.get_child())
        stack_page.set_name(self._sidebar.get_name())
        stack_page.set_title(self._sidebar.get_title())
        stack_page.set_icon_name(self._sidebar.get_icon_name())
        stack_page.set_visible(False)

        self._stack_page = stack_page
