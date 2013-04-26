#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
"""
"""

from kivy.app import App
from kivy.uix.widget import Widget

import midi


class MobileMMAUI(Widget):
    def play_pause(self, filename):
        """Play the selected filename.
        """
        midi.play(filename)

    def stop(self):
        """Stop playing.
        """
        midi.stop()

    def file_content(self, filename):
        """Return content of a mma test file.
        """
        assert filename.lower().endswith(".mma")
        with open(filename, "rt") as fid:
            text = fid.read()
        return text


class MobileMMAApp(App):
    def build(self):
        return MobileMMAUI()


if __name__ == '__main__':
    MobileMMAApp().run()
