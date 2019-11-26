#!/bin/sh

python -c "import setup; print setup.LONG_DESCRIPTION" | pandoc --from rst --to markdown -o README.md
