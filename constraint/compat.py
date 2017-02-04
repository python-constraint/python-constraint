#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
import sys
import six

PY2 = sys.version_info[0] == 2
PY3 = (sys.version_info[0] >= 3)

if PY3:
    string_types = str
    xrange = range
else:
    string_types = six.string_types  # noqa
    xrange = xrange
