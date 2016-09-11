General
=======

This is a simple implementation of a clipboard monitor (just the CLIPBOARD selection, not the PRIMARY or SECONDARY selections etc) so that I could audit clipboard changes during VNC sessions. Unfortunately it depends on GTK3 due to the use of Python 3...


Requirements
============

Tested with (packages without links are available in Debian repos):

Python v3.4  
GTK 3.20  
python-sh v1.11 (post a bug if you want this dependency dropped, if enough people complain I will, I just want to get more EXP with this tool)


Documentation
=============

Just run the script in a shell - firstly it will describe the available 'clipboard targets' (various data formats that can be requested from the clipboard) and then the contents of the clipboard in the default format:

    Available targets: MULTIPLE, SAVE_TARGETS, STRING, TARGETS, TIMESTAMP, UTF8_STRING
    Clipboard text: 'GTK 3.20'

Then it will wait for clipboard changes to occur indefinitely.

Copying some text in a Pale Moon window resulted in the following output:

    Clipboard owner change detected:
    Window: Pale Moon (ID 68194350), reason: new-owner, selection: CLIPBOARD
    Available targets: COMPOUND_TEXT, MULTIPLE, SAVE_TARGETS, STRING, TARGETS, TEXT, text/_moz_htmlcontext, text/_moz_htmlinfo, text/html, text/x-moz-url-priv, TIMESTAMP, UTF8_STRING
    Clipboard text: 'If you follow the sendemail'

Bugs And Feature Requests
=========================

See the [issue tracker](https://github.com/OmegaPhil/clipboard-observer/issues)

Contact Details
===============

OmegaPhil: OmegaPhil@startmail.com
