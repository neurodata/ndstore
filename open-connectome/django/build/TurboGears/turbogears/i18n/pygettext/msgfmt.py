#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-
# Written by Martin v. Löwis <loewis@informatik.hu-berlin.de>

"""Generate binary message catalog from textual translation description.

This program converts a textual Uniforum-style message catalog (.po file) into
a binary GNU catalog (.mo file).  This is essentially the same function as the
GNU msgfmt program, however, it is a simpler implementation.

Usage: msgfmt.py [OPTIONS] filename.po

Options:
    -o file
    --output-file=file
        Specify the output file to write to.  If omitted, output will go to a
        file named filename.mo (based off the input file name).

    -h
    --help
        Print this message and exit.

    -V
    --version
        Display version information and exit.
"""

import sys
import os
import getopt
import struct
import array

__version__ = '1.1'

MESSAGES = {}


def usage(code, msg=''):
    print >> sys.stderr, __doc__
    if msg:
        print >> sys.stderr, msg
    sys.exit(code)


def add(msgid, msgstr, fuzzy):
    """Add a non-fuzzy translation to the dictionary."""
    if not fuzzy and msgstr:
        MESSAGES[msgid] = msgstr


def generate():
    """Return the generated output."""
    keys = MESSAGES.keys()
    # the keys are sorted in the .mo file
    keys.sort()
    offsets = []
    msgids = msgstrs = ''
    for msgid in keys:
        # For each string, we need size and file offset.  Each string is NUL
        # terminated; the NUL does not count into the size.
        offsets.append((len(msgids), len(msgid),
            len(msgstrs), len(MESSAGES[msgid])))
        msgids += msgid + '\0'
        msgstrs += MESSAGES[msgid] + '\0'
    # The header is 7 32-bit unsigned integers.
    # We don't use hash tables, so the keys start right after the index tables
    keystart = 7*4+16*len(keys)
    # and the values start after the keys
    valuestart = keystart + len(msgids)
    koffsets = []
    voffsets = []
    # The string table first has the list of keys, then the list of values.
    # Each entry has first the size of the string, then the file offset.
    for offset1, len1, offset2, len2 in offsets:
        koffsets += [len1, offset1 + keystart]
        voffsets += [len2, offset2 + valuestart]
    offsets = koffsets + voffsets
    output = struct.pack("Iiiiiii",
                         0x950412deL,       # Magic
                         0,                 # Version
                         len(keys),         # # of entries
                         7*4,               # start of key index
                         7*4+len(keys)*8,   # start of value index
                         0, 0)              # size and offset of hash table
    output += array.array("i", offsets).tostring()
    output += msgids
    output += msgstrs
    return output


def make(filename, outfile):
    """Generate the binary message catalog."""

    MESSAGES.clear()

    MSGID = 1
    MSGSTR = 2

    # Compute .mo name from .po name and arguments
    if filename.endswith('.po'):
        infile = filename
    else:
        infile = filename + '.po'
    if outfile is None:
        outfile = os.path.splitext(infile)[0] + '.mo'

    try:
        lines = open(infile).readlines()
    except IOError, msg:
        print >> sys.stderr, msg
        sys.exit(1)

    section = None
    fuzzy = 0

    # Parse the catalog
    lno = 0
    msgid = msgstr = ''
    for line in lines:
        lno += 1
        # If we get a comment line after a msgstr, this is a new entry
        if line[0] == '#' and section == MSGSTR:
            add(msgid, msgstr, fuzzy)
            section = None
            fuzzy = 0
        # Record a fuzzy mark
        if line[:2] == '#,' and line.find('fuzzy'):
            fuzzy = 1
        # Skip comments
        if line[0] == '#':
            continue
        # Now we are in a msgid section, output previous section
        if line.startswith('msgid'):
            if section == MSGSTR:
                add(msgid, msgstr, fuzzy)
            section = MSGID
            line = line[5:]
            msgid = msgstr = ''
        # Now we are in a msgstr section
        elif line.startswith('msgstr'):
            section = MSGSTR
            line = line[6:]
        # Skip empty lines
        line = line.strip()
        if not line:
            continue
        # XXX: Does this always follow Python escape semantics?
        line = eval(line)
        if section == MSGID:
            msgid += line
        elif section == MSGSTR:
            msgstr += line
        else:
            print >> sys.stderr, 'Syntax error on %s:%d' % (infile, lno), \
                  'before:'
            print >> sys.stderr, line
            sys.exit(1)
    # Add last entry
    if section == MSGSTR:
        add(msgid, msgstr, fuzzy)

    # Compute output
    output = generate()

    try:
        open(outfile,"wb").write(output)
    except IOError,msg:
        print >> sys.stderr, msg


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hVo:',
                                   ['help', 'version', 'output-file='])
    except getopt.error, msg:
        usage(1, msg)

    outfile = None
    # parse options
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage(0)
        elif opt in ('-V', '--version'):
            print >> sys.stderr, "msgfmt.py", __version__
            sys.exit(0)
        elif opt in ('-o', '--output-file'):
            outfile = arg
    # do it
    if not args:
        print >> sys.stderr, 'No input file given'
        print >> sys.stderr, "Try `msgfmt --help' for more information."
        return

    for filename in args:
        make(filename, outfile)


if __name__ == '__main__':
    main()
