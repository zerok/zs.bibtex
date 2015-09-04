import io
import pyparsing
import pytest

from zs.bibtex import exceptions, structures, parser
from .helpers import parse_entry, parse_bibliography


def test_basic():
    """
    Run some basic tests to see if parsing works at all.
    """
    inp = '@article{somename, author={Max Mustermann}, ' \
            'title={Hello world}}'
    bib = parse_bibliography(inp)
    assert 1 == len(bib)
    assert 'somename' == bib['somename'].name

    entry = bib['somename']
    assert 'Max Mustermann' == entry['author']
    assert 'Hello world' == entry['title']


def test_regression_number_in_name():
    """
    Make sure that numbers can be used in entry-names.
    """
    entry = parse_entry('''@article{mm09,
    author = {Max Mustermann},
    title = {The story of my life},
    year = {2009},
    journal = {Life Journale}
    }''')
    assert 'mm09' == entry.name


def test_regression_optional_last_comma():
    """
    The last statement may or may not be finished with a ,
    """
    parse_entry('''@ARTICLE{article-crossref,
        crossref = {WHOLE-JOURNAL},
        author = {L[eslie] A. Aamport},
        title = {The Gnats and Gnus Document Preparation System},
        pages = "73+",
        note = "This is a cross-referencing ARTICLE entry",
    }''')


def test_regression_numeric_value_without_quotes():
    parse_entry('''@article{mm09,
    author = {Max Mustermann},
    title = {The story of my life},
    year = 2009,
    journal = {Life Journale}
    }''')


def test_uppercase():
    """
    Fieldnames and types should get normalized to their lowercase
    representation.
    """
    entry = parse_entry("@ARTICLE{somename, AUTHOR={Max Mustermann1},"
            " title={Hello world}, journal={My Journal}, year={2009}}")
    assert structures.Article == type(entry)
    entry.validate()

def test_syntaxerror():
    """
    Check if pyparsing.ParseException is raised on syntax errors.
    """
    inp = '@article{name}'
    with pytest.raises(pyparsing.ParseException):
        parse_entry(inp)


def test_comments():
    """
    Make sure that comments don't interfer with the rest of the
    parsing.
    """
    bib = parse_bibliography('''% some comment
@article { name, % whatever
title = {la%la}
}''')
    assert len(bib) == 1
    assert 'la%la' == bib['name']['title']


def test_entry_subtype():
    """
    Check if an UnsupportedEntryType exception is raised if no type could
    be found for a given entry-type.
    """
    inp = '@bibliography{name, title={test}}'
    with pytest.raises(exceptions.UnsupportedEntryType):
        parse_entry(inp)
    inp = '@article2{name, title={test}}'
    with pytest.raises(exceptions.UnsupportedEntryType):
        parse_entry(inp)


def test_basetypes():
    """
    Tests that all basic Entry-subclasses are registered.
    """
    types = ('article', 'book', 'booklet', 'incollection',
                'inproceedings', 'conference', 'inbook', 'manual',
                'mastersthesis', 'misc', 'phdthesis', 'proceedings',
                'techreport', 'unpublished',)
    for type_ in types:
        inp = '@%s {name, title = {test}}' % type_
        parse_entry(inp)


def test_with_validation():
    inp = '''% some comment
    @article { name, author = {Max Mustermann},
        title = {la%la}
    }
    '''
    with pytest.raises(exceptions.InvalidStructure):
        parser.parse_string(inp, validate=True)

    inp = '''% some comment
    @article { name, author = {Max Mustermann},
        year = {2009},
        journal = {Life Journale},
        title = {la%la}
    }
    '''
    parser.parse_string(inp, validate=True)


def test_file_as_path(tmpdir):
    test_file = tmpdir.join('test.bib')
    test_file.write('''
    @article { name, author = {Max Mustermann},
        year = {2009},
        journal = {Life Journale},
        title = {la%la}
    }
    ''')
    parser.parse_file(str(test_file))
    parser.parse_file(str(test_file), validate=True)

    # Invalid structure
    test_file.write('''
    @article { name, author = {Max Mustermann},
        title = {la%la}
    }
    ''')
    parser.parse_file(str(test_file))
    with pytest.raises(exceptions.InvalidStructure):
        parser.parse_file(str(test_file), validate=True)


def test_file_as_object(tmpdir):
    test_file = tmpdir.join('test.bib')
    test_file.write('''
    @article { name, author = {Max Mustermann},
        year = {2009},
        journal = {Life Journale},
        title = {la%la}
    }
    ''')
    with io.open(str(test_file), encoding='utf-8') as fp:
        parser.parse_file(fp)
    with io.open(str(test_file), encoding='utf-8') as fp:
        parser.parse_file(fp, validate=True)

    # Invalid structure
    test_file.write('''
    @article { name, author = {Max Mustermann},
        title = {la%la}
    }
    ''')
    with io.open(str(test_file), encoding='utf-8') as fp:
        parser.parse_file(fp)
    with io.open(str(test_file), encoding='utf-8') as fp:
        with pytest.raises(exceptions.InvalidStructure):
            parser.parse_file(fp, validate=True)
