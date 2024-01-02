# table.py
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

class Table(GObject.GObject):
    def __init__(self, _canvas, _rows_box, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.canvas = _canvas
        self.rows_box = _rows_box

        self._active = False
        self._style = 0

        self.canvas.click_gesture.connect("pressed", self.on_click_pressed)
        self.canvas.click_gesture.connect("released", self.on_click_released)
        self.canvas.click_gesture.connect("stopped", self.on_click_stopped)

        self.flip = False
        self.start_x = 0
        self.start_y = 0

        self.x_mul = 12
        self.y_mul = 24

        self.table_x = 0
        self.table_y = 0

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

    def on_click_pressed(self, click, arg, x, y):
        if not self._active: return
        pass

    def on_click_stopped(self, click):
        if not self._active: return
        pass

    def on_click_released(self, click, arg, x, y):
        if not self._active: return

        if self.flip:
            if self.drawing_area_width == 0:
                self.update_area_width()
            x = self.drawing_area_width - x
        x_char = int(x / self.x_mul)
        y_char = int(y / self.y_mul)

        self.table_x = x_char
        self.table_y = y_char
        self.canvas.clear_preview()
        # table_type = self.table_types_combo.get_selected()
        self.preview_table()

    def draw_table(self):
        self.insert_table(0, True)

    def preview_table(self):
        self.insert_table(0, False)

    def insert_table(self, table_type: int, draw: bool):
        child = self.rows_box.get_first_child()
        columns_widths = []
        table = []
        column = 0
        while child != None:
            this_row = []
            entry = child.get_first_child()
            while entry != None:
                value = entry.get_text()
                if len(columns_widths) < column + 1:
                    columns_widths.append(len(value))
                elif len(value) > columns_widths[column]:
                    columns_widths[column] = len(value)
                this_row.append(value)
                columns_widths
                entry = entry.get_next_sibling()
                column += 1
            column = 0
            table.append(this_row)
            child = child.get_next_sibling()

        if len(columns_widths) == 0:
            return

        width = 1
        for column_width in columns_widths:
            width += column_width + 1

        if table_type == 1: # all divided
            height = 1 + self.rows_number * 2
        elif table_type == 0: # first line divided
            height = 3 + self.rows_number
        else: # not divided
            height = 2 + self.rows_number

        for y in range(height):
            for x in range(width):
                self.canvas.set_char_at(self.table_x + x, self.table_y + y, ' ',True)

        self.canvas.draw_rectangle(self.table_x, self.table_y, width, height, draw)

        x = self.table_x
        for column in range(self.columns_number - 1):
            x += columns_widths[column] + 1
            self.vertical_line(x, self.table_y + 1, height - 2, grid, self.right_vertical())
            self.set_char_at(x, self.table_y + height - 1, grid, self.top_intersect())
            self.set_char_at(x, self.table_y, grid, self.bottom_intersect())

        y = self.table_y
        if table_type == 1: # all divided
            for row in range(self.rows_number - 1):
                y += 2
                self.horizontal_line(y, self.table_x + 1, width - 2, grid, self.bottom_horizontal())
                self.set_char_at(self.table_x, y, grid, self.right_intersect())
                self.set_char_at(self.table_x + width - 1, y, grid, self.left_intersect())
        elif table_type == 0: # first line divided
            y += 2
            self.horizontal_line(y, self.table_x + 1, width - 2, grid, self.bottom_horizontal())
            self.set_char_at(self.table_x, y, grid, self.right_intersect())
            self.set_char_at(self.table_x + width - 1, y, grid, self.left_intersect())

        y = self.table_y + 1
        x = self.table_x + 1
        for index_row, row in enumerate(table):
            for index, column in enumerate(row):
                self.insert_text(grid, x, y, column)
                x += columns_widths[index] + 1
            if table_type == 1: # all divided
                y += 2
            elif table_type == 0 and index_row == 0: # first line divided
                y += 2
            else:
                y += 1
            x = self.table_x + 1