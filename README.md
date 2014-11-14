pytest-regtest
==============

This *pytest*-plugin allows capturing of output of test functions which
can be compared to the captured output from former runs. This is a
common technique to start
[TDD](http://en.wikipedia.org/wiki/Test-driven_development) if you have
to refactor legacy code which ships without tests.

To install and activate this plugin you have to run:

``` {.sourceCode .bash}
$ pip install pytest-regtest
```

from your command line.

This *py.test* plugin provides a fixture named *regtest* for recording
data by writing to this fixture, which behaves like an output stream:

``` {.sourceCode .python}
def test_squares_up_to_ten(regtest):

    result = [i*i for i in range(10)]

    # one way to record output:
    print >> regtest, result

    # alternative method to record output:
    regtest.write("done")
```

We can redirect stdout to this stream using the *regtest\_redirect*
fixture:

``` {.sourceCode .python}
def test_squares_up_to_ten(regtest_redirect):

    result = [i*i for i in range(10)]

    with regtest_redirect():
        print result
```

For recording the *approved* output, you run *py.test* with the
*--reset-regtest* flag:

``` {.sourceCode .bash}
$ py.test --regtest-reset
```

The recorded output is written to text files in the subfolder
`_regtest_outputs` next to your test scripts.

You can reset recorded output of files and functions individually as:

``` {.sourceCode .bash}
$ py.test --regtest-reset tests/test_00.py
$ py.test --regtest-reset tests/test_00.py::test_squares_up_to_ten
```

If you want to check that the testing function still produces the same
output, you ommit the flag and run you tests as usual:

``` {.sourceCode .bash}
$ py.test
```

This shows diffs for the tests failing because the current and recorded
output deviate.

To supress the diff and only see the stats use:

``` {.sourceCode .bash}
$ py.test --regtest-nodiff
```
