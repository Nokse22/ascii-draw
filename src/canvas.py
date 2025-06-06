# canvas.py
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

from gi.repository import Adw
from gi.repository import Gtk
from gi.repository import GObject


class Change():
    def __init__(self, _name):
        self.changes = []
        self.name = _name

    def add_change(self, x, y, prev_char):
        for change in self.changes:
            if change[0] == x and change[1] == y:
                return
        self.changes.append((x, y, prev_char))

    def __repr__(self):
        return f"The change named {self.name} has {len(self.changes)} changes"


@Gtk.Template(resource_path='/io/github/nokse22/asciidraw/ui/canvas.ui')
class Canvas(Adw.Bin):
    __gtype_name__ = 'Canvas'
    draw_drawing_area = Gtk.Template.Child()
    preview_drawing_area = Gtk.Template.Child()
    fixed = Gtk.Template.Child()

    __gsignals__ = {
        'undo-added': (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        'undo-removed': (GObject.SignalFlags.RUN_FIRST, None, ()),
        'redo-removed': (GObject.SignalFlags.RUN_FIRST, None, ())
    }

    def __init__(self, _styles, _flip):
        super().__init__()
        self.color = 0

        self.styles = _styles
        self.primary_char = '#'
        self.secondary_char = '+'

        self.drawing: list[list[str]] = []
        self.preview: list[list[str]] = []

        self.primary_selected = True

        self._style = 1

        self.drag_gesture = Gtk.GestureDrag()
        self.drag_gesture.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.drag_gesture.set_button(0)
        self.fixed.add_controller(self.drag_gesture)

        self.click_gesture = Gtk.GestureClick()
        self.click_gesture.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.click_gesture.set_button(0)
        self.fixed.add_controller(self.click_gesture)

        self.zoom_gesture = Gtk.GestureZoom()
        self.zoom_gesture.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.zoom_gesture.connect("scale-changed", self.on_scale_changed)
        self.fixed.add_controller(self.zoom_gesture)

        self.draw_drawing_area.set_draw_func(self.drawing_function, None)
        self.preview_drawing_area.set_draw_func(
            self.preview_drawing_function, None)

        self.x_mul = 12
        self.y_mul = 24

        self.canvas_width = 40
        self.canvas_height = 20

        self.draw_drawing_area.set_size_request(
            self.canvas_width*self.x_mul, self.canvas_height*self.y_mul)

        for y in range(self.canvas_height):
            new_line = []
            for x in range(self.canvas_width):
                new_line.append(" ")
            self.drawing.append(new_line)
            self.preview.append(new_line)

        self.x_mul = 12
        self.y_mul = 24

        self.undo_changes = []
        self.changed_chars = []

        self.redo_changes = []

        self.canvas_max_x = 100
        self.canvas_max_y = 50

        self.scale_factor = 1

        self.is_saved = True

    def get_canvas_size(self):
        return self.canvas_width, self.canvas_height

    @GObject.Property(type=bool, default=True)
    def primary_selected(self):
        return self._primary_selected

    @primary_selected.setter
    def primary_selected(self, value):
        self._primary_selected = value
        self.notify('primary_selected')

    @GObject.Property(type=str, default='#')
    def primary_char(self):
        return self._primary_char

    @primary_char.setter
    def primary_char(self, value):
        self._primary_char = value
        self.notify('primary_char')

    @GObject.Property(type=str, default='#')
    def secondary_char(self):
        return self._secondary_char

    @secondary_char.setter
    def secondary_char(self, value):
        self._secondary_char = value
        self.notify('secondary_char')

    @GObject.Property(type=int, default=0)
    def style(self):
        return self._style

    @style.setter
    def style(self, value):
        self._style = value
        self.notify('style')

    def on_scale_changed(self, gesture, scale):
        # print(scale)
        pass
        # if scale > 2:
        #     self.scale_factor = 2

    def drawing_function(self, area, cr, width, height, data):
        cr.set_source_rgb(self.color, self.color, self.color)
        cr.select_font_face("Adwaita Mono")
        cr.set_font_size(20 * self.scale_factor)

        for y, line in enumerate(self.drawing):
            for x, char in enumerate(line):
                cr.move_to(
                    x * self.x_mul,
                    (y + 1) * self.y_mul * self.scale_factor - 5)
                cr.show_text(char)

    def preview_drawing_function(self, area, cr, width, height, data):
        cr.set_source_rgb(self.color, self.color, self.color)
        cr.select_font_face("Adwaita Mono")
        cr.set_font_size(20 * self.scale_factor)

        for y, line in enumerate(self.preview):
            for x, char in enumerate(line):
                cr.move_to(
                    x * self.x_mul,
                    (y + 1) * self.y_mul * self.scale_factor - 5)
                cr.show_text(char)

    def update(self):
        self.draw_drawing_area.queue_draw()

    def update_preview(self):
        self.preview_drawing_area.queue_draw()

    def undo(self):
        try:
            change_object = self.undo_changes[-1]
        except Exception:
            return
        redo_object = Change(change_object.name)
        for x, y, char in change_object.changes:
            if (y >= len(self.drawing) or x >= len(self.drawing[0])
                    or x < 0 or y < 0):
                return
            redo_object.add_change(x, y, self.get_char_at(x, y))
            self.drawing[int(y)][int(x)] = char

        self.redo_changes.append(redo_object)
        self.undo_changes.pop(-1)
        self.emit("undo-removed")
        self.update()

    def redo(self):
        try:
            change_object = self.redo_changes[-1]
        except Exception:
            return
        self.add_undo_action(change_object.name)
        for x, y, char in change_object.changes:
            if (y >= len(self.drawing) or x >= len(self.drawing[0])
                    or x < 0 or y < 0):
                return
            self.undo_changes[-1].add_change(x, y, self.get_char_at(x, y))
            self.drawing[int(y)][int(x)] = char
        self.redo_changes.pop(-1)
        self.emit("redo-removed")
        self.update()

    def add_undo_action(self, undo_name):
        self.undo_changes.append(Change(undo_name))
        self.emit('undo-added', undo_name)

        self.is_saved = False

    def get_char_at(self, x: int, y: int, draw=True):
        if (y >= len(self.drawing) or x >= len(self.drawing[0])
                or x < 0 or y < 0):
            return
        if draw:
            return self.drawing[int(y)][int(x)]
        return self.preview[int(y)][int(x)]

    def set_selected_char(self, char):
        if self._primary_selected:
            self.primary_char = char
        else:
            self.secondary_char = char

    def get_selected_char(self):
        if self._primary_selected:
            return self.primary_char
        return self.secondary_char

    def get_unselected_char(self):
        if not self._primary_selected:
            return self.primary_char
        return self.secondary_char

    def draw_text(self, start_x, start_y, text, transparent, draw):
        if text == "":
            return
        _layer = self.drawing if draw else self.preview

        self.__draw_text(start_x, start_y, text, transparent, draw, _layer)

    def __draw_text(self, start_x, start_y, text, transparent, draw, _layer):
        lines = text.splitlines()
        max_line_length = max(len(line) for line in lines)
        array2 = [list(line.ljust(max_line_length)) for line in lines]

        rows1, cols1 = len(_layer), len(_layer[0])
        rows2, cols2 = len(array2), len(array2[0])

        if start_x >= cols1 or start_y >= rows1:
            return

        for i in range(rows2):
            for j in range(cols2):
                new_i, new_j = i + start_y, j + start_x

                if 0 <= new_i < rows1 and 0 <= new_j < cols1:
                    if transparent and array2[i][j] == " ":
                        continue
                    if draw:
                        prev_char = self.get_char_at(new_j, new_i)
                        self.undo_changes[-1].add_change(
                            new_j, new_i, prev_char)
                    _layer[int(new_i)][int(new_j)] = array2[i][j]

    def draw_rectangle(self, start_x_char, start_y_char, width, height, draw):
        if width <= 1 or height <= 1:
            return

        self.horizontal_line(
            start_y_char, start_x_char + 1, width - 2,
            self.top_horizontal(), draw)
        self.horizontal_line(
            start_y_char + height - 1, start_x_char + 1, width - 2,
            self.bottom_horizontal(), draw)
        self.vertical_line(
            start_x_char, start_y_char + 1, height - 2,
            self.left_vertical(), draw)
        self.vertical_line(
            start_x_char + width - 1, start_y_char + 1, height - 2,
            self.right_vertical(), draw)

        self.set_char_at(
            start_x_char + width - 1, start_y_char,
            self.top_right(), draw)
        self.set_char_at(
            start_x_char + width - 1, start_y_char + height - 1,
            self.bottom_right(), draw)
        self.set_char_at(
            start_x_char, start_y_char,
            self.top_left(), draw)
        self.set_char_at(
            start_x_char, start_y_char + height - 1,
            self.bottom_left(), draw)

    def horizontal_line(self, y, start_x, length, char, draw):
        if length < 0:
            length = -length
            start_x -= length

        for x in range(abs(length)):
            prev_label = self.get_char_at(start_x + x, y, draw)
            if ((prev_label == self.left_vertical()
                    or prev_label == self.right_vertical())
                    and self.crossing() != " "):
                self.set_char_at(start_x + x, y, self.crossing(), draw)
            else:
                self.set_char_at(start_x + x, y, char, draw)

    def vertical_line(self, x, start_y, length, char, draw):
        if length < 0:
            length = -length
            start_y -= length

        for y in range(abs(length)):
            prev_label = self.get_char_at(x, start_y + y, draw)
            if ((prev_label == self.top_horizontal() or
                    prev_label == self.bottom_horizontal()) and
                    self.crossing() != " "):
                self.set_char_at(x, start_y + y, self.crossing(), draw)
            else:
                self.set_char_at(x, start_y + y, char, draw)

    def set_char_at(self, x, y, char, draw):
        _layer = self.drawing if draw else self.preview

        if char == "":
            char = " "

        if y >= len(_layer) or x >= len(_layer[0]) or x < 0 or y < 0:
            return
        if draw:
            prev_char = self.get_char_at(x, y)
            self.undo_changes[-1].add_change(x, y, prev_char)
        _layer[int(y)][int(x)] = char

    def draw_at(self, x, y):
        if (y >= len(self.drawing) or x >= len(self.drawing[0])
                or x < 0 or y < 0):
            return
        prev_char = self.get_char_at(x, y)
        self.undo_changes[-1].add_change(x, y, prev_char)
        self.drawing[int(y)][int(x)] = self.get_selected_char()

    def draw_inverted_at(self, x, y):
        if (y >= len(self.drawing) or x >= len(self.drawing[0])
                or x < 0 or y < 0):
            return
        prev_char = self.get_char_at(x, y)
        self.undo_changes[-1].add_change(x, y, prev_char)
        self.drawing[int(y)][int(x)] = self.get_unselected_char()

    def draw_primary_at(self, x, y, draw):
        _layer = self.drawing if draw else self.preview

        if y >= len(_layer) or x >= len(_layer[0]) or x < 0 or y < 0:
            return
        if draw:
            prev_char = self.get_char_at(x, y)
            self.undo_changes[-1].add_change(x, y, prev_char)
        _layer[int(y)][int(x)] = self.primary_char

    def draw_secondary_at(self, x, y, draw):
        _layer = self.drawing if draw else self.preview

        if y >= len(_layer) or x >= len(_layer[0]) or x < 0 or y < 0:
            return
        if draw:
            prev_char = self.get_char_at(x, y)
            self.undo_changes[-1].add_change(x, y, prev_char)
        _layer[int(y)][int(x)] = self.secondary_char

    def clear_preview(self):
        self.preview = []
        for y in range(self.canvas_height):
            new_line = []
            for x in range(self.canvas_width):
                new_line.append(" ")
            self.preview.append(new_line)

        self.preview_drawing_area.queue_draw()

    def clear_canvas(self):
        for y in range(self.canvas_height):
            for x in range(self.canvas_width):
                self.set_char_at(x, y, "", True)

        self.draw_drawing_area.queue_draw()

    def wipe_canvas(self):
        for y in range(self.canvas_height):
            for x in range(self.canvas_width):
                if (y >= len(self.drawing) or x >= len(self.drawing[0])
                        or x < 0 or y < 0):
                    return
                self.drawing[int(y)][int(x)] = ""

        self.draw_drawing_area.queue_draw()

    def change_canvas_size(self, final_x, final_y):
        content = self.get_content()

        self.drawing = []
        self.preview = []

        self.canvas_width = final_x
        self.canvas_height = final_y

        for y in range(self.canvas_height):
            new_line = []
            for x in range(self.canvas_width):
                new_line.append(" ")
            self.drawing.append(new_line)
            self.preview.append(new_line)

        self.draw_drawing_area.set_size_request(
            self.canvas_width*self.x_mul, self.canvas_height*self.y_mul)

        self.__draw_text(0, 0, content, False, False, self.drawing)

    def get_content(self):
        content = ""

        for index, line in enumerate(self.drawing):
            line_string = ''.join(w if w != "" else " " for w in line)
            content += line_string + "\n"

        return content

    def set_content(self, content):
        self.wipe_canvas()
        lines = content.split('\n')
        num_lines = len(lines)
        max_chars = max(len(line) for line in lines)
        self.change_canvas_size(max(max_chars, 10), max(num_lines - 1, 5))
        self.clear_preview()
        self.__draw_text(0, 0, content, False, False, self.drawing)
        self.update()

    def top_horizontal(self):
        return self.styles[self._style - 1][0]

    def bottom_horizontal(self):
        return self.styles[self._style - 1][1]

    def left_vertical(self):
        return self.styles[self._style - 1][2]

    def right_vertical(self):
        return self.styles[self._style - 1][3]

    def top_left(self):
        return self.styles[self._style - 1][4]

    def top_right(self):
        return self.styles[self._style - 1][5]

    def bottom_right(self):
        return self.styles[self._style - 1][6]

    def bottom_left(self):
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
        return self.styles[self._style - 1][9]

    def left_intersect(self):
        return self.styles[self._style - 1][10]

    def top_intersect(self):
        return self.styles[self._style - 1][11]

    def bottom_intersect(self):
        return self.styles[self._style - 1][12]
