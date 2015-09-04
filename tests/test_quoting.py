from zs.bibtex import parser
from .helpers import parse_entry, parse_bibliography


def test_bstring():
    """
    Test nested bibtex strings.
    """
    inp = r'{{test} {{test2}}}'
    assert '{test} {{test2}}' == parser.bstring.parseString(inp)[0]

def test_quotedliteral_escapes():
    """
    Check if escap sequence for quote characters are removed from
    the result.
    """
    inp = r'@article{somename, author="Max \"Mustermann", ' \
            r'title={Hello world}}'
    bib = parse_bibliography(inp)
    assert 1 == len(bib)
    assert 'somename' == bib['somename'].name

    entry = bib['somename']
    assert 'Max "Mustermann' == entry['author']


def test_multiline_quotedliteral():
    """
    Make sure that quoting works for multiple lines.
    """
    inp = """@article{somename, author="Max
            Mustermann", title={Hello world}}"""
    entry = parse_entry(inp)
    assert 'Max Mustermann' == entry.get('author')


def test_multiline_blockliteral():
    """
    Quoting with braces should also work for multiple lines.
    """
    inp = """@article{somename, author={Max
            Mustermann}, title={Hello world}}"""
    entry = parse_entry(inp)
    assert 'Max Mustermann' == entry.get('author')
