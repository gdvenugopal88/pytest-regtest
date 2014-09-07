from setuptools import setup

VERSION = (0, 0, 5)

AUTHOR = "Uwe Schmitt"
AUTHOR_EMAIL = "uwe.schmitt@id.ethz.ch"

DESCRIPTION = "py.test plugin for regression tests"

LICENSE = "http://opensource.org/licenses/GPL-3.0"

URL="https://sissource.ethz.ch/uweschmitt/pytest-regtest/tree/master"

LONG_DESCRIPTION = """

pytest-regtest
==============

This *py.test* plugin provides a fixture named *regtest* for recording
data like a file output stream. Your tests just record the *tobe-state* by writing to
this stream::

    def test_0(regtest):
        computation = [i*i for i in range(10)]
        print >> regtest, computation

For recording the *approved* state, you run *py.test* with the *--reset-regtest* flag::

    $ py.test --reset-regtest

If you want to check that the testing function produces the same output for later runs, you ommit
the flag and run you tests as usual::

    $ py.test

"""

setup(
    version= "%d.%d.%d" % VERSION,
    name="pytest-regtest",
    py_modules = ['pytest_regtest'],
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license=LICENSE,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,

    # the following makes a plugin available to pytest
    entry_points = {
        'pytest11': [
            'regtest = pytest_regtest',
        ]
    },
)
