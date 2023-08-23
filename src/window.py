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
from gi.repository import Gdk, Gio, GObject

import threading
import math
import time

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
        return f"The change has {len(self.changes)}"

class AsciiDrawWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'AsciiDrawWindow'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.settings = Gio.Settings.new('io.github.nokse22.asciidraw')

        self.props.width_request=350
        self.props.height_request=400

        self.toolbar_view = Gtk.Box(orientation=1, vexpand=True) #Adw.ToolbarView()
        headerbar = Adw.HeaderBar()
        self.toolbar_view.append(headerbar)#add_top_bar(headerbar)
        self.set_title("ASCII Draw")

        # self.set_default_size(800, 800)

        self.settings.bind("window-width", self, "default-width", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("window-height", self, "default-height", Gio.SettingsBindFlags.DEFAULT)

        self.overlay_split_view = Adw.Flap(vexpand=True, flap_position=1, fold_policy=0) #Adw.OverlaySplitView()
        self.overlay_split_view.set_reveal_flap(False)

        # sidebar_condition = Adw.BreakpointCondition.new_length(1, 600, 2)
        # sidebar_breakpoint = Adw.Breakpoint.new(sidebar_condition)

        # sidebar_breakpoint.set_condition(sidebar_condition)
        # sidebar_breakpoint.add_setter(self.overlay_split_view, "collapsed", True) #collapsed

        # self.add_breakpoint(sidebar_breakpoint)

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
                ["─", "─", "│", "│", "┌", "┐", "┘","└", "┼", "├", "┤", "┴","┬", "▲", "▼", ">", "<"],
                ["═", "═", "║", "║", "╔", "╗", "╝","╚", "╬", "╠", "╣", "╩","╦", "A", "V", ">", "<"],
                ["-", "-", "|", "|", "+", "+", "+","+", "+", "+", "+", "+","+", "↑", "↓", "→", "←"],
                ["_", "_", "│", "│", " ", " ", "│","│", "│", "│", "│", "┴","┬", "▲", "▼", "►", "◄"],
                ["•", "•", "•", "•", "•", "•", "•","•", "•", "•", "•", "•","•", "▲", "▼", ">", "<"],
                ["˜", "˜", "│", "│", "│", "│", " "," ", "│", "│", "│", "˜","˜", "▲", "▼", "►", "◄"],
                ["═", "═", "│", "│", "╒", "╕", "╛","╘", "╪", "╞", "╡", "╧","╤", "▲", "▼", "►", "◄"],
                ["─", "─", "║", "║", "╓", "╖", "╜","╙", "╫", "╟", "╢", "╨","╥", "▲", "▼", ">", "<"],
                ["─", "─", "│", "│", "╔", "╗", "╝","╚", "┼", "├", "┤", "┴","┬", "▲", "▼", ">", "<"],
                ["▄", "▀", "▐", "▌", " ", " ", " "," ", "┼", "├", "┤", "┴","┬", "▲", "▼", "►", "◄"],
        ]
        action_bar = Gtk.ActionBar()
        self.rectangle_button = Gtk.ToggleButton(icon_name="rectangle-symbolic",
                tooltip_text="Rectangle Ctrl+R")
        self.rectangle_button.connect("toggled", self.on_choose_rectangle)
        action_bar.pack_start(self.rectangle_button)

        self.filled_rectangle_button = Gtk.ToggleButton(icon_name="filled-rectangle-symbolic",
                tooltip_text="Rectangle Ctrl+Shift+R")
        self.filled_rectangle_button.connect("toggled", self.on_choose_filled_rectangle)
        self.filled_rectangle_button.set_group(self.rectangle_button)
        action_bar.pack_start(self.filled_rectangle_button)

        self.line_button = Gtk.ToggleButton(icon_name="line-symbolic",
                tooltip_text="Line Ctrl+L")
        self.line_button.connect("toggled", self.on_choose_line)
        self.line_button.set_group(self.rectangle_button)
        action_bar.pack_start(self.line_button)

        self.arrow_button = Gtk.ToggleButton(icon_name="arrow-symbolic",
                tooltip_text="Arrow Ctrl+W")
        self.arrow_button.connect("toggled", self.on_choose_arrow)
        self.arrow_button.set_group(self.rectangle_button)
        action_bar.pack_start(self.arrow_button)

        self.free_line_button = Gtk.ToggleButton(icon_name="free-line-symbolic",
                tooltip_text="Free Line Ctrl+G")
        self.free_line_button.connect("toggled", self.on_choose_free_line)
        self.free_line_button.set_group(self.rectangle_button)
        action_bar.pack_start(self.free_line_button)

        self.free_button = Gtk.ToggleButton(icon_name="paintbrush-symbolic",
                tooltip_text="Free Hand Ctrl+F")
        self.free_button.connect("clicked", self.on_choose_free)
        self.free_button.set_group(self.rectangle_button)
        action_bar.pack_start(self.free_button)

        self.text_button = Gtk.ToggleButton(icon_name="text-symbolic",
                tooltip_text="Text Ctrl+T")
        self.text_button.connect("toggled", self.on_choose_text)
        self.text_button.set_group(self.rectangle_button)
        action_bar.pack_start(self.text_button)

        self.eraser_button = Gtk.ToggleButton(icon_name="eraser-symbolic",
                tooltip_text="Eraser Ctrl+E")
        self.eraser_button.connect("toggled", self.on_choose_eraser)
        self.eraser_button.set_group(self.rectangle_button)
        action_bar.pack_start(self.eraser_button)

        self.picker_button = Gtk.ToggleButton(icon_name="color-select-symbolic",
                tooltip_text="Picker Ctrl+P")
        self.picker_button.connect("toggled", self.on_choose_picker)
        self.picker_button.set_group(self.rectangle_button)
        action_bar.pack_start(self.picker_button)

        clear_button = Gtk.Button(icon_name="user-trash-symbolic")
        clear_button.connect("clicked", self.clear, self.grid)
        action_bar.pack_end(clear_button)

        save_button = Gtk.Button(label="Save")
        save_button.connect("clicked", self.save)
        headerbar.pack_start(save_button)

        self.undo_button = Gtk.Button(icon_name="edit-undo-symbolic", sensitive=False)
        self.undo_button.connect("clicked", self.undo_first_change)
        headerbar.pack_start(self.undo_button)

        text_direction = save_button.get_child().get_direction()

        if text_direction == Gtk.TextDirection.LTR:
            self.flip = False
        elif text_direction == Gtk.TextDirection.RTL:
            self.flip = True

        self.lines_styles_selection = Gtk.Box(orientation=1, css_classes=["padded"], spacing=6)

        prev_btn = None

        for style in self.styles:
            if self.flip:
                name = style[5] + style[1] + style[1] + style[1] + style[4] + " " + style[3] + " " + style[15] + style[1] + style[1] + style[4] + "  " + style[3] + "  "  + style[13] + "\n"
                name += style[3] + "   " + style[2] + " " + style[3] + "    " + style[2] + "  " + style[3] + "  " + style[3] + "\n"
                name += style[6] + style[0] + style[0] + style[0] + style[7] + " " + style[6] + style[0] + style[0] + style[16] + " " + style[2] + "  " + style[14] + "  " + style[3]
            else:
                name = style[4] + style[0] + style[0] + style[0] + style[5] + "  " + style[2] + " " + style[16] + style[0] + style[0] + style[5] + "  " + style[3] + "  "  + style[13] + "\n"
                name += style[2] + "   " + style[3] + "  " + style[2] + "    " + style[3] + "  " + style[3] + "  " + style[3] + "\n"
                name += style[7] + style[1] + style[1] + style[1] + style[6] + "  " + style[7] + style[1] + style[1] + style[15] + " " + style[3] + "  " + style[14] + "  " + style[3]
            label = Gtk.Label(label = name)
            style_btn = Gtk.ToggleButton(css_classes=["flat", "ascii"])
            style_btn.set_child(label)
            if prev_btn != None:
                style_btn.set_group(prev_btn)
            prev_btn = style_btn
            style_btn.connect("toggled", self.change_style, self.lines_styles_selection)

            self.lines_styles_selection.append(style_btn)

        menu_button = Gtk.MenuButton()
        menu_button.set_icon_name("open-menu-symbolic")
        menu = Gio.Menu()
        # menu.append(_("Preferences"), "app.preferences")
        menu.append(_("Keyboard shortcuts"), "win.show-help-overlay")
        menu.append(_("About ASCII Draw"), "app.about")
        menu_button.set_menu_model(menu)
        headerbar.pack_end(menu_button)

        # show_sidebar_button = Gtk.Button(icon_name="sidebar-show-right-symbolic")
        # show_sidebar_button.connect("clicked", self.show_sidebar)
        # headerbar.pack_end(show_sidebar_button)

        copy_button = Gtk.Button(icon_name="edit-copy-symbolic")
        copy_button.connect("clicked", self.copy_content)
        headerbar.pack_end(copy_button)

        increase_button = Gtk.MenuButton(icon_name="list-add-symbolic")
        increase_canvas_popover = Gtk.Popover()
        increase_button.set_popover(increase_canvas_popover)
        headerbar.pack_end(increase_button)

        increase_box = Gtk.Box(orientation=1, width_request=200, spacing=6)
        increase_canvas_popover.set_child(increase_box)

        width_row = Adw.ActionRow(title="Width") #Adw.SpinRow(title="Width")
        width_spin = Gtk.SpinButton(valign=Gtk.Align.CENTER)
        width_spin.set_range(0, 40)
        width_spin.get_adjustment().set_step_increment(1)
        width_row.add_suffix(width_spin)
        increase_box.append(width_row)
        height_row = Adw.ActionRow(title="Height") #Adw.SpinRow(title="Height")
        height_spin = Gtk.SpinButton(valign=Gtk.Align.CENTER)
        height_spin.set_range(0, 40)
        height_row.add_suffix(height_spin)
        height_spin.get_adjustment().set_step_increment(1)
        increase_box.append(height_row)
        increase_btn = Gtk.Button(label="Increase canvas")
        increase_box.append(increase_btn)
        increase_btn.connect("clicked", self.increase_size, width_spin, height_spin)

        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_draw_func(self.drawing_area_draw, None)
        # self.drawing_area.connect("show", self.update_area_width)

        self.overlay = Gtk.Overlay(halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER)
        scrolled_window = Gtk.ScrolledWindow(hexpand=True, width_request=300)
        scrolled_window.set_child(self.overlay)

        # self.overlay_split_view.set_sidebar_width_fraction(0.4)
        # self.overlay_split_view.set_max_sidebar_width(300)
        # self.overlay_split_view.set_sidebar_position(1)
        self.overlay_split_view.set_content(scrolled_window)

        self.free_char_list = Gtk.FlowBox(can_focus=False)
        self.free_char_list.set_selection_mode(0)
        self.scrolled = Gtk.ScrolledWindow(halign=Gtk.Align.END, width_request=300)
        self.scrolled.set_policy(2,2)
        # scrolled = Gtk.ScrolledWindow(vexpand=True)
        # scrolled.set_policy(2,1)
        # scrolled.set_child(self.free_char_list)
        # self.scrolled.set_child(scrolled)

        self.overlay_split_view.set_separator(Gtk.Separator())
        self.overlay_split_view.set_flap(self.scrolled) #set_sidebar(self.scrolled)

        self.overlay.set_child(self.grid)
        self.overlay.add_overlay(self.preview_grid)

        self.overlay.add_overlay(self.drawing_area)

        self.text_entry = Gtk.TextView(css_classes=["mono-entry"], vexpand=True,
                margin_start=12, margin_end=12, margin_top=12, margin_bottom=12)

        self.toolbar_view.append(self.overlay_split_view) #set_content(self.overlay_split_view)
        self.toolbar_view.append(action_bar)#add_bottom_bar(action_bar)

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

        self.prev_x = 0
        self.prev_y = 0

        self.tool = ""
        self.style = 1
        self.free_char = "+"
        self.free_size = 1
        self.eraser_size = 1

        self.chars = ""

        self.prev_char = ""
        self.prev_char_pos = []
        self.prev_pos = []

        self.changed_chars = []

        self.line_direction = []
        self.prev_line_pos = [0,0]

        self.undo_changes = []

        self.text_x = 0
        self.text_y = 0

        self.text_entry.get_buffer().connect("changed", self.insert_text)

        char = " "
        prev_button = Gtk.ToggleButton(label=char, css_classes=["flat"])
        prev_button.connect("toggled", self.change_char, self.free_char_list)
        self.free_char_list.append(prev_button)

        for i in range(33, 255):
            if i == 127:
                continue
            char = bytes([i]).decode('cp437')
            new_button = Gtk.ToggleButton(label=char, css_classes=["flat", "ascii"])
            new_button.connect("toggled", self.change_char, self.free_char_list)
            self.free_char_list.append(new_button)
            new_button.set_group(prev_button)

        self.eraser_scale = Gtk.Scale.new_with_range(0, 1, 10,1)
        self.eraser_scale.set_draw_value(True)
        self.eraser_scale.set_value_pos(1)
        self.eraser_scale.connect("value-changed", self.on_scale_value_changed, self.eraser_size)

        self.free_scale = Gtk.Scale.new_with_range(0, 1, 10,1)
        self.free_scale.set_draw_value(True)
        self.free_scale.set_value_pos(1)
        self.free_scale.connect("value-changed", self.on_scale_value_changed, self.free_size)

        self.drawing_area_width = 0

    def update_area_width(self):
        allocation = self.drawing_area.get_allocation()
        self.drawing_area_width = allocation.width

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
        if response == Gtk.ResponseType.CANCEL:
            dialog.destroy()
            return
        elif response == Gtk.ResponseType.ACCEPT:
            path = dialog.get_file().get_path()
            try:
                with open(path, 'w') as file:
                    file.write(self.get_canvas_content())
                print(f"Content written to {path} successfully.")
            except IOError:
                print(f"Error writing to {path}.")

        dialog.destroy()

    def change_char(self, btn, flow_box):
        self.free_char = btn.get_label()

    def show_sidebar(self, btn):
        # self.overlay_split_view.set_show_sidebar(not self.overlay_split_view.get_show_sidebar())
        self.overlay_split_view.set_reveal_flap(not self.overlay_split_view.get_reveal_flap())

    def get_canvas_content(self):
        final_text = ""
        text = ""
        text_row = ""
        row_empty = True
        rows_empty = True
        for y in range(self.canvas_y):
            for x in range(self.canvas_x):
                if self.flip:
                    child = self.grid.get_child_at(self.canvas_x - x, y)
                else:
                    child = self.grid.get_child_at(x, y)
                if child:
                    char = child.get_label()
                    if char == None or char == "" or char == " ":
                        char = " "
                        text += char
                    else:
                        if self.flip and char == "<":
                            char = ">"
                        elif self.flip and char == ">":
                            char = "<"
                        text += char
                        text_row += text
                        text = ""
                        rows_empty = False
            text = ""
            if not rows_empty:
                rows_empty = True
                text_row += "\n"
                final_text += text_row
                text_row = ""
            else:
                text_row += "\n"
        return final_text

    def copy_content(self, btn):
        text = self.get_canvas_content()

        clipboard = Gdk.Display().get_default().get_clipboard()
        clipboard.set(text)

    def increase_size(self, btn, width_row, height_row):
        x_inc = int(width_row.get_value())
        y_inc = int(height_row.get_value())
        print(x_inc, y_inc)
        if y_inc != 0:
            for line in range(y_inc):
                self.canvas_y += 1
                for x in range(self.canvas_x):
                    self.grid.attach(Gtk.Label(name=str(self.canvas_y), label=" ", css_classes=["ascii"], width_request=self.x_mul, height_request=self.y_mul), x, self.canvas_y - 1, 1, 1)
                    self.preview_grid.attach(Gtk.Label(label=" ", css_classes=["ascii"], width_request=self.x_mul, height_request=self.y_mul), x, self.canvas_y - 1, 1, 1)

        print(self.canvas_x, self.canvas_y)
        if x_inc != 0:
            for column in range(x_inc):
                self.canvas_x += 1
                for y in range(self.canvas_y):
                    self.grid.attach(Gtk.Label(name=str(self.canvas_x), label=" ", css_classes=["ascii"], width_request=self.x_mul, height_request=self.y_mul), self.canvas_x - 1, y, 1, 1)
                    self.preview_grid.attach(Gtk.Label(label=" ", css_classes=["ascii"], width_request=self.x_mul, height_request=self.y_mul), self.canvas_x - 1, y, 1, 1)


        print(self.canvas_x, self.canvas_y)
        self.drawing_area_width = self.drawing_area.get_allocation().width

    def change_style(self, btn, box):
        child = box.get_first_child()
        index = 1
        while child != None:
            if child.get_active():
                self.style = index
                return
            child = child.get_next_sibling()
            index += 1

    def on_click_pressed(self, click, x, y, arg):
        pass

    def on_click_released(self, click, x, y, arg):
        if self.flip:
            if self.drawing_area_width == 0:
                self.update_area_width()
            x = self.drawing_area_width - x
        x_char = int(self.start_x / self.x_mul)
        y_char = int(self.start_y / self.y_mul)

        if self.tool == "TEXT":
            self.text_x = x_char
            self.text_y = y_char
            self.insert_text(None)

        elif self.tool == "PICKER":
            child = self.grid.get_child_at(x_char, y_char)
            if child:
                self.free_char = child.get_label()

        # elif self.tool == "FREE":
        #     self.draw_char(x_char, y_char)

    def on_click_stopped(self, arg):
        pass

    def on_choose_free_line(self, btn):
        self.reset_text_entry()
        if btn.get_active():
            self.tool = "FREE-LINE"
        else:
            self.tool = ""

        self.overlay_split_view.set_reveal_flap(True)

        self.scrolled.set_child(None)
        box = Gtk.Box(orientation=1, name="FREE-LINE")
        scrolled = Gtk.ScrolledWindow(vexpand=True)
        scrolled.set_policy(2,1)
        scrolled.set_child(self.lines_styles_selection)
        box.append(scrolled)
        self.scrolled.set_child(box)

    def on_choose_picker(self, btn):
        self.reset_text_entry()
        if btn.get_active():
            self.tool = "PICKER"
        self.overlay_split_view.set_reveal_flap(False)

    def on_choose_rectangle(self, btn):
        self.reset_text_entry()
        if btn.get_active():
            self.tool = "RECTANGLE"

        self.overlay_split_view.set_reveal_flap(True)

        self.scrolled.set_child(None)
        box = Gtk.Box(orientation=1, name="RECTANGLE")
        scrolled = Gtk.ScrolledWindow(vexpand=True)
        scrolled.set_policy(2,1)
        scrolled.set_child(self.lines_styles_selection)
        box.append(scrolled)
        self.scrolled.set_child(box)

    def on_choose_filled_rectangle(self, btn):
        self.reset_text_entry()
        if btn.get_active():
            self.tool = "FILLED-RECTANGLE"

        self.overlay_split_view.set_reveal_flap(True)

        self.scrolled.set_child(None)
        box = Gtk.Box(orientation=1, name="FILLED-RECTANGLE")
        scrolled = Gtk.ScrolledWindow(vexpand=True)
        scrolled.set_policy(2,1)
        scrolled.set_child(self.free_char_list)
        box.append(scrolled)
        self.scrolled.set_child(box)

    def on_choose_line(self, btn):
        self.reset_text_entry()
        if btn.get_active():
            self.tool = "LINE"

        self.overlay_split_view.set_reveal_flap(True)

        self.scrolled.set_child(None)
        box = Gtk.Box(orientation=1, name="LINE")
        scrolled = Gtk.ScrolledWindow(vexpand=True)
        scrolled.set_policy(2,1)
        scrolled.set_child(self.lines_styles_selection)
        box.append(scrolled)
        self.scrolled.set_child(box)

    def on_choose_text(self, btn):
        if btn.get_active():
            self.tool = "TEXT"

        self.overlay_split_view.set_reveal_flap(True)

        self.scrolled.set_child(None)
        box = Gtk.Box(orientation=1, name="TEXT")
        box.append(self.text_entry)
        write_button = Gtk.Button(label="Enter", margin_start=12, margin_end=12, margin_bottom=12)
        write_button.connect("clicked", self.insert_text, self.grid)
        box.append(write_button)
        self.scrolled.set_child(box)

    def on_choose_free(self, btn):
        self.reset_text_entry()
        if btn.get_active():
            self.tool = "FREE"

        self.overlay_split_view.set_reveal_flap(True)

        self.scrolled.set_child(None)
        box = Gtk.Box(orientation=1, name="FREE")
        scrolled = Gtk.ScrolledWindow(vexpand=True)
        scrolled.set_policy(2,1)
        scrolled.set_child(self.free_char_list)
        box.append(scrolled)
        # box.append(Gtk.Separator())
        # box.append(self.free_scale)
        self.scrolled.set_child(box)

    def on_choose_eraser(self, btn):
        self.reset_text_entry()
        if btn.get_active():
            self.tool = "ERASER"

        self.overlay_split_view.set_reveal_flap(False)

        self.scrolled.set_child(None)
        box = Gtk.Box(orientation=1, name="ERASER", margin_start=12)
        self.eraser_size = self.eraser_scale.get_value()
        # box.append(self.eraser_scale)
        self.scrolled.set_child(box)

    def reset_text_entry(self):
        self.text_entry.get_buffer().set_text("")

    def on_scale_value_changed(self, scale, var):
        var = scale.get_value()

    def on_choose_arrow(self, btn):
        self.reset_text_entry()
        if btn.get_active():
            self.tool = "ARROW"

        self.overlay_split_view.set_reveal_flap(True)

        self.scrolled.set_child(None)
        box = Gtk.Box(orientation=1, name="ARROW")
        scrolled = Gtk.ScrolledWindow(vexpand=True)
        scrolled.set_policy(2,1)
        scrolled.set_child(self.lines_styles_selection)
        box.append(scrolled)
        self.scrolled.set_child(box)

    def clear(self, btn=None, grid=None):
        if grid != self.grid:
            start = time.time()
            if len(self.changed_chars) < 100:
                for pos in self.changed_chars:
                    child = grid.get_child_at(pos[0], pos[1])
                    if not child:
                        continue
                    child.set_label("")
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
        if grid == None:
            self.add_undo_action("Clear Screen")
            grid = self.grid
        for y in range(self.canvas_y):
            for x in range(self.canvas_x):
                child = grid.get_child_at(x, y)
                if not child:
                    continue
                if grid == self.grid:
                    self.undo_changes[0].add_change(x, y, child.get_label())
                child.set_label(" ")

    def clear_list_of_char(self, chars_list_start, chars_list_end):
        for index in range(chars_list_start, chars_list_end):
            pos = self.changed_chars[index]
            child = self.preview_grid.get_child_at(pos[0], pos[1])
            if not child:
                continue
            child.set_label("")

    def on_drag_begin(self, gesture, start_x, start_y):
        self.start_x = start_x
        if self.flip:
            if self.drawing_area_width == 0:
                self.update_area_width()
            self.start_x = self.drawing_area_width - self.start_x
        self.start_y = start_y
        start_x_char = self.start_x // self.x_mul
        start_y_char = self.start_y // self.y_mul

        if self.tool == "FREE-LINE":
            self.add_undo_action("Free Hand Line")
            self.prev_char_pos = [start_x_char, start_y_char]
        elif self.tool == "FREE":
            self.add_undo_action("Free Hand")
        elif self.tool == "ERASER":
            self.add_undo_action("Eraser")

    def on_drag_follow(self, gesture, end_x, end_y):
        if self.flip:
            end_x = - end_x
        start_x_char = self.start_x // self.x_mul
        start_y_char = self.start_y // self.y_mul

        width = int((end_x + self.start_x) // self.x_mul - start_x_char)
        height = int((end_y + self.start_y) // self.y_mul - start_y_char)

        self.end_x = width * self.x_mul
        self.end_y = height * self.y_mul

        if self.tool == "FREE":
            self.draw_char((self.start_x + self.end_x)/self.x_mul, (self.start_y + self.end_y)/self.y_mul)

        elif self.tool == "ERASER":
            self.erase_char((self.start_x + self.end_x)/self.x_mul, (self.start_y + self.end_y)/self.y_mul)

        elif self.tool == "RECTANGLE":
            if self.prev_x != width or self.prev_y != height:
                self.clear(None, self.preview_grid)
                self.prev_x = width
                self.prev_y = height
            if width < 0:
                width = -width
                start_x_char -= width
            width += 1
            if height < 0:
                height = - height
                start_y_char -= height
            height += 1
            self.draw_rectangle(start_x_char, start_y_char, width, height, self.preview_grid)
        elif self.tool == "FILLED-RECTANGLE":
            if abs(self.prev_x) > abs(width) or abs(self.prev_y) > abs(height) or math.copysign(1, self.prev_x) != math.copysign(1, width) or math.copysign(1, self.prev_y) != math.copysign(1, height):
                self.clear(None, self.preview_grid)
            self.prev_x = width
            self.prev_y = height
            self.changed_chars = []

            if width < 0:
                width = -width
                start_x_char -= width
            width += 1
            if height < 0:
                height = - height
                start_y_char -= height
            height += 1
            self.draw_filled_rectangle(start_x_char, start_y_char, width, height, self.preview_grid)
        elif self.tool == "LINE" or self.tool == "ARROW":
            self.clear(None, self.preview_grid)
            if width < 0:
                width -= 1
            else:
                width += 1
            if height < 0:
                height -= 1
            else:
                height += 1
            if self.prev_line_pos != [start_x_char + width, start_y_char + height]:
                self.line_direction = self.normalize_vector([start_x_char + width - self.prev_line_pos[0], start_y_char + height - self.prev_line_pos[1]])
                self.line_direction = [abs(self.line_direction[0]), abs(self.line_direction[1])]
            self.draw_line(start_x_char, start_y_char, width, height, self.preview_grid)

        elif self.tool == "FREE-LINE":
            self.draw_free_line(start_x_char + width, start_y_char + height, self.grid)
            self.drawing_area.queue_draw()

    def on_drag_end(self, gesture, delta_x, delta_y):
        if self.tool != "TEXT":
            self.force_clear(self.preview_grid)
        if self.flip:
            delta_x = - delta_x
        start_x_char = self.start_x // self.x_mul
        start_y_char = self.start_y // self.y_mul
        width = int((delta_x + self.start_x) // self.x_mul - start_x_char)
        height = int((delta_y + self.start_y) // self.y_mul - start_y_char)

        self.prev_x = 0
        self.prev_y = 0

        if self.tool == "RECTANGLE":
            self.add_undo_action("Rectangle")
            if width < 0:
                width = -width
                start_x_char -= width
            width += 1
            if height < 0:
                height = - height
                start_y_char -= height
            height += 1
            self.draw_rectangle(start_x_char, start_y_char, width, height, self.grid)
        elif self.tool == "FILLED-RECTANGLE":
            self.add_undo_action("Filled Rectangle")
            if width < 0:
                width = -width
                start_x_char -= width
            width += 1
            if height < 0:
                height = - height
                start_y_char -= height
            height += 1
            self.draw_filled_rectangle(start_x_char, start_y_char, width, height, self.grid)
        elif self.tool == "LINE" or self.tool == "ARROW":
            self.add_undo_action(self.tool.capitalize())
            if width < 0:
                width -= 1
            else:
                width += 1
            if height < 0:
                height -= 1
            else:
                height += 1
            self.draw_line(start_x_char, start_y_char, width, height, self.grid)

        elif self.tool == "FREE-LINE":
            self.prev_char = ""
            self.prev_char_pos = []
            self.prev_pos = []

    def add_undo_action(self, name):
        self.undo_changes.insert(0, Change(name))
        self.undo_button.set_sensitive(True)
        self.undo_button.set_tooltip_text("Undo " + self.undo_changes[0].name)

    def drawing_area_draw(self, area, cr, width, height, data):
        cr.save()
        # if self.tool == "FREE-LINE":
        #     cr.rectangle(self.prev_char_pos[0]*self.x_mul + self.x_mul/2, self.prev_char_pos[1]*self.y_mul + self.y_mul/2, self.x_mul, self.y_mul)
        cr.stroke()
        cr.restore()

    def normalize_vector(self, vector):
        magnitude = math.sqrt(vector[0]**2 + vector[1]**2)
        if magnitude == 0:
            return [0, 0]  # Avoid division by zero
        normalized = [round(vector[0] / magnitude), round(vector[1] / magnitude)]
        return normalized

    def draw_free_line(self, new_x, new_y, grid):
        pos = [new_x, new_y]
        if self.prev_pos == [] or pos == self.prev_pos:
            self.prev_pos = [new_x, new_y]
            return
        pos = [new_x, new_y]
        direction = [int(pos[0] - self.prev_pos[0]), int(pos[1] - self.prev_pos[1])]
        dir2 = direction
        direction = self.normalize_vector(direction)
        prev_direction = [int(self.prev_pos[0] - self.prev_char_pos[0]), int(self.prev_pos[1] - self.prev_char_pos[1])]

        if direction == [1, 0] or direction == [-1, 0]:
            self.set_char_at(new_x, new_y, grid, self.bottom_horizontal())
        elif direction == [0, 1] or direction == [0, -1]:
            self.set_char_at(new_x, new_y, grid, self.right_vertical())

        # ["─", "─", "│", "│", "┌", "┐", "┘","└", "┼", "├", "┤", "┴","┬", "▲", "▼", "►", "◄"],

        if direction == [1, 0]:
            if dir2 != direction:
                self.horizontal_line(new_y, new_x - dir2[0], dir2[0], grid, self.bottom_horizontal())
            if prev_direction == [0, -1]:
                self.set_char_at(self.prev_pos[0], self.prev_pos[1], grid, self.top_left())
            elif prev_direction == [0, 1]:
                self.set_char_at(self.prev_pos[0], self.prev_pos[1], grid, self.bottom_left())
            else:
                self.set_char_at(self.prev_pos[0], self.prev_pos[1], grid, self.bottom_horizontal())
        elif direction == [-1, 0]:
            if prev_direction == [0, -1]:
                self.set_char_at(self.prev_pos[0], self.prev_pos[1], grid, self.top_right())
            elif prev_direction == [0, 1]:
                self.set_char_at(self.prev_pos[0], self.prev_pos[1], grid, self.bottom_right())
            else:
                self.set_char_at(self.prev_pos[0], self.prev_pos[1], grid, self.bottom_horizontal())

        if direction == [0, -1]:
            if prev_direction == [1, 0]:
                self.set_char_at(self.prev_pos[0], self.prev_pos[1], grid, self.bottom_right())
            elif prev_direction == [-1, 0]:
                self.set_char_at(self.prev_pos[0], self.prev_pos[1], grid, self.bottom_left())
            else:
                self.set_char_at(self.prev_pos[0], self.prev_pos[1], grid, self.right_vertical())
        elif direction == [0, 1]:
            if prev_direction == [1, 0]:
                self.set_char_at(self.prev_pos[0], self.prev_pos[1], grid, self.top_right())
            elif prev_direction == [-1, 0]:
                self.set_char_at(self.prev_pos[0], self.prev_pos[1], grid, self.top_left())
            else:
                self.set_char_at(self.prev_pos[0], self.prev_pos[1], grid, self.right_vertical())
        # self.set_char_at(self.prev_pos[0], self.prev_pos[1], grid, "2")
        self.prev_char_pos = [self.prev_pos[0], self.prev_pos[1]]
        self.prev_pos = [new_x, new_y]

    def insert_text(self, widget=None, grid=None):
        self.clear(None, self.preview_grid)
        if grid == None:
            grid = self.preview_grid
        x = self.text_x
        y = self.text_y
        buffer = self.text_entry.get_buffer()
        start = buffer.get_start_iter()
        end = buffer.get_end_iter()
        text = buffer.get_text(start, end, False)
        if text != "" and grid == self.grid:
            self.add_undo_action(self.tool.capitalize())
        for char in text:
            child = grid.get_child_at(x, y)
            if ord(char) < 32:
                if ord(char) == 10:
                    y += 1
                    x = self.text_x
                    continue
                continue
            if not child:
                continue
            if grid == self.grid:
                self.undo_changes[0].add_change(x, y, child.get_label())
            child.set_label(char)
            self.changed_chars.append([x, y])
            if self.flip:
                x -= 1
            else:
                x += 1

    def draw_char(self, x_coord, y_coord):
        child = self.grid.get_child_at(x_coord, y_coord)
        if child:
            self.undo_changes[0].add_change(x_coord, y_coord, child.get_label())
            child.set_label(self.free_char)

    def erase_char(self, x_coord, y_coord):
        child = self.grid.get_child_at(x_coord, y_coord)
        if child:
            self.undo_changes[0].add_change(x_coord, y_coord, child.get_label())
            child.set_label("")

    def draw_filled_rectangle(self, start_x_char, start_y_char, width, height, grid):
        for y in range(height):
            for x in range(width):
                self.set_char_at(start_x_char + x, start_y_char + y, grid, self.free_char)

    def draw_rectangle(self, start_x_char, start_y_char, width, height, grid):
        top_vertical = self.left_vertical()
        top_horizontal = self.top_horizontal()

        bottom_vertical = self.right_vertical()
        bottom_horizontal = self.bottom_horizontal()

        if width <= 1 or height <= 1:
            return

        self.horizontal_line(start_y_char, start_x_char, width, grid, top_horizontal)
        self.horizontal_line(start_y_char + height - 1, start_x_char + 1, width - 2, grid, bottom_horizontal)
        self.vertical_line(start_x_char, start_y_char + 1, height - 1, grid, top_vertical)
        self.vertical_line(start_x_char + width - 1, start_y_char + 1, height - 1, grid, bottom_vertical)

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

        end_vertical = self.left_vertical()
        start_vertical = self.right_vertical()
        end_horizontal = self.top_horizontal()
        start_horizontal = self.bottom_horizontal()

        if width > 0 and height > 0:
            if self.line_direction == [1, 0]:
                self.horizontal_line(start_y_char + height - 1, start_x_char + 1, width - 1, grid, start_horizontal)
                if height > 1:
                    self.vertical_line(start_x_char, start_y_char, height - 1, grid, end_vertical)
                if height != 1:
                    self.set_char_at(start_x_char, start_y_char + height - 1, grid, self.bottom_left())
                if arrow:
                    self.set_char_at(start_x_char + width - 1, start_y_char + height - 1, grid, self.right_arrow())
            else:
                self.horizontal_line(start_y_char, start_x_char, width - 1, grid, end_horizontal)
                if height > 1:
                    self.vertical_line(start_x_char + width - 1, start_y_char + 1, height - 1, grid, start_vertical)
                if width != 1 and height != 1:
                    self.set_char_at(start_x_char + width - 1, start_y_char, grid, self.top_right())
                if arrow:
                    self.set_char_at(start_x_char + width - 1, start_y_char + height - 1, grid, self.down_arrow())
        elif width > 0 and height < 0:
            if self.line_direction == [1, 0]:
                self.horizontal_line(start_y_char + height + 1, start_x_char + 1, width - 1, grid, end_horizontal)
                if height < 1:
                    self.vertical_line(start_x_char, start_y_char + 1, height + 1, grid, end_vertical)
                if width != 1 and height != 1:
                    self.set_char_at(start_x_char, start_y_char + height + 1, grid, self.top_left())
                if arrow:
                    self.set_char_at(start_x_char + width - 1, start_y_char + height + 1, grid, self.right_arrow())
            else:
                self.horizontal_line(start_y_char, start_x_char, width - 1, grid, end_horizontal)
                if height < 1:
                    self.vertical_line(start_x_char + width - 1, start_y_char, height + 1, grid, end_vertical)
                if width != 1 and height != 1:
                    self.set_char_at(start_x_char + width - 1, start_y_char, grid, self.bottom_right())
                if arrow:
                    self.set_char_at(start_x_char + width - 1, start_y_char + height + 1, grid, self.up_arrow())
        elif width < 0 and height > 0:
            if self.line_direction == [1, 0]:
                self.horizontal_line(start_y_char + height - 1, start_x_char, width + 1, grid, start_horizontal)
                if height > 1:
                    self.vertical_line(start_x_char, start_y_char, height - 1, grid, start_vertical)
                if width != 1 and height != 1:
                    self.set_char_at(start_x_char, start_y_char + height - 1, grid, self.bottom_right())
                if arrow:
                    self.set_char_at(start_x_char + width + 1, start_y_char + height - 1, grid, self.left_arrow())
            else:
                self.horizontal_line(start_y_char, start_x_char + 1, width + 1, grid, end_horizontal)
                if height > 1:
                    self.vertical_line(start_x_char + width + 1, start_y_char + 1, height - 1, grid, end_vertical)
                if width != 1 and height != 1:
                    self.set_char_at(start_x_char + width + 1, start_y_char, grid, self.top_left())
                if arrow:
                    self.set_char_at(start_x_char + width + 1, start_y_char + height - 1, grid, self.down_arrow())
        elif width < 0 and height < 0:
            if self.line_direction == [1, 0]:
                self.horizontal_line(start_y_char + height + 1, start_x_char, width + 1, grid, end_horizontal)
                if height < 1:
                    self.vertical_line(start_x_char, start_y_char + 1, height + 1, grid, start_vertical)
                if width != 1 and height != 1:
                    self.set_char_at(start_x_char, start_y_char + height + 1, grid, self.top_right())
                if arrow:
                    self.set_char_at(start_x_char + width + 1, start_y_char + height + 1, grid, self.left_arrow())
            else:
                self.horizontal_line(start_y_char, start_x_char + 1, width + 1, grid, start_horizontal)
                if height < 1:
                    self.vertical_line(start_x_char + width + 1, start_y_char, height + 1, grid, end_vertical)
                if width != 1 and height != 1:
                    self.set_char_at(start_x_char + width + 1, start_y_char, grid, self.bottom_left())
                if arrow:
                    self.set_char_at(start_x_char + width + 1, start_y_char + height + 1, grid, self.up_arrow())

        if width == 1 and height < 0:
            self.set_char_at(start_x_char, start_y_char, grid, self.left_vertical())
        elif width == 1 and height > 0:
            self.set_char_at(start_x_char, start_y_char, grid, self.right_vertical())
        elif height == 1:
            self.set_char_at(start_x_char, start_y_char, grid, self.bottom_horizontal())

        if arrow and height == 1:
            if width < 0:
                self.set_char_at(start_x_char + width + 1, start_y_char + height - 1, grid, self.left_arrow())
            else:
                self.set_char_at(start_x_char + width - 1, start_y_char + height - 1, grid, self.right_arrow())

        self.prev_line_pos = [start_x_char + width, start_y_char + height]

    def set_char_at(self, x, y, grid, char):
        child = grid.get_child_at(x, y)
        if child:
            if grid == self.grid:
                self.undo_changes[0].add_change(x, y, child.get_label())
            child.set_label(char)
            self.changed_chars.append([x, y])

    def vertical_line(self, x, start_y, length, grid, char):
        if length > 0:
            for y in range(abs(length)):
                child = grid.get_child_at(x, start_y + y)
                if not child:
                    continue
                if grid == self.grid:
                    self.undo_changes[0].add_change(x, start_y + y, child.get_label())
                prev_label = child.get_label()
                if prev_label == "" or prev_label == " ":
                    child.set_label(char)
                elif prev_label == self.top_horizontal():
                    child.set_label(self.crossing())
                else:
                    child.set_label(char)
                self.changed_chars.append([x, start_y + y])
        else:
            for y in range(abs(length)):
                child = grid.get_child_at(x, start_y + y + length)
                if not child:
                    continue
                if grid == self.grid:
                    self.undo_changes[0].add_change(x, start_y + y + length, child.get_label())
                if child.get_label() == "─":
                    child.set_label("┼")
                else:
                    child.set_label(char)
                self.changed_chars.append([x, start_y + y + length])

    def horizontal_line(self, y, start_x, width, grid, char):
        if width > 0:
            for x in range(abs(width)):
                child = grid.get_child_at(start_x + x, y)
                if not child:
                    continue
                prev_label = child.get_label()
                if grid == self.grid:
                    self.undo_changes[0].add_change(start_x + x, y, prev_label)
                if prev_label == "" or prev_label == " ":
                    child.set_label(char)
                elif prev_label == self.left_vertical():
                    child.set_label(self.crossing())
                else:
                    child.set_label(char)
                self.changed_chars.append([start_x + x, y])
        else:
            for x in range(abs(width)):
                child = grid.get_child_at(start_x + x + width, y)
                if not child:
                    continue
                prev_label = child.get_label()
                if grid == self.grid:
                    self.undo_changes[0].add_change(start_x + x + width, y, prev_label)
                if prev_label == "" or prev_label == " ":
                    child.set_label(char)
                elif prev_label == self.left_vertical():
                    child.set_label(self.crossing())
                else:
                    child.set_label(char)
                self.changed_chars.append([start_x + x + width, y])

    def undo_first_change(self, btn=None):
        try:
            change_object = self.undo_changes[0]
        except:
            return
        for change in change_object.changes:
            child = self.grid.get_child_at(change[0], change[1])
            if not child:
                continue
            child.set_label(change[2])
        self.undo_changes.pop(0)
        if len(self.undo_changes) == 0:
            self.undo_button.set_sensitive(False)
        else:
            self.undo_button.set_tooltip_text("Undo " + self.undo_changes[0].name)

    def top_horizontal(self):
        return self.styles[self.style - 1][0]
    def bottom_horizontal(self):
        return self.styles[self.style - 1][1]
    def left_vertical(self):
        if self.flip:
            return self.styles[self.style - 1][3]
        return self.styles[self.style - 1][2]
    def right_vertical(self):
        if self.flip:
            return self.styles[self.style - 1][2]
        return self.styles[self.style - 1][3]
    def top_left(self):
        if self.flip:
            return self.styles[self.style - 1][5]
        return self.styles[self.style - 1][4]
    def top_right(self):
        if self.flip:
            return self.styles[self.style - 1][4]
        return self.styles[self.style - 1][5]
    def bottom_right(self):
        if self.flip:
            return self.styles[self.style - 1][7]
        return self.styles[self.style - 1][6]
    def bottom_left(self):
        if self.flip:
            return self.styles[self.style - 1][6]
        return self.styles[self.style - 1][7]
    def up_arrow(self):
        return self.styles[self.style - 1][13]
    def down_arrow(self):
        return self.styles[self.style - 1][14]
    def left_arrow(self):
        return self.styles[self.style - 1][16]
    def right_arrow(self):
        return self.styles[self.style - 1][15]
    def crossing(self):
        return self.styles[self.style - 1][8]
    def right_intersect(self):
        if self.flip:
            return self.styles[self.style - 1][10]
        return self.styles[self.style - 1][9]
    def left_intersect(self):
        if self.flip:
            return self.styles[self.style - 1][9]
        return self.styles[self.style - 1][10]
    def top_intersect(self):
        return self.styles[self.style - 1][11]
    def bottom_intersect(self):
        return self.styles[self.style - 1][12]

    def select_rectangle_tool(self):
        self.rectangle_button.set_active(True)
        self.tool = "RECTANGLE"

    def select_filled_rectangle_tool(self):
        self.filled_rectangle_button.set_active(True)
        self.tool = "FILLED-RECTANGLE"

    def select_line_tool(self):
        self.line_button.set_active(True)
        self.tool = "LINE"

    def select_text_tool(self):
        self.text_button.set_active(True)
        self.tool = "TEXT"

    def select_free_tool(self):
        self.free_button.set_active(True)
        self.tool = "FREE"

    def select_eraser_tool(self):
        self.eraser_button.set_active(True)
        self.tool = "ERASER"

    def select_arrow_tool(self):
        self.arrow_button.set_active(True)
        self.tool = "ARROW"

    def select_free_line_tool(self):
        self.free_line_button.set_active(True)
        self.tool = "FREE-LINE"

    def select_picker_tool(self):
        self.picker_button.set_active(True)
        self.tool = "PICKER"
