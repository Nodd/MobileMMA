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

PYTHON = sys.executable
MMA_DIR = os.path.dirname(__file__)
MMA_EXECFILE = os.path.join(MMA_DIR, "mma.py")
MMA_PATH = os.path.dirname(MMA_EXECFILE)
sys.path.insert(0, MMA_DIR)
logging.debug("Added %s to sys.path" % MMA_DIR)

import MMA
global MMA_main, MMA_gbl, MMA_grooves
MMA_main = MMA_gbl = MMA_grooves = None


def init():
    """Initialise MMA with grooves
    """
    current_dir = os.getcwd()
    os.chdir(MMA_PATH)
    logger.debug("cd from %s to %s" % (current_dir, MMA_PATH))
    try:
        sys.argv = [MMA_EXECFILE, '-G']
        logger.debug("Updating grooves...")
        import MMA.main
    except Exception as err:
        logger.error("Error running MMA")
        logger.exception(err)
        raise
#    except SystemExit:
#        # MMA closes after update with sys.exit(0)
#        logger.debug("Grooves updated")
    finally:
        # Back to the previous working dir
        logger.debug("cd back to %s" % (current_dir))
        os.chdir(current_dir)


def build(filename_mma):
    """Run the MMA program for the given filename and returns the filename of
    the MIDI file created.

    Even if MMA is written in python, it is sadly far easier to run in with
    popen().
    """
    global MMA_main, MMA_gbl, MMA_grooves
    assert filename_mma.lower().endswith(".mma")
    assert os.path.isfile(filename_mma)
    assert os.access(filename_mma, os.R_OK)

    # The working diretory will be temporarilly changed
    filename_mma = os.path.abspath(filename_mma).encode("utf8")

    filename_midi = filename_mma[:-4] + ".mid"
    logger.debug("Building midifile from %s to %s" %
                 (filename_mma, filename_midi))

    # MMA must run from mma.py path
    current_dir = os.getcwd()
    os.chdir(MMA_PATH)
    logger.debug("cd from %s to %s" % (current_dir, MMA_PATH))
    try:
        try:
            os.remove(filename_midi)
            logger.debug("Removed %s" % filename_midi)
        except Exception:
            logger.debug("No midi file to remove")
            pass

        # Generate the midi file
        #    quote pythonPath to handle correctly space characters in it
        sys.argv = [MMA_EXECFILE, '-d', filename_mma]
        logger.debug("Launching MMA : %s -d %s" % (MMA_EXECFILE, filename_mma))
#        if MMA_main is None:
#            import MMA.main
#            MMA_main = MMA.main
#        else:
#            MMA.main = reload(MMA.main)
        try:
            reload(MMA_gbl)
            reload(MMA_grooves)
            reload(MMA_main)
        except (AttributeError, UnboundLocalError, TypeError) as err:
            logger.exception(err)
            import MMA.main
            MMA_main = MMA.main
            MMA_gbl = MMA.gbl
            MMA_grooves = MMA.grooves
    except Exception as err:
        logger.error("Error running MMA")
        logger.exception(err)
        raise
    finally:
        # Back to the previous working dir
        logger.debug("cd back to %s" % (current_dir))
        os.chdir(current_dir)

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
