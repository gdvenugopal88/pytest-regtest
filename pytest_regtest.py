"""Regresstion test plugin for pytest.

This plugin enables recording of ouput of testfunctions which can be compared on subsequent
runs.
"""

import os
import cStringIO
import difflib

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

    reset, full_path, id_ = _setup(request)
    if reset:
        _record_output(fp.getvalue(), full_path)
    else:
        _compare_output(fp.getvalue(), full_path, request, id_)


def _setup(request):

    reset = request.config.getoption("--reset-regtest")
    path = request.fspath.strpath
    func_name = request.function.__name__
    dirname = os.path.dirname(path)
    basename = os.path.basename(path)
    stem, ext = os.path.splitext(basename)

    target_dir = os.path.join(dirname, "_regtest_outputs")
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    id_ = "%s.%s" % (stem, func_name)
    full_path = os.path.join(target_dir, "%s.out" % (id_))

    return reset, full_path, id_


def _compare_output(is_, path, request, id_):
    capman = request.config.pluginmanager.getplugin('capturemanager')
    if capman:
        stdout, stderr = capman.suspendcapture(request)
    else:
        stdout, stderr = None, None
    with open(path, "r") as fp:
        tobe = fp.read()
    __tracebackhide__ = True
    collected = list(difflib.unified_diff(is_.split("\n"), tobe.split("\n")))
    if collected:
        pytest.fail("\n".join(collected), pytrace=False)



def _record_output(is_, path):
    with open(path, "w") as fp:
        fp.write(is_)
