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

from .palette import Palette

from .tools import *
from .canvas import Canvas

import threading
import math
import pyfiglet
import unicodedata
import emoji
import os

@Gtk.Template(resource_path='/io/github/nokse22/asciidraw/window.ui')
class AsciiDrawWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'AsciiDrawWindow'

    # drawing_area = Gtk.Template.Child()
    toast_overlay = Gtk.Template.Child()
    char_flow_box = Gtk.Template.Child()
    box_char_flow_box = Gtk.Template.Child()
    block_char_flow_box = Gtk.Template.Child()
    geometric_char_flow_box = Gtk.Template.Child()
    math_char_flow_box = Gtk.Template.Child()
    arrow_char_flow_box = Gtk.Template.Child()
    chars_carousel = Gtk.Template.Child()
    char_group_label = Gtk.Template.Child()
    char_carousel_go_back = Gtk.Template.Child()
    char_carousel_go_next = Gtk.Template.Child()

    font_box = Gtk.Template.Child()
    tree_text_entry = Gtk.Template.Child()
    tree_text_entry_buffer = Gtk.Template.Child()
    transparent_check = Gtk.Template.Child()
    text_entry_buffer = Gtk.Template.Child()
    undo_button = Gtk.Template.Child()

    free_button = Gtk.Template.Child()
    rectangle_button = Gtk.Template.Child()
    freehand_brush_adjustment = Gtk.Template.Child()

    save_import_button = Gtk.Template.Child()
    # preview_grid = Gtk.Template.Child()
    # grid = Gtk.Template.Child()
    lines_styles_box = Gtk.Template.Child()

    sidebar_stack = Gtk.Template.Child()

    free_scale = Gtk.Template.Child()
    eraser_scale = Gtk.Template.Child()
    columns_spin = Gtk.Template.Child()
    rows_box = Gtk.Template.Child()
    table_types_drop_down = Gtk.Template.Child()

    sidebar_stack_switcher = Gtk.Template.Child()

    title_widget = Gtk.Template.Child()

    width_spin = Gtk.Template.Child()
    height_spin = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.settings = Gio.Settings.new('io.github.nokse22.asciidraw')

        self.props.width_request=420
        self.props.height_request=400

        self.settings.bind("window-width", self, "default-width", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("window-height", self, "default-height", Gio.SettingsBindFlags.DEFAULT)

        self.x_mul = 12
        self.y_mul = 24

        self.canvas_x = 50
        self.canvas_y = 25

        self.canvas_max_x = 100
        self.canvas_max_y = 50

        # for y in range(self.canvas_y):
        #     for x in range(self.canvas_x):
        #         self.grid.attach(Gtk.Inscription(nat_chars=0, nat_lines=0, min_chars=0, min_lines=0, css_classes=["ascii"], width_request=self.x_mul, height_request=self.y_mul), x, y, 1, 1)
        #         self.preview_grid.attach(Gtk.Inscription(nat_chars=0, nat_lines=0, min_chars=0, min_lines=0, css_classes=["ascii"], width_request=self.x_mul, height_request=self.y_mul), x, y, 1, 1)

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

        text_direction = self.save_import_button.get_child().get_direction()

        if text_direction == Gtk.TextDirection.LTR:
            self.flip = False
        elif text_direction == Gtk.TextDirection.RTL:
            self.flip = True

        self.canvas = Canvas(self.styles, self.flip)
        self.canvas.connect("undo-added", self.on_undo_added)
        self.toast_overlay.set_child(self.canvas)

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
            style_btn.connect("toggled", self.change_style, self.lines_styles_box)

            self.lines_styles_box.append(style_btn)

        # self.drawing_area.set_draw_func(self.drawing_area_draw, None)

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

        ranges_and_pages = [
            [[  range(0x0021, 0x007F),  # Basic Latin
                range(0x00A0, 0x0100),  # Latin-1 Supplement
                range(0x0100, 0x0180),  # Latin Extended-A
                ], self.char_flow_box],
            [[  range(0x2500, 0x2580),  # Box Drawing
                ], self.box_char_flow_box],
            [[  range(0x2580, 0x25A0),  # Block Elements
                ], self.block_char_flow_box],
            [[  range(0x25A0, 0x25FC),  # Geometric Shapes
                range(0x25FF, 0x2600),
                ], self.geometric_char_flow_box],
            [[  range(0x2190, 0x2200),
                ], self.arrow_char_flow_box],
            [[  range(0x2200, 0x22C7),  # Mathematical Operators
                range(0x22CB, 0x2300),
                ], self.math_char_flow_box]
        ]

        for chars_group in ranges_and_pages:
            unicode_ranges = chars_group[0]
            flow_box = chars_group[1]

            for code_range in unicode_ranges:
                for code_point in code_range:
                    char = chr(code_point)
                    new_button = Gtk.Button(label=char, css_classes=["flat", "ascii"])
                    new_button.connect("clicked", self.change_char, flow_box)
                    flow_box.append(new_button)

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

        self.selected_font = "Normal"

        for font in self.font_list:
            if font == "Normal":
                text = "font 123"
            else:
                text = pyfiglet.figlet_format("font 123", font=font)
            font_text_view = Gtk.Label(css_classes=["font-preview"], name=font)

            font_text_view.set_label(text)
            self.font_box.append(font_text_view)

        self.font_box.select_row(self.font_box.get_first_child())

        self.table_x = 0
        self.table_y = 0

        self.rows_number = 0
        self.columns_number = 0

        self.tree_x = 0
        self.tree_y = 0

        self.file_path = ""

        self.sidebar_stack.set_visible_child_name("character_page")

        self.palettes = []

        directory_path = "palettes"
        os.makedirs(directory_path, exist_ok=True)
        files = os.listdir(directory_path)

        for filename in os.listdir(directory_path):
            filepath = os.path.join(directory_path, filename)
            if os.path.isfile(filepath):
                with open(filepath, 'r') as file:
                    chars = file.read()
                palette_name = os.path.splitext(filename)[0]
                palette = Palette(palette_name, chars)
                self.palettes.append(palette)

        self.add_palette_to_ui(self.palettes)

        self.freehand = Freehand(self.canvas)
        self.freehand.bind_property('active', self.free_button, 'active', GObject.BindingFlags.BIDIRECTIONAL)
        self.freehand.bind_property('size', self.freehand_brush_adjustment, 'value', GObject.BindingFlags.BIDIRECTIONAL)
        self.freehand.bind_property('char', self.canvas, 'char', GObject.BindingFlags.BIDIRECTIONAL)

        self.rectangle = Rectangle(self.canvas)
        self.rectangle.bind_property('active', self.rectangle_button, 'active', GObject.BindingFlags.BIDIRECTIONAL)

    def add_palette_to_ui(self, palettes):
        for palette in palettes:
            flow_box = Gtk.FlowBox(selection_mode=2, margin_top=3, margin_bottom=3, margin_start=3, margin_end=3, valign=Gtk.Align.START)
            for char in palette.chars:
                new_button = Gtk.Button(label=char, css_classes=["flat", "ascii"])
                new_button.connect("clicked", self.change_char, flow_box)
                flow_box.append(new_button)
            scrolled_window = Gtk.ScrolledWindow(name=palette.name)
            scrolled_window.set_child(flow_box)
            self.chars_carousel.append(scrolled_window)
            print(f"added {palette}")

        pos = self.chars_carousel.get_position()
        if pos != self.chars_carousel.get_n_pages() - 1:
            self.char_carousel_go_next.set_sensitive(True)

    def add_new_palette(self, palette_name, palette_chars):
        os.makedirs("/palettes", exist_ok=True)

        with open(f"palettes/{palette_name}", 'w') as file:
            file.write(palette_chars)

        palette = Palette(palette_name ,palette_chars)

        self.add_palette_to_ui([palette])

    @Gtk.Template.Callback("char_pages_go_back")
    def char_pages_go_back(self, btn):
        print("back")
        pos = self.chars_carousel.get_position()
        if pos == 0:
            return
        new_page = self.chars_carousel.get_nth_page(pos - 1)
        self.chars_carousel.scroll_to(new_page, False)
        self.char_group_label.set_label(new_page.get_name())
        self.char_carousel_go_next.set_sensitive(True)
        if pos - 1 == 0:
            btn.set_sensitive(False)

    @Gtk.Template.Callback("char_pages_go_next")
    def char_pages_go_next(self, btn):
        print("next")
        pos = self.chars_carousel.get_position()
        if pos == self.chars_carousel.get_n_pages() - 1:
            return
        new_page = self.chars_carousel.get_nth_page(pos + 1)
        self.chars_carousel.scroll_to(new_page, False)
        self.char_group_label.set_label(new_page.get_name())
        self.char_carousel_go_back.set_sensitive(True)
        if pos + 1 == self.chars_carousel.get_n_pages() - 1:
            btn.set_sensitive(False)

    @Gtk.Template.Callback("preview_table")
    def preview_table(self, entry=None, arg=None):
        self.clear(None, self.preview_grid)
        table_type = self.table_types_drop_down.get_selected()
        self.insert_table(table_type, self.preview_grid)

    @Gtk.Template.Callback("insert_text_definitely")
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

    @Gtk.Template.Callback("insert_text_preview")
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

    @Gtk.Template.Callback("on_reset_row_clicked")
    def on_reset_row_clicked(self, btn):
        child = self.rows_box.get_first_child()
        prev_child = None
        while child != None:
            prev_child = child
            child = prev_child.get_next_sibling()
            self.rows_box.remove(prev_child)
        self.columns_spin.set_sensitive(True)
        self.rows_number = 0

    @Gtk.Template.Callback("on_add_row_clicked")
    def on_add_row_clicked(self, btn):
        self.rows_number += 1
        self.columns_spin.set_sensitive(False)
        values = int(self.columns_spin.get_value())
        self.columns_number = values

        rows_values_box = Gtk.Box(spacing=6, margin_start=6, margin_end=6, margin_bottom=6, margin_top=6)
        for value in range(values):
            entry = Gtk.Entry(valign=Gtk.Align.CENTER, halign=Gtk.Align.START)
            entry.connect("changed", self.preview_table)
            rows_values_box.append(entry)
        self.rows_box.append(rows_values_box)

    def is_renderable(self, character):
        return unicodedata.category(character) != "Cn"

    @Gtk.Template.Callback("font_row_selected")
    def font_row_selected(self, list_box, row):
        if self.tool == "TEXT":
            self.selected_font = list_box.get_selected_row().get_child().get_name()
            start = self.text_entry_buffer.get_start_iter()
            end = self.text_entry_buffer.get_end_iter()
            text = self.text_entry_buffer.get_text(start, end, False)
            self.clear(None, self.preview_grid)
            self.insert_text(self.preview_grid, self.text_x, self.text_y, text)
        print(self.selected_font)

    @Gtk.Template.Callback("on_delete_all_button_clicked")
    def on_delete_all_button_clicked(self, btn):
        # self.clear(btn, self.grid)
        self.canvas.clear_canvas()

    # @Gtk.Template.Callback("update_area_width")
    # def update_area_width(self):
    #     allocation = self.drawing_area.get_allocation()
    #     self.drawing_area_width = allocation.width

    @Gtk.Template.Callback("save_button_clicked")
    def save_button_clicked(self, btn):
        if self.file_path != "":
            self.save_file(self.file_path)
            return
        self.open_file_chooser()

    def open_file(self):
        dialog = Gtk.FileChooserNative(
            title=_("Open File"),
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
                    toast = Adw.Toast(title=_("Opened file exceeds the maximum canvas size"))
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
            title=_("Save File"),
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
            toast = Adw.Toast(title=_("Saved successfully"), timeout=2)
            self.toast_overlay.add_toast(toast)
        except IOError:
            print(f"Error writing to {file_path}.")

    def change_char(self, btn, flow_box):
        self.free_char = btn.get_label()
        self.canvas.char = btn.get_label()
        print(f"0x{ord(self.free_char):04X}")

    def show_sidebar(self, btn):
        self.overlay_split_view.set_show_sidebar(not self.overlay_split_view.get_show_sidebar())

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
                    char = child.get_text()
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

    @Gtk.Template.Callback("on_change_canvas_size_btn_clicked")
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
                    self.grid.attach(Gtk.Inscription(nat_chars=0, nat_lines=0, min_chars=0, min_lines=0, css_classes=["ascii"], width_request=self.x_mul, height_request=self.y_mul), x, self.canvas_y - 1, 1, 1)
                    self.preview_grid.attach(Gtk.Inscription(nat_chars=0, nat_lines=0, min_chars=0, min_lines=0, css_classes=["ascii"], width_request=self.x_mul, height_request=self.y_mul), x, self.canvas_y - 1, 1, 1)
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
                    self.grid.attach(Gtk.Inscription(nat_chars=0, nat_lines=0, min_chars=0, min_lines=0, css_classes=["ascii"], width_request=self.x_mul, height_request=self.y_mul), self.canvas_x - 1, y, 1, 1)
                    self.preview_grid.attach(Gtk.Inscription(nat_chars=0, nat_lines=0, min_chars=0, min_lines=0, css_classes=["ascii"], width_request=self.x_mul, height_request=self.y_mul), self.canvas_x - 1, y, 1, 1)
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
                self.canvas.style = index
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

        # if self.tool == "FREE":
        #     self.add_undo_action("Freehand")
        #     self.draw_char(x_char, y_char)

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
                self.free_char = child.get_text()

    def on_click_stopped(self, arg):
        pass

    @Gtk.Template.Callback("on_choose_free_line")
    def on_choose_free_line(self, btn):
        # self.reset_text_entry()
        if btn.get_active():
            self.tool = "FREE-LINE"
        else:
            self.tool = ""
        print("free line")
        self.sidebar_stack.set_visible_child_name("style_page")

    @Gtk.Template.Callback("on_choose_picker")
    def on_choose_picker(self, btn):
        # self.reset_text_entry()
        if btn.get_active():
            self.tool = "PICKER"
        print("picker")
        self.sidebar_stack.set_visible_child_name("character_page")

    @Gtk.Template.Callback("on_choose_rectangle")
    def on_choose_rectangle(self, btn):
        # self.reset_text_entry()
        if btn.get_active():
            self.tool = "RECTANGLE"
        print("rect")
        self.sidebar_stack.set_visible_child_name("style_page")

    @Gtk.Template.Callback("on_choose_filled_rectangle")
    def on_choose_filled_rectangle(self, btn):
        # self.reset_text_entry()
        if btn.get_active():
            self.tool = "FILLED-RECTANGLE"
        print("f rect")
        self.sidebar_stack.set_visible_child_name("character_page")

    @Gtk.Template.Callback("on_choose_line")
    def on_choose_line(self, btn):
        # self.reset_text_entry()
        if btn.get_active():
            self.tool = "LINE"
        print("line")
        self.sidebar_stack.set_visible_child_name("style_page")

    @Gtk.Template.Callback("on_choose_text")
    def on_choose_text(self, btn):
        if btn.get_active():
            self.tool = "TEXT"
        print("text")
        self.sidebar_stack.set_visible_child_name("text_page")

    @Gtk.Template.Callback("on_choose_table")
    def on_choose_table(self, btn):
        if btn.get_active():
            self.tool = "TABLE"

        print("table")
        self.sidebar_stack.set_visible_child_name("table_page")

    @Gtk.Template.Callback("on_choose_tree_list")
    def on_choose_tree_list(self, btn):
        if btn.get_active():
            self.tool = "TREE"
        print("tree")
        self.sidebar_stack.set_visible_child_name("tree_page")

    @Gtk.Template.Callback("on_choose_select")
    def on_choose_select(self, btn):
        if btn.get_active():
            self.tool = "SELECT"
        print("select")
        self.sidebar_stack.set_visible_child_name("select_page")

    @Gtk.Template.Callback("on_choose_free")
    def on_choose_free(self, btn):
        if btn.get_active():
            self.tool = "FREE"
            self.freehand.active = True
        print("free")
        self.sidebar_stack.set_visible_child_name("freehand_page")

    @Gtk.Template.Callback("on_choose_eraser")
    def on_choose_eraser(self, btn):
        # self.reset_text_entry()
        if btn.get_active():
            self.tool = "ERASER"
        print("eraser")
        self.sidebar_stack.set_visible_child_name("eraser_page")

    def reset_text_entry(self):
        self.text_entry_buffer.set_text("")

    def on_scale_value_changed(self, scale, var):
        var = scale.get_value()

    @Gtk.Template.Callback("on_choose_arrow")
    def on_choose_arrow(self, btn):
        # self.reset_text_entry()
        if btn.get_active():
            self.tool = "ARROW"
        print("arrow")
        self.sidebar_stack.set_visible_child_name("style_page")

    def clear(self, btn=None, grid=None):
        print("clear")
        if grid != self.grid:
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
            grid = self.grid
        for y in range(self.canvas_y):
            for x in range(self.canvas_x):
                child = grid.get_child_at(x, y)
                if not child:
                    continue
                if grid == self.grid:
                    self.undo_changes[0].add_change(x, y, child.get_text())
                child.set_text(" ")

    def clear_list_of_char(self, chars_list_start, chars_list_end):
        for index in range(chars_list_start, chars_list_end):
            pos = self.changed_chars[index]
            child = self.preview_grid.get_child_at(pos[0], pos[1])
            if not child:
                continue
            child.set_text("")

    def on_drag_begin(self, gesture, start_x, start_y):
        self.start_x = start_x
        self.start_y = start_y

        if self.flip:
            if self.drawing_area_width == 0:
                self.update_area_width()
            self.start_x = self.drawing_area_width - self.start_x

        start_x_char = self.start_x // self.x_mul
        start_y_char = self.start_y // self.y_mul

        if self.tool == "FREE-LINE":
            self.add_undo_action("Freehand Line")
            self.prev_char_pos = [start_x_char, start_y_char]
        # elif self.tool == "FREE":
        #     self.add_undo_action("Freehand")
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

        # if self.tool == "FREE":
        #     self.draw_char((self.start_x + self.end_x)/self.x_mul, (self.start_y + self.end_y)/self.y_mul)

        if self.tool == "ERASER":
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

        elif self.tool == "SELECT":
            # self.draw_free_line(start_x_char + width, start_y_char + height, self.grid)
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

    def add_undo_action(self, name, *args):
        self.undo_changes.insert(0, Change(name))
        self.undo_button.set_sensitive(True)
        self.undo_button.set_tooltip_text(_("Undo ") + self.undo_changes[0].name)

    def on_undo_added(self, widget, undo_name):
        self.undo_button.set_sensitive(True)
        self.undo_button.set_tooltip_text(_("Undo ") + undo_name)

    def drawing_area_draw(self, area, cr, width, height, data):
        cr.save()
        cr.set_source_rgb(0.208, 0.518, 0.894)
        if self.tool == "SELECT":
            cr.rectangle((self.start_x // self.x_mul) * self.x_mul + self.x_mul/2, (self.start_y // self.y_mul) * self.y_mul + self.y_mul/2, self.end_x, self.end_y)
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
                            self.undo_changes[0].add_change(x, y, child.get_text())
                        child.set_text(" ")
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
                self.undo_changes[0].add_change(x, y, child.get_text())
            child.set_text(char)
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
                if child.get_text() == self.free_char:
                    continue
                self.undo_changes[0].add_change(x_coord + delta[0], y_coord + delta[1], child.get_text())
                child.set_text(self.free_char)

    def erase_char(self, x_coord, y_coord):
        brush_size = self.eraser_scale.get_adjustment().get_value()
        for delta in self.brush_sizes[int(brush_size - 1)]:
            child = self.grid.get_child_at(x_coord + delta[0], y_coord + delta[1])
            if child:
                if child.get_text() == " ":
                    continue
                self.undo_changes[0].add_change(x_coord + delta[0], y_coord + delta[1], child.get_text())
                child.set_text(" ")

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

    @Gtk.Template.Callback("on_tree_text_inserted")
    def on_tree_text_inserted(self, buffer, loc, text, length):
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

    @Gtk.Template.Callback("preview_tree")
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
        # print("------tree------")
        for index, line in enumerate(lines):
            # print("------line------")
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
                        # print(indent_level, indent_space, leading_spaces[i])
                        if i != 0:
                            leading_spaces[i] #previous spaces
                            indent_space # current spaces
                            if leading_spaces[i] < indent_space:
                                break
                            if leading_spaces[i] < previos_spaces:
                                indent_level -= 1
                                previos_spaces = leading_spaces[i]
                            elif leading_spaces[i] > previos_spaces:
                                # print(f"the indent is {processed_lines[i - line_number][0]} was {indent_level}")
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
            height = 1 + self.rows_number * 2
        elif table_type == 0: # first line divided
            height = 3 + self.rows_number
        else: # not divided
            height = 2 + self.rows_number

        self.draw_filled_rectangle(self.table_x, self.table_y, width, height, grid, " ")
        self.draw_rectangle(self.table_x, self.table_y, width, height, grid)

        x = self.table_x
        for column in range(self.columns_number - 1):
            x += columns_widths[column] + 1
            self.vertical_line(x, self.table_y + 1, height - 2, grid, self.right_vertical())
            self.set_char_at(x, self.table_y + height - 1, grid, self.top_intersect())
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
                self.undo_changes[0].add_change(x, y, child.get_text())
            child.set_text(char)
            self.changed_chars.append([x, y])

    def vertical_line(self, x, start_y, length, grid, char):
        if length > 0:
            for y in range(abs(length)):
                child = grid.get_child_at(x, start_y + y)
                if not child:
                    continue
                prev_label = child.get_text()
                if grid == self.grid:
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
                if grid == self.grid:
                    self.undo_changes[0].add_change(x, start_y + y + length, child.get_text())
                if child.get_text() == "─": # FIXME make it work universally
                    child.set_text("┼")
                else:
                    child.set_text(char)
                self.changed_chars.append([x, start_y + y + length])

    def horizontal_line(self, y, start_x, width, grid, char):
        if width > 0:
            for x in range(abs(width)):
                child = grid.get_child_at(start_x + x, y)
                if not child:
                    continue
                prev_label = child.get_text()
                if grid == self.grid:
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
                if grid == self.grid:
                    self.undo_changes[0].add_change(start_x + x + width, y, prev_label)
                if prev_label == "" or prev_label == " ":
                    child.set_text(char)
                elif prev_label == self.left_vertical():
                    child.set_text(self.crossing())
                else:
                    child.set_text(char)
                self.changed_chars.append([start_x + x + width, y])

    @Gtk.Template.Callback("undo_first_change")
    def undo_first_change(self, btn=None):
        try:
            change_object = self.undo_changes[0]
        except:
            return
        for change in change_object.changes:
            child = self.grid.get_child_at(change[0], change[1])
            if not child:
                continue
            child.set_text(change[2])
        self.undo_changes.pop(0)
        if len(self.undo_changes) == 0:
            self.undo_button.set_sensitive(False)
            self.undo_button.set_tooltip_text("")
        else:
            self.undo_button.set_tooltip_text(_("Undo ") + self.undo_changes[0].name)

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

    # def select_free_tool(self):
    #     self.free_button.set_active(True)
    #     self.tool = "FREE"

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
