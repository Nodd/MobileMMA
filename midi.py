#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
"""Functions to build and play midi files from mma files.

Most code is adapted from LeMMA.
"""

import os
import sys
import subprocess

import pygame
pygame.init()
pygame.mixer.init()
pygame.mixer.music.set_volume(1.0)

PYTHON = sys.executable
MMA_EXECFILE = os.path.join(os.path.dirname(__file__), "mma/mma.py")
MMA_PATH = os.path.dirname(MMA_EXECFILE)


def build(filename):
    """Run the MMA program for the given filename and returns the filename of
    the MIDI file created.

    Even if MMA is written in python, it is sadly far easier to run in with
    popen().
    """
    assert filename.lower().endswith(".mma")
    assert os.path.isfile(filename)
    assert os.access(filename, os.R_OK)

    # The working diretory will be temporarilly changed
    filename = os.path.abspath(filename)

    # MMA must run from mma.py path
    current_dir = os.getcwd()
    os.chdir(MMA_PATH)

    try:
        # delete the temp midi file first, if any
        tempmidifile = os.path.normcase(current_dir + "/_temp_.mid")
        try:
            os.remove(tempmidifile)
        except Exception:
            pass

        # Generate the midi file
        #    quote pythonPath to handle correctly space characters in it
        cmd = os.path.normcase("'%s' %s %s"
                               % (sys.executable, MMA_EXECFILE, filename))
        print(subprocess.check_call(cmd, shell=True))
    except subprocess.CalledProcessError:
        raise
    finally:
        # Back to the previous working dir
        os.chdir(current_dir)

    return filename[:-4] + ".mid"


def play(filename=None):
    """Plays a MIDI file using pygame
    """
    if filename:
        if filename.lower().endswith(".mma"):
            assert os.path.isfile(filename)
            assert os.access(filename, os.R_OK)
            filename = build(filename)

        assert filename.lower().endswith((".mid", ".midi"))
        assert os.path.isfile(filename)
        assert os.access(filename, os.R_OK)

        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
    else:
        pygame.mixer.music.unpause()


def stop():
    """Stop the midifile play
    """
    pygame.mixer.music.stop()


def pause():
    """Pause the midifile play
    """
    pygame.mixer.music.pause()
