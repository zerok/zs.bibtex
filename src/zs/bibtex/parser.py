import string
import re
import codecs
import pyparsing as pp

from ..bibtex import structures, exceptions


def normalize_value(str):
    """
    This removes newlines and multiple spaces from a string.
    """
    result = str.replace('\n', ' ')
    result = re.subn('[ ]{2,}', ' ', result)[0]
    return result

###############################################################################
# Actions

def parse_field(s, loc, tokens):
    name = unicode(tokens[0]).lower()
    value = normalize_value(unicode(tokens[2]))
    if name == u'author' and u' and ' in value:
        value = map(string.strip, value.split(u' and '))
    return (name, value)

def parse_entry(s, loc, tokens):
    type_ = unicode(tokens[1])
    entry_type = getattr(structures, type_.capitalize(), None)
    if entry_type is None or not issubclass(entry_type, structures.Entry):
        raise exceptions.UnsupportedEntryType, \
                "%s is not a supported entry type" % type_
    entry = entry_type()
    entry.name = unicode(tokens[3])
    for k, v in [t for t in tokens[4:-1] if t != ',']:
        entry[k]=v
    return entry

def parse_bibliography(s, loc, tokens):
    bib = structures.Bibliography()
    for entry in tokens:
        bib.add(entry)
    return bib

def parse_bstring(s, loc, tokens):
    return u''.join(tokens)

###############################################################################
# Grammar

comment = pp.Literal('%') + pp.SkipTo(pp.LineEnd(), include=True)
bstring_nested = pp.Forward()
bstring_nested << '{' + pp.ZeroOrMore(bstring_nested | pp.Regex('[^{}]+')) + '}'
bstring = pp.Suppress('{') + pp.ZeroOrMore(pp.Or([bstring_nested, pp.Regex('[^{}]+')])).leaveWhitespace() + pp.Suppress('}')
bstring.setParseAction(parse_bstring)

label = pp.Regex(r'[a-zA-Z0-9-_:/]+')
value = pp.Or([
        bstring,
        pp.QuotedString(quoteChar='"', multiline=True, escChar='\\'),
        pp.QuotedString(quoteChar="'", multiline=True, escChar='\\')
        ])

field = (label + '=' + value).setName("field")
field.setParseAction(parse_field)

entry = (u'@' + label + u"{" + label + "," + pp.ZeroOrMore(field + ',') + field + u"}").setName("entry")
entry.setParseAction(parse_entry)

bibliography = (pp.OneOrMore(entry)).setName("bibliography")
bibliography.setParseAction(parse_bibliography)

pattern = bibliography + pp.StringEnd()
pattern.ignore(comment)

###############################################################################
# Helper functions

def parse_string(str, validate=False):
    """
    Tries to parse a given string into a Bibliography instance. If ``validate``
    is passed as keyword argument and set to ``True``, the Bibliography 
    will be validated using the standard rules.
    """
    result = pattern.parseString(str)[0]
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
        with codecs.open(file_or_path, 'r', encoding) as fp:
            result = pattern.parseFile(fp)[0]
    else:
        result = pattern.parseFile(file_or_path)[0]
    if validate:
        result.validate()
    return result
