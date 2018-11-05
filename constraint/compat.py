#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] >= 3

if PY3:
    string_types = str
    xrange = range
else:
    string_types = basestring  # noqa
    xrange = xrange
