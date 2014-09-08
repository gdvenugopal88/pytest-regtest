#!/bin/sh

python -c "import setup; print setup.LONG_DESCRIPTION" | pandoc -o README.md
