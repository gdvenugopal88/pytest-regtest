from setuptools import setup

VERSION = (0, 13, 0)

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

To install and activate this plugin execute::

    $ pip install pytest-regtest

from your command line.

This *py.test* plugin provides a fixture named *regtest* for recording data by writing to this
fixture, which behaves like an output stream::

    from __future__ import print_function

    def test_squares_up_to_ten(regtest):

        result = [i*i for i in range(10)]

        # one way to record output:
        print(result, file=regtest)

        # alternative method to record output:
        regtest.write("done")

If you run this test script with *py.test* the first time there is no recorded output for this test
function so far and thus the test will fail with a message including a diff::

    $ py.test
    ...

    def test_squares_up_to_ten(regtest):
    E
    >       Regression test failed
    >
    >       --- is
    >       +++ tobe
    >       @@ -1,2 +1 @@
    >       -[0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
    >       -done
    >       +

For accepting this output, we run *py.test* with the *--reset-regtest* flag::

    $ py.test --regtest-reset

The recorded output is written to files in the subfolder ``_regtest_outputs`` next to your
test script(s).

Now the next execution of *py.test* will succeed::

    $ py.test


Other features
--------------

Another way to record output is the *regtest_redirect* fixture::

    def test_squares_up_to_ten(regtest_redirect):

        result = [i*i for i in range(10)]

        with regtest_redirect():
            print result

You can reset recorded output of files and functions individually as::

    $ py.test --regtest-reset tests/test_00.py
    $ py.test --regtest-reset tests/test_00.py::test_squares_up_to_ten


To supress the diff and only see the stats use::

    $ py.test --regtest-nodiff

If you want to see the during the test run recorded output use::

    $ py.test --regtest-tee -s

If you develop on mixed platforms it might be usefull to ignore white spaces at the
end of the lines when comparing output. This can be achieved by specifying::

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
        install_requires=["pytest"],
    )
