#!/usr/bin/python2
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
"""
This module is necessary to launch MobileMMA with kivy launcher.
"""

from mobilemma import MobileMMAApp

# Needed for MMA...
import platform
import os
MMAdir = os.path.abspath(os.path.dirname(__file__))

if __name__ == "__main__":
    MobileMMAApp().run()
