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

        self.canvas.drag_gesture.connect("drag-begin", self.on_drag_begin)
        self.canvas.drag_gesture.connect("drag-update", self.on_drag_follow)
        self.canvas.drag_gesture.connect("drag-end", self.on_drag_end)

        self.canvas.click_gesture.connect("pressed", self.on_click_pressed)

        self.flip = False
        self.start_x = 0
        self.start_y = 0

        self.x_mul = 12
        self.y_mul = 24

        self.table_x = 0
        self.table_y = 0

        self.drag_x = 0
        self.drag_y = 0

        self.rows_number = 0
        self.columns_number = 0

        self._table_type = 0

    @GObject.Property(type=bool, default=False)
    def active(self):
        return self._active

    @active.setter
    def active(self, value):
        self._active = value
        self.notify('active')

        self.canvas.clear_preview()

    @GObject.Property(type=str, default='#')
    def style(self):
        return self._style

    @style.setter
    def style(self, value):
        self._style = value
        self.notify('style')

    @GObject.Property(type=str, default='#')
    def table_type(self):
        return self._table_type

    @table_type.setter
    def table_type(self, value):
        self._table_type = value
        self.notify('table_type')

        self.preview()

    def on_drag_begin(self, gesture, start_x, start_y):
        if not self._active: return

        self.drag_start_x = start_x
        self.drag_start_y = start_y

    def on_drag_follow(self, gesture, x, y):
        if not self._active: return

        self.drag_x = int((x + self.drag_start_x) // self.x_mul - self.drag_start_x// self.x_mul)
        self.drag_y = int((y + self.drag_start_y) // self.y_mul - self.drag_start_y// self.y_mul)

        self.canvas.clear_preview()
        self.preview()

        print(self.table_x + self.drag_x)

    def on_drag_end(self, gesture, delta_x, delta_y):
        if not self._active: return

        self.table_x += self.drag_x
        self.table_y += self.drag_y

        self.drag_x = 0
        self.drag_y = 0

    def on_click_pressed(self, click, arg, x, y):
        if not self._active: return

        self.table_x = int(x / self.x_mul)
        self.table_y = int(y / self.y_mul)
        self.canvas.clear_preview()
        self.preview()

    def insert(self):
        self.canvas.add_undo_action(_("Table"))
        self.draw_table(self.table_x + self.drag_x, self.table_y + self.drag_y, self._table_type, True)
        self.canvas.update()

    def preview(self):
        if not self._active: return
        self.canvas.clear_preview()
        self.draw_table(self.table_x + self.drag_x, self.table_y + self.drag_y, self._table_type, False)
        self.canvas.update_preview()

    def draw_table(self, table_x, table_y, table_type: int, draw: bool):
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

        if int(table_type) == 1: # all divided
            height = 1 + self.rows_number * 2
        elif int(table_type) == 0 and len(table) > 1: # first line divided
            height = 3 + self.rows_number
        else: # not divided
            height = 2 + self.rows_number

        for y in range(height):
            for x in range(width):
                self.canvas.set_char_at(table_x + x, table_y + y, ' ', draw)

        self.canvas.draw_rectangle(table_x, table_y, width, height, draw)

        x = table_x
        for column in range(self.columns_number - 1):
            x += columns_widths[column] + 1
            self.canvas.vertical_line(x, table_y + 1, height - 2, self.canvas.right_vertical(), draw)
            self.canvas.set_char_at(x, table_y + height - 1, self.canvas.top_intersect(), draw)
            self.canvas.set_char_at(x, table_y, self.canvas.bottom_intersect(), draw)

        y = table_y

        if int(table_type) == 1: # all divided
            for row in range(self.rows_number - 1):
                y += 2
                self.canvas.horizontal_line(y, table_x + 1, width - 2, self.canvas.bottom_horizontal(), draw)
                self.canvas.set_char_at(table_x, y, self.canvas.right_intersect(), draw)
                self.canvas.set_char_at(table_x + width - 1, y, self.canvas.left_intersect(), draw)
        elif int(table_type) == 0 and len(table) > 1: # first line divided
            y += 2
            self.canvas.horizontal_line(y, table_x + 1, width - 2, self.canvas.bottom_horizontal(), draw)
            self.canvas.set_char_at(table_x, y, self.canvas.right_intersect(), draw)
            self.canvas.set_char_at(table_x + width - 1, y, self.canvas.left_intersect(), draw)

        y = table_y + 1
        x = table_x + 1
        for index_row, row in enumerate(table):
            for index, column in enumerate(row):
                self.canvas.draw_text(x, y, column, False, draw)
                x += columns_widths[index] + 1
            if int(table_type) == 1: # all divided
                y += 2
            elif int(table_type) == 0 and index_row == 0: # first line divided
                y += 2
            else:
                y += 1
            x = table_x + 1
