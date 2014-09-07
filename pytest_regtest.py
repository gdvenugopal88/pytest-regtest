import pdb
"""Regresstion test plugin for pytest.

This plugin enables recording of ouput of testfunctions which can be compared on subsequent
runs.
"""

import os
import sys
import cStringIO
import pytest


def pytest_addoption(parser):
    """Add options to control the timeout plugin"""
    group = parser.getgroup('regtest', 'regression test plugin')
    group.addoption('--reset-regtest',
                    action="store_true",
                    help="do not run regtest but record current output")



@pytest.yield_fixture()
def regtest(request):

    fp = cStringIO.StringIO()
    yield fp

    reset = request.config.getoption("--reset-regtest")
    path = request.fspath.strpath
    func_name = request.function.__name__
    dirname = os.path.dirname(path)
    basename = os.path.basename(path)
    stem, ext = os.path.splitext(basename)

    target_dir = os.path.join(dirname, "_regtest_outputs")
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    full_path = os.path.join(target_dir, "%s.%s.out" % (stem, func_name))
    if reset:
        record_output(fp.getvalue(), full_path)
    else:
        compare_output(fp.getvalue(), full_path)


def compare_output(is_, path):
    with open(path, "r") as fp:
        tobe = fp.read()
    assert is_ == tobe


def record_output(is_, path):
    with open(path, "w") as fp:
        fp.write(is_)
