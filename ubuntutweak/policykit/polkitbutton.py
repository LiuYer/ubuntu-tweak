# Ubuntu Tweak - Ubuntu Configuration Tool
#
# Copyright (C) 2007-2011 Tualatrix Chou <tualatrix@gmail.com>
#
# Ubuntu Tweak is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Ubuntu Tweak is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ubuntu Tweak; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA

import dbus
import gobject
from gi.repository import Gtk

from dbusproxy import proxy

class PolkitAction(gobject.GObject):
    """
    PolicyKit action, if changed return 0, means authenticate failed, 
    return 1, means authenticate successfully
    """
    result = 0
    session_bus = dbus.SessionBus()
    __gsignals__ = {
        'changed': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
                    (gobject.TYPE_INT,)),
    }

    def __init__(self, widget):
        gobject.GObject.__init__(self)

        self.widget = widget

    def authenticate(self):
        self.do_authenticate()

    def get_authenticated(self):
        return self.result

    def do_authenticate(self):
        try:
            is_auth = proxy.is_authorized()
        except:
            return

        self.__class__.result = bool(is_auth)

        if self.__class__.result == 1:
            self.emit('changed', 1)
        else:
            self.emit('changed', 0)


class PolkitButton(Gtk.Button):
    __gsignals__ = {
        'changed': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
                    (gobject.TYPE_INT,)),
    }

    def __init__(self):
        gobject.GObject.__init__(self)

        self.set_label(_('_Unlock'))
        self.set_use_underline(True)
        image = Gtk.Image.new_from_stock(Gtk.STOCK_DIALOG_AUTHENTICATION,
                                         Gtk.IconSize.BUTTON)
        self.set_image(image)

        self.action = PolkitAction(self)
        self.action.connect('changed', self.on_action_changed)
        self.connect('clicked', self.on_button_clicked)

    def on_button_clicked(self, widget):
        self.action.authenticate()

    def on_action_changed(self, widget, action):
        if action:
            self.change_button_state()

        self.emit('changed', self.action.get_authenticated())

    def change_button_state(self):
        image = Gtk.Image.new_from_stock(Gtk.STOCK_YES, Gtk.IconSize.BUTTON)
        self.set_image(image)
        self.set_sensitive(False)
