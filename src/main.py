# main.py
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

import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Gio, Adw, Gdk, GLib
from .window import AsciiDrawWindow

theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
theme.add_resource_path("/data/resources/icons/")

class AsciiDrawApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self):
        super().__init__(application_id='io.github.nokse22.asciidraw',
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)

        # self.create_action('quit', self.on_quit, ['<primary>q'])
        self.create_action('about', self.on_about_action)
        self.create_action('preferences', self.on_preferences_action)

        self.create_action('save-as', self.on_save_as_action, ['<control><shift>s'])
        self.create_action('copy-to-clipboard', self.on_copy_to_clipboard_action)
        self.create_action('open', self.on_open_action, ['<control>o'])
        self.create_action('new-canvas', self.on_new_canvas_action, ['<control>n'])

        self.create_action('undo', self.on_undo_action, ['<control>z'])

        self.create_action('rectangle-tool', self.select_rectangle_tool, ['<control>r'])
        self.create_action('filled-rectangle-tool', self.select_filled_rectangle_tool, ['<control><shift>r'])
        self.create_action('line-tool', self.select_line_tool, ['<control>l'])
        self.create_action('text-tool', self.select_text_tool, ['<control>t'])
        self.create_action('table-tool', self.select_table_tool, ['<control><shift>t'])
        self.create_action('tree-tool', self.select_tree_tool, ['<control>U'])
        self.create_action('free-tool', self.select_free_tool, ['<control>f'])
        self.create_action('eraser-tool', self.select_eraser_tool, ['<control>e'])
        self.create_action('arrow-tool', self.select_arrow_tool, ['<control>w'])
        self.create_action('free-line-tool', self.select_free_line_tool, ['<control>g'])
        self.create_action('picker-tool', self.select_picker_tool, ['<control>p'])

        self.create_action('new-palette', self.on_new_palette_action)
        self.create_action('open-palette-folder', self.on_open_palette_folder_action)
        self.create_action('new-palette-from-canvas', self.on_new_palette_from_canvas_action)
        self.create_action('import-palettes', self.on_import_palettes_action)

        self.create_action('clear-canvas', self.on_clear_canvas_action)

        css = '''
        .styles-preview{
            font-family: Monospace;
            font-size: 20px;
            opacity:0.8;
            color: @window_fg_color;
        }
        .ascii-preview{
            background: transparent;
            background-size: 12px 24px;
            background-image:
                linear-gradient(to right, #aaaaaa 1px, transparent 1px),
                linear-gradient(to bottom, #aaaaaa 1px, transparent 1px);
            box-shadow:
                inset 0px 0px 0px 1px #777777,
                0px 0px 10px 10px @headerbar_shade_color;
            opacity:0.4;
        }
        .ascii{
            font-family: Monospace;
            font-size: 20px;
            color: @window_fg_color;
        }
        .mono-entry{
            font-family: Monospace;
            font-size: 20px;
            background: @window_bg_color;
        }
        .font-preview{
            font-family: Monospace;
            font-size: 7px;
            color: @window_fg_color;
        }
        .switcher button{
	        margin-left:3px;
	        margin-right:3px;
            transition: background-color 0ms linear;
        }
        '''
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(css, -1)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def on_new_palette_action(self, *args):
        self.win.show_new_palette_window()

    def on_clear_canvas_action(self, *args):
        self.win.canvas.add_undo_action(_("Clear"))
        self.win.canvas.clear_canvas()

    def on_open_palette_folder_action(self, *args):
        pass

    def on_new_palette_from_canvas_action(self, *args):
        self.win.new_palette_from_canvas()

    def on_import_palettes_action(self, *args):
        pass

    def on_new_canvas_action(self, *args):
        self.win.new_canvas()

    def on_copy_to_clipboard_action(self, *args):
        self.win.copy_to_clipboard()

    def on_save_as_action(self, *args):
        self.win.save_as_action()

    def on_import_action(self, *args):
        pass

    def on_open_action(self, *args):
        self.win.open_file()

    def on_undo_action(self, *args):
        self.win.undo_first_change()

    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        self.win = self.props.active_window
        if not self.win:
            self.win = AsciiDrawWindow(application=self)

        self.win.connect("close-request", self.on_shutdown)

        self.win.present()

    def on_about_action(self, *args):
        """Callback for the app.about action."""
        about = Adw.AboutWindow(transient_for=self.props.active_window,
                                application_name=_("ASCII Draw"),
                                application_icon='io.github.nokse22.asciidraw',
                                developer_name='Nokse',
                                version='0.3.0',
                                website='https://github.com/Nokse22/ascii-draw',
                                issue_url='https://github.com/Nokse22/ascii-draw/issues',
                                developers=['Nokse'],
                                copyright='© 2023 Nokse')
        # Translator credits. Replace "translator-credits" with your name/username, and optionally an email or URL.
        # One name per line, please do not remove previous names.
        about.set_translator_credits(_("translator-credits"))        
        about.present()

    def on_preferences_action(self, widget, _):
        """Callback for the app.preferences action."""
        print('app.preferences action activated')

    def create_action(self, name, callback, shortcuts=None):
        """Add an application action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is
              activated
            shortcuts: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)

    def on_shutdown(self, *args):

        if not self.win.canvas.is_saved and self.win.file_path == "":
            dialog = Adw.MessageDialog(
                heading=_("Save this file?"),
                body=_("You have never saved this file."),
                close_response="cancel",
                modal=True,
                transient_for=self.win,
            )

            dialog.add_response("cancel", _("Cancel"))
            dialog.add_response("discard", _("Discard"))
            dialog.add_response("save", _("Save"))

            dialog.set_response_appearance("discard", Adw.ResponseAppearance.DESTRUCTIVE)
            dialog.set_response_appearance("save", Adw.ResponseAppearance.SUGGESTED)

            # entry = Adw.EntryRow(title="Filename")
            # list_box = Gtk.ListBox(css_classes=["boxed-list"], width_request=340)
            # list_box.append(entry)

            # dialog.set_extra_child(list_box)

            dialog.choose(None, self.on_save_file_with_name_response)
            return True

        if not self.win.canvas.is_saved and self.win.file_path != "":
            dialog = Adw.MessageDialog(
                heading=_("Save changes?"),
                body=_("Not saving will result in losing all changes"),
                close_response="cancel",
                modal=True,
                transient_for=self.win,
            )

            dialog.add_response("cancel", _("Cancel"))
            dialog.add_response("discard", _("Discard"))
            dialog.add_response("save", _("Save"))

            dialog.set_response_appearance("discard", Adw.ResponseAppearance.DESTRUCTIVE)
            dialog.set_response_appearance("save", Adw.ResponseAppearance.SUGGESTED)

            dialog.choose(None, self.on_save_file_with_name_response)
            return True

    def on_save_file_with_name_response(self, dialog, task, *args):
        response = dialog.choose_finish(task)
        if response == "save":
            self.win.save(self.quit)
        elif response == "discard":
            self.quit()

    def on_save_changes(self, dialog, task, *args):
        response = dialog.choose_finish(task)
        if response == "save":
            self.win.save()
        elif response == "discard":
            self.quit()

    def select_rectangle_tool(self, widget, _):
        self.win.select_rectangle_tool()

    def select_filled_rectangle_tool(self, widget, _):
        self.win.select_filled_rectangle_tool()

    def select_line_tool(self, widget, _):
        self.win.select_line_tool()

    def select_text_tool(self, widget, _):
        self.win.select_text_tool()

    def select_table_tool(self, widget, _):
        self.win.select_table_tool()

    def select_tree_tool(self, widget, _):
        self.win.select_tree_tool()

    def select_free_tool(self, widget, _):
        self.win.select_free_tool()

    def select_eraser_tool(self, widget, _):
        self.win.select_eraser_tool()

    def select_arrow_tool(self, widget, _):
        self.win.select_arrow_tool()

    def select_free_line_tool(self, widget, _):
        self.win.select_free_line_tool()

    def select_picker_tool(self, widget, _):
        self.win.select_picker_tool()

def main(version):
    """The application's entry point."""
    app = AsciiDrawApplication()
    return app.run(sys.argv)
