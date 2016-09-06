# encoding: utf-8
from __future__ import print_function, division, absolute_import


def test_should_allways_fail(regtest, tmpdir):
    print("sdlfkjadflkadjsf ", file=regtest)
    print(tmpdir.strpath, file=regtest)
    print("sdlfkjadflkadjsf ", file=regtest)


def test_bytes(regtest, tmpdir):
    contains_bin = "".join(chr(i) for i in range(13, 32))
    print(contains_bin, file=regtest)
