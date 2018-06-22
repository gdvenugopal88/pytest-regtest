from __future__ import print_function

import os
import sys
from setuptools import setup

VERSION = (1, 2, 1)

AUTHOR = "Uwe Schmitt"
AUTHOR_EMAIL = "uwe.schmitt@id.ethz.ch"

DESCRIPTION = "pytest plugin for regression tests"

LICENSE = "http://opensource.org/licenses/GPL-3.0"

URL = "https://gitlab.com/uweschmitt/pytest-regtest"

LONG_DESCRIPTION = ""

if len(sys.argv) > 1 and "dist" in sys.argv[1] and "wheel" not in sys.argv[1]:

    assert sys.version_info.major == 3, "please use python 3 to build package"
    from subprocess import check_output

    here = os.path.dirname(os.path.abspath(__file__))
    try:
        rst_content = check_output("pandoc {} -t rst".format(os.path.join(here, "README.md")),
                                shell=True)

        LONG_DESCRIPTION = str(rst_content, encoding="ascii")

    except:
        pass


if __name__ == "__main__":

    setup(
        version="%d.%d.%d" % VERSION,
        name="pytest-regtest",
        py_modules=['pytest_regtest'],
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        url=URL,
        license=LICENSE,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,

        # the following makes a plugin available to pytest
        entry_points={
            'pytest11': [
                'regtest = pytest_regtest',
            ]
        },
        install_requires=["pytest>=3.3.2"],
    )
