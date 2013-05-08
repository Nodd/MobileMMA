#!/usr/bin/python
# -*- coding: utf-8 -*-
u"""
:author: Joseph Martinot-Lagarde

Created on Sat Jan 19 14:57:57 2013
"""
import logging
logger = logging.getLogger()


def search_info(filename, label):
    if not filename.endswith(".mma"):
        logger.debug("Not a MMA file")
        return []

    logger.debug("Looking for " + label + " in " + filename)
    values = []
    with open(filename, 'rt') as fid:
        for line in fid:
            # remove comments and unused whitespaces
            line = line.split("//")[0].strip()
            if not line:
                continue

            if line.lower().startswith(label.lower()):
                values.append(line.strip()[len(label):].lstrip())
    logger.debug("Found : " + ", ".join(values))
    return values
