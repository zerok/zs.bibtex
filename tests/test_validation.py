import pytest

from zs.bibtex import structures, parser, exceptions
from .helpers import parse_entry, parse_bibliography


def test_article_structure():
    """
    The validator should notice missing required and optionally
    also probably unsupported fields.
    """
    entry = parse_entry("@article{somename, author={Max Mustermann1},"
                                " title={Hello world}, journal={My Journal}, "
                                "year={2009}, url={}}")
    entry.validate()
    try:
        entry.validate(raise_unsupported=True)
        pytest.fail('An unsupported url field should have been detected')
    except exceptions.InvalidStructure as e:
        assert str(e) == 'Missing or unsupported fields found [Unsupported fields: url]'

    broken_article = parse_entry("@article{somename, author={Max "
                                        "Mustermann1}, title={Hello world}, "
                                        "journal={My Journal}}")
    try:
        broken_article.validate(raise_unsupported=True)
        pytest.fail('A missing year field should have been detected')
    except exceptions.InvalidStructure as e:
        assert str(e) == 'Missing or unsupported fields found [Missing required fields: year]'


def test_alternative():
    entries = [
        '@inbook{name, author={authorname}, title={title}, publisher={publisher}, year=1990, chapter=2}',
        '@inbook{name, editor={authorname}, title={title}, publisher={publisher}, year=1990, chapter=2}',
        '@inbook{name, editor={authorname}, title={title}, publisher={publisher}, year=1990, pages=2}',
        '@inbook{name, author={authorname}, title={title}, publisher={publisher}, year=1990, pages=2}',
        ]
    for entry in entries:
        parse_entry(entry).validate()


def test_regression_article_with_volume():
    """
    Articles should support the volume attribute
    """
    entry = parser.parse_string('''@article{mm09,
    author = {Max Mustermann},
    title = {The story of my life},
    year = {2009},
    journal = {Life Journale},
    volume = {1}
    }''')
    entry.validate(raise_unsupported=True)


def test_broken_crossref():
    """
    Checks the cross-reference validation within the Bibliography class.
    """
    bib = parse_bibliography("@article{somename, author={Max "
            "Mustermann1}, crossref={test}, title={Hello world}, "
            "journal={My Journal}, year={2009}, url={}}")
    try:
        bib.validate()
        pytest.fail('Missing crossreference to "test" should have been detected')
    except exceptions.BrokenCrossReferences as e:
        assert str(e) == 'One or more cross reference could not be resolved [Broken references: somename => test]'
