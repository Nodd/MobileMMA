#!/usr/bin/python2
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
"""Functions to build and play midi files from mma files.

Most code is adapted from LeMMA.
"""

import os
import sys
import logging
logger = logging.getLogger()

try:
    import pygame
    pygame.init()
    import pygame.mixer as mixer
except ImportError:
    import android_mixer as mixer
mixer.init()
mixer.music.set_volume(1.0)

#from kivy.core.audio import SoundLoader

MMA_DIR = os.path.dirname(__file__)
MMA_EXECFILE = os.path.join(MMA_DIR, "mma.py")
MMA_PATH = os.path.dirname(MMA_EXECFILE)
sys.path.insert(0, MMA_DIR)
logging.debug("Added %s to sys.path" % MMA_DIR)

global MMA
import MMA


def mma_run(*opts):
    """Run mma with the given commandline options
    """
    # Why does it needs to be global ?
    global MMA

    # Send a fake sys.argv to MMA
    sys.argv = [MMA_EXECFILE] + list(opts)
    logger.debug("Launching MMA : '%s'" % " ".join(sys.argv))

    # Call MMA via imports (MMA must run from MMA_PATH)
    current_dir = os.getcwd()
    os.chdir(MMA_PATH)
    logger.debug("cd from %s to %s" % (current_dir, MMA_PATH))
    try:
        try:
            # Reset mma if already run
            # Fails with "TypeError: reload() argument must be module" if
            # modules were not imported
            reload(MMA.gbl)
            reload(MMA.auto)
            reload(MMA.grooves)

            # Relaunch mma
            reload(MMA.main)
        except AttributeError as err:
            logger.exception(err)
            # Run MMA for the first time
            import MMA.main

    finally:
        # Back to the previous working dir
        logger.debug("cd back to %s" % (current_dir))
        os.chdir(current_dir)


def update_grooves():
    """Initialise MMA with grooves
    """
    logger.debug("Updating grooves...")
    try:
        mma_run('-g')
    except Exception as err:
        logger.error("Error running MMA")
        logger.exception(err)
        raise
    except SystemExit:
        # MMA closes after update with sys.exit(0)
        logger.debug("Grooves updated")


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
    filename_mma = os.path.abspath(filename_mma).encode("utf8")

    filename_midi = filename_mma[:-4] + ".mid"
    try:
        os.remove(filename_midi)
        logger.debug("Removed %s" % filename_midi)
    except Exception:
        logger.debug("No midi file to remove")

    logger.debug("Building midifile from %s to %s..." %
                 (filename_mma, filename_midi))
    try:
        # Generate the midi file with MMA
        mma_run(filename_mma)
    except Exception as err:
        logger.error("Error running MMA")
        logger.exception(err)
        raise

    return filename_midi


def play(filename=None):
    """Plays a MIDI file using pygame
    """
    logger.debug("Play %s" % filename)
    if filename:
        if filename.lower().endswith(".mma"):
            logger.debug("MMA file, building MIDI...")
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

        logger.debug("Play %s" % filename)
        mixer.music.load(filename)
        mixer.music.play()
    else:
        mixer.music.unpause()


def stop():
    """Stop the midifile play
    """
    logger.debug("Stop playing")
    mixer.music.stop()


def pause():
    """Pause the midifile play
    """
    logger.debug("Pause playing")
    mixer.music.pause()
