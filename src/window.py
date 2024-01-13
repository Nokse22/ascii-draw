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
from .new_palette_window import NewPaletteWindow

from .tools import *
from .canvas import Canvas

import threading
import math
import pyfiglet
import unicodedata
import emoji
import os

@Gtk.Template(resource_path='/io/github/nokse22/asciidraw/ui/window.ui')
class AsciiDrawWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'AsciiDrawWindow'

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
    filled_rectangle_button = Gtk.Template.Child()
    line_button = Gtk.Template.Child()
    select_button = Gtk.Template.Child()
    text_button = Gtk.Template.Child()
    tree_button = Gtk.Template.Child()
    table_button = Gtk.Template.Child()
    picker_button = Gtk.Template.Child()
    eraser_button = Gtk.Template.Child()

    eraser_adjustment = Gtk.Template.Child()
    line_arrow_switch = Gtk.Template.Child()
    line_type_combo = Gtk.Template.Child()

    freehand_brush_adjustment = Gtk.Template.Child()

    primary_char_button = Gtk.Template.Child()
    secondary_char_button = Gtk.Template.Child()

    save_import_button = Gtk.Template.Child()
    lines_styles_box = Gtk.Template.Child()

    sidebar_stack = Gtk.Template.Child()

    free_scale = Gtk.Template.Child()
    eraser_scale = Gtk.Template.Child()
    columns_spin = Gtk.Template.Child()
    rows_box = Gtk.Template.Child()
    table_types_combo = Gtk.Template.Child()

    sidebar_stack_switcher = Gtk.Template.Child()

    title_widget = Gtk.Template.Child()

    width_spin = Gtk.Template.Child()
    height_spin = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.settings = Gio.Settings.new('io.github.nokse22.asciidraw')

        self.settings.bind("window-width", self, "default-width", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("window-height", self, "default-height", Gio.SettingsBindFlags.DEFAULT)

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
        self.canvas.bind_property('primary_selected', self.primary_char_button, 'active', GObject.BindingFlags.BIDIRECTIONAL)
        self.canvas.bind_property('primary_char', self.primary_char_button, 'label', GObject.BindingFlags.BIDIRECTIONAL)
        self.canvas.bind_property('secondary_char', self.secondary_char_button, 'label', GObject.BindingFlags.BIDIRECTIONAL)
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

        self.freehand = Freehand(self.canvas)
        self.freehand.bind_property('active', self.free_button, 'active', GObject.BindingFlags.BIDIRECTIONAL)
        self.freehand.bind_property('size', self.freehand_brush_adjustment, 'value', GObject.BindingFlags.BIDIRECTIONAL)
        # self.freehand.bind_property('char', self.canvas, 'char', GObject.BindingFlags.BIDIRECTIONAL)

        self.eraser = Eraser(self.canvas)
        self.eraser.bind_property('active', self.eraser_button, 'active', GObject.BindingFlags.BIDIRECTIONAL)
        self.eraser.bind_property('size', self.eraser_adjustment, 'value', GObject.BindingFlags.BIDIRECTIONAL)

        self.rectangle = Rectangle(self.canvas)
        self.rectangle.bind_property('active', self.rectangle_button, 'active', GObject.BindingFlags.BIDIRECTIONAL)

        self.filled_rectangle = FilledRectangle(self.canvas)
        self.filled_rectangle.bind_property('active', self.filled_rectangle_button, 'active', GObject.BindingFlags.BIDIRECTIONAL)

        self.line = Line(self.canvas)
        self.line.bind_property('active', self.line_button, 'active', GObject.BindingFlags.BIDIRECTIONAL)
        self.line.bind_property('arrow', self.line_arrow_switch, 'active', GObject.BindingFlags.BIDIRECTIONAL)
        self.line.bind_property('line_type', self.line_type_combo, 'selected', GObject.BindingFlags.BIDIRECTIONAL)

        self.select = Select(self.canvas)
        self.select.bind_property('active', self.select_button, 'active', GObject.BindingFlags.BIDIRECTIONAL)

        self.text = Text(self.canvas)
        self.text.bind_property('active', self.text_button, 'active', GObject.BindingFlags.BIDIRECTIONAL)
        self.text.bind_property('transparent', self.transparent_check, 'active', GObject.BindingFlags.BIDIRECTIONAL)
        self.text.bind_property('text', self.text_entry_buffer, 'text', GObject.BindingFlags.BIDIRECTIONAL)

        self.table = Table(self.canvas, self.rows_box)
        self.table.bind_property('active', self.table_button, 'active', GObject.BindingFlags.BIDIRECTIONAL)
        self.table.bind_property('table_type', self.table_types_combo, 'selected', GObject.BindingFlags.BIDIRECTIONAL)
        # self.table.bind_property('text', self.text_entry_buffer, 'text', GObject.BindingFlags.BIDIRECTIONAL)

        self.piker = Picker(self.canvas)
        self.piker.bind_property('active', self.picker_button, 'active', GObject.BindingFlags.BIDIRECTIONAL)

        self.tree = Tree(self.canvas)
        self.tree.bind_property('active', self.tree_button, 'active', GObject.BindingFlags.BIDIRECTIONAL)
        self.tree.bind_property('text', self.tree_text_entry_buffer, 'text', GObject.BindingFlags.BIDIRECTIONAL)

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

        self.style_manager = Adw.StyleManager()
        self.style_manager.connect("notify::dark", self.change_theme)

        self.change_theme()

    def change_theme(self, manager=Adw.StyleManager(), *args):
        print(manager)
        self.canvas.color = 1 if manager.get_dark() else 0
        self.canvas.update()

    def show_new_palette_window(self, chars=''):
        win = NewPaletteWindow(self, palette_chars=chars)
        win.present()

        win.connect("on-add-clicked", self.on_new_palette_add_clicked)

    def on_new_palette_add_clicked(self, win, palette_name, palette_chars):
        palette = Palette(palette_name, palette_chars)
        self.palettes.append(palette)

        self.add_palette_to_ui([palette])

    def add_palette_to_ui(self, palettes):
        for palette in palettes:
            flow_box = Gtk.FlowBox(homogeneous=True, selection_mode=0, margin_top=3, margin_bottom=3, margin_start=3, margin_end=3, valign=Gtk.Align.START)
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

    @Gtk.Template.Callback("insert_text")
    def insert_text_callback(self, *args):
        self.text.insert_text()

    @Gtk.Template.Callback("preview_text")
    def preview_text_callback(self,  *args):
        self.text.preview_text()

    @Gtk.Template.Callback("preview_table") # TABLE
    def preview_table_callback(self, *args):
        self.table.preview_table()
        # self.clear(None, self.preview_grid)
        # table_type = self.table_types_combo.get_selected()
        # self.insert_table(table_type, self.preview_grid)

    @Gtk.Template.Callback("insert_table") # TABLE
    def insert_table_callback(self, btn):
        self.table.insert_table()
        # table_type = self.table_types_combo.get_selected()
        # self.add_undo_action("Table")
        # self.insert_table(table_type, self.grid)

    @Gtk.Template.Callback("on_reset_row_clicked") # TABLE
    def on_reset_row_clicked(self, btn):
        child = self.rows_box.get_first_child()
        prev_child = None
        while child != None:
            prev_child = child
            child = prev_child.get_next_sibling()
            self.rows_box.remove(prev_child)
        self.columns_spin.set_sensitive(True)
        self.table.rows_number = 0

    @Gtk.Template.Callback("on_add_row_clicked") # TABLE
    def on_add_row_clicked(self, btn):
        self.table.rows_number += 1
        self.columns_spin.set_sensitive(False)
        values = int(self.columns_spin.get_value())
        self.table.columns_number = values

        rows_values_box = Gtk.Box(spacing=6, margin_start=6, margin_end=6, margin_bottom=6, margin_top=6)
        for value in range(values):
            entry = Gtk.Entry(valign=Gtk.Align.CENTER, halign=Gtk.Align.START)
            entry.connect("changed", lambda _: self.table.preview_table())
            rows_values_box.append(entry)
        self.rows_box.append(rows_values_box)

    def is_renderable(self, character):
        return unicodedata.category(character) != "Cn"

    @Gtk.Template.Callback("font_row_selected")
    def font_row_selected(self, list_box, row):
        self.text.set_selected_font(list_box.get_selected_row().get_child().get_name())
        self.text.preview_text()

    @Gtk.Template.Callback("save_button_clicked")
    def save_button_clicked(self, btn):
        self.save()

    def save(self, callback=None):
        if self.file_path != "":
            self.save_file(self.file_path)
            if callback:
                callback()
            return
        self.open_file_chooser(callback)

    def open_file(self):
        dialog = Gtk.FileDialog(
            title=_("Open File"),
        )
        dialog.open(self, None, self.on_open_file_response)

    def on_open_file_response(self, dialog, response):
        file = dialog.open_finish(response)
        print(f"Selected File: {file.get_path()}")

        if file:
            path = file.get_path()
            try:
                with open(path, 'r') as file:
                    input_string = file.read()
                lines = input_string.split('\n')
                num_lines = len(lines)
                max_chars = max(len(line) for line in lines)
                # if num_lines > self.canvas_max_x or max_chars > self.canvas_max_y:
                #     toast = Adw.Toast(title=_("Opened file exceeds the maximum canvas size"))
                #     self.toast_overlay.add_toast(toast)
                self.canvas.change_canvas_size(max(max_chars, 10), max(num_lines, 5))
                # self.canvas.add_undo_action("Open")
                self.canvas.clear_canvas()
                self.canvas.draw_text(0, 0, input_string, False, True)
                self.file_path = path
                file_name = os.path.basename(self.file_path)
                self.title_widget.set_subtitle(file_name)
            except IOError:
                print(f"Error reading {path}.")

    def on_response_selected(self, _dialog, task):
        response = _dialog.choose_finish(task)
        print(f'Selected "{response}" response.')

        match response:
            case "discard":
                self.make_new_canvas()
            case "save":
                self.save(self.make_new_canvas)
            case "cancel":
                pass

    def new_canvas(self):
        dialog = Adw.MessageDialog(
            heading="Save Changes?",
            body="You have unsaved changes, do you want to save them?",
            close_response="cancel",
            modal=True,
            transient_for=self,
        )

        dialog.add_response("cancel", "Cancel")
        dialog.add_response("discard", "Discard")
        dialog.add_response("save", "Save")

        dialog.set_response_appearance("discard", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.set_response_appearance("save", Adw.ResponseAppearance.SUGGESTED)

        dialog.choose(None, self.on_response_selected)

    def make_new_canvas(self):
        self.canvas.clear_canvas()
        # self.canvas.change_canvas_size(50, 25)
        self.file_path = ""
        self.title_widget.set_subtitle("")
        self.canvas.undo_changes = []
        self.undo_button.set_sensitive(False)
        self.undo_button.set_tooltip_text("")

    def save_as_action(self):
        self.open_file_chooser()

    def open_file_chooser(self, callback=None):
        dialog = Gtk.FileDialog(
            title=_("Save File As"),
            initial_name=_("drawing"),
        )
        print("saving as")
        dialog.save(self, None, self.on_save_file_response, callback)

    def on_save_file_response(self, dialog, response, callback=None):
        file = dialog.save_finish(response)
        print(f"Selected File: {file.get_path()}")

        if file:
            file_path = file.get_path()
            self.save_file(file_path)

            if callback:
                callback()

    def save_file(self, file_path):
        self.file_path = file_path
        file_name = os.path.basename(file_path)
        self.title_widget.set_subtitle(file_name)
        try:
            with open(file_path, 'w') as file:
                file.write(self.canvas.get_content())
            print(f"Content written to {file_path} successfully.")
            toast = Adw.Toast(title=_("Saved successfully"), timeout=2)
            self.toast_overlay.add_toast(toast)
        except IOError:
            print(f"Error writing to {file_path}.")

    def change_char(self, btn, flow_box):
        if self.primary_char_button.get_active():
            self.primary_char_button.set_label(btn.get_label())
            self.canvas.primary_char = btn.get_label()
        else:
            self.secondary_char_button.set_label(btn.get_label())
            self.canvas.secondary_char = btn.get_label()

    def copy_to_clipboard(self):
        text = self.canvas.get_content()

        clipboard = Gdk.Display().get_default().get_clipboard()
        clipboard.set(text)

    @Gtk.Template.Callback("on_change_canvas_size_btn_clicked")
    def on_change_canvas_size_btn_clicked(self, btn):
        x = int(self.width_spin.get_value())
        y = int(self.height_spin.get_value())

        self.canvas.change_canvas_size(x, y)

    def change_style(self, btn, box):
        child = box.get_first_child()
        index = 1
        while child != None:
            if child.get_active():
                self.style = index
                self.canvas.style = index
                return
            child = child.get_next_sibling()
            index += 1

    @Gtk.Template.Callback("on_choose_picker")
    def on_choose_picker(self, btn):
        print("picker")
        self.sidebar_stack.set_visible_child_name("character_page")

    @Gtk.Template.Callback("on_choose_rectangle")
    def on_choose_rectangle(self, btn):
        print("rect")
        self.sidebar_stack.set_visible_child_name("style_page")

    @Gtk.Template.Callback("on_choose_filled_rectangle")
    def on_choose_filled_rectangle(self, btn):
        print("f rect")
        self.sidebar_stack.set_visible_child_name("character_page")

    @Gtk.Template.Callback("on_choose_line")
    def on_choose_line(self, btn):
        print("line")
        self.sidebar_stack.set_visible_child_name("line_page")

    @Gtk.Template.Callback("on_choose_text")
    def on_choose_text(self, btn):
        print("text")
        self.sidebar_stack.set_visible_child_name("text_page")

    @Gtk.Template.Callback("on_choose_table")
    def on_choose_table(self, btn):
        print("table")
        self.sidebar_stack.set_visible_child_name("table_page")

    @Gtk.Template.Callback("on_choose_tree_list")
    def on_choose_tree_list(self, btn):
        print("tree")
        self.sidebar_stack.set_visible_child_name("tree_page")

    @Gtk.Template.Callback("on_choose_select")
    def on_choose_select(self, btn):
        print("select")
        self.sidebar_stack.set_visible_child_name("character_page")

    @Gtk.Template.Callback("on_choose_free")
    def on_choose_free(self, btn):
        print("free")
        self.sidebar_stack.set_visible_child_name("freehand_page")

    @Gtk.Template.Callback("on_choose_eraser")
    def on_choose_eraser(self, btn):
        print("eraser")
        self.sidebar_stack.set_visible_child_name("eraser_page")

    def new_palette_from_canvas(self):
        content = self.canvas.get_content()
        content = content.replace('\n', '')
        unique_chars = set()

        for char in content:
            if char not in unique_chars:
                unique_chars.add(char)

        unique_string = ''.join(sorted(unique_chars))

        self.show_new_palette_window(unique_string)

    # def add_undo_action(self, name, *args):
    #     self.undo_changes.insert(0, Change(name))
    #     self.undo_button.set_sensitive(True)
    #     self.undo_button.set_tooltip_text(_("Undo ") + self.undo_changes[0].name)

    def on_undo_added(self, widget, undo_name):
        self.undo_button.set_sensitive(True)
        self.undo_button.set_tooltip_text(_("Undo ") + undo_name)

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

        self.tree.preview_tree()

    @Gtk.Template.Callback("preview_tree")
    def preview_tree(self, widget=None):
        self.tree.preview_tree()

    @Gtk.Template.Callback("insert_tree")
    def insert_tree(self, *args):
        self.tree.insert_tree()

    @Gtk.Template.Callback("undo_first_change")
    def undo_first_change(self, btn=None):
        self.canvas.undo(btn or self.undo_button)

    def select_rectangle_tool(self):
        self.rectangle_button.set_active(True)

    def select_filled_rectangle_tool(self):
        self.filled_rectangle_button.set_active(True)

    def select_line_tool(self):
        self.line_button.set_active(True)

    def select_text_tool(self):
        self.text_button.set_active(True)

    def select_table_tool(self):
        self.table_button.set_active(True)

    def select_tree_tool(self):
        self.tree_button.set_active(True)

    def select_free_tool(self):
        self.free_button.set_active(True)

    def select_eraser_tool(self):
        self.eraser_button.set_active(True)

    def select_arrow_tool(self):
        self.arrow_button.set_active(True)

    def select_free_line_tool(self):
        self.free_line_button.set_active(True)

    def select_picker_tool(self):
        self.picker_button.set_active(True)
