# new_palette.py
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
from gi.repository import Gtk, GObject

@Gtk.Template(resource_path="/io/github/nokse22/asciidraw/ui/new_palette.ui")
class NewPaletteDialog(Adw.Dialog):
    __gtype_name__ = 'NewPaletteDialog'

    palette_name_entry = Gtk.Template.Child()
    palette_chars_buffer = Gtk.Template.Child()
    save_button = Gtk.Template.Child()

    __gsignals__ = {
        'on-add-clicked': (GObject.SignalFlags.RUN_FIRST, None, (str,str,))
    }

    def __init__(self, window, palette_chars=''):
        super().__init__()

        self.palette_chars = palette_chars

        self.palette_chars_buffer.set_text(self.palette_chars)

    @Gtk.Template.Callback("on_add_clicked")
    def on_add_clicked(self, btn):
        palette_name = self.palette_name_entry.get_text()
        palette_chars = self.palette_chars_buffer.get_text(self.palette_chars_buffer.get_start_iter(), self.palette_chars_buffer.get_end_iter(), False)
        self.emit('on-add-clicked', palette_name, palette_chars)

        self.close()

    @Gtk.Template.Callback("on_palette_name_text_inserted")
    def on_palette_name_text_inserted(self, entry):
        if entry.get_text() != "":
            self.save_button.set_sensitive(True)
        else:
            self.save_button.set_sensitive(False)
