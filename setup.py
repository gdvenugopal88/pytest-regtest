from setuptools import setup

VERSION = (0, 9, 0)

AUTHOR = "Uwe Schmitt"
AUTHOR_EMAIL = "uwe.schmitt@id.ethz.ch"

DESCRIPTION = "py.test plugin for regression tests"

LICENSE = "http://opensource.org/licenses/GPL-3.0"

URL = "https://sissource.ethz.ch/uweschmitt/pytest-regtest/tree/master"

LONG_DESCRIPTION = """

pytest-regtest
==============

This *pytest*-plugin allows capturing of output of test functions which can be compared
to the captured output from former runs.
This is a common technique to start `TDD <http://en.wikipedia.org/wiki/Test-driven_development>`_
if you have to refactor legacy code which ships without tests.

To install and activate this plugin you have to run:

    $ pip install pytest-regtest

from your command line.

This *py.test* plugin provides a fixture named *regtest* for recording data by writing to this
fixture, which behaves like an output stream::

    def test_squares_up_to_ten(regtest):

        result = [i*i for i in range(10)]

        # one way to record output:
        print >> regtest, result

        # alternative method to record output:
        regtest.write("done")

We can redirect stdout to this stream using the *regtest_redirect* fixture::

    def test_squares_up_to_ten(regtest_redirect):

        result = [i*i for i in range(10)]

        with regtest_redirect():
            print result

For recording the *approved* output, you run *py.test* with the *--reset-regtest* flag::

    $ py.test --regtest-reset

The recorded output is written to text files in the subfolder ``_regtest_outputs`` next to your
test scripts.

You can reset recorded output of files and functions individually as::

    $ py.test --regtest-reset tests/test_00.py
    $ py.test --regtest-reset tests/test_00.py::test_squares_up_to_ten


If you want to check that the testing function still produces the same output, you ommit the flag
and run you tests as usual::

    $ py.test

This shows diffs for the tests failing because the current and recorded output deviate.

To supress the diff and only see the stats use::

    $ py.test --regtest-nodiff

If you want to see the recorded output on the commandline use::

    $ py.test --regtest-tee -s

If you develop on mixed platforms it might be usefull to ignore white spaces at the
end of the lines when comparing output. This can be achieved by specifying

    $ py.test --regtest-ignore-line-endings

"""

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
        install_requires = ["pytest"],
    )
