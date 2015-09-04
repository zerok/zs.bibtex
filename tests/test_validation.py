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
    with pytest.raises(exceptions.InvalidStructure):
        entry.validate(raise_unsupported=True)
    broken_article = parse_entry("@article{somename, author={Max "
                                        "Mustermann1}, title={Hello world}, "
                                        "journal={My Journal}}")
    with pytest.raises(exceptions.InvalidStructure):
        broken_article.validate(raise_unsupported=True)


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
    with pytest.raises(exceptions.BrokenCrossReferences):
        bib.validate()
