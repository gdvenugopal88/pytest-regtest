import pdb
import pytest

def test0(regtest):
    print >> regtest, range(10)
