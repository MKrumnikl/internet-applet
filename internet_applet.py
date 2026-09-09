#!/usr/bin/env python3
import signal
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')

from gi.repository import Gtk, AppIndicator3, GObject, GLib
import os
import sys
import time
import subprocess
import argparse
from threading import Thread

APPLET_NAME = 'internet_applet'

CHECK_HOST = '8.8.8.8'  # Google's public DNS
CHECK_INTERVAL = 15  # seconds

def check_connectivity():
    try:
        result = subprocess.run(
            ['ping', '-c', '1', '-W', '1', CHECK_HOST],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return result.returncode == 0
    except Exception:
        return False


class Indicator:
    def __init__(self, check_interval):
        self.check_interval = check_interval
        self.app = 'internet_applet'
        self.icon_connected = "/usr/share/internet-applet/green_icon.png"  # Custom icon for connected
        self.icon_disconnected = "/usr/share/internet-applet/red_icon.png"  # Custom icon for disconnected

        self.indicator = AppIndicator3.Indicator.new(
            self.app, self.icon_disconnected,
            AppIndicator3.IndicatorCategory.SYSTEM_SERVICES
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self.create_menu())

        # Start the thread to monitor connectivity
        self.update = Thread(target=self.monitor_connectivity)
        self.update.daemon = True
        self.update.start()

    def create_menu(self):
        menu = Gtk.Menu()
        item_quit = Gtk.MenuItem(label='Quit')
        item_quit.connect('activate', self.stop)
        menu.append(item_quit)
        menu.show_all()
        return menu

    def monitor_connectivity(self):
        while True:
            time.sleep(self.check_interval)
            connected = check_connectivity()
            icon = self.icon_connected if connected else self.icon_disconnected
            status = "Connected" if connected else "Disconnected"
            
            GLib.idle_add(self.indicator.set_icon, icon)
            GLib.idle_add(self.indicator.set_label, status, self.app, priority=GLib.PRIORITY_DEFAULT)

    def stop(self, source):
        Gtk.main_quit()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check-interval', help='How often to check internet connectivity', default=CHECK_INTERVAL, type=int)
    args = parser.parse_args()

    Indicator(args.check_interval)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    Gtk.main()


if __name__ == "__main__":
    main()

