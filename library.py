#!/usr/bin/python
# -*- coding: utf-8 -*-
u"""
:author: Joseph Martinot-Lagarde

Created on Sat Jan 19 14:57:57 2013
"""
from __future__ import division, print_function, unicode_literals

import os
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

    logger.debug("Looking for " + label + " in " + filename)
    values = set()
    with open(filename, 'rt') as fid:
        for line in fid:
            # remove comments and unused whitespaces
            line = line.split("//")[0].strip()
            if not line:
                continue

            if line.lower().startswith(label.lower()):
                values.add(line.strip()[len(label):].lstrip())
    logger.debug("Found : " + ", ".join(values))
    return sorted(values)


def md5(filename):
    # Need to close the file ?
    return hashlib.md5(open(filename, 'rb').read()).digest()


class Library(object):
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
                file_hash = md5(filename)

                if (filename not in self.files
                        or self.files[filename].hash != file_hash):
                    if filename in self.files:
                        updated += 1
                    else:
                        added += 1
                    self.files[filename] = FileInfo(
                        file_hash,
                        search_info(filename, "KeySig"),
                        search_info(filename, "Tempo"),
                        search_info(filename, "TimeSig"),
                        search_info(filename, "Groove"))

                # Update set of each category
                info = self.files[filename]
                for key_sig in info.key_sig:
                    self.key_sig.add(key_sig)
                for tempo in info.tempo:
                    self.tempo.add(tempo)
                for time_sig in info.time_sig:
                    self.time_sig.add(time_sig)
                for groove in info.groove:
                    self.groove.add(groove)

        logger.info(
            "Library refreshed: %d updated, %d added and %s removed"
            % (updated, added, removed))

logging.debug("Module library imported")
