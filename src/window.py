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
from gi.repository import Gdk, Gio

class AsciiDrawWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'AsciiDrawWindow'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.settings = Gio.Settings.new('io.github.nokse22.asciidraw')

        self.props.width_request=400
        self.props.height_request=400

        self.toolbar_view = Adw.ToolbarView()
        headerbar = Adw.HeaderBar()
        self.toolbar_view.add_top_bar(headerbar)
        self.set_title("ASCII Draw")

        self.settings.bind("window-width", self, "default-width", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("window-height", self, "default-height", Gio.SettingsBindFlags.DEFAULT)

        self.overlay_split_view = Adw.OverlaySplitView()

        sidebar_condition = Adw.BreakpointCondition.new_length(1, 600, 2)
        sidebar_breakpoint = Adw.Breakpoint.new(sidebar_condition)

        sidebar_breakpoint.set_condition(sidebar_condition)
        sidebar_breakpoint.add_setter(self.overlay_split_view, "collapsed", True)
        # sidebar_breakpoint.add_setter(sidebar_button, "visible", True)

        self.add_breakpoint(sidebar_breakpoint)

        self.set_content(self.toolbar_view)

        self.x_mul = 12
        self.y_mul = 24

        self.canvas_x = 60
        self.canvas_y = 30
        self.grid = Gtk.Grid(css_classes=["ascii-textview"], halign=Gtk.Align.START, valign=Gtk.Align.START)
        self.preview_grid = Gtk.Grid(css_classes=["ascii-preview"], halign=Gtk.Align.START, valign=Gtk.Align.START, can_focus=False)

        for y in range(self.canvas_y):
            for x in range(self.canvas_x):
                self.grid.attach(Gtk.Label(label="", css_classes=["ascii"], width_request=self.x_mul, height_request=self.y_mul), x, y, 1, 1)
                self.preview_grid.attach(Gtk.Label(label="", css_classes=["ascii"], width_request=self.x_mul, height_request=self.y_mul), x, y, 1, 1)

        self.empty_grid = self.preview_grid

        self.styles = [
<<<<<<< ours
                ["─", "─", "│", "│", "┌", "┐", "┘","└", "┼", "├", "┤", "┴","┬", "▲", "▼", "►", "◄"],
                ["═", "═", "║", "║", "╔", "╗", "╝","╚", "┼", "├", "┤", "┴","┬", "^", "V", ">", "<"],
=======
                ["═", "═", "║", "║", "╔", "╗", "╝","╚", "┼", "├", "┤", "┴","┬", "▲", "▼", "►", "◄"],
>>>>>>> theirs
                ["-", "-", "│", "│", "+", "+", "+","+", "┼", "├", "┤", "┴","┬", "▲", "▼", "►", "◄"],
                ["_", "_", "│", "│", " ", " ", "│","│", "┼", "├", "┤", "┴","┬", "▲", "▼", "►", "◄"],
                ["•", "•", ":", ":", "•", "•", "•","•", "┼", "├", "┤", "┴","┬", "▲", "▼", "►", "◄"],
                ["˜", "˜", "│", "│", "│", "│", " "," ", "┼", "├", "┤", "┴","┬", "▲", "▼", "►", "◄"],
                ["═", "═", "│", "│", "╒", "╕", "╛","╘", "┼", "├", "┤", "┴","┬", "▲", "▼", "►", "◄"],
                ["▄", "▀", "▐", "▌", " ", " ", " "," ", "┼", "├", "┤", "┴","┬", "▲", "▼", "►", "◄"],
                ["─", "─", "│", "│", "╔", "╗", "╝","╚", "┼", "├", "┤", "┴","┬", "▲", "▼", "►", "◄"],
<<<<<<< ours
=======
                ["─", "─", "│", "│", "┌", "┐", "┘","└", "┼", "├", "┤", "┴","┬", "▲", "▼", "►", "◄"],
>>>>>>> theirs
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

        eraser_button = Gtk.ToggleButton(icon_name="switch-off-symbolic")
        eraser_button.connect("clicked", self.on_choose_eraser)
        eraser_button.set_group(rectangle_button)
        action_bar.pack_start(eraser_button)

        arrow_button = Gtk.ToggleButton(icon_name="mail-forward-symbolic")
        arrow_button.connect("clicked", self.on_choose_arrow)
        arrow_button.set_group(rectangle_button)
        action_bar.pack_start(arrow_button)

        clear_button = Gtk.Button(icon_name="user-trash-symbolic")
        clear_button.connect("clicked", self.clear, self.grid)
        action_bar.pack_end(clear_button)

        styles_button = Gtk.MenuButton(icon_name="preferences-color-symbolic")
        styles_popover = Gtk.Popover()
        styles_button.set_popover(styles_popover)
        action_bar.pack_start(styles_button)

        styles_box = Gtk.Box(orientation=1, spacing = 6)
        styles_popover.set_child(styles_box)

        style = self.styles[0]
        name = style[0] + style[0] + style[0] + style[0] + style[5]
        style1_btn = Gtk.ToggleButton(label=name, css_classes=["flat"], active=True)
        style1_btn.connect("toggled", self.change_style, styles_box)

        for style in self.styles:
            name = style[0] + style[0] + style[0] + style[0] + style[5]
            style_btn = Gtk.ToggleButton(label=name, css_classes=["flat"])
            style_btn.set_group(style1_btn)
            style_btn.connect("toggled", self.change_style, styles_box)
            styles_box.append(style_btn)

        save_button = Gtk.Button(label="Save")
        save_button.connect("clicked", self.save)
        headerbar.pack_start(save_button)

        show_sidebar_button = Gtk.Button(icon_name="sidebar-show-right-symbolic")
        show_sidebar_button.connect("clicked", self.show_sidebar)
        headerbar.pack_end(show_sidebar_button)

        increase_button = Gtk.MenuButton(icon_name="list-add-symbolic")
        increase_canvas_popover = Gtk.Popover()
        increase_button.set_popover(increase_canvas_popover)
        # increase_button.connect("clicked", self.increase_size, 1, 1)
        headerbar.pack_end(increase_button)

        increase_box = Gtk.Box(orientation=1)
        increase_canvas_popover.set_child(increase_box)

        width_row = Adw.SpinRow(title="Width")
        width_row.set_range(1, 100)
        increase_box.append(width_row)
        height_row = Adw.SpinRow(title="Height")
        height_row.set_range(1, 100)
        increase_box.append(height_row)
        increase_box.append(Gtk.Button(label="Increase canvas"))

        copy_button = Gtk.Button(icon_name="edit-copy-symbolic")
        copy_button.connect("clicked", self.copy_content)
        headerbar.pack_end(copy_button)

        self.toolbar_view.add_bottom_bar(action_bar)

        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_draw_func(self.drawing_area_draw, None)

        self.overlay = Gtk.Overlay(halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER)
        scrolled_window = Gtk.ScrolledWindow(hexpand=True)
        scrolled_window.connect("scroll-child", self.scrolled)
        scrolled_window.set_child(self.overlay)

        self.overlay_split_view.set_sidebar_width_fraction(0.4)
        self.overlay_split_view.set_max_sidebar_width(300)
        self.overlay_split_view.set_sidebar_position(1)
        self.overlay_split_view.set_content(scrolled_window)

        box1 = Gtk.Box()
        flow_box = Gtk.FlowBox()
        flow_box.set_selection_mode(0)
        scrolled = Gtk.ScrolledWindow(hexpand=True)
        scrolled.set_child(flow_box)
        box1.append(Gtk.Separator())
        box1.append(scrolled)

        self.overlay_split_view.set_sidebar(box1)

        self.overlay.set_child(self.grid)
        self.overlay.add_overlay(self.preview_grid)

        self.overlay.add_overlay(self.drawing_area)

        self.toolbar_view.set_content(self.overlay_split_view)

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

        self.chars = ""

        char = bytes([33]).decode('cp437')
        prev_button = Gtk.ToggleButton(label=char, css_classes=["flat"])
        prev_button.connect("toggled", self.change_char, flow_box)
        flow_box.append(prev_button)

        for i in range(34, 255):
            char = bytes([i]).decode('cp437')
            new_button = Gtk.ToggleButton(label=char, css_classes=["flat"])
            new_button.connect("toggled", self.change_char, flow_box)
            flow_box.append(new_button)
            new_button.set_group(prev_button)

    def scrolled(self, scrolled_window, horizontal):
        print("scrolled")

    def save(self, btn):
        dialog = Gtk.FileChooserNative(
            title="Save File",
            transient_for=self,
            action=Gtk.FileChooserAction.SAVE,
            modal=True
        )

        dialog.set_accept_label("Save")
        dialog.set_cancel_label("Cancel")

        response = dialog.show()

        dialog.connect("response", self.on_save_file_response)

    def on_save_file_response(self, dialog, response):
        path = dialog.get_file().get_path()

        if response == Gtk.ResponseType.CANCEL:
            dialog.destroy()
        elif response == Gtk.ResponseType.ACCEPT:
            try:
                with open(path, 'w') as file:
                    file.write(self.get_canvas_content())
                print(f"Content written to {path} successfully.")
            except IOError:
                print(f"Error writing to {path}.")

        dialog.destroy()
    def change_char(self, btn, flow_box):
        self.free_char = btn.get_label()
        self.tool = "FREE"

    def show_sidebar(self, btn):
        self.overlay_split_view.set_show_sidebar(not self.overlay_split_view.get_show_sidebar())

    def get_canvas_content(self):
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
        return text

    def copy_content(self, btn):
        text = self.get_canvas_content()

        clipboard = Gdk.Display().get_default().get_clipboard()
        clipboard.set(text)

    def increase_size(self, btn, x_inc, y_inc):
        for column in range(x_inc):
            for y in range(self.canvas_y):
                self.grid.attach(Gtk.Label(label=" ", css_classes=["ascii"], width_request=self.x_mul, height_request=self.y_mul), self.canvas_x + 1, y, 1, 1)
                self.preview_grid.attach(Gtk.Label(label=" ", css_classes=["ascii"], width_request=self.x_mul, height_request=self.y_mul), self.canvas_x + 1, y, 1, 1)
            self.canvas_y += 1
        for line in range(y_inc):
            for x in range(self.canvas_x):
                self.grid.attach(Gtk.Label(label=" ", css_classes=["ascii"], width_request=self.x_mul, height_request=self.y_mul), x, self.canvas_y + 1, 1, 1)
                self.preview_grid.attach(Gtk.Label(label=" ", css_classes=["ascii"], width_request=self.x_mul, height_request=self.y_mul), x, self.canvas_y + 1, 1, 1)
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

    def on_choose_arrow(self, btn):
        if btn.get_active():
            self.tool = "ARROW"
        else:
            self.tool = ""

    def clear(self, btn=None, grid=None):
        for y in range(self.canvas_y):
            for x in range(self.canvas_x):
                child = grid.get_child_at(x, y)
                if not child:
                    continue
                grid.remove(child)
                grid.attach(Gtk.Label(label="", css_classes=["ascii"], width_request=self.x_mul, height_request=self.y_mul), x, y, 1, 1)

        # self.overlay.remove_overlay(grid)
        # self.overlay.add_overlay(self.empty_grid)
        # grid = self.empty_grid

    def on_drag_begin(self, gesture, start_x, start_y):
        self.start_x = start_x # round((start_x) / self.x_mul) * self.x_mul - self.x_mul/2
        self.start_y = start_y # round((start_y) / self.y_mul) * self.y_mul + self.y_mul/2

    def on_drag_follow(self, gesture, end_x, end_y):
        start_x_char = self.start_x // self.x_mul
        start_y_char = self.start_y // self.y_mul
        width = int((end_x + self.start_x) // self.x_mul - start_x_char) # round((end_x) / self.x_mul) * self.x_mul
        height = int((end_y + self.start_y) // self.y_mul - start_y_char) # round((end_y) / self.y_mul) * self.y_mul

        self.end_x = width * self.x_mul
        self.end_y = height * self.y_mul

        if self.tool == "FREE":
            self.draw_char((self.start_x + self.end_x)/self.x_mul, (self.start_y + self.end_y)/self.y_mul)

        elif self.tool == "ERASER":
            self.erase_char((self.start_x + self.end_x)/self.x_mul, (self.start_y + self.end_y)/self.y_mul)

        elif self.tool == "RECTANGLE":
            # self.clear(None, self.preview_grid)
            if width < 0:
                width = -width
                start_x_char -= width
            width += 1
            if height < 0:
                height = - height
                start_y_char -= height
            height += 1
            self.draw_rectangle(start_x_char, start_y_char, width, height, self.preview_grid)
        elif self.tool == "LINE" or self.tool == "ARROW":
            # self.clear(None, self.preview_grid)
            if width < 0:
                width -= 1
            else:
                width += 1
            if height < 0:
                height -= 1
            else:
                height += 1
            self.draw_line(start_x_char, start_y_char, width, height, self.preview_grid)
            # self.drawing_area.queue_draw()

    def on_drag_end(self, gesture, delta_x, delta_y):
        start_x_char = self.start_x // self.x_mul
        start_y_char = self.start_y // self.y_mul
        width = int((delta_x + self.start_x) // self.x_mul - start_x_char) # round((end_x) / self.x_mul) * self.x_mul
        height = int((delta_y + self.start_y) // self.y_mul - start_y_char) # round((end_y) / self.y_mul) * self.y_mul

        self.clear(None, self.preview_grid)

        if self.tool == "RECTANGLE":
            if width < 0:
                width = -width
                start_x_char -= width
            width += 1
            if height < 0:
                height = - height
                start_y_char -= height
            height += 1
            self.draw_rectangle(start_x_char, start_y_char, width, height, self.grid)

        if self.tool == "LINE" or self.tool == "ARROW":
            if width < 0:
                width -= 1
            else:
                width += 1
            if height < 0:
                height -= 1
            else:
                height += 1
            self.draw_line(start_x_char, start_y_char, width, height, self.grid)

    def drawing_area_draw(self, area, cr, width, height, data):
        cr.save()
        # if self.tool == "LINE":
        #     cr.rectangle(self.start_x, self.start_y, self.end_x, self.end_y)
        cr.stroke()
        cr.restore()

    def write_text(self, x_coord, y_coord):
        entry = Gtk.Entry(margin_start=x_coord*self.x_mul,
                margin_top=y_coord*self.y_mul,
                halign=Gtk.Align.START, valign=Gtk.Align.START,
                css_classes=["mono-entry", "flat"],
                height_request = 24)
        self.set_focus(entry)
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
        self.set_focus(None)

    def draw_char(self, x_coord, y_coord):
        child = self.grid.get_child_at(x_coord, y_coord)
        if child:
            child.set_label(self.free_char)

    def erase_char(self, x_coord, y_coord):
        child = self.grid.get_child_at(x_coord, y_coord)
        if child:
            child.set_label("")

    def draw_rectangle(self, start_x_char, start_y_char, width, height, grid):
        print(width)
        print(height)

        top_vertical = self.top_vertical()
        top_horizontal = self.top_horizontal()

        bottom_vertical = self.bottom_vertical()
        bottom_horizontal = self.bottom_horizontal()

        if width <= 1 or height <= 1:
            return

        for x in range(width - 2):
            child = grid.get_child_at(start_x_char + x + 1, start_y_char)
            if child:
                child.set_label(top_horizontal)
        for x in range(width - 2):
            child = grid.get_child_at(start_x_char + x + 1, start_y_char + height - 1)
            if child:
                child.set_label(bottom_horizontal)
        for y in range(height - 2):
            child = grid.get_child_at(start_x_char, start_y_char + y + 1)
            if child:
                child.set_label(top_vertical)
        for y in range(height - 2):
            child = grid.get_child_at(start_x_char + width - 1, start_y_char + y + 1)
            if child:
                child.set_label(bottom_vertical)

        child = grid.get_child_at(start_x_char + width - 1, start_y_char)
        if child:
            child.set_label(self.top_right())
        child = grid.get_child_at(start_x_char + width - 1, start_y_char + height - 1)
        if child:
            child.set_label(self.bottom_right())
        child = grid.get_child_at(start_x_char, start_y_char)
        if child:
            child.set_label(self.top_left())
        child = grid.get_child_at(start_x_char, start_y_char + height - 1)
        if child:
            child.set_label(self.bottom_left())

    def draw_line(self, start_x_char, start_y_char, width, height, grid):
        arrow = self.tool == "ARROW"
        print(width)
        print(height)

        vertical = self.top_vertical()
        horizontal = self.top_horizontal()

        sideway = abs(height) == 1
        left = width < 0

<<<<<<< ours
=======
        # if arrow and sideway:
        #     if left:
        #         self.set_char_at(start_x_char + width - 1, start_y_char + height, grid, self.left_arrow())
        #     else:
        #         self.set_char_at(start_x_char + width, start_y_char + height - 1, grid, self.right_arrow())
        #     arrow = False

>>>>>>> theirs
        if width > 0 and height > 0:
            self.horizontal_line(start_y_char, start_x_char, width - 1, grid, horizontal)
            self.vertical_line(start_x_char + width - 1, start_y_char, height, grid, vertical)
            self.set_char_at(start_x_char + width - 1, start_y_char, grid, self.top_right())
            if arrow:
                self.set_char_at(start_x_char + width - 1, start_y_char + height - 1, grid, self.down_arrow())
        elif width > 0 and height < 0:
            self.horizontal_line(start_y_char, start_x_char, width - 1, grid, horizontal)
            self.vertical_line(start_x_char + width - 1, start_y_char + 1, height, grid, vertical)
            self.set_char_at(start_x_char + width - 1, start_y_char, grid, self.bottom_right())
            if arrow:
                self.set_char_at(start_x_char + width - 1, start_y_char + height + 1, grid, self.up_arrow())
        elif width < 0 and height > 0:
            self.horizontal_line(start_y_char, start_x_char + 1, width, grid, horizontal)
            self.vertical_line(start_x_char + width + 1, start_y_char, height, grid, vertical)
            self.set_char_at(start_x_char + width + 1, start_y_char, grid, self.top_left())
            if arrow:
                self.set_char_at(start_x_char + width + 1, start_y_char + height - 1, grid, self.down_arrow())
        elif width < 0 and height < 0:
            self.horizontal_line(start_y_char, start_x_char + 1, width, grid, horizontal)
            self.vertical_line(start_x_char + width + 1, start_y_char + 1, height, grid, vertical)
            self.set_char_at(start_x_char + width + 1, start_y_char, grid, self.bottom_left())
            if arrow:
                self.set_char_at(start_x_char + width + 1, start_y_char + height + 1, grid, self.up_arrow())
<<<<<<< ours

        if arrow and sideway:
            if left:
                self.set_char_at(start_x_char + width + 1, start_y_char + height - 1, grid, self.left_arrow())
            else:
                self.set_char_at(start_x_char + width, start_y_char + height - 1, grid, self.right_arrow())
=======
>>>>>>> theirs

        if width == 1:
            child = grid.get_child_at(start_x_char + width - 1, start_y_char)
            if child:
                child.set_label(vertical)
            return
        elif width == -1:
            child = grid.get_child_at(start_x_char + width + 1, start_y_char)
            if child:
                child.set_label(vertical)
            return

        if height == 1 and width < 0:
            child = grid.get_child_at(start_x_char + width + 1, start_y_char)
            if child:
                child.set_label(horizontal)
            return
        elif height == 1 and width > 0:
            child = grid.get_child_at(start_x_char + width - 1, start_y_char)
            if child:
                child.set_label(horizontal)
            return

    def set_char_at(self, x, y, grid, char):
        child = grid.get_child_at(x, y)
        if child:
            child.set_label(char)

    def vertical_line(self, x, start_y, lenght, grid, char):
        if lenght > 0:
            for y in range(abs(lenght)):
                child = grid.get_child_at(x, start_y + y)
                if not child:
                    continue
                if child.get_label() == "─":
                    child.set_label("┼")
                else:
                    child.set_label(char)
        else:
            for y in range(abs(lenght)):
                child = grid.get_child_at(x, start_y + y + lenght)
                if not child:
                    continue
                if child.get_label() == "─":
                    child.set_label("┼")
                else:
                    child.set_label(char)

    def horizontal_line(self, y, start_x, width, grid, char):
        if width > 0:
            for x in range(abs(width)):
                child = grid.get_child_at(start_x + x, y)
                if not child:
                    continue
                if child.get_label() == "│":
                    child.set_label("┼")
                else:
                    child.set_label(char)
        else:
            for x in range(abs(width)):
                child = grid.get_child_at(start_x + x + width, y)
                if not child:
                    continue
                if child.get_label() == "│":
                    child.set_label("┼")
                else:
                    child.set_label(char)

    def top_horizontal(self):
        return self.styles[self.style - 1][0]
    def bottom_horizontal(self):
        return self.styles[self.style - 1][1]
    def top_vertical(self):
        return self.styles[self.style - 1][2]
    def bottom_vertical(self):
        return self.styles[self.style - 1][3]
    def top_left(self):
        return self.styles[self.style - 1][4]
    def top_right(self):
        return self.styles[self.style - 1][5]
    def bottom_right(self):
        return self.styles[self.style - 1][6]
    def bottom_left(self):
        return self.styles[self.style - 1][7]
    def up_arrow(self):
        return self.styles[self.style - 1][13]
    def down_arrow(self):
        return self.styles[self.style - 1][14]
    def left_arrow(self):
        return self.styles[self.style - 1][16]
    def right_arrow(self):
        return self.styles[self.style - 1][15]

