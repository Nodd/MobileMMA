#!/usr/bin/python2
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
"""Functions to build and play midi files from mma files.

Most code is adapted from LeMMA.
"""

import os
import sys
import subprocess
import logging

try:
    import pygame
    pygame.init()
    import pygame.mixer as mixer
except ImportError:
    import android_mixer as mixer
mixer.init()
mixer.music.set_volume(1.0)

#from kivy.core.audio import SoundLoader

PYTHON = sys.executable
MMA_EXECFILE = os.path.join(os.path.dirname(__file__), "mma/mma.py")
MMA_PATH = os.path.dirname(MMA_EXECFILE)


def build(filename_mma):
    """Run the MMA program for the given filename and returns the filename of
    the MIDI file created.

    Even if MMA is written in python, it is sadly far easier to run in with
    popen().
    """
    assert filename_mma.lower().endswith(".mma")
    assert os.path.isfile(filename_mma)
    assert os.access(filename_mma, os.R_OK)

    # The working diretory will be temporarilly changed
    filename_mma = os.path.abspath(filename_mma)

    filename_midi = filename_mma[:-4] + ".mid"
    logging.debug("Building midifile from %s to %s" %
                  (filename_mma, filename_midi))

    # MMA must run from mma.py path
    current_dir = os.getcwd()
    os.chdir(MMA_PATH)
    logging.debug("cd from %s to %s" % (current_dir, MMA_PATH))
    try:
        try:
            os.remove(filename_midi)
            logging.debug("Removed %s" % filename_midi)
        except Exception:
            logging.debug("No midi file to remove")
            pass

        # Generate the midi file
        #    quote pythonPath to handle correctly space characters in it
        cmd = os.path.normcase("%s %s"
                               % (MMA_EXECFILE, filename_mma))
        logging.debug("Running \"%s\"" % cmd)
        errcode = subprocess.check_call(cmd, shell=True)
        logging.debug("MMA returned error code %d" % errcode)
    except Exception as err:
        logging.error("Error running MMA")
        logging.exception(err)
        raise
    finally:
        # Back to the previous working dir
        logging.debug("cd back to %s" % (current_dir))
        os.chdir(current_dir)

    return filename_midi


def play(filename=None):
    """Plays a MIDI file using pygame
    """
    logging.debug("Play %s" % filename)
    if filename:
        if filename.lower().endswith(".mma"):
            logging.debug("MMA file, building MIDI...")
            assert os.path.isfile(filename)
            assert os.access(filename, os.R_OK)
            filename = build(filename)

        assert filename.lower().endswith((".mid", ".midi"))
        assert os.path.isfile(filename)
        assert os.access(filename, os.R_OK)

#        sound = SoundLoader.load(filename)
#        print(sound)
#        if sound:
#            print("Sound found at %s" % sound.source)
#            print("Sound is %.3f seconds" % sound.length)
#        sound.play()
#        return sound

        logging.debug("Play %s" % filename)
        mixer.music.load(filename)
        mixer.music.play()
    else:
        mixer.music.unpause()


def stop():
    """Stop the midifile play
    """
    logging.debug("Stop playing")
    mixer.music.stop()


def pause():
    """Pause the midifile play
    """
    logging.debug("Pause playing")
    mixer.music.pause()
