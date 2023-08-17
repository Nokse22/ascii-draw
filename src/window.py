# window.py
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
from gi.repository import Gdk

class AsciiDrawWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'AsciiDrawWindow'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.toolbar_view = Adw.ToolbarView()
        headerbar = Adw.HeaderBar()
        self.toolbar_view.add_top_bar(headerbar)
        self.set_title("ASCII Draw")
        self.set_default_size(600, 500)

        self.set_content(self.toolbar_view)

        self.x_mul = 12
        self.y_mul = 24

        self.canvas_x = 60
        self.canvas_y = 30
        self.grid = Gtk.Grid(css_classes=["ascii-textview"], halign=Gtk.Align.START, valign=Gtk.Align.START)

        for y in range(self.canvas_y):
            for x in range(self.canvas_x):
                self.grid.attach(Gtk.Label(label="", css_classes=["ascii"], width_request=self.x_mul, height_request=self.y_mul), x, y, 1, 1)

        self.styles = [
                ["═", "║", "╔", "╗", "╝","╚"],
                ["-", "|", "+", "+", "+","+"],
                ["_", "|", " ", " ", "|","|"],
                ["•", ":", "•", "•", "•","•"],
                ["˜", "|", "|", "|", " "," "],
        ]
        action_bar = Gtk.ActionBar()
        rectangle_button = Gtk.ToggleButton(icon_name="window-maximize-symbolic")
        rectangle_button.connect("clicked", self.on_choose_rectangle)
        action_bar.pack_start(rectangle_button)

        line_button = Gtk.ToggleButton(icon_name="function-linear-symbolic")
        line_button.connect("clicked", self.on_choose_line)
        line_button.set_group(rectangle_button)
        action_bar.pack_start(line_button)

        text_button = Gtk.ToggleButton(icon_name="format-text-plaintext-symbolic")
        text_button.connect("clicked", self.on_choose_text)
        text_button.set_group(rectangle_button)
        action_bar.pack_start(text_button)

        free_button = Gtk.ToggleButton(icon_name="document-edit-symbolic")
        free_button.connect("clicked", self.on_choose_free)
        free_button.set_group(rectangle_button)
        action_bar.pack_start(free_button)

        text_char_button = Gtk.MenuButton(icon_name="preferences-color-symbolic")
        text_char_popover = Gtk.Popover()
        text_char_button.set_popover(text_char_popover)
        entry = Gtk.Entry(max_length=1, width_chars=1)
        entry.connect("activate", self.change_free_char)
        text_char_popover.set_child(entry)
        action_bar.pack_start(text_char_button)

        eraser_button = Gtk.ToggleButton(icon_name="switch-off-symbolic")
        eraser_button.connect("clicked", self.on_choose_eraser)
        eraser_button.set_group(rectangle_button)
        action_bar.pack_start(eraser_button)

        clear_button = Gtk.Button(icon_name="user-trash-symbolic")
        clear_button.connect("clicked", self.clear)
        action_bar.pack_end(clear_button)

        styles_button = Gtk.MenuButton(icon_name="preferences-color-symbolic")
        styles_popover = Gtk.Popover()
        styles_button.set_popover(styles_popover)
        action_bar.pack_start(styles_button)

        styles_box = Gtk.Box(orientation=1, spacing = 6)
        styles_popover.set_child(styles_box)

        style = self.styles[0]
        name = style[0] + style[0] + style[0] + style[0] + style[3]
        style1_btn = Gtk.ToggleButton(label=name, css_classes=["flat"], active=True)
        style1_btn.connect("toggled", self.change_style, styles_box)

        for style in self.styles:
            name = style[0] + style[0] + style[0] + style[0] + style[3]
            style_btn = Gtk.ToggleButton(label=name, css_classes=["flat"])
            style_btn.set_group(style1_btn)
            style_btn.connect("toggled", self.change_style, styles_box)
            styles_box.append(style_btn)

        increase_button = Gtk.Button(icon_name="list-add-symbolic")
        increase_button.connect("clicked", self.increase_width)
        headerbar.pack_end(increase_button)

        copy_button = Gtk.Button(icon_name="edit-copy-symbolic")
        copy_button.connect("clicked", self.copy_content)
        headerbar.pack_end(copy_button)

        self.toolbar_view.add_bottom_bar(action_bar)

        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_draw_func(self.drawing_area_draw, None)

        self.overlay = Gtk.Overlay()
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_child(self.overlay)
        self.overlay.set_child(self.grid)
        self.overlay.add_overlay(self.drawing_area)
        self.toolbar_view.set_content(scrolled_window)

        drag = Gtk.GestureDrag()
        drag.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        drag.connect("drag-begin", self.on_drag_begin)
        drag.connect("drag-update", self.on_drag_follow)
        drag.connect("drag-end", self.on_drag_end)
        self.drawing_area.add_controller(drag)

        click = Gtk.GestureClick()
        click.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        click.connect("pressed", self.on_click_pressed)
        click.connect("released", self.on_click_released)
        click.connect("stopped", self.on_click_stopped)
        self.drawing_area.add_controller(click)

        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0

        self.tool = ""
        self.style = 1
        self.free_char = "+"

        # self.connect(key-press-event)

    def copy_content(self, btn):
        text = ""
        for y in range(self.canvas_y):
            for x in range(self.canvas_x):
                child = self.grid.get_child_at(x, y)
                if child:
                    char = child.get_label()
                    if char == None or char == "":
                        char = " "
                    text += char
            text += "\n"

        clipboard = Gdk.Display().get_default().get_clipboard()
        clipboard.set(text)

    def change_free_char(self, entry):
        self.free_char = entry.get_text()
        print(self.free_char)

    def increase_width(self, btn):
        for y in range(self.canvas_y):
            self.grid.attach(Gtk.Label(label=" ", css_classes=["ascii"], width_request=self.x_mul, height_request=self.y_mul), self.canvas_x + 1, y, 1, 1)
        self.canvas_x += 1

    def change_style(self, btn, box):
        child = box.get_first_child()
        index = 1
        while child != None:
            if child.get_active():
                self.style = index
                print(index)
                return
            child = child.get_next_sibling()
            index += 1


    def on_click_pressed(self, click, x, y, arg):
        pass

    def on_click_released(self, click, x, y, arg):
        x_char = int(self.start_x / self.x_mul)
        y_char = int(self.start_y / self.y_mul)

        if self.tool == "TEXT":
            self.write_text(x_char, y_char)

    def on_key_pressed(self, event, arg):
        print(event)

    def on_click_stopped(self, arg):
        pass

    def on_choose_rectangle(self, btn):
        if btn.get_active():
            self.tool = "RECTANGLE"
        else:
            self.tool = ""

    def on_choose_line(self, btn):
        if btn.get_active():
            self.tool = "LINE"
        else:
            self.tool = ""

    def on_choose_text(self, btn):
        if btn.get_active():
            self.tool = "TEXT"
        else:
            self.tool = ""

    def on_choose_free(self, btn):
        if btn.get_active():
            self.tool = "FREE"
        else:
            self.tool = ""

    def on_choose_eraser(self, btn):
        if btn.get_active():
            self.tool = "ERASER"
        else:
            self.tool = ""

    def clear(self, btn=None):
        print("clear")
        for y in range(self.canvas_y):
            for x in range(self.canvas_x):
                child = self.grid.get_child_at(x, y)
                if not child:
                    continue
                self.grid.remove(child)
                self.grid.attach(Gtk.Label(label="", css_classes=["ascii"], width_request=self.x_mul, height_request=self.y_mul), x, y, 1, 1)

    def on_drag_begin(self, gesture, start_x, start_y):
        self.start_x = start_x # round((start_x) / self.x_mul) * self.x_mul - self.x_mul/2
        self.start_y = start_y # round((start_y) / self.y_mul) * self.y_mul + self.y_mul/2

    def on_drag_follow(self, gesture, end_x, end_y):
        self.end_x = end_x # round((end_x) / self.x_mul) * self.x_mul
        self.end_y = end_y # round((end_y) / self.y_mul) * self.y_mul
        self.drawing_area.queue_draw()

        if self.tool == "FREE":
            self.draw_char((self.start_x + self.end_x)/self.x_mul, (self.start_y + self.end_y)/self.y_mul)

        if self.tool == "ERASER":
            self.erase_char((self.start_x + self.end_x)/self.x_mul, (self.start_y + self.end_y)/self.y_mul)

    def on_drag_end(self, gesture, delta_x, delta_y):
        start_x_char = self.start_x // self.x_mul
        start_y_char = self.start_y // self.y_mul
        width = int((delta_x + self.start_x) // self.x_mul - start_x_char) # round((end_x) / self.x_mul) * self.x_mul
        height = int((delta_y + self.start_y) // self.y_mul - start_y_char) # round((end_y) / self.y_mul) * self.y_mul
        self.drawing_area.queue_draw()

        # self.clear()

        if self.tool == "RECTANGLE":
            if width < 0:
                width = -width
                start_x_char -= width
            width += 1
            if height < 0:
                height = - height
                start_y_char -= height
            height += 1
            self.draw_rectangle(start_x_char, start_y_char, width, height)

        if self.tool == "LINE":
            if width < 0:
                width = -width
                start_x_char -= width
            width += 1
            if height < 0:
                height = - height
                start_y_char -= height
            height += 1
            self.draw_line(start_x_char, start_y_char, width, height)

    def drawing_area_draw(self, area, cr, width, height, data):
        cr.save()
        if self.tool == "RECTANGLE":
            cr.rectangle(self.start_x, self.start_y, self.end_x, self.end_y)
            pass
        elif self.tool == "LINE":
            cr.rectangle(self.start_x, self.start_y, self.end_x, self.end_y)
        cr.stroke()
        cr.restore()

    def write_text(self, x_coord, y_coord):
        entry = Gtk.Entry(margin_start=x_coord*self.x_mul,
                margin_top=y_coord*self.y_mul,
                halign=Gtk.Align.START, valign=Gtk.Align.START,
                css_classes=["mono-entry", "flat"],
                height_request = 24)
        self.overlay.add_overlay(entry)
        entry.connect("activate", self.insert_text, x_coord, y_coord)

    def insert_text(self, entry, x_coord, y_coord):
        text = entry.get_text()
        for char in text:
            child = self.grid.get_child_at(x_coord, y_coord)
            if not child:
                continue
            child.set_label(char)
            x_coord += 1
        self.overlay.remove_overlay(entry)

    def draw_char(self, x_coord, y_coord):
        child = self.grid.get_child_at(x_coord, y_coord)
        if child:
            child.set_label(self.free_char)

    def erase_char(self, x_coord, y_coord):
        child = self.grid.get_child_at(x_coord, y_coord)
        if child:
            child.set_label("")

    def draw_rectangle(self, start_x_char, start_y_char, width, height):
        print(width)
        print(height)

        vertical = self.vertical()
        horizontal = self.horizontal()

        if width <= 1 or height <= 1:
            return
        for x in range(width - 2):
            child = self.grid.get_child_at(start_x_char + x + 1, start_y_char)
            if child:
                child.set_label(horizontal)
        for x in range(width - 2):
            child = self.grid.get_child_at(start_x_char + x + 1, start_y_char + height - 1)
            if child:
                child.set_label(horizontal)
        for y in range(height - 2):
            child = self.grid.get_child_at(start_x_char, start_y_char + y + 1)
            if child:
                child.set_label(vertical)
        for y in range(height - 2):
            child = self.grid.get_child_at(start_x_char + width - 1, start_y_char + y + 1)
            if child:
                child.set_label(vertical)

        child = self.grid.get_child_at(start_x_char + width - 1, start_y_char)
        if child:
            child.set_label(self.top_right())
        child = self.grid.get_child_at(start_x_char + width - 1, start_y_char + height - 1)
        if child:
            child.set_label(self.bottom_right())
        child = self.grid.get_child_at(start_x_char, start_y_char)
        if child:
            child.set_label(self.top_left())
        child = self.grid.get_child_at(start_x_char, start_y_char + height - 1)
        if child:
            child.set_label(self.bottom_left())
        # ╗ ╝ ╔ ╚

        self.drawing_area.queue_draw()

    def horizontal(self):
        return self.styles[self.style - 1][0]
    def vertical(self):
        return self.styles[self.style - 1][1]
    def top_left(self):
        return self.styles[self.style - 1][2]
    def top_right(self):
        return self.styles[self.style - 1][3]
    def bottom_right(self):
        return self.styles[self.style - 1][4]
    def bottom_left(self):
        return self.styles[self.style - 1][5]


    def draw_line(self, start_x_char, start_y_char, width, height):
        print(width)
        print(height)

        vertical = self.vertical()
        horizontal = self.horizontal()

        if width < 0:
            for x in range(abs(width) + 2):
                child = self.grid.get_child_at(start_x_char + x + width, start_y_char)
                if not child:
                    continue
                child.set_label(horizontal)
        else:
            for x in range(width - 2):
                child = self.grid.get_child_at(start_x_char + x + 1, start_y_char)
                if not child:
                    continue
                child.set_label(horizontal)

        if height < 0:
            for y in range(abs(height)):
                child = self.grid.get_child_at(start_x_char + width - 1, start_y_char + y + height)
                if not child:
                    continue
                child.set_label(vertical)
        else:
            for y in range(height - 2):
                child = self.grid.get_child_at(start_x_char + width - 1, start_y_char + y + 1)
                if not child:
                    continue
                child.set_label(vertical)

        if width > 0 and height > 0:
            child = self.grid.get_child_at(start_x_char + width - 1, start_y_char)
            if child:
                child.set_label("╗")
        elif width > 0 and height < 0:
            child = self.grid.get_child_at(start_x_char + width - 1, start_y_char)
            if child:
                child.set_label("╝")
        elif width < 0 and height > 0:
            child = self.grid.get_child_at(start_x_char + width - 1, start_y_char)
            if child:
                child.set_label("╔")
        elif width < 0 and height < 0:
            child = self.grid.get_child_at(start_x_char + width - 1, start_y_char)
            if child:
                child.set_label("╚")
        # ╗ ╝ ╔ ╚

        self.drawing_area.queue_draw()
