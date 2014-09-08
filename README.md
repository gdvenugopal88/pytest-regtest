pytest-regtest
==============

This *pytest*-plugin allows capturing of output of test functions which
can be compared to the captured output from former runs. This is a
common technique to start
<http://en.wikipedia.org/wiki/Test-driven_development> if you have to
refactor legacy code which ships without tests.

To install and activate this plugin you have to run

    $ pip install pytest-regtest

from your commandline.

This *py.test* plugin provides a fixture named *regtest* for recording
data by writing to this fixture, which behaves like an output stream::

    def test_squares_up_to_ten(regtest):

        result = [i*i for i in range(10)]

        # one way to record output:
        print >> regtest, result

        # alterntive method to record output:
        regtest.write("done")

For recording the *approved* output, you run *py.test* with the
*--reset-regtest* flag::

    $ py.test --reset-regtest

Now the recorded output is written to a text file in the subfolder
`_regtest_outputs` next to your test scripts.

If you want to check that the testing function still produces the same
output, you ommit the flag and run you tests as usual::

    $ py.test
