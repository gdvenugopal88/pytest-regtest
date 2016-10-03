# encoding: utf-8

from __future__ import print_function


import pkg_resources
_version = pkg_resources.require("pytest-regtest")[0].version.split(".")

__version__ = tuple(map(int, _version))


"""Regresstion test plugin for pytest.

This plugin enables recording of ouput of testfunctions which can be compared on subsequent
runs.
"""

import contextlib
import difflib
import os
import re
import string
import sys
import tempfile

import py
import pytest


IS_PY3 = sys.version_info.major == 3

if IS_PY3:
    from io import StringIO
    ljust = lambda s, *a: s.ljust(*a)
else:
    from cStringIO import StringIO
    ljust = string.ljust


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
    group.addoption('--regtest-nodiff',
                    action="store_true",
                    default=False,
                    help="do not show diff output for failed regresson tests")


ignore_line_endings = True
tee = False
reset = False
nodiff = False


def pytest_configure(config):
    global tee, ignore_line_endings, reset, nodiff
    tee = config.getvalue("--regtest-tee")
    ignore_line_endings = not config.getvalue("--regtest-regard-line-endings")
    reset = config.getvalue("--regtest-reset")
    nodiff = config.getvalue("--regtest-nodiff")


class WithAttributes(object):

    """we need to add an attribute to an StringIO instance, which
    is not allowed if we want to do this directly. Instead we wrap
    the object in an instance of this class, so attribute access
    is allowed again"""

    def __init__(self, obj):
        self.obj = obj

    def __getattr__(self, name):
        return getattr(self.obj, name)


class Tee(object):

    def __init__(self, string_io, tw):
        self.string_io = string_io
        self.tw = tw

    def write(self, data):
        self.string_io.write(data)
        self.tw.write(data, green=True)

    def __getattr__(self, name):
        return getattr(self.string_io, name)


@pytest.yield_fixture(scope="function")
def regtest(request):
    """This fixture acts like a writeable stream which can be used to record expected / current
    output depending on the flag --regtest-reset which causes recording of approved output. Without
    this flag the regtest fixture will decide during teardown if the currently recorded output is
    still the same as the previously recorded output.  """

    # we attach the request to the fixture object as I found no other way to retreive the request
    # in the pytest_runtest_call hook

    fp = WithAttributes(StringIO())

    if tee:
        tw = py.io.TerminalWriter()
        fp = Tee(fp, tw)
        tw.line()
        id_ = _test_function_identifier(request)
        line = "REGTEST OUTPUT FROM %s " % id_
        line = ljust(line, tw.fullwidth, "-")
        tw.line(line, green=True)
        tw.line()

    fp.request = request
    yield fp


@pytest.yield_fixture(scope="function")
def regtest_redirect(request):
    """regest_redirect is a context manager which records output to sys.stdout as long as active.
    Else it works similar to the regtest fixture.  """

    fp = WithAttributes(StringIO())
    tw = None
    if tee:
        tw = py.io.TerminalWriter()
        fp = Tee(fp, tw)

    @contextlib.contextmanager
    def context(fp=fp, tw=tw, request=request):
        old = sys.stdout
        sys.stdout = fp
        if tw is not None:
            tw.line()
            id_ = _test_function_identifier(request)
            line = "REGTEST REDIRECT OUTPUT FROM %s " % id_
            line = ljust(line, tw.fullwidth, "-")
            tw.line(line, green=True)
            tw.line()
        try:
            yield
        finally:
            sys.stdout = old

    # we attach the request to the fixture object as I found no other way to retreive the request
    # in the pytest_runtest_call hook, the fp attribute is needed in the hook as well:

    context.fp = fp
    context.request = request

    yield context

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


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):

    try:
        outcome = yield
    except Exception:
        raise
    else:
        # we only handle regtest fixture if no other other exception came up when testing:
        if outcome.excinfo is not None:
            return

        regtest = item.funcargs.get("regtest")
        if regtest is not None:
            _handle_regtest_result(regtest)

        regtest_redirect = item.funcargs.get("regtest_redirect")
        if regtest_redirect is not None:
            _handle_regtest_redirect_result(regtest_redirect)


def _handle_regtest_result(fp):
    request = fp.request
    extra_id = getattr(fp, "identifier", "")
    _finalize(fp.getvalue(), request, extra_id)


def _handle_regtest_redirect_result(context):
    request = context.request
    fp = context.fp
    extra_id = getattr(fp, "identifier", "")
    _finalize(fp.getvalue(), request, extra_id)


""" the function below is from
http://stackoverflow.com/questions/898669/how-can-i-detect-if-a-file-is-binary-non-text-in-python
"""

textchars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7f})


def is_binary_string(bytes):
    return bool(bytes.translate(None, textchars))


def _finalize(recorded, request, extra_id):

    if "tmpdir" in request.fixturenames:
        tmpdir = request.getfixturevalue("tmpdir").strpath
        replacement = "<tmpdir_from_fixture>"
    else:
        tmpdir = os.path.realpath(tempfile.gettempdir())
        replacement = "<tmpdir_from_module>"

    recorded = recorded.replace(tmpdir, replacement)

    def cleanup(recorded):
        """replace hex object ids in output by 0x?????????"""
        return re.sub(" 0x[0-9a-f]+", " 0x?????????", recorded)

    recorded = cleanup(recorded)
    # in python 3 a string should not contain binary symbols...:
    if not IS_PY3 and is_binary_string(recorded):
        request.raiseerror("recorded output for regression test contains unprintable characters.")

    path = _path_to_regest_recording_file(request, extra_id)
    if reset:
        _reset(recorded, path)
    else:
        tobe = _read(path)
        diff = _compare(recorded, tobe)
        if diff is not None:
            msg = "\nRegression test failed"
            msg += "\n   checked against %s\n" % path
            if not nodiff:
                msg += "\n\n" + diff
            request.raiseerror(msg)


def _test_function_identifier(request):
    path = request.fspath.strpath
    func_name = request.node.name
    return "%s::%s" % (path, func_name)


def _path_to_regest_recording_file(request, extra_id):

    path = request.fspath.strpath
    func_name = request.node.name
    dirname = os.path.dirname(path)
    basename = os.path.basename(path)
    stem, ext = os.path.splitext(basename)

    target_dir = os.path.join(dirname, "_regtest_outputs")
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    id_ = "%s.%s" % (stem, func_name)
    if extra_id:
        id_ = id_ + "__" + extra_id
    full_path = os.path.join(target_dir, "%s.out" % (id_))
    return full_path


def _read(path):
    if os.path.exists(path):
        with open(path, "rb") as fp:
            if IS_PY3:
                tobe = str(fp.read(), "utf-8")
            else:
                tobe = fp.read()
    else:
        tobe = ""
    return tobe


def _compare(is_, tobe):
    is_ = is_.split("\n")
    tobe = tobe.split("\n")
    if ignore_line_endings:
        is_ = [line.rstrip() for line in is_]
        tobe = [line.rstrip() for line in tobe]
    collected = list(difflib.unified_diff(is_, tobe, "is", "tobe", lineterm=""))
    if collected:
        return "\n".join(collected)
    return None


def _reset(recorded_output, path):
    if ignore_line_endings:
        lines = recorded_output.split("\n")
        lines = [line.rstrip() for line in lines]
        recorded_output = "\n".join(lines)

    with open(path, "wb") as fp:
        if IS_PY3:
            fp.write(recorded_output.encode("utf-8"))
        else:
            fp.write(recorded_output)
