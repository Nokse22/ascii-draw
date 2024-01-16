# text.py
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

import pyfiglet

class Text(GObject.GObject):
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

        self.start_x = 0
        self.start_y = 0

        self.x_mul = 12
        self.y_mul = 24

        self.text_x = 0
        self.text_y = 0

        self.text_drag_x = 0
        self.text_drag_y = 0

        self._text = ''

        self.selected_font = "Normal"

        self._transparent = False

    def set_selected_font(self, value):
        self.selected_font = value

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

    @GObject.Property(type=bool, default=False)
    def transparent(self):
        return self._transparent

    @transparent.setter
    def transparent(self, value):
        self._transparent = value
        self.notify('transparent')

    @GObject.Property(type=str, default='')
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        self.notify('text')

    def on_drag_begin(self, gesture, start_x, start_y):
        if not self._active: return

    def on_drag_follow(self, gesture, x, y):
        if not self._active: return

        x_char = int(x / self.x_mul)
        y_char = int(y / self.y_mul)

        self.text_drag_x = x_char
        self.text_drag_y = y_char

        self.canvas.clear_preview()
        self.preview_text()

    def on_drag_end(self, gesture, delta_x, delta_y):
        if not self._active: return

        self.text_x += self.text_drag_x
        self.text_y += self.text_drag_y

        self.text_drag_x = 0
        self.text_drag_y = 0

    def on_click_pressed(self, click, arg, x, y):
        if not self._active: return

        x_char = int(x / self.x_mul)
        y_char = int(y / self.y_mul)

        self.text_x = x_char
        self.text_y = y_char

        self.canvas.clear_preview()
        self.preview_text()

    def on_click_stopped(self, click):
        if not self._active: return
        pass

    def on_click_released(self, click, arg, x, y):
        if not self._active: return
        pass

    def insert_text(self):
        self.canvas.add_undo_action(_("Text"))
        self.canvas.clear_preview()

        text = self._text
        if self.selected_font != "Normal":
            text = pyfiglet.figlet_format(text, font=self.selected_font)

        self.canvas.draw_text(self.text_x + self.text_drag_x, self.text_y + self.text_drag_y, text, self._transparent, True)
        self.canvas.update()

    def preview_text(self):
        self.canvas.clear_preview()

        text = self._text
        if self.selected_font != "Normal":
            text = pyfiglet.figlet_format(text, font=self.selected_font)

        self.canvas.draw_text(self.text_x + self.text_drag_x, self.text_y + self.text_drag_y, text, self._transparent, False)

        self.canvas.update_preview()
