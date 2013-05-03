#!/usr/bin/python
# -*- coding: utf-8 -*-
u"""
:author: Joseph Martinot-Lagarde

Created on Sat Jan 19 14:57:57 2013
"""


from pygments.lexer import RegexLexer
import pygments.token as tkn

from MMA.chordtable import chordlist
# Get the chords, join them as a OR regexp and remove leading and trailing
# string marks.
chords = repr('|'.join(sorted(chordlist.iterkeys()))).strip("'")
# Escape problematic chars in chords
for char in "+#()":
    chords = chords.replace(char, '\\' + char)

from MMA.parse import simpleFuncs, trackFuncs
commands = '|'.join(sorted(simpleFuncs.iterkeys()))
track_commands = '|'.join(sorted(trackFuncs.iterkeys()))

from MMA.alloc import trkClasses
track_classes = '|'.join(sorted(trkClasses.iterkeys()))


class MMALexer(RegexLexer):
    """A lexer corresponding to MMA files.

    MMA (Musical MIDI Accompaniment) is an accompaniment generator. It creates
    MIDI tracks for a soloist to perform over from a user supplied file
    containing chords and MMA directives.
    http://www.mellowood.ca/mma/
    """
    name = 'MMA'
    aliases = ['mma']
    filenames = ['*.mma']

    tokens = {
        'root': [
            (r'//.*\n', tkn.Comment.Single),
            (r'^\d+\b', tkn.Comment),
            # (?i) is for case insensitive
            (r'(?i)\b(' + commands + r')\b', tkn.Keyword),
            (r'(?i)\b(' + track_commands + r')\b', tkn.Keyword),
            (r'(?i)\b(' + track_classes + r')\b', tkn.Name.Builtin),
            (r'[*]', tkn.Operator),
            (r'[{}]', tkn.Punctuation),
            (r'\b(/|z|[A-G][b#]?(' + chords + r')?)\b', tkn.String.Symbol),
        ]
    }
