General
=======

This is a simple script to monitor all X selections (CLIPBOARD, PRIMARY,
SECONDARY) and the X cut buffer 0 (there are actually 8 cut buffers created by
default, only 0 seems to be used) so that I can audit clipboard changes during
VNC sessions.

Unfortunately it depends on GTK3 due to the use of Python 3, and cut buffer 0
polling is just dumb spawning of xcb every second and checking its state.

Run xcb on its own and you get a simple GUI showing the state of all current cut
buffers, nice for auditing.


Requirements
============

Tested with (packages without links are available in Debian repos):

Python v3.5  
GTK v3.20  
python3-gi v3.20  
python3-sh v1.11 (post a bug if you want this dependency dropped, if
enough people complain I will, I just want to get more EXP with this tool)
x11-utils v7.7 (for xprop, will work with much older version too)
xcb v2.4-4.3 (for dumb cut buffer polling, will probably work with older
versions)


Documentation
=============

Without arguments, run the script in a shell will monitor the CLIPBOARD
selection - firstly it will describe the available 'targets' (various data
formats that can be requested from the selection) and then the contents of the
selection in the default format:

    Available targets: COMPOUND_TEXT, MULTIPLE, SAVE_TARGETS, STRING, TARGETS, TEXT, text/_moz_htmlcontext, text/_moz_htmlinfo, text/html, text/x-moz-url-priv, TI
    MESTAMP, UTF8_STRING
    Selection 'CLIPBOARD' text: 'sudo smartctl -x <device>|grep 'of test remaining''

It will wait for clipboard changes to occur indefinitely.

Copying some text in a Pale Moon window resulted in the following output:

    Selection (CLIPBOARD) owner change detected:
    Window: Pale Moon (ID 68194350), reason: new-owner, selection: CLIPBOARD
    Available targets: COMPOUND_TEXT, MULTIPLE, SAVE_TARGETS, STRING, TARGETS, TEXT, text/_moz_htmlcontext, text/_moz_htmlinfo, text/html, text/x-moz-url-priv, TIMESTAMP, UTF8_STRING
    Clipboard text: 'If you follow the sendemail'

You can now also add '--primary', '--secondary' and '--cut-buffer' to monitor
the other X selections/cut buffer 0 at the same time as CLIPBOARD, however
nothing seems to use the SECONDARY selection and so far only VNC has set cut
buffer 0 in my testing (but at least it proves what doesn't happen).


Bugs And Feature Requests
=========================

See the [issue tracker](https://github.com/OmegaPhil/clipboard-observer/issues)


Contact Details
===============

OmegaPhil: OmegaPhil@startmail.com
