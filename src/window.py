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
import pyfiglet
import unicodedata
import emoji
import os

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

        self.props.width_request=420
        self.props.height_request=400

        self.toolbar_view = Gtk.Box(orientation=1, vexpand=True)
        headerbar = Adw.HeaderBar()
        self.title_widget = Adw.WindowTitle(title="ASCII Draw")
        headerbar.set_title_widget(self.title_widget)
        self.toolbar_view.append(headerbar)
        self.set_title("ASCII Draw")

        self.settings.bind("window-width", self, "default-width", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("window-height", self, "default-height", Gio.SettingsBindFlags.DEFAULT)

        self.overlay_split_view = Adw.Flap(vexpand=True, flap_position=1)
        self.overlay_split_view.set_reveal_flap(False)

        self.set_content(self.toolbar_view)

        self.x_mul = 12
        self.y_mul = 24

        self.canvas_x = 50
        self.canvas_y = 25

        self.canvas_max_x = 100
        self.canvas_max_y = 50

        self.grid = Gtk.Grid(css_classes=["ascii-textview", "canvas-shadow"], halign=Gtk.Align.START, valign=Gtk.Align.START)
        self.preview_grid = Gtk.Grid(css_classes=["ascii-preview"], halign=Gtk.Align.START, valign=Gtk.Align.START, can_focus=False)

        for y in range(self.canvas_y):
            for x in range(self.canvas_x):
                self.grid.attach(Gtk.Label(label="", css_classes=["ascii"], width_request=self.x_mul, height_request=self.y_mul), x, y, 1, 1)
                self.preview_grid.attach(Gtk.Label(label="", css_classes=["ascii"], width_request=self.x_mul, height_request=self.y_mul), x, y, 1, 1)

        self.empty_grid = self.preview_grid

        self.brush_sizes = [
                [[0,0] ],
                [[0,0],[-1,0],[1,0] ],
                [[0,0],[-1,0],[1,0],[0,1],[0,-1] ],
                [[0,0],[-1,0],[1,0],[0,1],[0,-1],[-2,0],[2,0] ],
                [[0,0],[-1,0],[1,0],[0,1],[0,-1],[-2,0],[2,0],[1,1],[-1,-1],[-1,1],[1,-1], ],
                [[0,0],[-1,0],[1,0],[0,1],[0,-1],[-2,0],[2,0],[1,1],[-1,-1],[-1,1],[1,-1],[-2,1],[2,1],[-2,-1],[2,-1], ],
                [[0,0],[-1,0],[1,0],[0,1],[0,-1],[-2,0],[2,0],[1,1],[-1,-1],[-1,1],[1,-1],[-2,1],[2,1],[-2,-1],[2,-1],[0,2],[0,-2],[-3,0],[3,0], ],
                [[0,0],[-1,0],[1,0],[0,1],[0,-1],[-2,0],[2,0],[1,1],[-1,-1],[-1,1],[1,-1],[-2,1],[2,1],[-2,-1],[2,-1],[0,2],[0,-2],[-3,0],[3,0],[1,2],[1,-2],[-1,-2],[-1,2], ],
                ]

        self.styles = [
                ["─", "─", "│", "│", "┌", "┐", "┘","└", "┼", "├", "┤", "┴","┬", "∧", "∨", ">", "<"],
                ["╶", "╶", "╎", "╎", "┌", "┐", "┘","└", "┼", "├", "┤", "┴","┬", "∧", "∨", ">", "<"],
                ["─", "─", "│", "│", "╭", "╮", "╯","╰", "┼", "├", "┤", "┴","┬", "▲", "▼", ">", "<"],
                ["▁", "▔", "▏", "▕", "▁", "▁", "▔","▔", " ", "▏", "▕", "▔","▁", "∧", "∨", ">", "<"],
                ["━", "━", "┃", "┃", "┏", "┓", "┛","┗", "╋", "┣", "┫", "┻","┳", "▲", "▼", "▶", "◀"],
                ["╺", "╺", "╏", "╏", "┏", "┓", "┛","┗", "╋", "┣", "┫", "┻","┳", "▲", "▼", "▶", "◀"],
                ["═", "═", "║", "║", "╔", "╗", "╝","╚", "╬", "╠", "╣", "╩","╦", "A", "V", ">", "<"],
                ["-", "-", "|", "|", "+", "+", "+","+", "+", "+", "+", "+","+", "↑", "↓", "→", "←"],
                ["_", "_", "│", "│", " ", " ", "│","│", "│", "│", "│", "│","_", "▲", "▼", "▶", "◀"],
                ["•", "•", "•", "•", "•", "•", "•","•", "•", "•", "•", "•","•", "▲", "▼", ">", "<"],
                ["·", "·", "·", "·", ".", ".", "'","'", "·", "·", "·", "·","·", "∧", "∨", ">", "<"],
                ["═", "═", "│", "│", "╒", "╕", "╛","╘", "╪", "╞", "╡", "╧","╤", "▲", "▼", "▶", "◀"],
                ["─", "─", "║", "║", "╓", "╖", "╜","╙", "╫", "╟", "╢", "╨","╥", "▲", "▼", ">", "<"],
                ["─", "─", "│", "│", "╔", "╗", "╝","╚", "┼", "├", "┤", "┴","┬", "▲", "▼", ">", "<"],
                ["▄", "▀", "▐", "▌", "▗", "▖", "▘","▝", "▛", "▐", "▌", "▀","▄", "▲", "▼", "▶", "◀"],
                ["▀", "▄", "▌", "▐", "▛", "▜", "▟","▙", "▜", "▙", "▟", "▟","▜", "▲", "▼", "▶", "◀"],
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
                tooltip_text="Freehand Ctrl+F")
        self.free_button.connect("clicked", self.on_choose_free)
        self.free_button.set_group(self.rectangle_button)
        action_bar.pack_start(self.free_button)

        self.text_button = Gtk.ToggleButton(icon_name="text-symbolic",
                tooltip_text="Text Ctrl+T")
        self.text_button.connect("toggled", self.on_choose_text)
        self.text_button.set_group(self.rectangle_button)
        action_bar.pack_start(self.text_button)

        self.table_button = Gtk.ToggleButton(icon_name="table-symbolic",
                tooltip_text="Table Ctrl+Shift+T")
        self.table_button.connect("toggled", self.on_choose_table)
        self.table_button.set_group(self.rectangle_button)
        action_bar.pack_start(self.table_button)

        self.tree_button = Gtk.ToggleButton(icon_name="tree-list-symbolic",
                tooltip_text="Tree View Ctrl+U")
        self.tree_button.connect("toggled", self.on_choose_tree_list)
        self.tree_button.set_group(self.rectangle_button)
        action_bar.pack_start(self.tree_button)

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

        save_import_button = Adw.SplitButton(label="Save")
        import_menu = Gio.Menu()
        import_menu.append(_("Save As"), "app.save-as")
        import_menu.append(_("New Canvas"), "app.new-canvas")
        import_menu.append(_("Open file"), "app.open")
        save_import_button.set_menu_model(import_menu)
        save_import_button.connect("clicked", self.save_button_clicked)
        copy_button = Gtk.Button(icon_name="edit-copy-symbolic")
        copy_button.connect("clicked", self.copy_content)

        headerbar.pack_start(save_import_button)
        headerbar.pack_start(copy_button)

        self.undo_button = Gtk.Button(icon_name="edit-undo-symbolic", sensitive=False)
        self.undo_button.connect("clicked", self.undo_first_change)
        headerbar.pack_start(self.undo_button)

        text_direction = save_import_button.get_child().get_direction()

        if text_direction == Gtk.TextDirection.LTR:
            self.flip = False
        elif text_direction == Gtk.TextDirection.RTL:
            self.flip = True

        lines_styles_box = Gtk.Box(orientation=1, margin_start=6, margin_bottom=6, margin_end=6, margin_top=6, spacing=6)
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
            style_btn = Gtk.ToggleButton(css_classes=["flat", "styles-preview"])
            style_btn.set_child(label)
            if prev_btn != None:
                style_btn.set_group(prev_btn)
            prev_btn = style_btn
            style_btn.connect("toggled", self.change_style, lines_styles_box)

            lines_styles_box.append(style_btn)

        self.lines_styles_selection = Gtk.ScrolledWindow(vexpand=True)
        self.lines_styles_selection.set_policy(2,1)
        self.lines_styles_selection.set_child(lines_styles_box)

        menu_button = Gtk.MenuButton()
        menu_button.set_icon_name("open-menu-symbolic")
        menu = Gio.Menu()
        # menu.append(_("Preferences"), "app.preferences")
        menu.append(_("Keyboard shortcuts"), "win.show-help-overlay")
        menu.append(_("About ASCII Draw"), "app.about")
        menu_button.set_menu_model(menu)
        headerbar.pack_end(menu_button)

        self.show_sidebar_button = Gtk.Button(icon_name="sidebar-show-right-symbolic", sensitive=False)
        self.show_sidebar_button.connect("clicked", self.show_sidebar)
        headerbar.pack_end(self.show_sidebar_button)

        increase_button = Gtk.MenuButton(icon_name="list-add-symbolic")
        increase_canvas_popover = Gtk.Popover()
        increase_button.set_popover(increase_canvas_popover)
        headerbar.pack_end(increase_button)

        increase_box = Gtk.Box(orientation=1, width_request=200, spacing=6)
        increase_canvas_popover.set_child(increase_box)

        width_row = Adw.ActionRow(title="Width") #Adw.SpinRow(title="Width")
        self.width_spin = Gtk.SpinButton(valign=Gtk.Align.CENTER, width_request=120)
        self.width_spin.set_range(10, self.canvas_max_x)
        self.width_spin.set_value(self.canvas_x)
        self.width_spin.get_adjustment().set_step_increment(1)
        width_row.add_suffix(self.width_spin)
        increase_box.append(width_row)
        height_row = Adw.ActionRow(title="Height") #Adw.SpinRow(title="Height")
        self.height_spin = Gtk.SpinButton(valign=Gtk.Align.CENTER, width_request=120)
        self.height_spin.set_range(5, self.canvas_max_y)
        self.height_spin.set_value(self.canvas_y)
        height_row.add_suffix(self.height_spin)
        self.height_spin.get_adjustment().set_step_increment(1)
        increase_box.append(height_row)
        discaimer_row = Adw.ActionRow(title='''Increasing the canvas too
much can slow the app down,
use just the size you need.''')
        increase_box.append(discaimer_row)
        increase_btn = Gtk.Button(label="Change size")
        increase_box.append(increase_btn)
        increase_btn.connect("clicked", self.on_change_canvas_size_btn_clicked)

        self.drawing_area = Gtk.DrawingArea(css_classes=["drawing-area"])
        self.drawing_area.set_draw_func(self.drawing_area_draw, None)
        # self.drawing_area.connect("show", self.update_area_width)

        self.overlay = Gtk.Overlay(halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER,
                margin_start=10, margin_top=10, margin_bottom=10, margin_end=10)
        scrolled_window = Gtk.ScrolledWindow(hexpand=True)
        scrolled_window.set_child(self.overlay)
        self.toast_overlay = Adw.ToastOverlay()
        self.toast_overlay.set_child(scrolled_window)

        self.overlay_split_view.set_content(self.toast_overlay)

        char_flow_box = Gtk.FlowBox(can_focus=False)
        char_flow_box.set_selection_mode(0)
        self.free_char_list = Gtk.ScrolledWindow(vexpand=True)
        self.free_char_list.set_policy(2,1)
        self.free_char_list.set_child(char_flow_box)

        self.sidebar_notebook = Gtk.Notebook(width_request=430, css_classes=["sidebar"])

        self.overlay_split_view.set_separator(Gtk.Separator())
        self.overlay_split_view.set_flap(self.sidebar_notebook)

        self.overlay.add_overlay(self.preview_grid)
        self.overlay.set_child(self.grid)

        self.overlay.add_overlay(self.drawing_area)

        self.text_entry = Gtk.TextView(vexpand=True, css_classes=["mono-entry", "card"],
                left_margin=12, top_margin=12, wrap_mode=2, height_request=100)
        self.text_entry_buffer = self.text_entry.get_buffer()
        self.text_entry_buffer.connect("changed", self.insert_text_preview)

        self.toolbar_view.append(self.overlay_split_view)
        self.toolbar_view.append(action_bar)

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

        unicode_ranges = [
            range(0x0021, 0x007F),  # Basic Latin
            range(0x00A0, 0x0100),  # Latin-1 Supplement
            range(0x0100, 0x0180),  # Latin Extended-A
            range(0x2500, 0x2580),  # Box Drawing
            range(0x2580, 0x25A0),  # Block Elements
            range(0x25A0, 0x25FC),  # Geometric Shapes
            range(0x25FF, 0x2600),
            range(0x2190, 0x2200),  # Arrows
            range(0x2200, 0x22C7),  # Mathematical Operators
            range(0x22CB, 0x2300),
        ]

        char = " "
        prev_button = Gtk.ToggleButton(label=char, css_classes=["flat"])
        prev_button.connect("toggled", self.change_char, char_flow_box)
        char_flow_box.append(prev_button)

        for code_range in unicode_ranges:
            for code_point in code_range:
                char = chr(code_point)
                if not self.is_renderable(char):
                    continue
                new_button = Gtk.ToggleButton(label=char, css_classes=["flat", "ascii"])
                new_button.connect("toggled", self.change_char, char_flow_box)
                char_flow_box.append(new_button)
                new_button.set_group(prev_button)

        self.eraser_scale = Gtk.Scale.new_with_range(0, 1, len(self.brush_sizes), 1)
        self.eraser_scale.set_draw_value(True)
        self.eraser_scale.set_value_pos(1)
        self.eraser_scale.set_size_request(200, -1)
        self.eraser_scale.connect("value-changed", self.on_scale_value_changed, self.eraser_size)
        eraser_size_row = Adw.ActionRow(title="Size", css_classes=["card"])
        eraser_size_row.add_suffix(self.eraser_scale)
        self.eraser_sidebar = Gtk.Box(orientation=1, margin_start=12, margin_end=12, margin_bottom=12, margin_top=12)
        self.eraser_sidebar.append(eraser_size_row)

        self.free_scale = Gtk.Scale.new_with_range(0, 1, len(self.brush_sizes), 1)
        self.free_scale.set_draw_value(True)
        self.free_scale.set_value_pos(1)
        self.free_scale.set_size_request(200, -1)
        self.free_scale.connect("value-changed", self.on_scale_value_changed, self.free_size)
        freehand_size_row = Adw.ActionRow(title="Size", css_classes=["card"])
        freehand_size_row.add_suffix(self.free_scale)
        self.freehand_sidebar = Gtk.Box(orientation=1, margin_start=12, margin_end=12, margin_bottom=12, margin_top=12)
        self.freehand_sidebar.append(freehand_size_row)

        self.drawing_area_width = 0

        self.font_list = ["Normal","3x5","avatar","big","bell","briteb",
                "bubble","bulbhead","chunky","contessa","computer","crawford",
                "cricket","cursive","cyberlarge","cybermedium","cybersmall",
                "digital","doom","double","drpepper","eftifont",
                "eftirobot","eftitalic","eftiwall","eftiwater","fourtops","fuzzy",
                "gothic","graceful","graffiti","invita","italic","lcd",
                "letters","linux","lockergnome","madrid","maxfour","mike","mini",
                "morse","ogre","puffy","rectangles","rowancap","script","serifcap",
                "shadow","shimrod","short","slant","slide","slscript","small",
                "smisome1","smkeyboard","smscript","smshadow","smslant",
                "speed","stacey","stampatello","standard","stop","straight",
                "thin","threepoint","times","tombstone","tinker-toy","twopoint",
                "wavy","weird"]

        self.text_sidebar = Gtk.Box(orientation=1, margin_start=12, margin_end=12, margin_bottom=12, margin_top=12)

        write_button = Gtk.Button(label="Enter")
        write_button.connect("clicked", self.insert_text_definitely)
        self.font_box = Gtk.ListBox(css_classes=["navigation-sidebar"], vexpand=True)
        self.selected_font = "Normal"
        self.font_box.connect("row-selected", self.font_row_selected)
        scrolled_window = Gtk.ScrolledWindow(vexpand=True, margin_bottom=12)
        scrolled_window.set_policy(2,1)
        scrolled_window.set_child(self.text_entry)
        self.text_sidebar.append(scrolled_window)
        scrolled_window = Gtk.ScrolledWindow(margin_bottom=12, css_classes=["card"])
        scrolled_window.set_policy(2,1)
        scrolled_window.set_child(self.font_box)

        self.text_sidebar.append(scrolled_window)

        transparent_box = Adw.ActionRow(title="Spaces do not overwrite", margin_bottom=12, css_classes=["card"])
        self.transparent_check = Gtk.CheckButton()
        transparent_box.add_suffix(self.transparent_check)

        # self.text_sidebar.append(homogeneous_box)
        self.text_sidebar.append(transparent_box)
        self.text_sidebar.append(write_button)

        for font in self.font_list:
            if font == "Normal":
                text = "font 123"
            else:
                text = pyfiglet.figlet_format("font 123", font=font)
            font_text_view = Gtk.Label(css_classes=["font-preview"], name=font)

            font_text_view.set_label(text)
            self.font_box.append(font_text_view)

        self.font_box.select_row(self.font_box.get_first_child())

        self.table_sidebar = Gtk.Box(orientation=1, margin_start=12, margin_end=12, margin_bottom=12, margin_top=12)

        columns_row = Adw.ActionRow(title="Columns", css_classes=["card"], margin_bottom=12) #Adw.SpinRow(title="Width")
        columns_spin = Gtk.SpinButton(valign=Gtk.Align.CENTER)
        columns_spin.set_range(1, 5)
        columns_spin.get_adjustment().set_step_increment(1)
        columns_row.add_suffix(columns_spin)
        self.table_sidebar.append(columns_row)

        rows_row = Adw.ActionRow(title="Rows", css_classes=["card"], margin_bottom=12) #Adw.SpinRow(title="Width")
        buttons_box = Gtk.Box(spacing=10)
        rows_adder_button = Gtk.Button(valign=Gtk.Align.CENTER, icon_name="list-add-symbolic")
        rows_adder_button.connect("clicked", self.on_add_row_clicked, columns_spin)
        rows_reset_button = Gtk.Button(valign=Gtk.Align.CENTER, icon_name="user-trash-symbolic")
        buttons_box.append(rows_reset_button)
        buttons_box.append(rows_adder_button)
        rows_row.add_suffix(buttons_box)
        self.table_sidebar.append(rows_row)
        rows_scrolled_window = Gtk.ScrolledWindow(vexpand=True, css_classes=["card"], margin_bottom=12)
        rows_scrolled_window.set_policy(2,1)
        self.rows_box = Gtk.Box(orientation=1, margin_top=6, margin_bottom=6)
        rows_scrolled_window.set_child(self.rows_box)
        self.table_sidebar.append(rows_scrolled_window)

        self.table_types_drop_down = Gtk.DropDown.new_from_strings(["First line as header", "Divide each row", "Not divided"])
        self.table_types_drop_down.connect("notify::selected", self.preview_table)
        self.table_types_drop_down.set_valign(Gtk.Align.CENTER)
        settings_row = Adw.ActionRow(title="Table type", margin_bottom=12, css_classes=["card"])
        settings_row.add_suffix(self.table_types_drop_down)
        self.table_sidebar.append(settings_row)
        rows_reset_button.connect("clicked", self.on_reset_row_clicked, columns_spin)
        enter_button = Gtk.Button(valign=Gtk.Align.END, label="Enter")
        enter_button.connect("clicked", self.insert_table_definitely)
        self.table_sidebar.append(enter_button)

        self.picker_sidebar = Gtk.Box(orientation=1)

        self.table_x = 0
        self.table_y = 0

        self.rows_number = 0
        self.columns_number = 0

        self.tree_sidebar = Gtk.Box(orientation=1, margin_start=12, margin_end=12, margin_bottom=12, margin_top=12)

        self.tree_text_entry = Gtk.TextView(vexpand=True, css_classes=["mono-entry", "card"],
                left_margin=12, top_margin=12, wrap_mode=2, height_request=100, accepts_tab=False)
        self.tree_text_entry_buffer = self.tree_text_entry.get_buffer()
        self.tree_text_entry_buffer.connect("insert-text", self.on_tree_text_inserted)
        self.tree_text_entry_buffer.connect("changed", self.preview_tree)

        scrolled_window = Gtk.ScrolledWindow(vexpand=True, margin_bottom=12, width_request=405)
        scrolled_window.set_policy(2,1)
        scrolled_window.set_child(self.tree_text_entry)
        self.tree_sidebar.append(scrolled_window)
        write_button = Gtk.Button(label="Enter")
        write_button.connect("clicked", self.insert_tree_definitely)
        self.tree_sidebar.append(write_button)

        self.tree_x = 0
        self.tree_y = 0

        self.file_path = ""

    def preview_table(self, entry=None, arg=None):
        self.clear(None, self.preview_grid)
        table_type = self.table_types_drop_down.get_selected()
        self.insert_table(table_type, self.preview_grid)

    def insert_text_definitely(self, btn):
        print("clicked")
        start = self.text_entry_buffer.get_start_iter()
        end = self.text_entry_buffer.get_end_iter()
        text = self.text_entry_buffer.get_text(start, end, False)
        if text == "":
            return
        self.add_undo_action(self.tool.capitalize())
        self.clear(None, self.preview_grid)
        self.insert_text(self.grid, self.text_x, self.text_y, text)

    def insert_text_preview(self, widget):
        start = self.text_entry_buffer.get_start_iter()
        end = self.text_entry_buffer.get_end_iter()
        text = self.text_entry_buffer.get_text(start, end, False)
        self.clear(None, self.preview_grid)
        self.insert_text(self.preview_grid, self.text_x, self.text_y, text)

    def insert_table_definitely(self, btn):
        table_type = self.table_types_drop_down.get_selected()
        self.add_undo_action("Table")
        self.insert_table(table_type, self.grid)

    def on_reset_row_clicked(self, btn, columns_spin):
        child = self.rows_box.get_first_child()
        prev_child = None
        while child != None:
            prev_child = child
            child = prev_child.get_next_sibling()
            self.rows_box.remove(prev_child)
        columns_spin.set_sensitive(True)
        self.rows_number = 0

    def on_add_row_clicked(self, btn, columns_spin):
        self.rows_number += 1
        columns_spin.set_sensitive(False)
        values = int(columns_spin.get_value())
        self.columns_number = values

        rows_values_box = Gtk.Box(spacing=6, margin_start=12, margin_end=12, margin_bottom=6, margin_top=6)
        for value in range(values):
            entry = Gtk.Entry(valign=Gtk.Align.CENTER, halign=Gtk.Align.START)
            entry.connect("changed", self.preview_table)
            rows_values_box.append(entry)
        self.rows_box.append(rows_values_box)

        print("new row")

    def is_renderable(self, character):
        return unicodedata.category(character) != "Cn"

    def font_row_selected(self, list_box, row):
        if self.tool == "TEXT":
            self.selected_font = list_box.get_selected_row().get_child().get_name()
            start = self.text_entry_buffer.get_start_iter()
            end = self.text_entry_buffer.get_end_iter()
            text = self.text_entry_buffer.get_text(start, end, False)
            self.clear(None, self.preview_grid)
            self.insert_text(self.preview_grid, self.text_x, self.text_y, text)
        print(self.selected_font)

    def update_area_width(self):
        allocation = self.drawing_area.get_allocation()
        self.drawing_area_width = allocation.width

    def save_button_clicked(self, btn):
        if self.file_path != "":
            self.save_file(self.file_path)
            return
        self.open_file_chooser()

    def open_file(self):
        dialog = Gtk.FileChooserNative(
            title="Open File",
            transient_for=self,
            action=Gtk.FileChooserAction.OPEN,
            modal=True
        )

        dialog.set_accept_label("Open")
        dialog.set_cancel_label("Cancel")

        response = dialog.show()

        dialog.connect("response", self.on_open_file_response)

    def on_open_file_response(self, dialog, response):
        if response == Gtk.ResponseType.CANCEL:
            dialog.destroy()
            return
        elif response == Gtk.ResponseType.ACCEPT:
            path = dialog.get_file().get_path()
            try:
                with open(path, 'r') as file:
                    input_string = file.read()
                lines = input_string.split('\n')
                num_lines = len(lines)
                max_chars = max(len(line) for line in lines)
                if num_lines > self.canvas_max_x or max_chars > self.canvas_max_y:
                    toast = Adw.Toast(title="Opened file exceeds the maximum canvas size")
                    self.toast_overlay.add_toast(toast)
                self.change_canvas_size(max(max_chars, 10), max(num_lines, 5))
                self.add_undo_action("Open")
                self.force_clear(self.grid)
                self.insert_text(self.grid, 0, 0, input_string)
                self.file_path = path
                file_name = os.path.basename(self.file_path)
                self.title_widget.set_subtitle(file_name)
            except IOError:
                print(f"Error reading {path}.")

        dialog.destroy()

    def new_canvas(self):
        self.add_undo_action("Clear")
        self.force_clear(self.grid)
        self.change_canvas_size(50, 25)
        self.file_path = ""
        self.title_widget.set_subtitle("")
        self.undo_changes = []
        self.undo_button.set_sensitive(False)
        self.undo_button.set_tooltip_text("")


    def save_as_action(self):
        self.open_file_chooser()

    def open_file_chooser(self):
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
            file_path = dialog.get_file().get_path()
            self.save_file(file_path)
        dialog.destroy()

    def save_file(self, file_path):
        self.file_path = file_path
        file_name = os.path.basename(file_path)
        self.title_widget.set_subtitle(file_name)
        try:
            with open(file_path, 'w') as file:
                file.write(self.get_canvas_content())
            print(f"Content written to {file_path} successfully.")
            toast = Adw.Toast(title="Saved successfully", timeout=2)
            self.toast_overlay.add_toast(toast)
        except IOError:
            print(f"Error writing to {file_path}.")

    def change_char(self, btn, flow_box):
        self.free_char = btn.get_label()
        print(f"0x{ord(self.free_char):04X}")

    def show_sidebar(self, btn):
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

    def on_change_canvas_size_btn_clicked(self, btn):
        x = int(self.width_spin.get_value())
        y = int(self.height_spin.get_value())

        self.change_canvas_size(x, y)

    def change_canvas_size(self, final_x, final_y):
        x_delta = final_x - self.canvas_x
        y_delta = final_y - self.canvas_y

        if y_delta > 0:
            for line in range(y_delta):
                if self.canvas_y + 1 > self.canvas_max_y:
                    break
                self.canvas_y += 1
                for x in range(self.canvas_x):
                    self.grid.attach(Gtk.Label(name=str(self.canvas_y), label=" ", css_classes=["ascii"], width_request=self.x_mul, height_request=self.y_mul), x, self.canvas_y - 1, 1, 1)
                    self.preview_grid.attach(Gtk.Label(label=" ", css_classes=["ascii"], width_request=self.x_mul, height_request=self.y_mul), x, self.canvas_y - 1, 1, 1)
        elif y_delta < 0:
            for line in range(abs(y_delta)):
                if self.canvas_y == 0:
                    break
                self.canvas_y -= 1
                for x in range(self.canvas_x):
                    self.grid.remove(self.grid.get_child_at(x, self.canvas_y))
                    self.preview_grid.remove(self.preview_grid.get_child_at(x, self.canvas_y))

        if x_delta > 0:
            for column in range(x_delta):
                if self.canvas_x + 1 > self.canvas_max_x:
                    break
                self.canvas_x += 1
                for y in range(self.canvas_y):
                    self.grid.attach(Gtk.Label(name=str(self.canvas_x), label=" ", css_classes=["ascii"], width_request=self.x_mul, height_request=self.y_mul), self.canvas_x - 1, y, 1, 1)
                    self.preview_grid.attach(Gtk.Label(label=" ", css_classes=["ascii"], width_request=self.x_mul, height_request=self.y_mul), self.canvas_x - 1, y, 1, 1)
        elif x_delta < 0:
            for column in range(abs(x_delta)):
                if self.canvas_x == 0:
                    break
                self.canvas_x -= 1
                for y in range(self.canvas_y):
                    self.grid.remove(self.grid.get_child_at(self.canvas_x, y))
                    self.preview_grid.remove(self.preview_grid.get_child_at(self.canvas_x, y))

        self.drawing_area_width = self.drawing_area.get_allocation().width

        self.width_spin.set_value(self.canvas_x)
        self.height_spin.set_value(self.canvas_y)

    def change_style(self, btn, box):
        child = box.get_first_child()
        index = 1
        while child != None:
            if child.get_active():
                self.style = index
                if self.tool == "TABLE":
                    self.preview_table()
                elif self.tool == "TREE":
                    self.preview_tree()
                return
            child = child.get_next_sibling()
            index += 1

    def remove_all_pages(self):
        pages_number = self.sidebar_notebook.get_n_pages()
        for n in range(pages_number):
            self.sidebar_notebook.remove_page(0)
        self.clear(None, self.preview_grid)

    def on_click_pressed(self, click, arg, x, y):
        if self.flip:
            if self.drawing_area_width == 0:
                self.update_area_width()
            x = self.drawing_area_width - x
        x_char = int(x / self.x_mul)
        y_char = int(y / self.y_mul)

        if self.tool == "FREE":
            self.add_undo_action("Freehand")
            self.draw_char(x_char, y_char)

    def on_click_released(self, click, arg, x, y):
        if self.flip:
            if self.drawing_area_width == 0:
                self.update_area_width()
            x = self.drawing_area_width - x
        x_char = int(x / self.x_mul)
        y_char = int(y / self.y_mul)

        if self.tool == "TEXT":
            self.text_x = x_char
            self.text_y = y_char
            start = self.text_entry_buffer.get_start_iter()
            end = self.text_entry_buffer.get_end_iter()
            text = self.text_entry_buffer.get_text(start, end, False)
            self.clear(None, self.preview_grid)
            self.insert_text(self.preview_grid, self.text_x, self.text_y, text)

        elif self.tool == "TABLE":
            self.table_x = x_char
            self.table_y = y_char
            self.clear(None, self.preview_grid)
            table_type = self.table_types_drop_down.get_selected()
            self.insert_table(table_type, self.preview_grid)

        elif self.tool == "TREE":
            self.tree_x = x_char
            self.tree_y = y_char
            self.preview_tree()

        elif self.tool == "PICKER":
            child = self.grid.get_child_at(x_char, y_char)
            if child:
                self.free_char = child.get_label()

    def on_click_stopped(self, arg):
        pass

    def on_choose_free_line(self, btn):
        self.reset_text_entry()
        if btn.get_active():
            self.tool = "FREE-LINE"
        else:
            self.tool = ""

        self.show_sidebar_button.set_sensitive(True)
        if not self.overlay_split_view.get_folded():
            self.overlay_split_view.set_reveal_flap(True)

        self.remove_all_pages()
        label = Gtk.Label(label="Styles")
        self.sidebar_notebook.append_page(self.lines_styles_selection, label)

    def on_choose_picker(self, btn):
        self.reset_text_entry()
        if btn.get_active():
            self.tool = "PICKER"

        self.show_sidebar_button.set_sensitive(True)
        if not self.overlay_split_view.get_folded():
            self.overlay_split_view.set_reveal_flap(True)

        self.remove_all_pages()
        label = Gtk.Label(label="Picker")
        self.sidebar_notebook.append_page(self.picker_sidebar, label)

    def on_choose_rectangle(self, btn):
        self.reset_text_entry()
        if btn.get_active():
            self.tool = "RECTANGLE"

        self.show_sidebar_button.set_sensitive(True)
        if not self.overlay_split_view.get_folded():
            self.overlay_split_view.set_reveal_flap(True)

        self.remove_all_pages()
        label = Gtk.Label(label="Styles")
        self.sidebar_notebook.append_page(self.lines_styles_selection, label)

    def on_choose_filled_rectangle(self, btn):
        self.reset_text_entry()
        if btn.get_active():
            self.tool = "FILLED-RECTANGLE"

        self.show_sidebar_button.set_sensitive(True)
        if not self.overlay_split_view.get_folded():
            self.overlay_split_view.set_reveal_flap(True)

        self.remove_all_pages()
        label = Gtk.Label(label="Chars")
        self.sidebar_notebook.append_page(self.free_char_list, label)

    def on_choose_line(self, btn):
        self.reset_text_entry()
        if btn.get_active():
            self.tool = "LINE"

        self.show_sidebar_button.set_sensitive(True)
        if not self.overlay_split_view.get_folded():
            self.overlay_split_view.set_reveal_flap(True)

        self.remove_all_pages()
        label = Gtk.Label(label="Styles")
        self.sidebar_notebook.append_page(self.lines_styles_selection, label)

    def on_choose_text(self, btn):
        if btn.get_active():
            self.tool = "TEXT"

        self.show_sidebar_button.set_sensitive(True)
        self.overlay_split_view.set_reveal_flap(True)

        self.remove_all_pages()
        label = Gtk.Label(label="Text")
        self.sidebar_notebook.append_page(self.text_sidebar, label)

    def on_choose_table(self, btn):
        if btn.get_active():
            self.tool = "TABLE"

        self.show_sidebar_button.set_sensitive(True)
        self.overlay_split_view.set_reveal_flap(True)

        self.remove_all_pages()
        label = Gtk.Label(label="Table")
        self.sidebar_notebook.append_page(self.table_sidebar, label)
        label = Gtk.Label(label="Styles")
        self.sidebar_notebook.append_page(self.lines_styles_selection, label)

    def on_choose_tree_list(self, btn):
        if btn.get_active():
            self.tool = "TREE"

        self.show_sidebar_button.set_sensitive(True)
        self.overlay_split_view.set_reveal_flap(True)

        self.remove_all_pages()
        label = Gtk.Label(label="Tree View")
        self.sidebar_notebook.append_page(self.tree_sidebar, label)
        label = Gtk.Label(label="Styles")
        self.sidebar_notebook.append_page(self.lines_styles_selection, label)

    def on_choose_free(self, btn):
        self.reset_text_entry()
        if btn.get_active():
            self.tool = "FREE"

        self.show_sidebar_button.set_sensitive(True)
        if not self.overlay_split_view.get_folded():
            self.overlay_split_view.set_reveal_flap(True)

        self.remove_all_pages()
        label = Gtk.Label(label="Chars")
        self.sidebar_notebook.append_page(self.free_char_list, label)
        label = Gtk.Label(label="Freehand Brush")
        self.sidebar_notebook.append_page(self.freehand_sidebar, label)

    def on_choose_eraser(self, btn):
        self.reset_text_entry()
        if btn.get_active():
            self.tool = "ERASER"

        self.show_sidebar_button.set_sensitive(True)
        if not self.overlay_split_view.get_folded():
            self.overlay_split_view.set_reveal_flap(True)

        self.remove_all_pages()
        label = Gtk.Label(label="Eraser")
        self.sidebar_notebook.append_page(self.eraser_sidebar, label)

    def reset_text_entry(self):
        self.text_entry_buffer.set_text("")

    def on_scale_value_changed(self, scale, var):
        var = scale.get_value()

    def on_choose_arrow(self, btn):
        self.reset_text_entry()
        if btn.get_active():
            self.tool = "ARROW"

        self.show_sidebar_button.set_sensitive(True)
        if not self.overlay_split_view.get_folded():
            self.overlay_split_view.set_reveal_flap(True)

        self.remove_all_pages()
        label = Gtk.Label(label="Styles")
        self.sidebar_notebook.append_page(self.lines_styles_selection, label)

    def clear(self, btn=None, grid=None):
        print("clear")
        if grid != self.grid:
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
        print("force clear")
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
            self.add_undo_action("Freehand Line")
            self.prev_char_pos = [start_x_char, start_y_char]
        elif self.tool == "FREE":
            self.add_undo_action("Freehand")
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
            self.draw_filled_rectangle(start_x_char, start_y_char, width, height, self.preview_grid, self.free_char)
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
        if self.tool != "TEXT" and self.tool != "TABLE" and self.tool != "TREE":
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
            self.draw_filled_rectangle(start_x_char, start_y_char, width, height, self.grid, self.free_char)
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
        self.prev_char_pos = [self.prev_pos[0], self.prev_pos[1]]
        self.prev_pos = [new_x, new_y]

    def insert_text(self, grid, start_x, start_y, text):
        # self.clear(None, self.preview_grid)
        transparent = self.transparent_check.get_active()
        # print(text)
        x = start_x
        y = start_y
        if self.selected_font != "Normal" and self.tool == "TEXT":
            text = pyfiglet.figlet_format(text, font=self.selected_font)
        for char in text:
            if x >= self.canvas_x:
                if ord(char) == 10: # \n char
                    y += 1
                    x = start_x
                continue
            if y >= self.canvas_y:
                break
            if emoji.is_emoji(char):
                continue
            child = grid.get_child_at(x, y)
            if not child:
                continue
            elif ord(char) < 32: # empty chars
                if ord(char) == 10: # \n char
                    y += 1
                    x = start_x
                    continue
                if ord(char) == 9: # tab
                    for i in range(4):
                        if transparent:
                            if self.flip:
                                x -= 1
                            else:
                                x += 1
                            continue
                        child = grid.get_child_at(x, y)
                        if not child:
                            continue
                        if grid == self.grid:
                            self.undo_changes[0].add_change(x, y, child.get_label())
                        child.set_label(" ")
                        self.changed_chars.append([x, y])
                        if self.flip:
                            x -= 1
                        else:
                            x += 1
                    continue
            elif char == " " and transparent:
                if self.flip:
                    x -= 1
                else:
                    x += 1
                continue
            if grid == self.grid:
                self.undo_changes[0].add_change(x, y, child.get_label())
            child.set_label(char)
            self.changed_chars.append([x, y])
            if self.flip:
                x -= 1
            else:
                x += 1
        print(self.canvas_x, self.canvas_y)

    def draw_char(self, x_coord, y_coord):
        brush_size = self.free_scale.get_adjustment().get_value()
        for delta in self.brush_sizes[int(brush_size - 1)]:
            child = self.grid.get_child_at(x_coord + delta[0], y_coord + delta[1])
            if child:
                if child.get_label() == self.free_char:
                    continue
                self.undo_changes[0].add_change(x_coord + delta[0], y_coord + delta[1], child.get_label())
                child.set_label(self.free_char)

    def erase_char(self, x_coord, y_coord):
        brush_size = self.eraser_scale.get_adjustment().get_value()
        for delta in self.brush_sizes[int(brush_size - 1)]:
            child = self.grid.get_child_at(x_coord + delta[0], y_coord + delta[1])
            if child:
                if child.get_label() == " ":
                    continue
                self.undo_changes[0].add_change(x_coord + delta[0], y_coord + delta[1], child.get_label())
                child.set_label(" ")

    def draw_filled_rectangle(self, start_x_char, start_y_char, width, height, grid, char):
        for y in range(height):
            for x in range(width):
                self.set_char_at(start_x_char + x, start_y_char + y, grid, char)

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

        self.set_char_at(start_x_char + width - 1, start_y_char, grid, self.top_right())
        self.set_char_at(start_x_char + width - 1, start_y_char + height - 1, grid, self.bottom_right())
        self.set_char_at(start_x_char, start_y_char, grid, self.top_left())
        self.set_char_at(start_x_char, start_y_char + height - 1, grid, self.bottom_left())

    def on_tree_text_inserted(self, buffer, loc, text, lenght):
        spaces = 0
        if text == "\n":
            start_iter = loc.copy()
            start_iter.set_line_offset(0)
            end_iter = start_iter.copy()
            start_iter.backward_char()
            while not end_iter.ends_line():
                start_iter.forward_char()
                end_iter.forward_char()
                char = buffer.get_text(start_iter, end_iter, False)
                if char != " ":
                    break
                spaces += 1
            indentation = " " * spaces
            buffer.insert(loc, f"{indentation}")
            loc.backward_chars(spaces)
            end_iter = buffer.get_end_iter()

        self.preview_tree()

    def preview_tree(self, widget=None):
        self.clear(None, self.preview_grid)
        start = self.tree_text_entry_buffer.get_start_iter()
        end = self.tree_text_entry_buffer.get_end_iter()
        input_text = self.tree_text_entry_buffer.get_text(start, end, False)
        self.insert_tree(self.preview_grid, self.tree_x, self.tree_y, input_text)

    def insert_tree_definitely(self, widget=None):
        self.clear(None, self.preview_grid)
        self.add_undo_action("Treeview")
        start = self.tree_text_entry_buffer.get_start_iter()
        end = self.tree_text_entry_buffer.get_end_iter()
        input_text = self.tree_text_entry_buffer.get_text(start, end, False)
        self.insert_tree(self.grid, self.tree_x, self.tree_y, input_text)

    def insert_tree(self, grid, start_x, start_y, input_text):
        lines = input_text.split("\n")
        processed_lines = []
        current_indent = 0
        leading_spaces = []
        indent_level = 0
        print("------tree------")
        for index, line in enumerate(lines):
            print("------line------")
            stripped_line = line.lstrip(' ')  # Remove leading underscores
            indent_space = len(line) - len(stripped_line)
            line_number = len(leading_spaces)
            if line_number > 0:
                if indent_space > leading_spaces[-1]:
                    indent_level = current_indent + 1
                elif indent_space == leading_spaces[-1]:
                    indent_level = current_indent
                else:
                    previos_spaces = 0
                    indent_level = current_indent - 1
                    for i in range(line_number - 1, 0, -1):
                        print(indent_level, indent_space, leading_spaces[i])
                        if i != 0:
                            leading_spaces[i] #previous spaces
                            indent_space # current spaces
                            if leading_spaces[i] < indent_space:
                                break
                            if leading_spaces[i] < previos_spaces:
                                indent_level -= 1
                                previos_spaces = leading_spaces[i]
                            elif leading_spaces[i] > previos_spaces:
                                print(f"the indent is {processed_lines[i - line_number][0]} was {indent_level}")
                                indent_level = processed_lines[i - line_number][0]
                                previos_spaces = leading_spaces[i]
            current_indent = indent_level
            leading_spaces.append(indent_space)
            processed_lines.append([indent_level, stripped_line])

        tree_structure = ""

        y = self.tree_y
        for index, (indent, text) in enumerate(processed_lines):
            x = self.tree_x + (indent) * 4
            self.insert_text(grid, x, y, text)
            if indent != 0:
                self.set_char_at(x - 1, y, grid, " ")
                self.set_char_at(x - 2, y, grid, self.bottom_horizontal())
                self.set_char_at(x - 3, y, grid, self.bottom_horizontal())
                self.set_char_at(x - 4, y, grid, self.bottom_left())

                prev_index = index - 1
                while processed_lines[prev_index][0] != processed_lines[index][0] - 1:
                    if prev_index < 0:
                        break
                    if processed_lines[prev_index][0] == processed_lines[index][0]:
                        self.set_char_at(x - 4, y - (index - prev_index), grid, self.right_intersect())
                    else:
                        self.set_char_at(x - 4, y - (index - prev_index), grid, self.left_vertical())
                    prev_index -= 1
            y += 1

    def insert_table(self, table_type, grid):
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

        if table_type == 1: # all divided
            heigth = 1 + self.rows_number * 2
        elif table_type == 0: # first line divided
            heigth = 3 + self.rows_number
        else: # not divided
            heigth = 2 + self.rows_number

        self.draw_filled_rectangle(self.table_x, self.table_y, width, heigth, grid, " ")
        self.draw_rectangle(self.table_x, self.table_y, width, heigth, grid)

        x = self.table_x
        for column in range(self.columns_number - 1):
            x += columns_widths[column] + 1
            self.vertical_line(x, self.table_y + 1, heigth - 2, grid, self.right_vertical())
            self.set_char_at(x, self.table_y + heigth - 1, grid, self.top_intersect())
            self.set_char_at(x, self.table_y, grid, self.bottom_intersect())

        y = self.table_y
        if table_type == 1: # all divided
            for row in range(self.rows_number - 1):
                y += 2
                self.horizontal_line(y, self.table_x + 1, width - 2, grid, self.bottom_horizontal())
                self.set_char_at(self.table_x, y, grid, self.right_intersect())
                self.set_char_at(self.table_x + width - 1, y, grid, self.left_intersect())
        elif table_type == 0: # first line divided
            y += 2
            self.horizontal_line(y, self.table_x + 1, width - 2, grid, self.bottom_horizontal())
            self.set_char_at(self.table_x, y, grid, self.right_intersect())
            self.set_char_at(self.table_x + width - 1, y, grid, self.left_intersect())

        y = self.table_y + 1
        x = self.table_x + 1
        for index_row, row in enumerate(table):
            for index, column in enumerate(row):
                self.insert_text(grid, x, y, column)
                x += columns_widths[index] + 1
            if table_type == 1: # all divided
                y += 2
            elif table_type == 0 and index_row == 0: # first line divided
                y += 2
            else:
                y += 1
            x = self.table_x + 1

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
                self.horizontal_line(start_y_char, start_x_char, width - 1, grid, start_horizontal)
                if height < 1:
                    self.vertical_line(start_x_char + width - 1, start_y_char, height + 1, grid, start_vertical)
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
        # if char == " " or char == "":
        #     return
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
                prev_label = child.get_label()
                if grid == self.grid:
                    self.undo_changes[0].add_change(x, start_y + y, prev_label)
                if prev_label == "" or prev_label == " ":
                    child.set_label(char)
                elif prev_label == self.top_horizontal() and self.crossing() != " ":
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
            self.undo_button.set_tooltip_text("")
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

    def select_table_tool(self):
        self.table_button.set_active(True)
        self.tool = "TABLE"

    def select_tree_tool(self):
        self.tree_button.set_active(True)
        self.tool = "TREE"

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
