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
from kivy.uix.listview import ListItemButton
from kivy.uix.button import Button
from kivy.adapters.listadapter import ListAdapter
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
        self.update_tune_list()

    def play_pause(self):
        """Play the selected filename.
        """
        logger.debug("Play button pressed")
        filename = os.path.join(self.mma_library.path,
                                self.tune_list.adapter.selection[0].text)
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

    def fill_groove_tree(self):
        _populate_tree_view(self.groove_tree, self.groove_tree.root, None,
                            self.mma_library.groove_tree)

    def toggle_groove(self, groove_item):
        if groove_item.nodes:
            for child in groove_item.nodes:
                child.state = groove_item.state
        else:
            self.update_tune_list()

    def selected_grooves(self, _tree=None):
        # Initilaization
        selected = set()
        if _tree is None:
            _tree = self.groove_tree.root

        # Recursive filling
        for groove in _tree.nodes:
            if groove.state == 'down':
                selected.add(groove.text)
            selected = selected | self.selected_grooves(groove)
        return selected

    def update_tune_list(self):
        data = sorted(self.mma_library.get_match(self.selected_grooves()))
        self.tune_list.adapter = ListAdapter(
            data=data,
            selection_mode='single',
            allow_empty_selection=False,
            cls=ListItemButton)


class TreeViewToggleButton(ToggleButton, TreeViewNode):
    def on_press(self):
        # Apply selection to all childrens (recursively)
        self.set_childs_state(self.state)

        # Unselect parent if child unselected (recursive)
        # Select parent if all childs selected (recursive)
        self.set_parents_state(self.state)

        # Update tune list
        App.get_running_app().root.update_tune_list()

    def set_childs_state(self, state):
        u"""Apply state to childrens recursively
        """
        for child in self.nodes:
            child.state = state
            child.set_childs_state(state)

    def set_parents_state(self, state):
        u"""Manage the state of the parents.

        Unselect parent if any child unselected (recursive)
        Select parent if all childs selected (recursive)
        """
        if self.parent_node and isinstance(self.parent_node,
                                           TreeViewToggleButton):
            if state == "normal":
                self.parent_node.state = "normal"
                self.parent_node.set_parents_state(state)
            else:
                for child in self.parent_node.nodes:
                    if child.state == "normal":
                        break
                else:
                    self.parent_node.state = "down"
                    self.parent_node.set_parents_state(state)


class GrooveSelectAllButton(Button):
    def on_press(self):
        for groove in App.get_running_app().root.groove_tree.children:
            groove.state = 'down'
            groove.set_childs_state('down')
        App.get_running_app().root.update_tune_list()


class GrooveSelectNoneButton(Button):
    def on_press(self):
        for groove in App.get_running_app().root.groove_tree.children:
            groove.state = 'normal'
            groove.set_childs_state('normal')
        App.get_running_app().root.update_tune_list()


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
