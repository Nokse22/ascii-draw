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

from gi.repository import Gtk, Gio, Adw, Gdk
from .window import AsciiDrawWindow


class AsciiDrawApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self):
        super().__init__(application_id='io.github.nokse22.asciidraw',
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
        self.create_action('quit', lambda *_: self.quit(), ['<primary>q'])
        self.create_action('about', self.on_about_action)
        self.create_action('preferences', self.on_preferences_action)

        self.create_action('rectangle-tool', self.select_rectangle_tool, ['<control>r'])
        self.create_action('line-tool', self.select_line_tool, ['<control>l'])
        self.create_action('text-tool', self.select_text_tool, ['<control>t'])
        self.create_action('free-tool', self.select_free_tool, ['<control>f'])
        self.create_action('eraser-tool', self.select_eraser_tool, ['<control>e'])
        self.create_action('arrow-tool', self.select_arrow_tool, ['<control>a'])
        self.create_action('free-line-tool', self.select_free_line_tool, ['<control>g'])
        self.create_action('picker-tool', self.select_picker_tool, ['<control>p'])

        css = '''
        .ascii-textview{
            background-size: 12px 24px;
            background-image:
                linear-gradient(to right, #c0bfbc55 1px, transparent 1px),
                linear-gradient(to bottom, #c0bfbc55 1px, transparent 1px);
            box-shadow:
                inset 0px 0px 0px 1px #c0bfbc55,
                0px 0px 10px 10px #c0bfbc44;
        }
        .ascii-preview{
            background: transparent;
            opacity: 0.3;
            background-size: 12px 24px;
        }
        .ascii{
            font-family: Monospace;
            font-size: 20px;
        }
        .mono-entry{
            font-family: Monospace;
            font-size: 20px;
            background-size: 12px 24px;
            background-image:
                linear-gradient(to right, #c0bfbc55 1px, transparent 1px),
                linear-gradient(to bottom, #c0bfbc55 1px, transparent 1px);
        }
        .padded{
            padding: 12px;
        }

        '''
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(css, -1)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        self.win = self.props.active_window
        if not self.win:
            self.win = AsciiDrawWindow(application=self)
        self.win.present()

    def on_about_action(self, widget, _):
        """Callback for the app.about action."""
        about = Adw.AboutWindow(transient_for=self.props.active_window,
                                application_name='ascii-draw',
                                application_icon='io.github.nokse22.asciidraw',
                                developer_name='Nokse',
                                version='0.1.0',
                                developers=['Nokse'],
                                copyright='© 2023 Nokse')
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

    def select_rectangle_tool(self, widget, _):
        self.win.select_rectangle_tool()

    def select_line_tool(self, widget, _):
        self.win.select_line_tool()

    def select_text_tool(self, widget, _):
        self.win.select_text_tool()

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
