#!/usr/bin/python
# -*- coding: utf-8 -*-
u"""
:author: Joseph Martinot-Lagarde

Created on Sat Jan 19 14:57:57 2013
"""


from pygments.lexer import RegexLexer
from pygments.token import *

from MMA.chordtable import chordlist
# Get the chords, join them as a OR regexp and remove leading and trailing
# string marks.
chords = repr('|'.join(sorted(chordlist.iterkeys()))).strip("'")
# Escape problematic chars in chords
for char in "+#()":
    chords = chords.replace(char,'\\' + char)


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
            (r'//.*\n', Comment.Single),
            # Taken from mma -Dk
            # (?i) is for case insensitive
            (r'(?i)\b(ADJUSTVOLUME|ALLGROOVES|ALLTRACKS|AUTHOR|AUTOSOLOTRACKS|'
             r'BEATADJUST|BEGIN|CHANNELPREF|CHORDADJUST|COMMENT|CRESC|CUT|'
             r'DEBUG|DEC|DECRESC|DEFALIAS|DEFCHORD|DEFGROOVE|DELETE|DOC|DOCVAR|'
             r'DRUMVOLTR|ELSE|END|ENDIF|ENDMSET|ENDREPEAT|EOF|FERMATA|GOTO|'
             r'GROOVE|GROOVECLEAR|IF|IFEND|INC|INCLUDE|KEYSIG|LABEL|LYRIC|MIDI|'
             r'MIDICOPYRIGHT|MIDICUE|MIDIDEF|MIDIFILE|MIDIINC|MIDIMARK|'
             r'MIDISPLIT|MIDITEXT|MIDITNAME|MMAEND|MMASTART|MSET|MSETEND|'
             r'NEWSET|PATCH|PRINT|PRINTACTIVE|PRINTCHORD|REPEAT|REPEATEND|'
             r'REPEATENDING|RESTART|RNDSEED|RNDSET|SEQ|SEQCLEAR|SEQRND|'
             r'SEQRNDWEIGHT|SEQSIZE|SET|SETINCPATH|SETLIBPATH|SETMIDIPLAYER|'
             r'SETOUTPATH|SETSYNCTONE|SHOWVARS|STACKVALUE|SWELL|SWINGMODE|'
             r'SYNCHRONIZE|TEMPO|TIME|TIMESIG|TONETR|TRANSPOSE|TRUNCATE|TWEAKS|'
             r'UNSET|USE|VARCLEAR|VEXPAND|VOICETR|VOICEVOLTR|VOLUME|'
             r'ACCENT|ARPEGGIATE|ARTICULATE|CAPO|CHANNEL|CHORDS|CHSHARE|'
             r'COMPRESS|COPY|CRESC|CUT|DECRESC|DEFINE|DELAY|DIRECTION|DRUMTYPE|'
             r'DUPRIFF|DUPROOT|FORCEOUT|GROOVE|HARMONY|HARMONYONLY|'
             r'HARMONYVOLUME|INVERT|LIMIT|MALLET|MIDICLEAR|MIDICRESC|MIDICUE|'
             r'MIDIDECRESC|MIDIDEF|MIDIGLIS|MIDINOTE|MIDIPAN|MIDISEQ|MIDITEXT|'
             r'MIDITNAME|MIDIVOICE|MIDIVOLUME|MOCTAVE|NOTESPAN|OCTAVE|OFF|ON|'
             r'ORNAMENT|RANGE|RESTART|RIFF|RSKIP|RTIME|RVOLUME|'
             r'SCALETYPE|SEQCLEAR|SEQRND|SEQRNDWEIGHT|SEQUENCE|STRETCH|STRUM|'
             r'SWELL|TONE|TUNING|UNIFY|VOICE|VOICING|VOLUME)\s*\b',
             Keyword),
            (r'\b(ARIA|ARPEGGIO|BASS|CHORD|DRUM|MELODY|PLECTRUM|SCALE|SOLO|'
             r'WALK)\s*\b(?!\.)',
             Name.Builtin),
            (r'[*]', Operator),
            (r'[{}]', Punctuation),
            (r'\b(/|z|[A-G][b#]?(' + chords + r')?)\b', Name.Entity),
        ]
    }
