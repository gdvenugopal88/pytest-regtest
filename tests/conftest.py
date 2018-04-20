#! /usr/bin/env python
# encoding: utf-8
from __future__ import print_function, division, absolute_import


import pytest_regtest


@pytest_regtest.register_converter_pre
def result(txt):
    return txt


@pytest_regtest.register_converter_post
def result(txt):
    return txt.upper()
