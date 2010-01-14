"""
Copyright (c) 2009, Horst Gutmann
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this 
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice, 
  this list of conditions and the following disclaimer in the documentation 
  and/or other materials provided with the distribution.
  
* Neither the name of the project nor the names of its contributors may 
  be used to endorse or promote products derived from this software without   
  specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

-----------------------------------------------------------------------------

This module contains a simple BibTeX parser based on pyparsing. If all you
want is to parse some BibTeX, give ``parse_file`` and ``parse_string`` a 
try.
"""
from __future__ import with_statement

import string
import re
import codecs
import pyparsing as pp

from ..bibtex import structures, exceptions


def normalize_value(text):
    """
    This removes newlines and multiple spaces from a string.
    """
    result = text.replace('\n', ' ')
    result = re.subn('[ ]{2,}', ' ', result)[0]
    return result

###############################################################################
# Actions

def parse_field(source, loc, tokens):
    """
    Returns the tokens of a field as key-value pair.
    """
    name = unicode(tokens[0]).lower()
    value = normalize_value(unicode(tokens[2]))
    if name == u'author' and u' and ' in value:
        value = map(string.strip, value.split(u' and '))
    return (name, value)

def parse_entry(source, loc, tokens):
    """
    Converts the tokens of an entry into an Entry instance. If no applicable
    type is available, an UnsupportedEntryType exception is raised.
    """
    type_ = unicode(tokens[1]).lower()
    entry_type = structures.TypeRegistry.get_type(type_)
    if entry_type is None or not issubclass(entry_type, structures.Entry):
        raise exceptions.UnsupportedEntryType, \
                "%s is not a supported entry type" % type_
    new_entry = entry_type()
    new_entry.name = unicode(tokens[3])
    for key, value in [t for t in tokens[4:-1] if t != ',']:
        new_entry[key] = value
    return new_entry

def parse_bibliography(source, loc, tokens):
    """
    Combines the parsed entries into a Bibliography instance.
    """
    bib = structures.Bibliography()
    for entry in tokens:
        bib.add(entry)
    return bib

def parse_bstring(source, loc, tokens):
    """
    Combines all the found subtokens into a single string.
    """
    return u''.join(tokens)

###############################################################################
# Grammar

comment = pp.Literal('%') + pp.SkipTo(pp.LineEnd(), include=True)
bstring_nested = pp.Forward()
bstring_nested << '{' + pp.ZeroOrMore(bstring_nested | pp.Regex('[^{}]+')) + '}'
bstring = pp.Suppress('{') + pp.ZeroOrMore(pp.Or([bstring_nested, pp.Regex('[^{}]+')])).leaveWhitespace() + pp.Suppress('}')
bstring.setParseAction(parse_bstring)

label = pp.Regex(r'[a-zA-Z0-9-_:/]+')
field_value = pp.Or([
        bstring,
        pp.QuotedString(quoteChar='"', multiline=True, escChar='\\'),
        pp.QuotedString(quoteChar="'", multiline=True, escChar='\\')
        ])

field = (label + '=' + field_value).setName("field")
field.setParseAction(parse_field)

entry_content = field + pp.ZeroOrMore(',' + field) + pp.Optional(',')

entry = (u'@' + label + u"{" + label + "," + entry_content + u"}").setName("entry")
entry.setParseAction(parse_entry)

bibliography = (pp.OneOrMore(entry)).setName("bibliography")
bibliography.setParseAction(parse_bibliography)

pattern = bibliography + pp.StringEnd()
pattern.ignore(comment)

###############################################################################
# Helper functions

def parse_string(str_, validate=False):
    """
    Tries to parse a given string into a Bibliography instance. If ``validate``
    is passed as keyword argument and set to ``True``, the Bibliography 
    will be validated using the standard rules.
    """
    result = pattern.parseString(str_)[0]
    if validate:
        result.validate()
    return result

def parse_file(file_or_path, encoding='utf-8', validate=False):
    """
    Tries to parse a given filepath or fileobj into a Bibliography instance. If
    ``validate`` is passed as keyword argument and set to ``True``, the 
    Bibliography will be validated using the standard rules.
    """
    if isinstance(file_or_path, (unicode, str)):
        with codecs.open(file_or_path, 'r', encoding) as file_:
            result = pattern.parseFile(file_)[0]
    else:
        result = pattern.parseFile(file_or_path)[0]
    if validate:
        result.validate()
    return result
