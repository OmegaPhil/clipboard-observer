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


import argparse
import re
import sys

from sh import xcb, xprop  # pylint: disable=no-name-in-module

# Unfortunately for Python 3 I can't get at GTK2, so I have to depend on GTK3...
from gi import require_version
require_version("Gdk", "3.0")
require_version("Gtk", "3.0")
from gi.repository import Gdk, GLib, Gtk


# Used for any situation where the code fails to look up a window name
UNKNOWN_WINDOW_NAME = '<UNKNOWN>'

cutbuffer_contents = None

# pylint: disable=redefined-outer-name


def analyse_selection(selection, selection_type):
    '''Print state of selection after change detected'''

    # Fetching initial available targets for the selection
    targets_available, targets = selection.wait_for_targets()

    # Remember that named tuples are only available GTK3.20+ so should not be used
    # I have now had an incident with the laptop where no targets were available,
    # but there was clearly a piece of text on the clipboard (and it was
    # noticeably slow to fetch) - so this is no longer an error situation
    if not targets_available:
        print('Failed to fetch \'%s\' selection targets! Data may still be '
              'available in the selection' % selection_type, file=sys.stderr)

    # This fetches and converts the selection contents as UTF-8 text - some
    # selections (e.g. SECONDARY) may be genuinely empty, and therefore return
    # None
    selection_text = selection.wait_for_text()

    # Reporting
    print('Available targets: %s\nSelection \'%s\' text: \'%s\'\n'
          % (pretty_print_targets_list(targets), selection_type, selection_text))


def check_cut_buffer():
    '''Check state of cut buffer 0 and print on change - callback for polling'''

    global cutbuffer_contents  # pylint: disable=global-statement

    # Querying first cut buffer (looks like the other 7 aren't really used?
    # More than 8 buffers can exist
    output = xcb('-p', 0)

    # Report initial value and detect further changes
    if cutbuffer_contents is None:
        print('Initial cutbuffer 0 value: \'%s\'\n' % output)
        cutbuffer_contents = output
    else:
        if cutbuffer_contents != output:
            print('cutbuffer 0 value changed: \'%s\'\n' % output)
            cutbuffer_contents = output

    # This is used as a GLib callback so must return True to not be destroyed
    return True


def get_window_name(window_id):
    '''Fetch WM_NAME from the xprop output, or raise an error'''

    # Note that this name isn't really the window title - e.g. for this window,
    # its 'Eclipse', rather than its true title 'Eclipse Workspace - Debug...' etc
    # Its not obvious how to get the real window title currently, I'm satisfied
    # with just the owning program
    output = xprop('-id', window_id)
    for line in output:

        # Only attempt to match on actual text - the call returns a bytes, which
        # upsets re when the values are out of range. Some windows do offer an
        # '_NET_WM_NAME(UTF8_STRING)' atom, but this is not common enough
        if line.startswith('WM_NAME(STRING)'):
            result = re.match(r'WM_NAME\(STRING\) = "(.*)"', line)
            if result:
                return result.groups()[0]

    # Reaching here means no window name information was detected - this has
    # happened under VNC testing so is no longer an exception
    print('Unable to obtain window name from xprop output for window ID %s - '
          'output:\n\n%s' % (window_id, output), file=sys.stderr)
    return UNKNOWN_WINDOW_NAME


def owner_change(selection, event, selection_type):
    '''Print details of selection owner change and then trigger its analysis'''

    # Obtaining window name - have had some examples after starting up x11vnc
    # where there is no owner
    if not event.owner is None:
        window_id = str(event.owner.get_xid())
        window_name = get_window_name(window_id)
    else:
        print('Selection \'%s\' owner change event occurred without a valid event owner'
        'window!' % selection_type, file=sys.stderr)
        window_name = UNKNOWN_WINDOW_NAME
        window_id = '0'

    # Reporting details of the change
    # Note that GI enums aren't actually python enums, so instances don't have
    # the name property
    print('Selection (%s) owner change detected:\nWindow: %s (ID %s), reason: %s, '
          'selection: %s'
          % (selection_type, window_name, window_id, event.reason.value_nick,
             event.selection.name()))

    # Debug code
    # print('Owner window xid: %s' % event.owner.get_xid())

    # Analysing selection
    analyse_selection(selection, selection_type)


def pretty_print_targets_list(targets):
    '''Pretty print targets available in a selection'''

    # Targets is a list of Gdk.Atoms - these basically consist of a name and a
    # unimplemented boolean flag which is something to do with checking the
    # existence of the atom rather than just creating it - not relevant for me
    # anyway
    sorted_targets = sorted([target.name() for target in targets],
                            key=str.lower)
    return ', '.join(sorted_targets)


# Configuring and parsing passed options
parser = argparse.ArgumentParser()
parser.add_argument('-b', '--cut-buffer', dest='cut_buffer', help='monitor cut '
'buffer 0 contents', action='store_true', default=False)
parser.add_argument('-c', '--clipboard', dest='clipboard', help='monitor the '
'clipboard selection contents', action='store_true', default=True)
parser.add_argument('-p', '--primary', dest='primary', help='monitor the primary'
' selection contents', action='store_true', default=False)
parser.add_argument('-s', '--secondary', dest='secondary', help='monitor the '
'secondary  selection contents', action='store_true', default=False)
options = parser.parse_args()

# Determining selections to monitor
selection_types = []
if options.clipboard:
    selection_types.append(Gdk.SELECTION_CLIPBOARD)
if options.primary:
    selection_types.append(Gdk.SELECTION_PRIMARY)
if options.secondary:
    selection_types.append(Gdk.SELECTION_SECONDARY)

try:

    # Obtaining selections and doing initial analysis - these are not
    # 'clipboards' but X selections, one of which is the CLIPBOARD selection
    # (https://en.wikipedia.org/wiki/X_Window_selection#Selections)
    for selection_type in selection_types:
        selection = Gtk.Clipboard.get(selection_type)
        analyse_selection(selection, selection_type)

        # Hooking into future clipboard ownership change events
        selection.connect('owner-change', owner_change, selection_type)

    if options.cut_buffer:

        # Doing a dumb poll every second of cut buffer 0 when desired
        GLib.timeout_add_seconds(1, check_cut_buffer)

    # Starting off GLib mainloop rather than GTK mainloop - the latter is not
    # SIGINTable??
    GLib.MainLoop().run()

except KeyboardInterrupt:
    pass
