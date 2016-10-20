#!/usr/bin/env python3

'''
Version 0.1 2016.09.11

Copyright (c) 2016, OmegaPhil - OmegaPhil@startmail.com

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


import re
import sys

from sh import xprop

# Unfortunately for Python 3 I can't get at GTK2, so I have to depend on GTK3...
from gi import require_version
require_version("Gdk", "3.0")
require_version("Gtk", "3.0")
from gi.repository import Gdk, GLib, Gtk


# Used for any situation where the code fails to look up a window name
UNKNOWN_WINDOW_NAME = '<UNKNOWN>'


def analyse_clipboard(clipboard):

    # Fetching intial available targets for the clipboard
    targets_available, targets = clipboard.wait_for_targets()

    # Remember that named tuples are only available GTK3.20+ so should not be used
    # I have now had an incident with the laptop where no targets were available,
    # but there was clearly a piece of text on the clipboard (and it was
    # noticeably slow to fetch) - so this is no longer an error situation
    if not targets_available:
        print('Failed to fetch clipboard targets! Data may still be available '
              'on the clipboard', file=sys.stderr)

    # This fetches and converts the clipboard contents as UTF-8 text
    clipboard_text = clipboard.wait_for_text()
    if clipboard_text is None:
        raise Exception('Failed to fetch clipboard text!')

    # Reporting
    print('Available targets: %s\nClipboard text: \'%s\'\n'
          % (pretty_print_targets_list(targets), clipboard_text))


def get_window_name(window_id):

    # Fetching WM_NAME from the xprop output, or raising an error
    # Note that this name isn't really the window title - e.g. for this window,
    # its 'Eclipse', rather than its true title 'Eclipse Workspace - Debug...' etc
    # Its not obvious how to get the real window title currently, I'm satisfied
    # with just the owning program
    output = xprop('-id', window_id)
    for line in output:
        result = re.match('WM_NAME\(STRING\) = "(.*)"', line)
        if result:
            return result.groups()[0]

    # Reaching here means no window name information was detected - this has
    # happened under VNC testing so is no longer an exception
    print('Unable to obtain window name from xprop output for window ID %s - '
          'output:\n\n%s' % (window_id, output), file=sys.stderr)
    return UNKNOWN_WINDOW_NAME


def owner_change(clipboard, event):

    # Obtaining window name - have had some examples after starting up x11vnc
    # where there is no owner
    if not event.owner is None:
        window_id = str(event.owner.get_xid())
        window_name = get_window_name(window_id)
    else:
        print('Clipboard owner change event occurred without a valid event owner'
        'window!', file=sys.stderr)
        window_name = UNKNOWN_WINDOW_NAME
        window_id = 0

    # Reporting details of the change
    # Note that GI enums aren't actually python enums, so instances don't have
    # the name property
    print('Clipboard owner change detected:\nWindow: %s (ID %s), reason: %s, '
          'selection: %s'
          % (window_name, window_id, event.reason.value_nick,
             event.selection.name()))

    # Debug code
    # print('Owner window xid: %s' % event.owner.get_xid())

    # Analysing clipboard
    analyse_clipboard(clipboard)


def pretty_print_targets_list(targets):

    # Targets is a list of Gdk.Atoms - these basically consist of a name and a
    # unimplemented boolean flag which is something to do with checking the
    # existence of the atom rather than just creating it - not relevant for me
    # anyway
    sorted_targets = sorted([target.name() for target in targets],
                            key=str.lower)
    return ', '.join(sorted_targets)


try:

    # Obtaining clipboard and doing initial analysis - not interested in PRIMARY (yet?)
    clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
    analyse_clipboard(clipboard)

    # Hooking into future clipboard ownership change events
    clipboard.connect('owner-change', owner_change)

    # Starting off GLib mainloop rather than GTK mainloop - the latter is not
    # SIGINTable??
    GLib.MainLoop().run()

except KeyboardInterrupt:
    pass
