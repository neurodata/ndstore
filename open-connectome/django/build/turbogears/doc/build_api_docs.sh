#!/bin/bash
# build_api_docs.sh - Build TurboGears API documentation with epydoc

# Run this script from the top-level dir of a /branches/1.5 checkout
# or give the location of the turbogears package on the command line.
SRCDIR="${1:-turbogears}"

if [ ! -d "$SRCDIR" ]; then
    echo "Could not find source directory \"$SRCDIR\"."
    echo "Please see doc/README.txt for usage information."
    echo "Aborting..."
    exit 2
fi

exec epydoc --config doc/doc.ini "$SRCDIR"
