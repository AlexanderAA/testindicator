"""
================================================================================
Copyright (c) 2011 Alexander Abushkevich <alex@abushkevi.ch>

Permission to use, copy, modify, and distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

================================================================================

A very simple tests failure indicator (tray icon).

Usage:
    Set TEST_CMD, TEST_INTERVAL as needed
    Execute
    $ python testindicator.py %2>1 &
    
================================================================================
"""

## USER SETTINGS 
TEST_CMD = '/path_to/python /path_to/run_tests.py'
TEST_INTERVAL = 30 #seconds
## END USER SETTINGS 

import os
import datetime

import gtk
from twisted.internet import gtk2reactor # gtk-2.0
# to install the proper reactor this must be called before importing reactor from twisted.internet
gtk2reactor.install()
from twisted.internet import reactor, task
from twisted.spread import pb

__author__ = "Alexander Abushkevich"
__version__ = "0.1a"

APP_NAME = "Tests failure indicator"
APP_AUTHORS = (__author__,)
APP_DESCRIPTION = ""
APP_VERSION = __version__
APP_ICON      = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wait.png")
APP_ICON_PASS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pass1.png")
APP_ICON_FAIL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fail.png")
APP_ICON_WAIT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wait.png")

class AppGUI:

    def __init__(self):
        """
        """
        self.create_gui()
        reactor.run()

    def create_gui(self):
        """ Initialize application
        """
        self.tray = gtk.StatusIcon()
        self.tray.set_from_file(APP_ICON_WAIT)
        self.tray.connect('popup-menu', self.on_popup_menu)
        self.tray.connect('activate', self.on_activate)
        self.tray.set_visible(True)
        self.create_right_menu()
        self.tray.set_tooltip("Last run __, result __")
        
        # Run tests immediately after start
        reactor.callLater(0.05, self.run_tests)
        
    def create_right_menu(self):
        """ Create right-click menu
        """
        self._rmenu = gtk.Menu()
        about = gtk.ImageMenuItem(stock_id=gtk.STOCK_ABOUT)
        about.connect("activate", self.on_about_clicked)
        quit = gtk.ImageMenuItem(stock_id=gtk.STOCK_QUIT)
        quit.connect("activate", self.exit)
        self._rmenu.add(about)
        self._rmenu.add(quit)
        self._rmenu.show_all()
            
    def on_popup_menu(self, status, button, time):
        """ Show menu (on right mouse click)
        """
        self._rmenu.popup(None, None, gtk.status_icon_position_menu, button, time, self.tray)
 
    def on_activate(self, *args):
        """ Run tests when someone clicks on tray icon
        """
        self.tray.set_from_file(APP_ICON_WAIT)
        df_show = task.deferLater(reactor, 0, self.run_tests)
        df_show.addErrback(self.show_warning)
        
        
    def show_warning(self, args):
        """ TODO: show warnings
        """
        pass
        
    def on_about_clicked(self, widget):
        """ 'About' dialog
        """
        dlg = gtk.AboutDialog()
        dlg.set_name(APP_NAME)
        dlg.set_comments(APP_DESCRIPTION)
        dlg.set_version(APP_VERSION)
        dlg.set_authors(APP_AUTHORS)
        dlg.run()
        dlg.destroy()
        
    def run_tests(self, *args):
        """ Run TEST_CMD, get exit code, set appropriate icon.
        
        Adds itself to the list of deferred tasks.
        """
        exitcode = os.system(TEST_CMD)
        self.tray.set_tooltip("%s: exitcode %s" % (datetime.datetime.now().isoformat(), exitcode)) 
        if exitcode == 0:
            self.tray.set_from_file(APP_ICON_PASS)
        else:
            self.tray.set_from_file(APP_ICON_FAIL)
        
        # Run me again later
        df_test_again = task.deferLater(reactor, TEST_INTERVAL, self.on_activate)

    def exit(self, *args):
        """ Close the application
        """
        try:
            reactor.stop()
        except twisted.internet.error.ReactorNotRunning:
            print "Error: Reactor is not running"
        finally:
            gtk.main_quit()


if __name__ == "__main__":
    gtk.gdk.threads_init()
    app = AppGUI()
    try:
        gtk.main()
    except KeyboardInterrupt:
        app.exit()
