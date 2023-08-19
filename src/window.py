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

import math

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

        # self.empty_grid = self.preview_grid

        self.styles = [
                ["─", "─", "│", "│", "┌", "┐", "┘","└", "┼", "├", "┤", "┴","┬", "▲", "▼", ">", "<"],
                ["═", "═", "║", "║", "╔", "╗", "╝","╚", "┼", "├", "┤", "┴","┬", "^", "V", ">", "<"],
                ["-", "-", "|", "|", "+", "+", "+","+", "┼", "├", "┤", "┴","┬", "↑", "↓", "→", "←"],
                ["_", "_", "│", "│", " ", " ", "│","│", "┼", "├", "┤", "┴","┬", "▲", "▼", "►", "◄"],
                ["•", "•", ":", ":", "•", "•", "•","•", "┼", "├", "┤", "┴","┬", "▲", "▼", "►", "◄"],
                ["˜", "˜", "│", "│", "│", "│", " "," ", "┼", "├", "┤", "┴","┬", "▲", "▼", "►", "◄"],
                ["═", "═", "│", "│", "╒", "╕", "╛","╘", "┼", "├", "┤", "┴","┬", "▲", "▼", "►", "◄"],
                ["▄", "▀", "▐", "▌", " ", " ", " "," ", "┼", "├", "┤", "┴","┬", "▲", "▼", "►", "◄"],
                ["─", "─", "│", "│", "╔", "╗", "╝","╚", "┼", "├", "┤", "┴","┬", "▲", "▼", "►", "◄"],
                ["─", "─", "│", "│", "┌", "┐", "┘","└", "┼", "├", "┤", "┴","┬", "▲", "▼", "►", "◄"],
        ]
        action_bar = Gtk.ActionBar()
        rectangle_button = Gtk.ToggleButton(icon_name="checkbox-symbolic")
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

        self.free_button = Gtk.ToggleButton(icon_name="document-edit-symbolic")
        self.free_button.connect("clicked", self.on_choose_free)
        self.free_button.set_group(rectangle_button)
        action_bar.pack_start(self.free_button)

        eraser_button = Gtk.ToggleButton(icon_name="switch-off-symbolic")
        eraser_button.connect("clicked", self.on_choose_eraser)
        eraser_button.set_group(rectangle_button)
        action_bar.pack_start(eraser_button)

        arrow_button = Gtk.ToggleButton(icon_name="mail-forward-symbolic")
        arrow_button.connect("clicked", self.on_choose_arrow)
        arrow_button.set_group(rectangle_button)
        action_bar.pack_start(arrow_button)

        free_line_button = Gtk.ToggleButton(icon_name="mail-attachment-symbolic")
        free_line_button.connect("clicked", self.on_choose_free_line)
        free_line_button.set_group(rectangle_button)
        action_bar.pack_start(free_line_button)

        picker_button = Gtk.ToggleButton(icon_name="color-select-symbolic")
        picker_button.connect("clicked", self.on_choose_picker)
        picker_button.set_group(rectangle_button)
        action_bar.pack_start(picker_button)

        clear_button = Gtk.Button(icon_name="user-trash-symbolic")
        clear_button.connect("clicked", self.clear, self.grid)
        action_bar.pack_end(clear_button)

        self.lines_styles_selection = Gtk.Box(orientation=1, css_classes=["padded"], spacing=6)

        prev_btn = None

        for style in self.styles:
            name = style[4] + style[0] + style[0] + style[0] + style[5] + "\n"
            name += style[2] + "   " + style[3] + "\n"
            name += style[7] + style[1] + style[1] + style[1] + style[6]
            label = Gtk.Label(label = name)
            style_btn = Gtk.ToggleButton(css_classes=["flat", "ascii"])
            style_btn.set_child(label)
            if prev_btn != None:
                style_btn.set_group(prev_btn)
            prev_btn = style_btn
            style_btn.connect("toggled", self.change_style, self.lines_styles_selection)

            self.lines_styles_selection.append(style_btn)

        save_button = Gtk.Button(label="Save")
        save_button.connect("clicked", self.save)
        headerbar.pack_start(save_button)

        show_sidebar_button = Gtk.Button(icon_name="sidebar-show-right-symbolic")
        show_sidebar_button.connect("clicked", self.show_sidebar)
        headerbar.pack_end(show_sidebar_button)

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

        char = bytes([33]).decode('cp437')
        prev_button = Gtk.ToggleButton(label=char, css_classes=["flat"])
        prev_button.connect("toggled", self.change_char, self.free_char_list)
        self.free_char_list.append(prev_button)

        for i in range(34, 255):
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

        self.free_button.set_active(True)

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
                child = self.grid.get_child_at(x, y)
                if child:
                    char = child.get_label()
                    if char == None or char == "" or char == " ":
                        char = " "
                        text += char
                    else:
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
        for column in range(y_inc):
            for y in range(self.canvas_y):
                self.grid.attach(Gtk.Label(label=" ", css_classes=["ascii"], width_request=self.x_mul, height_request=self.y_mul), self.canvas_x + 1, y, 1, 1)
                self.preview_grid.attach(Gtk.Label(label=" ", css_classes=["ascii"], width_request=self.x_mul, height_request=self.y_mul), self.canvas_x + 1, y, 1, 1)
            self.canvas_y += 1
        for line in range(x_inc):
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
            self.insert_text(self.text_entry, x_char, y_char)

        elif self.tool == "PICKER":
            child = self.grid.get_child_at(x_char, y_char)
            if child:
                self.free_char = child.get_label()

    def on_key_pressed(self, event, arg):
        print(event)

    def on_click_stopped(self, arg):
        pass

    def on_choose_free_line(self, btn):
        self.reset_text_entry()
        if btn.get_active():
            self.tool = "FREE-LINE"
        else:
            self.tool = ""

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
        else:
            self.tool = ""

    def on_choose_rectangle(self, btn):
        self.reset_text_entry()
        if btn.get_active():
            self.tool = "RECTANGLE"
        else:
            self.tool = ""

        self.scrolled.set_child(None)
        box = Gtk.Box(orientation=1, name="RECTANGLE")
        scrolled = Gtk.ScrolledWindow(vexpand=True)
        scrolled.set_policy(2,1)
        scrolled.set_child(self.lines_styles_selection)
        box.append(scrolled)
        self.scrolled.set_child(box)

    def on_choose_line(self, btn):
        self.reset_text_entry()
        if btn.get_active():
            self.tool = "LINE"
        else:
            self.tool = ""

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
        else:
            self.tool = ""
        self.scrolled.set_child(None)
        box = Gtk.Box(orientation=1, name="TEXT")
        box.append(self.text_entry)
        self.scrolled.set_child(box)

    def on_choose_free(self, btn):
        self.reset_text_entry()
        if btn.get_active():
            self.tool = "FREE"
        else:
            self.tool = ""

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
        else:
            self.tool = ""

        self.scrolled.set_child(None)
        box = Gtk.Box(orientation=1, name="ERASER", margin_start=12)
        self.eraser_size = self.eraser_scale.get_value()
        # box.append(self.eraser_scale)
        self.scrolled.set_child(box)

    def reset_text_entry(self):
        self.text_entry.get_buffer().set_text("")

    def on_scale_value_changed(self, scale, var):
        var = scale.get_value()
        print(var)

    def on_choose_arrow(self, btn):
        self.reset_text_entry()
        if btn.get_active():
            self.tool = "ARROW"
        else:
            self.tool = ""

        self.scrolled.set_child(None)
        box = Gtk.Box(orientation=1, name="ARROW")
        scrolled = Gtk.ScrolledWindow(vexpand=True)
        scrolled.set_policy(2,1)
        scrolled.set_child(self.lines_styles_selection)
        box.append(scrolled)
        self.scrolled.set_child(box)

    def clear(self, btn=None, grid=None):
        if grid != self.grid:
            for pos in self.changed_chars:
                child = grid.get_child_at(pos[0], pos[1])
                if not child:
                    continue
                child.set_label("")
            self.changed_chars = []
        else:
            for y in range(self.canvas_y):
                for x in range(self.canvas_x):
                    child = grid.get_child_at(x, y)
                    if not child:
                        continue
                    child.set_label("")

    def on_drag_begin(self, gesture, start_x, start_y):
        self.start_x = start_x
        self.start_y = start_y
        start_x_char = self.start_x // self.x_mul
        start_y_char = self.start_y // self.y_mul

        if self.tool == "FREE-LINE":
            self.prev_char_pos = [start_x_char, start_y_char]

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
            self.clear(None, self.preview_grid)
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
            self.clear(None, self.preview_grid)
            self.draw_free_line(start_x_char + width, start_y_char + height, self.grid)
            self.drawing_area.queue_draw()

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

        elif self.tool == "LINE" or self.tool == "ARROW":
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
        print(direction)

        if direction == [1, 0] or direction == [-1, 0]:
            self.set_char_at(new_x, new_y, grid, self.bottom_horizontal())
        elif direction == [0, 1] or direction == [0, -1]:
            self.set_char_at(new_x, new_y, grid, self.bottom_vertical())

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
                self.set_char_at(self.prev_pos[0], self.prev_pos[1], grid, self.bottom_vertical())
        elif direction == [0, 1]:
            if prev_direction == [1, 0]:
                self.set_char_at(self.prev_pos[0], self.prev_pos[1], grid, self.top_right())
            elif prev_direction == [-1, 0]:
                self.set_char_at(self.prev_pos[0], self.prev_pos[1], grid, self.top_left())
            else:
                self.set_char_at(self.prev_pos[0], self.prev_pos[1], grid, self.bottom_vertical())
        # self.set_char_at(self.prev_pos[0], self.prev_pos[1], grid, "2")
        self.prev_char_pos = [self.prev_pos[0], self.prev_pos[1]]
        self.prev_pos = [new_x, new_y]

    def insert_text(self, entry, x_coord, y_coord):
        x = x_coord
        y = y_coord
        buffer = entry.get_buffer()
        start = buffer.get_start_iter()
        end = buffer.get_end_iter()
        text = buffer.get_text(start, end, False)
        for char in text:
            child = self.grid.get_child_at(x, y)
            if ord(char) < 32:
                if ord(char) == 10:
                    y += 1
                    x = x_coord
                    continue
                continue
            if not child:
                continue
            # print(f"{char} is {ord(char)} in {x},{y}")
            child.set_label(char)
            x += 1

    def draw_char(self, x_coord, y_coord):
        # for x in self.free_size:
        #     for y in self.free_size:
        child = self.grid.get_child_at(x_coord, y_coord)
        if child:
            child.set_label(self.free_char)

    def erase_char(self, x_coord, y_coord):
        child = self.grid.get_child_at(x_coord, y_coord)
        if child:
            child.set_label("")

    def draw_rectangle(self, start_x_char, start_y_char, width, height, grid):
        top_vertical = self.top_vertical()
        top_horizontal = self.top_horizontal()

        bottom_vertical = self.bottom_vertical()
        bottom_horizontal = self.bottom_horizontal()

        if width <= 1 or height <= 1:
            return

        self.horizontal_line(start_y_char, start_x_char, width, grid, top_horizontal)
        self.horizontal_line(start_y_char + height - 1, start_x_char, width, grid, bottom_horizontal)
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

        vertical = self.top_vertical()
        horizontal = self.top_horizontal()

        if width > 0 and height > 0:
            if self.line_direction == [1, 0]:
                self.horizontal_line(start_y_char + height - 1, start_x_char, width - 1, grid, horizontal)
                self.vertical_line(start_x_char, start_y_char, height, grid, vertical)
                self.set_char_at(start_x_char, start_y_char + height - 1, grid, self.bottom_left())
                if arrow:
                    self.set_char_at(start_x_char + width - 1, start_y_char + height - 1, grid, self.right_arrow())
            else:
                self.horizontal_line(start_y_char, start_x_char, width - 1, grid, horizontal)
                self.vertical_line(start_x_char + width - 1, start_y_char, height, grid, vertical)
                self.set_char_at(start_x_char + width - 1, start_y_char, grid, self.top_right())
                if arrow:
                    self.set_char_at(start_x_char + width - 1, start_y_char + height - 1, grid, self.down_arrow())
        elif width > 0 and height < 0:
            if self.line_direction == [1, 0]:
                self.horizontal_line(start_y_char + height + 1, start_x_char, width - 1, grid, horizontal)
                self.vertical_line(start_x_char, start_y_char + 1, height, grid, vertical)
                self.set_char_at(start_x_char, start_y_char + height + 1, grid, self.top_left())
                if arrow:
                    self.set_char_at(start_x_char + width - 1, start_y_char + height + 1, grid, self.right_arrow())
            else:
                self.horizontal_line(start_y_char, start_x_char, width - 1, grid, horizontal)
                self.vertical_line(start_x_char + width - 1, start_y_char + 1, height, grid, vertical)
                self.set_char_at(start_x_char + width - 1, start_y_char, grid, self.bottom_right())
                if arrow:
                    self.set_char_at(start_x_char + width - 1, start_y_char + height + 1, grid, self.up_arrow())
        elif width < 0 and height > 0:
            if self.line_direction == [1, 0]:
                self.horizontal_line(start_y_char + height - 1, start_x_char + 1, width, grid, horizontal)
                self.vertical_line(start_x_char, start_y_char, height, grid, vertical)
                self.set_char_at(start_x_char, start_y_char + height - 1, grid, self.bottom_right())
                if arrow:
                    self.set_char_at(start_x_char + width + 1, start_y_char + height - 1, grid, self.left_arrow())
            else:
                self.horizontal_line(start_y_char, start_x_char + 1, width, grid, horizontal)
                self.vertical_line(start_x_char + width + 1, start_y_char, height, grid, vertical)
                self.set_char_at(start_x_char + width + 1, start_y_char, grid, self.top_left())
                if arrow:
                    self.set_char_at(start_x_char + width + 1, start_y_char + height - 1, grid, self.down_arrow())
        elif width < 0 and height < 0:
            if self.line_direction == [1, 0]:
                self.horizontal_line(start_y_char + height + 1, start_x_char + 1, width, grid, horizontal)
                self.vertical_line(start_x_char, start_y_char + 1, height, grid, vertical)
                self.set_char_at(start_x_char, start_y_char + height + 1, grid, self.top_right())
                if arrow:
                    self.set_char_at(start_x_char + width + 1, start_y_char + height + 1, grid, self.left_arrow())
            else:
                self.horizontal_line(start_y_char, start_x_char + 1, width, grid, horizontal)
                self.vertical_line(start_x_char + width + 1, start_y_char + 1, height, grid, vertical)
                self.set_char_at(start_x_char + width + 1, start_y_char, grid, self.bottom_left())
                if arrow:
                    self.set_char_at(start_x_char + width + 1, start_y_char + height + 1, grid, self.up_arrow())

        if width == 1:
            child = grid.get_child_at(start_x_char + width - 1, start_y_char)
            if child:
                child.set_label(vertical)
        elif width == -1:
            child = grid.get_child_at(start_x_char + width + 1, start_y_char)
            if child:
                child.set_label(vertical)

        elif height == 1 and width < 0:
            child = grid.get_child_at(start_x_char + width + 1, start_y_char)
            if child:
                child.set_label(horizontal)
        elif height == 1 and width > 0:
            child = grid.get_child_at(start_x_char + width - 1, start_y_char)
            if child:
                child.set_label(horizontal)

        if arrow and height == 1:
            if width < 0:
                self.set_char_at(start_x_char + width + 1, start_y_char + height - 1, grid, self.left_arrow())
            else:
                self.set_char_at(start_x_char + width - 1, start_y_char + height - 1, grid, self.right_arrow())

        self.prev_line_pos = [start_x_char + width, start_y_char + height]

    def set_char_at(self, x, y, grid, char):
        child = grid.get_child_at(x, y)
        if child:
            child.set_label(char)
            self.changed_chars.append([x, y])

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
                self.changed_chars.append([x, start_y + y])
        else:
            for y in range(abs(lenght)):
                child = grid.get_child_at(x, start_y + y + lenght)
                if not child:
                    continue
                if child.get_label() == "─":
                    child.set_label("┼")
                else:
                    child.set_label(char)
                self.changed_chars.append([x, start_y + y + lenght])

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
                self.changed_chars.append([start_x + x, y])
        else:
            for x in range(abs(width)):
                child = grid.get_child_at(start_x + x + width, y)
                if not child:
                    continue
                if child.get_label() == "│":
                    child.set_label("┼")
                else:
                    child.set_label(char)
                self.changed_chars.append([start_x + x + width, y])

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

