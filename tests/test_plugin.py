# encoding: utf-8
from __future__ import print_function, division, absolute_import


def test_fixture(testdir):

    testdir.makepyfile("""
        from __future__ import print_function

        import os
        import tempfile

        here = os.path.abspath(__file__)

        def test_regtest(regtest, tmpdir):

            print("this is expected outcome", file=regtest)
            print(tmpdir.join("test").strpath, file=regtest)
            print(tempfile.gettempdir(), file=regtest)
            print("obj id is", hex(id(here)), file=regtest)

        def test_always_fail():
            assert 1 * 1 == 2

        def test_always_fail_regtest(regtest):
            assert 1 * 1 == 2

        def test_always_ok():
            assert 1 * 1 == 1

        def test_always_ok_regtest(regtest):
            regtest.identifier = "my_computer"
            assert 1 * 1 == 1

    """)

    # will fully fail
    result = testdir.runpytest()
    result.assert_outcomes(failed=3, passed=2)
    result.stdout.fnmatch_lines([
        "regression test output differences for test_fixture.py::test_regtest:"])

    print(result.stdout.str())

    expected_diff = """
                    >   --- current
                    >   +++ tobe
                    >   @@ -1,5 +1 @@
                    >   -this is expected outcome
                    >   -<tmpdir_from_fixture>/test
                    >   -<tmpdir_from_tempfile_module>
                    >   -obj id is 0x?????????
                    """.strip().split("\n")
    result.stdout.fnmatch_lines([l.lstrip() for l in expected_diff])

    # reset
    result = testdir.runpytest("--regtest-reset")
    result.assert_outcomes(failed=2, passed=3)

    # check recorded output
    def _read_output(fname):
        path = testdir.tmpdir.join("_regtest_outputs").join("test_fixture.{}.out".format(fname))
        return open(path.strpath).read()

    assert _read_output("test_regtest") == ("this is expected outcome\n"
                                            "<tmpdir_from_fixture>/test\n"
                                            "<tmpdir_from_tempfile_module>\n"
                                            "obj id is 0x?????????\n"
                                            )

    assert _read_output("test_always_fail_regtest") == ""

    # check if regtest.identifier = "my_computer" created the output file:
    assert _read_output("test_always_ok_regtest__my_computer") == ""

    # run again, reg test should succeed now
    result = testdir.runpytest()
    result.assert_outcomes(failed=2, passed=3)

    # just check if cmd line flags work without throwing exceptions:
    result = testdir.runpytest("--regtest-regard-line-endings")
    result.assert_outcomes(failed=2, passed=3)

    # just check if cmd line flags work without throwing exceptions:
    result = testdir.runpytest("--regtest-tee")
    result.assert_outcomes(failed=2, passed=3)
