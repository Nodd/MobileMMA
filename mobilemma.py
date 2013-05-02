#!/usr/bin/python2
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
"""
"""

import sys
import logging
# création de l'objet logger qui va nous servir à écrire dans les logs
logger = logging.getLogger()
# on met le niveau du logger à DEBUG, comme ça il écrit tout
logger.setLevel(logging.DEBUG)

# création d'un formateur qui va ajouter le temps, le niveau
# de chaque message quand on écrira un message dans le log
formatter = logging.Formatter(
    "%(levelname)s :: %(funcName)s:%(lineno)d :: %(message)s")
# création d'un handler qui va rediriger une écriture du log vers
# un fichier en mode 'append', avec 1 backup et une taille max de 1Mo
file_handler = logging.FileHandler('activity.log', mode='w', encoding="utf8")
# on lui met le niveau sur DEBUG, on lui dit qu'il doit utiliser le formateur
# créé précédement et on ajoute ce handler au logger
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


# http://www.electricmonk.nl/log/2011/08/14/redirect-stdout-and-stderr-to-a-logger-in-python/
class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

sys.stdout = StreamToLogger(logging.getLogger('STDOUT'), logging.INFO)
sys.stderr = StreamToLogger(logging.getLogger('STDERR'), logging.ERROR)


from kivy.app import App
from kivy.uix.widget import Widget

import midi


class MobileMMAUI(Widget):
    def play_pause(self, filename):
        """Play the selected filename.
        """
        logger.debug("Play button pressed")
        try:
            midi.play(filename)
        except Exception as err:
            logger.exception(err)

    def stop(self):
        """Stop playing.
        """
        logger.debug("Stop button pressed")
        midi.stop()

    def file_content(self, filename):
        """Return content of a mma test file.
        """
        logger.debug("Retrieve content of %s" % filename)
        if filename.endswith(('.mid', '.midi')):
            return "MIDI file"

        assert filename.lower().endswith(".mma")
        with open(filename, "rt") as fid:
            text = fid.read()
        return text

    def update_grooves(self):
        midi.init()


class MobileMMAApp(App):
    def build(self):
        logger.debug("Create Kivy UI")
        return MobileMMAUI()


if __name__ == '__main__':
    MobileMMAApp().run()
