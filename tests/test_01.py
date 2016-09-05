# encoding: utf-8
from __future__ import print_function, division, absolute_import

def test_0(regtest, tmpdir):
    print("sdlfkjadflkadjsf ", file=regtest)
    print(tmpdir.strpath, file=regtest)
    print("sdlfkjadflkadjsf ", file=regtest)
