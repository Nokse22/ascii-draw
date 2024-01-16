# select.py
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

class Select(GObject.GObject):
    def __init__(self, _canvas, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.canvas = _canvas

        self._active = False
        self._style = 0

        self.canvas.drag_gesture.connect("drag-begin", self.on_drag_begin)
        self.canvas.drag_gesture.connect("drag-update", self.on_drag_follow)
        self.canvas.drag_gesture.connect("drag-end", self.on_drag_end)

        self.canvas.click_gesture.connect("pressed", self.on_click_pressed)
        self.canvas.click_gesture.connect("released", self.on_click_released)
        self.canvas.click_gesture.connect("stopped", self.on_click_stopped)

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

        self.moved_text: str = ''

        self.click_released = False

    @GObject.Property(type=bool, default=False)
    def active(self):
        return self._active

    @active.setter
    def active(self, value):
        self._active = value
        self.notify('active')
        if value:
            self.canvas.drawing_area.set_draw_func(self.drawing_function, None)
        else:
            self.selection_start_x_char = -1
            self.selection_start_y_char = -1

            self.selection_delta_char_x = 0
            self.selection_delta_char_y = 0

            self.canvas.drawing_area.queue_draw()

    @GObject.Property(type=str, default='#')
    def style(self):
        return self._style

    @style.setter
    def style(self, value):
        self._style = value
        self.notify('style')

    def on_drag_begin(self, gesture, this_x, this_y):
        if not self._active: return

        this_x_char = this_x // self.x_mul
        this_y_char = this_y // self.y_mul

        start_x_char, start_y_char, width, height = self.translate(self.selection_start_x_char, self.selection_start_y_char, self.selection_delta_char_x, self.selection_delta_char_y)

        if (this_x_char > (start_x_char)
                and this_x_char < (start_x_char + width)
                and this_y_char > (start_y_char)
                and this_y_char < (start_y_char + height)):
            self.is_dragging = True

            self.canvas.add_undo_action(_("Move"))

            for y in range(1, int(height)):
                for x in range(1, int(width)):
                    self.moved_text += self.canvas.get_char_at(start_x_char + x, start_y_char + y) or " "
                self.moved_text += '\n'

            # Delete selection
            for y in range(1, int(height)):
                for x in range(1, int(width)):
                    self.canvas.set_char_at(start_x_char + x, start_y_char + y, ' ', True)

                start_x_char, start_y_char, width, height = self.translate(self.selection_start_x_char, self.selection_start_y_char, self.selection_delta_char_x, self.selection_delta_char_y)
                self.canvas.draw_text(start_x_char + self.dragging_delta_char_x + 1,
                                start_y_char + self.dragging_delta_char_y + 1, self.moved_text, True, False)
            self.canvas.update()
        else:
            print("new selection")
            self.selection_start_x_char = this_x // self.x_mul
            self.selection_start_y_char = this_y // self.y_mul

            self.drag_start_x = this_x # used to fix drag alignment
            self.drag_start_y = this_y # used to fix drag alignment

            self.is_dragging = False

    def on_drag_follow(self, gesture, delta_x, delta_y):
        if not self._active: return

        if self.is_dragging:
            new_delta_x = (self.drag_start_x + delta_x) // self.x_mul - self.drag_start_x // self.x_mul
            new_delta_y = (self.drag_start_y + delta_y) // self.y_mul - self.drag_start_y // self.y_mul

            if new_delta_x != self.dragging_delta_char_x or new_delta_y != self.dragging_delta_char_y:
                self.dragging_delta_char_x = new_delta_x
                self.dragging_delta_char_y = new_delta_y

                self.canvas.clear_preview()

                start_x_char, start_y_char, width, height = self.translate(self.selection_start_x_char, self.selection_start_y_char, self.selection_delta_char_x, self.selection_delta_char_y)

                self.canvas.draw_text(start_x_char + self.dragging_delta_char_x + 1,
                                start_y_char + self.dragging_delta_char_y + 1, self.moved_text, True, False)

                self.canvas.drawing_area.queue_draw()
                self.canvas.update()
        else:
            self.selection_delta_char_x = (self.drag_start_x + delta_x) // self.x_mul - self.drag_start_x // self.x_mul
            self.selection_delta_char_y = (self.drag_start_y + delta_y) // self.y_mul - self.drag_start_y // self.y_mul

            self.canvas.drawing_area.queue_draw()

    def on_drag_end(self, gesture, delta_x, delta_y):
        if not self._active: return

        if self.is_dragging:
            self.selection_start_x_char += self.dragging_delta_char_x
            self.selection_start_y_char += self.dragging_delta_char_y
            self.is_dragging = False

            self.canvas.clear_preview()

            start_x_char, start_y_char, width, height = self.translate(self.selection_start_x_char, self.selection_start_y_char, self.selection_delta_char_x, self.selection_delta_char_y)

            self.canvas.draw_text(start_x_char + 1, start_y_char + 1, self.moved_text, True, True)
            self.moved_text = ''
            self.dragging_delta_char_x = 0
            self.dragging_delta_char_y = 0

            self.canvas.update()

        self.has_selection = True

    def on_click_pressed(self, click, arg, x, y):
        if not self._active: return
        print("pressed")

        self.click_released = False

    def on_click_released(self, click, arg, x, y):
        if not self._active: return
        print("released")

        self.click_released = True

    def on_click_stopped(self, click):
        if not self._active: return
        print(f"stopped {self.click_released}")

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

        self.canvas.drawing_area.queue_draw()

    def drawing_function(self, area, cr, width, height, data):
        # cr.save()
        cr.set_source_rgb(0.208, 0.518, 0.894)
        cr.set_dash([5], 0)

        start_x_char, start_y_char, width, height = self.translate(self.selection_start_x_char, self.selection_start_y_char, self.selection_delta_char_x, self.selection_delta_char_y)

        cr.rectangle((start_x_char + self.dragging_delta_char_x + 1) * self.x_mul, # + self.x_mul/2,
                            (start_y_char + self.dragging_delta_char_y + 1) * self.y_mul, # + self.y_mul/2,
                            (width - 1) * self.x_mul,
                            (height - 1) * self.y_mul)

        # TEST
        # cr.set_source_rgb (0.0, 0.0, 0.0)
        # cr.select_font_face ("Monospace")
        # cr.set_font_size (20)
        # cr.move_to ((width - 1) * self.x_mul, (height - 1) * self.y_mul)
        # cr.show_text("Hello everybodyHello everybodyHello everybodyHello everybodyHello everybodyHello everybodyHello everybodyHello everybodyHello everybodyHello everybodyHello everybody")

        # cr.move_to (0, 50)
        # cr.show_text("Hello nobody!")

        cr.stroke()
        # cr.restore()

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
