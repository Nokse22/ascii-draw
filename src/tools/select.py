# select.py
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
from gi.repository import Gdk, GObject

from .tool import Tool

from gettext import gettext as _


class Select(Tool):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style = 0

        self.canvas.drag_gesture.connect("drag-begin", self.on_drag_begin)
        self.canvas.drag_gesture.connect("drag-update", self.on_drag_follow)
        self.canvas.drag_gesture.connect("drag-end", self.on_drag_end)

        self.canvas.click_gesture.connect("pressed", self.on_click_pressed)
        self.canvas.click_gesture.connect("released", self.on_click_released)
        self.canvas.click_gesture.connect("stopped", self.on_click_stopped)

        builder = Gtk.Builder.new_from_resource(
            "/io/github/nokse22/asciidraw/ui/move_sidebar.ui")
        self._sidebar = builder.get_object("move_stack_page")
        self.counterclockwise_button = builder.get_object(
            "counterclockwise_button")
        self.clockwise_button = builder.get_object("clockwise_button")
        self.copy_button = builder.get_object("copy_button")
        self.delete_button = builder.get_object("delete_button")

        self.selection = Adw.Bin(
            css_classes=["selection"],
            cursor=Gdk.Cursor.new_from_name("move"))

        self.x_mul = 12
        self.y_mul = 24

        self.drag_start_x = 0
        self.drag_start_y = 0

        self.dragging_delta_char_x = 0
        self.dragging_delta_char_y = 0

        self.selection_start_x_char = -1
        self.selection_start_y_char = -1

        self.selection_delta_char_x = 0
        self.selection_delta_char_y = 0

        self.has_selection = False
        self.is_dragging = False
        self.is_duplicating = False

        self.moved_text = []

        self.click_released = False

        self.counterclockwise_button.connect(
            "clicked", lambda *args: self.rotate(-90))

        self.clockwise_button.connect(
            "clicked", lambda *args: self.rotate(90))

        self.copy_button.connect("clicked", self.copy_selection)
        self.delete_button.connect("clicked", self.delete_selection)

    @GObject.Property(type=str, default='#')
    def style(self):
        return self._style

    @style.setter
    def style(self, value):
        self._style = value
        self.notify('style')

    def on_active_changed(self, value):

        self.selection.set_visible(False)

        self.selection_start_x_char = -1
        self.selection_start_y_char = -1

        self.selection_delta_char_x = 0
        self.selection_delta_char_y = 0

        self.update_selection()

    def on_drag_begin(self, gesture, this_x, this_y):
        if not self._active:
            return

        if gesture.get_last_event().get_modifier_state() == 4:  # CONTROL MASK
            self.is_duplicating = True
        else:
            self.is_duplicating = False

        this_x_char = this_x // self.x_mul
        this_y_char = this_y // self.y_mul

        start_x_char, start_y_char, width, height = self.translate(
            self.selection_start_x_char,
            self.selection_start_y_char,
            self.selection_delta_char_x,
            self.selection_delta_char_y)

        if (this_x_char > (start_x_char)
                and this_x_char < (start_x_char + width)
                and this_y_char > (start_y_char)
                and this_y_char < (start_y_char + height)):
            self.is_dragging = True

            self.canvas.add_undo_action(_("Move"))

            for y in range(1, int(height)):
                line = []
                for x in range(1, int(width)):
                    line.append(
                        self.canvas.get_char_at(
                            start_x_char + x, start_y_char + y) or " ")
                self.moved_text.append(line)

            if not self.is_duplicating:
                self.delete_selection()

        else:
            self.selection_start_x_char = this_x // self.x_mul
            self.selection_start_y_char = this_y // self.y_mul

            self.drag_start_x = this_x  # used to fix drag alignment
            self.drag_start_y = this_y  # used to fix drag alignment

            self.is_dragging = False

    def on_drag_follow(self, gesture, delta_x, delta_y):
        if not self._active:
            return

        if self.is_dragging:
            new_delta_x = (
                (self.drag_start_x + delta_x)
                // self.x_mul - self.drag_start_x // self.x_mul)
            new_delta_y = (
                (self.drag_start_y + delta_y)
                // self.y_mul - self.drag_start_y // self.y_mul)

            if (new_delta_x != self.dragging_delta_char_x or
                    new_delta_y != self.dragging_delta_char_y):
                self.dragging_delta_char_x = new_delta_x
                self.dragging_delta_char_y = new_delta_y

                self.canvas.clear_preview()

                start_x_char, start_y_char, width, height = self.translate(
                    self.selection_start_x_char,
                    self.selection_start_y_char,
                    self.selection_delta_char_x,
                    self.selection_delta_char_y)

                self.canvas.draw_text(
                    start_x_char + self.dragging_delta_char_x + 1,
                    start_y_char + self.dragging_delta_char_y + 1,
                    self.get_moved_string(),
                    True, False)

                self.update_selection()

                self.canvas.update()
        else:
            self.selection_delta_char_x = (
                (self.drag_start_x + delta_x)
                // self.x_mul - self.drag_start_x // self.x_mul)
            self.selection_delta_char_y = (
                (self.drag_start_y + delta_y)
                // self.y_mul - self.drag_start_y // self.y_mul)

            self.update_selection()

        self.selection.set_visible(True)

    def on_drag_end(self, gesture, delta_x, delta_y):
        if not self._active:
            return

        if self.is_dragging:
            self.selection_start_x_char += self.dragging_delta_char_x
            self.selection_start_y_char += self.dragging_delta_char_y
            self.is_dragging = False

            self.canvas.clear_preview()

            start_x_char, start_y_char, width, height = self.translate(
                self.selection_start_x_char,
                self.selection_start_y_char,
                self.selection_delta_char_x,
                self.selection_delta_char_y)

            self.canvas.draw_text(
                start_x_char + 1, start_y_char + 1,
                self.get_moved_string(),
                True, True)

            self.moved_text = []
            self.dragging_delta_char_x = 0
            self.dragging_delta_char_y = 0

            self.canvas.update()

        self.has_selection = True

    def on_click_pressed(self, click, arg, x, y):
        if not self._active:
            return

        self.click_released = False

    def on_click_released(self, click, arg, x, y):
        if not self._active:
            return

        self.click_released = True

    def on_click_stopped(self, click):
        if not self._active:
            return

        if not self.click_released:
            return

        self.drag_start_x = 0
        self.drag_start_y = 0

        self.dragging_delta_char_x = 0
        self.dragging_delta_char_y = 0

        self.selection_start_x_char = -1
        self.selection_start_y_char = -1

        self.selection_delta_char_x = 0
        self.selection_delta_char_y = 0

        self.has_selection = False
        self.is_dragging = False

        self.click_released = False

        self.selection.set_visible(False)

    def update_selection(self):
        if self.selection.get_parent() is None:
            self.canvas.fixed.put(self.selection, 0, 0)

        start_x_char, start_y_char, width, height = self.translate(
                self.selection_start_x_char,
                self.selection_start_y_char,
                self.selection_delta_char_x,
                self.selection_delta_char_y)

        self.canvas.fixed.move(
            self.selection,
            (start_x_char + self.dragging_delta_char_x + 1) * self.x_mul,
            (start_y_char + self.dragging_delta_char_y + 1) * self.y_mul)

        self.selection.set_size_request(
            (width - 1) * self.x_mul,
            (height - 1) * self.y_mul)

    def rotate(self, angle):
        if angle not in [90, -90]:
            raise ValueError("Angle must be 90 or -90 degrees")

        self.canvas.add_undo_action(_("Rotate"))

        start_x_char, start_y_char, width, height = self.translate(
                self.selection_start_x_char,
                self.selection_start_y_char,
                self.selection_delta_char_x,
                self.selection_delta_char_y)

        for y in range(1, int(height)):
            line = []
            for x in range(1, int(width)):
                line.append(
                    self.canvas.get_char_at(
                        start_x_char + x,
                        start_y_char + y
                    ) or " ")
            self.moved_text.append(line)

        self.delete_selection()

        if angle == 90:
            self.moved_text = list(zip(*self.moved_text[::-1]))
        elif angle == -90:
            self.moved_text = list(reversed(list(zip(*self.moved_text))))

        self.moved_text = [list(row) for row in self.moved_text]

        center_x = start_x_char + (width - 2) // 2
        center_y = start_y_char + (height - 2) // 2

        self.selection_start_x_char = center_x - (height - 2) // 2 + 1
        self.selection_start_y_char = center_y - (width - 2) // 2 + 1
        self.selection_delta_char_x = height - 2
        self.selection_delta_char_y = width - 2

        start_x_char, start_y_char, width, height = self.translate(
                self.selection_start_x_char,
                self.selection_start_y_char,
                self.selection_delta_char_x,
                self.selection_delta_char_y)

        self.delete_selection()

        self.canvas.draw_text(
            start_x_char + 1,
            start_y_char + 1,
            self.get_moved_string(),
            True, True)

        self.update_selection()

        self.canvas.update()

        self.moved_text = []

    def delete_selection(self, *args):
        start_x_char, start_y_char, width, height = self.translate(
                self.selection_start_x_char,
                self.selection_start_y_char,
                self.selection_delta_char_x,
                self.selection_delta_char_y
        )

        for y in range(1, int(height)):
            for x in range(1, int(width)):
                self.canvas.set_char_at(
                    start_x_char + x,
                    start_y_char + y,
                    ' ',
                    True
                )

        self.canvas.update()

    def translate(self, start_x, start_y, width, height):
        if width < 0:
            width = -width
            start_x -= width
        if height < 0:
            height = - height
            start_y -= height
        width += 2
        height += 2
        start_x -= 1
        start_y -= 1
        return start_x, start_y, width, height

    def get_moved_string(self):
        text = ""
        for line in self.moved_text:
            for char in line:
                text += char
            text += '\n'

        return text

    def copy_selection(self, *args):
        start_x_char, start_y_char, width, height = self.translate(
                self.selection_start_x_char,
                self.selection_start_y_char,
                self.selection_delta_char_x,
                self.selection_delta_char_y
        )

        selected_text = ""

        for y in range(1, int(height)):
            line = ""
            for x in range(1, int(width)):
                line += self.canvas.get_char_at(
                        start_x_char + x,
                        start_y_char + y
                    ) or " "
            selected_text += line + "\n"

        clipboard = Gdk.Display().get_default().get_clipboard()
        clipboard.set(selected_text)
