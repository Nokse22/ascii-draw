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

class Change():
    def __init__(self, _name):
        self.changes = []
        self.name = _name

    def add_change(self, x, y, prev_char):
        for change in self.changes:
            if change[0] == x and change[1] == y:
                return
        self.changes.append([x, y, prev_char])

    def __repr__(self):
        return f"The change has {len(self.changes)} changes"

@Gtk.Template(resource_path='/io/github/nokse22/asciidraw/canvas.ui')
class Canvas(Adw.Bin):
    __gtype_name__ = 'Canvas'
    drawing_area = Gtk.Template.Child()
    draw_grid = Gtk.Template.Child()
    preview_grid = Gtk.Template.Child()

    __gsignals__ = {
        'undo_added': (GObject.SignalFlags.RUN_FIRST, None, (str,))
    }

    def __init__(self, _styles, _flip):
        super().__init__()

        self.styles = _styles
        self.flip = _flip
        self._style = 1

        self.drag_gesture = Gtk.GestureDrag()
        self.drag_gesture.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.drawing_area.add_controller(self.drag_gesture)

        self.click_gesture = Gtk.GestureClick()
        self.click_gesture.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.drawing_area.add_controller(self.click_gesture)

        self.x_mul = 12
        self.y_mul = 24

        self.canvas_width = 50
        self.canvas_height = 25

        self.canvas_x = 50
        self.canvas_y = 25

        for y in range(self.canvas_height):
            for x in range(self.canvas_width):
                self.draw_grid.attach(Gtk.Inscription(nat_chars=0, nat_lines=0,
                        min_chars=0, min_lines=0, css_classes=["ascii"],
                        width_request=self.x_mul, height_request=self.y_mul), x, y, 1, 1)
                self.preview_grid.attach(Gtk.Inscription(nat_chars=0,
                        nat_lines=0, min_chars=0, min_lines=0,
                        css_classes=["ascii"], width_request=self.x_mul,
                        height_request=self.y_mul), x, y, 1, 1)

        self.x_mul = 12
        self.y_mul = 24

        self.undo_changes = []
        self.changed_chars = []

    @GObject.Property(type=str, default='#')
    def char(self):
        return self._char

    @char.setter
    def char(self, value):
        self._char = value
        self.notify('char')

    @GObject.Property(type=int, default=0)
    def style(self):
        return self._style

    @style.setter
    def style(self, value):
        self._style = value
        self.notify('style')

    def draw_char(self, x_coord, y_coord, char):
        child = self.draw_grid.get_child_at(x_coord, y_coord)
        if child:
            self.undo_changes[0].add_change(x_coord, y_coord, child.get_text())
            child.set_text(char)

    def add_undo_action(self, undo_name):
        self.undo_changes.insert(0, Change(undo_name))
        self.emit('undo_added', undo_name)

    def draw_rectangle(self, start_x_char, start_y_char, width, height, draw):
        top_vertical = self.left_vertical()
        top_horizontal = self.top_horizontal()

        bottom_vertical = self.right_vertical()
        bottom_horizontal = self.bottom_horizontal()

        if width <= 1 or height <= 1:
            return

        self.horizontal_line(start_y_char, start_x_char, width, top_horizontal, draw)
        self.horizontal_line(start_y_char + height - 1, start_x_char + 1, width - 2, bottom_horizontal, draw)
        self.vertical_line(start_x_char, start_y_char + 1, height - 1, top_vertical, draw)
        self.vertical_line(start_x_char + width - 1, start_y_char + 1, height - 1, bottom_vertical, draw)

        self.set_char_at(start_x_char + width - 1, start_y_char, self.top_right(), draw)
        self.set_char_at(start_x_char + width - 1, start_y_char + height - 1, self.bottom_right(), draw)
        self.set_char_at(start_x_char, start_y_char, self.top_left(), draw)
        self.set_char_at(start_x_char, start_y_char + height - 1, self.bottom_left(), draw)

    def horizontal_line(self, y, start_x, width, char, draw):
        grid = self.draw_grid if draw else self.preview_grid

        if width > 0:
            for x in range(abs(width)):
                child = grid.get_child_at(start_x + x, y)
                if not child:
                    continue
                prev_label = child.get_text()
                if grid == self.draw_grid:
                    self.undo_changes[0].add_change(start_x + x, y, prev_label)
                if prev_label == "" or prev_label == " ":
                    child.set_text(char)
                elif prev_label == self.left_vertical():
                    child.set_text(self.crossing())
                else:
                    child.set_text(char)
                self.changed_chars.append([start_x + x, y])
        else:
            for x in range(abs(width)):
                child = grid.get_child_at(start_x + x + width, y)
                if not child:
                    continue
                prev_label = child.get_text()
                if grid == self.draw_grid:
                    self.undo_changes[0].add_change(start_x + x + width, y, prev_label)
                if prev_label == "" or prev_label == " ":
                    child.set_text(char)
                elif prev_label == self.left_vertical():
                    child.set_text(self.crossing())
                else:
                    child.set_text(char)
                self.changed_chars.append([start_x + x + width, y])

    def vertical_line(self, x, start_y, length, char, draw):
        grid = self.draw_grid if draw else self.preview_grid

        if length > 0:
            for y in range(abs(length)):
                child = grid.get_child_at(x, start_y + y)
                if not child:
                    continue
                prev_label = child.get_text()
                if grid == self.draw_grid:
                    self.undo_changes[0].add_change(x, start_y + y, prev_label)
                if prev_label == "" or prev_label == " ":
                    child.set_text(char)
                elif prev_label == self.top_horizontal() and self.crossing() != " ":
                    child.set_text(self.crossing())
                else:
                    child.set_text(char)
                self.changed_chars.append([x, start_y + y])
        else:
            for y in range(abs(length)):
                child = grid.get_child_at(x, start_y + y + length)
                if not child:
                    continue
                if grid == self.draw_grid:
                    self.undo_changes[0].add_change(x, start_y + y + length, child.get_text())
                if child.get_text() == "─": # FIXME make it work universally
                    child.set_text("┼")
                else:
                    child.set_text(char)
                self.changed_chars.append([x, start_y + y + length])

    def set_char_at(self, x, y, char, draw):
        grid = self.draw_grid if draw else self.preview_grid

        child = grid.get_child_at(x, y)
        if child:
            if grid == self.draw_grid:
                self.undo_changes[0].add_change(x, y, child.get_text())
            child.set_text(char)
            self.changed_chars.append([x, y])

    def preview_char_at(self, x, y, char):
        self.set_char_at(x, y, self.preview_grid, char)

    def draw_char_at(self, x, y, char):
        self.set_char_at(x, y, self.draw_grid, char)

    def clear_preview(self):
        self.clear(self.preview_grid)

    def clear_canvas(self):
        self.clear(self.draw_grid)

    def clear(self, grid):
        if grid != self.draw_grid:
            if len(self.changed_chars) < 100:
                for pos in self.changed_chars:
                    child = grid.get_child_at(pos[0], pos[1])
                    if not child:
                        continue
                    child.set_text("")
                # print(f"normal finished in {time.time() - start} to remove{len(self.changed_chars)}")
                self.changed_chars = []
                return

            threads = []
            list_length = len(self.changed_chars)
            divided = 5

            quotient, remainder = divmod(list_length, divided)
            parts = [quotient] * divided

            for i in range(remainder):
                parts[i] += 1

            total = 0
            # print(f"making threads at {time.time() - start}")
            for part in parts:
                if part == 0:
                    return
                thread = threading.Thread(target=self.clear_list_of_char, args=(total, total + part))
                total += part
                thread.start()
                threads.append(thread)
                # print(f"added threads at {time.time() - start}")

            for thread in threads:
                thread.join()
                # print(f"joining at {time.time() - start}")
            # print(f"threads finished in {time.time() - start} to remove {list_length} every one with {parts[0]}")
            self.changed_chars = []

        else:
            self.force_clear(None)

    def force_clear(self, grid=None):
        print("force clear")
        if grid == None:
            self.add_undo_action("Clear Screen")
            grid = self.draw_grid
        for y in range(self.canvas_y):
            for x in range(self.canvas_x):
                child = grid.get_child_at(x, y)
                if not child:
                    continue
                if grid == self.draw_grid:
                    self.undo_changes[0].add_change(x, y, child.get_text())
                child.set_text(" ")

    def clear_list_of_char(self, chars_list_start, chars_list_end):
        for index in range(chars_list_start, chars_list_end):
            pos = self.changed_chars[index]
            child = self.preview_grid.get_child_at(pos[0], pos[1])
            if not child:
                continue
            child.set_text("")

    def top_horizontal(self):
        return self.styles[self._style - 1][0]
    def bottom_horizontal(self):
        return self.styles[self._style - 1][1]
    def left_vertical(self):
        if self.flip:
            return self.styles[self._style - 1][3]
        return self.styles[self._style - 1][2]
    def right_vertical(self):
        if self.flip:
            return self.styles[self._style - 1][2]
        return self.styles[self._style - 1][3]
    def top_left(self):
        if self.flip:
            return self.styles[self._style - 1][5]
        return self.styles[self._style - 1][4]
    def top_right(self):
        if self.flip:
            return self.styles[self._style - 1][4]
        return self.styles[self._style - 1][5]
    def bottom_right(self):
        if self.flip:
            return self.styles[self._style - 1][7]
        return self.styles[self._style - 1][6]
    def bottom_left(self):
        if self.flip:
            return self.styles[self._style - 1][6]
        return self.styles[self._style - 1][7]
    def up_arrow(self):
        return self.styles[self._style - 1][13]
    def down_arrow(self):
        return self.styles[self._style - 1][14]
    def left_arrow(self):
        return self.styles[self._style - 1][16]
    def right_arrow(self):
        return self.styles[self._style - 1][15]
    def crossing(self):
        return self.styles[self._style - 1][8]
    def right_intersect(self):
        if self.flip:
            return self.styles[self._style - 1][10]
        return self.styles[self._style - 1][9]
    def left_intersect(self):
        if self.flip:
            return self.styles[self._style - 1][9]
        return self.styles[self._style - 1][10]
    def top_intersect(self):
        return self.styles[self._style - 1][11]
    def bottom_intersect(self):
        return self.styles[self._style - 1][12]
