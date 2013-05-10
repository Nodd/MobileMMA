#!/usr/bin/python
# -*- coding: utf-8 -*-
u"""
:author: Joseph Martinot-Lagarde

Created on Sat Jan 19 14:57:57 2013
"""
from __future__ import division, print_function, unicode_literals

import os
import re
import hashlib
from collections import namedtuple
import logging
logger = logging.getLogger()


FileInfo = namedtuple('FileInfo',
                      ['hash', 'key_sig', 'tempo', 'time_sig', 'groove'])


def search_info(filename, label):
    if not filename.endswith(".mma"):
        logger.debug("Not a MMA file")
        return []

    values = set()
    try:
        with open(filename, 'rt') as fid:
            for line in fid:
                # remove comments and unused whitespaces
                line = line.decode("utf8").split("//")[0].strip()
                if not line:
                    continue

                if line.lower().startswith(label.lower()):
                    values.add(line.strip()[len(label):].lstrip())
    except Exception as err:
        logger.info("Problem with file '%s'" % filename)
        logger.exception(err)
    return sorted(values)


def md5(filename):
    # Need to close the file ?
    return hashlib.md5(open(filename, 'rb').read()).digest()


class Library(object):
    groove_split_regexp = re.compile(r"(\-?[A-Z][a-z]+)")

    def __init__(self, path):
        logger.debug("Create library")
        self.path = path

        self.files = dict()
        self.key_sig = set()
        self.tempo = set()
        self.time_sig = set()
        self.groove = set()

    def reset(self):
        logger.debug("Reset library")
        self.files = dict()
        self.key_sig = set()
        self.tempo = set()
        self.time_sig = set()
        self.groove = set()

    def update(self):
        logger.debug("Update library")
        removed = 0
        updated = 0
        added = 0

        # Discard removed files
        for filename in self.files:
            if not os.path.isfile(os.path.join(self.path, filename)):
                del self.files[filename]
                removed += 1

        # Add or update files recursively in the directory
        for dirpath, dirnames, filenames in os.walk(self.path):
            for filename in filenames:
                if not filename.lower().endswith(".mma"):
                    continue

                filename = os.path.join(dirpath, filename)
                filename_rel = os.path.relpath(filename, start=self.path)
                file_hash = md5(filename)

                if (filename not in self.files
                        or self.files[filename].hash != file_hash):
                    if filename in self.files:
                        updated += 1
                    else:
                        added += 1
                    self.files[filename_rel] = FileInfo(
                        file_hash,
                        search_info(filename, "KeySig"),
                        search_info(filename, "Tempo"),
                        search_info(filename, "TimeSig"),
                        set(groove
                            for groove in search_info(filename, "Groove")
                            if not groove.startswith("$")))

                # Update set of each category
                info = self.files[filename_rel]
                for key_sig in info.key_sig:
                    self.key_sig.add(key_sig)
                for tempo in info.tempo:
                    self.tempo.add(tempo)
                for time_sig in info.time_sig:
                    self.time_sig.add(time_sig)
                for groove in info.groove:
                    self.groove.add(groove)

        print("Library refreshed: %d updated, %d added and %s removed"
              % (updated, added, removed))

    def groove_split(self, groove):
        """Splits a groove name in parts.

        Examples :

        >>> lib = Library
        >>> lib.groove_split("Waltz")
        [u'Waltz']
        >>> lib.groove_split("Waltz1")
        [u'Waltz', u'1']
        >>> lib.groove_split("WaltzSusIntro")
        [u'Waltz', u'Sus', u'Intro']
        >>> lib.groove_split("R&B-Ballad")
        [u'R&B', u'-Ballad']
        >>> lib.groove_split("R&BPlus")
        [u'R&B', u'Plus']
        >>> lib.groove_split("BWMarchPlus")
        [u'BW', u'March', u'Plus']
        >>> lib.groove_split("50sRock")
        [u'50s', u'Rock']
        >>> lib.groove_split("68March")
        [u'68', u'March']
        """
        return (match.rstrip('-')
                for match in self.groove_split_regexp.split(groove)
                if match)

    @property
    def groove_tree(self):
        """Builds a tree of grooves using dictionnaries.
        """
        logger.debug("Build groove tree")

        # Build the tree
        tree = {}
        for groove in self.groove:
            groove_group = ''
            subtree = tree

            for groove_part in self.groove_split(groove):
                groove_group += groove_part
                if groove_group not in subtree:
                    subtree[groove_group] = {}
                subtree = subtree[groove_group]
            # Add the groove itself to the groove group
            subtree[groove_group] = {}

        # Recursively remove nodes with only one child
        def _simplify(name, node):
            # Simplify childrens
            childnames = node.keys()
            for childname in childnames:
                childname_new, childnode = _simplify(childname,
                                                     node[childname])
                del node[childname]
                node[childname_new] = childnode

            # Simplify itself if only one element
            if len(node) == 1:
                return node.keys()[0], node.values()[0]
            else:
                return name, node

        _, tree = _simplify("", tree)
        return tree

logging.debug("Module library imported")
