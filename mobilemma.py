#!/usr/bin/python2
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
"""
"""
import os
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
        # Log buffer
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

        # Print to console
        if self.log_level == logging.INFO:
            sys.__stdout__.write(buf)
        elif self.log_level == logging.ERROR:
            sys.__stderr__.write(buf)

sys.stdout = StreamToLogger(logging.getLogger('STDOUT'), logging.INFO)
sys.stderr = StreamToLogger(logging.getLogger('STDERR'), logging.ERROR)


from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.treeview import TreeViewNode
from kivy.config import ConfigParser

import midi
from library import Library

#CONFIG_FILENAME = "mobilemma.ini"


class MobileMMAUI(Widget):
    #config = ConfigParser()
    #config.read(CONFIG_FILENAME)

    def __init__(self, library_path, *args, **kwargs):
        Widget.__init__(self, *args, **kwargs)

        # Update grooves at startup
        midi.update_grooves()

        # Library od mma files
        self.mma_library = Library(library_path)
        self.mma_library.update()

        self.key_list.adapter.data = sorted(self.mma_library.key_sig)
        self.fill_groove_tree()

    def play_pause(self, filename):
        """Play the selected filename.
        """
        logger.debug("Play button pressed")
        try:
            midi.play(filename)
        except Exception as err:
            logger.exception(err)

        self.refresh_current_path()

    def stop(self):
        """Stop playing.
        """
        logger.debug("Stop button pressed")
        midi.stop()

        # Not needed but refreshing from time to time is good
        self.refresh_current_path()

    def refresh_current_path(self):
        """Refreshes list of files in path by changing temporarily the current
        path.

        Not very beautiful code but no kivy method does it.
        """
        path = self.file_chooser.path
        self.file_chooser.path = "/"
        self.file_chooser.path = path

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

    def fill_groove_tree(self):
        _populate_tree_view(self.groove_tree, self.groove_tree.root, None,
                            self.mma_library.groove_tree)


class TreeViewToggleButton(ToggleButton, TreeViewNode):
    pass


def _populate_tree_view(tree_view, parent, text, children):
    """
    from http://kivy.org/docs/api-kivy.uix.treeview.html#introduction
    """
    if text:
        tree_node = tree_view.add_node(TreeViewToggleButton(
            text=text, is_open=False), parent)
    else:
        tree_node = parent

    for child in sorted(children.iterkeys()):
        _populate_tree_view(tree_view, tree_node, child, children[child])


class MobileMMAApp(App):
    use_kivy_settings = False

    def build_config(self, config):
        config.setdefaults('Library', {
            'library_path': './'
        })

    def build_settings(self, settings):
        settings.add_json_panel('Library', self.config,
                                'settings_library.json')

    def build(self):
        logger.debug("Create Kivy UI")
        return MobileMMAUI(self.config.get('Library', 'library_path'))

logging.debug("Module mobilemma imported")
