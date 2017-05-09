from setuptools import setup

VERSION = (0, 15, 1)

AUTHOR = "Uwe Schmitt"
AUTHOR_EMAIL = "uwe.schmitt@id.ethz.ch"

DESCRIPTION = "pytest plugin for regression tests"

LICENSE = "http://opensource.org/licenses/GPL-3.0"

URL = "https://sissource.ethz.ch/sispub/pytest-regtest/tree/master"

LONG_DESCRIPTION = """

pytest-regtest
==============

pytest-regtest is a *pytest*-plugin for implementing regression tests. Compared to functional
testing a regression test does not test if software produces correct results, instead
a regression test checks if software behaves the same way as it did before introduced changes.

More about regression testing at https://en.wikipedia.org/wiki/Regression_testing\.
Regression testing is a common technique to get started when refactoring legacy code lacking a test
suite.

*pytest-regtest* allows capturing selected output which then can be compared to the captured output
from former runs.


To install and activate this plugin execute::

    $ pip install pytest-regtest

*pytest-regtest* plugin provides a fixture named *regtest* which can be used as a file handle for
recording data::

    from __future__ import print_function

    def test_squares_up_to_ten(regtest):

        result = [i*i for i in range(10)]

        # one way to record output:
        print(result, file=regtest)

        # alternative method to record output:
        regtest.write("done")

If you run this test script with *pytest* the first time there is no recorded output for this test
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

For accepting this output, we run *pytest* with the *--regtest-reset* flag::

    $ py.test --regtest-reset

Now the next execution of *py.test* will succeed::

    $ py.test

The recorded output was written to files in the subfolder ``_regtest_outputs`` next to your
test script(s). You might keep this folder under version control.


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

To see recorded output during test execution run::

    $ py.test --regtest-tee -s

To support testing of the same code on different platforms by default *pytest-regtest* ignores
differences in line breaks when comparing the approved to the actual output. To switch this off use
the *--regtest-regard-line-endings* flag::

    $ py.test --regtest-regard-line-endings

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
