# encoding: utf-8

"""Regresstion test plugin for pytest.

This plugin enables recording of ouput of testfunctions which can be compared on subsequent
runs.
"""

import sys


IS_PY3 = sys.version_info.major == 3

if IS_PY3:
    from io import StringIO
else:
    from cStringIO import StringIO

import contextlib
import difflib
import os
import sys
import re

import pytest


def pytest_addoption(parser):
    """Add options to control the timeout plugin"""
    group = parser.getgroup('regtest', 'regression test plugin')
    group.addoption('--regtest-reset',
                    action="store_true",
                    help="do not run regtest but record current output")
    group.addoption('--regtest-tee',
                    action="store_true",
                    default=False,
                    help="print recorded results to console too")
    group.addoption('--regtest-regard-line-endings',
                    action="store_true",
                    default=False,
                    help="do not strip whitespaces at end of recorded lines")


ignore_line_endings = True
tee = False


def pytest_configure(config):
    global tee, ignore_line_endings
    tee = False
    ignore_line_endings = True


def _finalize(fp, request):

    def value(fp):
        return re.sub(" 0x[0-9a-f]+", " 0x?????????", fp.getvalue())

    reset, full_path, id_ = _setup(request)
    if reset:
        _record_output(value(fp), full_path)
    else:
        return _compare_output(value(fp), full_path, request, id_)


class Tee(object):

    def __init__(self, string_io):
        self.string_io = string_io

    def write(self, data):
        self.string_io.write(data)
        sys.__stdout__.write(data)

    def __getattr__(self, name):
        return getattr(self.string_io, name)


@pytest.yield_fixture()
def regtest(request):
    """This fixture acts like a writeable stream which can be used to record
    expected / current output depending on the flag --regtest-reset which causes
    recording of approved output. Without this flag the regtest fixture will decide
    during teardown if the currently recorded output is still the same as the
    previously recorded output.
    """
    fp = StringIO()
    if tee:
        fp = Tee(fp)

    yield fp

    diff = _finalize(fp, request)

    if diff is not None:
        msg = "\nRegression test failed:\n\n"
        msg += diff
        request.raiseerror(msg)


@pytest.yield_fixture()
def regtest_redirect(request):
    """regest_redirect is a context manager which records output to sys.stdout
    as long as active. Else it works similar to the regtest fixture.
    """
    fp = StringIO()
    if tee:
        fp = Tee(fp)

    @contextlib.contextmanager
    def context(fp=fp):
        import sys
        old = sys.stdout
        sys.stdout = fp
        yield
        sys.stdout = old

    yield context

    _finalize(fp, request)


"""

# THIS DOES NOT WORK AS INTENDED BECAUSE OF py.tests INTERNAL REDIRECTION !
# I LEAVE THIS SNIPPET HERE TO AVOID ANOTHER UNSUCCUESSFULL IMPLEMENTATION IN THE FUTURE.

@pytest.yield_fixture()
def regtest_capture_all(request):

    fp = StringIO()

    import sys
    old = sys.stdout
    sys.stdout = fp

    try:
        yield
    finally:
        sys.stdout = old

    _finalize(fp, request)

"""


def _setup(request):

    global tee, ignore_line_endings
    tee = request.config.getoption("--regtest-tee")
    reset = request.config.getoption("--regtest-reset")
    ignore_line_endings = not request.config.getoption("--regtest-regard-line-endings")
    path = request.fspath.strpath
    func_name = request.node.name
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
    if os.path.exists(path):
        with open(path, "rb") as fp:
            if IS_PY3:
                tobe = str(fp.read(), "utf-8")
            else:
                tobe = fp.read()
    else:
        tobe = ""
    is_ = is_.split("\n")
    tobe = tobe.split("\n")
    if ignore_line_endings:
        is_ = [line.rstrip() for line in is_]
        tobe = [line.rstrip() for line in tobe]
    collected = list(difflib.unified_diff(is_, tobe, "is", "tobe", lineterm=""))
    if collected:
        return "\n".join(collected)
    return None


def _record_output(is_, path):
    if ignore_line_endings:
        lines = is_.split("\n")
        lines = [line.rstrip() for line in lines]
        is_ = "\n".join(lines)

    with open(path, "wb") as fp:
        if IS_PY3:
            fp.write(is_.encode("utf-8"))
        else:
            fp.write(is_)
