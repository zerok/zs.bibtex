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

This module includes the unittests for the parser and other components of this
package.

If you have the source distribution of zs.bibtex available, use ./bin/test to 
run these tests.
"""

import unittest
import pyparsing

from ..bibtex import structures, parser, exceptions


def parse_entry(string):
    """
    Small helper function for parsing a single entry.
    """
    for value in parser.parse_string(string).values():
        return value

def parse_bibliography(string):
    """
    Helper function for parsing a bibliography.
    """
    return parser.parse_string(string)


class ParserTests(unittest.TestCase):
    """Some general tests for the parser."""

    def test_basic(self):
        """
        Run some basic tests to see if parsing works at all.
        """
        inp = '@article{somename, author={Max Mustermann}, ' \
                'title={Hello world}}'
        bib = parse_bibliography(inp)
        self.assertEqual(1, len(bib))
        self.assertEqual('somename', bib['somename'].name)
        entry = bib['somename']
        self.assertEqual('Max Mustermann', entry['author'])
        self.assertEqual('Hello world', entry['title'])

    def test_regression_number_in_name(self):
        """
        Make sure that numbers can be used in entry-names.
        """
        entry = parse_entry('''@article{mm09,
        author = {Max Mustermann},
        title = {The story of my life},
        year = {2009},
        journal = {Life Journale}
        }''')
        self.assertEqual('mm09', entry.name)

    def test_regression_optional_last_comma(self):
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

    def test_regression_numeric_value_without_quotes(self):
        parse_entry('''@article{mm09,
        author = {Max Mustermann},
        title = {The story of my life},
        year = 2009,
        journal = {Life Journale}
        }''')

    def test_uppercase(self):
        """
        Fieldnames and types should get normalized to their lowercase 
        representation.
        """
        entry = parse_entry("@ARTICLE{somename, AUTHOR={Max Mustermann1},"
                " title={Hello world}, journal={My Journal}, year={2009}}")
        self.assertEquals(structures.Article, type(entry))
        entry.validate()

    def test_syntaxerror(self):
        """
        Check if pyparsing.ParseException is raised on syntax errors.
        """
        inp = '@article{name}'
        self.assertRaises(pyparsing.ParseException, parse_entry, inp)

    def test_comments(self):
        """
        Make sure that comments don't interfer with the rest of the 
        parsing.
        """
        bib = parse_bibliography('''% some comment
@article { name, % whatever
    title = {la%la}
    }''')
        self.assertEquals(1, len(bib))
        self.assertEquals('la%la', bib['name']['title'])

    def test_entry_subtype(self):
        """
        Check if an UnsupportedEntryType exception is raised if no type could
        be found for a given entry-type.
        """
        inp = '@bibliography{name, title={test}}'
        self.assertRaises(exceptions.UnsupportedEntryType, parse_entry, 
                inp)
        inp = '@article2{name, title={test}}'
        self.assertRaises(exceptions.UnsupportedEntryType, parse_entry, 
                inp)

    def test_basetypes(self):
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

class ValidationChecks(unittest.TestCase):
    """
    Various checks for the entry and bibliography validation.
    """

    def test_article_structure(self):
        """
        The validator should notice missing required and optionally
        also probably unsupported fields.
        """
        entry = parse_entry("@article{somename, author={Max Mustermann1},"
                                 " title={Hello world}, journal={My Journal}, "
                                 "year={2009}, url={}}")
        entry.validate()
        self.assertRaises(exceptions.InvalidStructure, entry.validate, 
                raise_unsupported=True)
        broken_article = parse_entry("@article{somename, author={Max "
                                          "Mustermann1}, title={Hello world}, "
                                          "journal={My Journal}}")
        self.assertRaises(exceptions.InvalidStructure, broken_article.validate,
                raise_unsupported=True)

    def test_regression_article_with_volume(self):
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

    def test_broken_crossref(self):
        """
        Checks the cross-reference validation within the Bibliography class.
        """
        bib = parse_bibliography("@article{somename, author={Max "
                "Mustermann1}, crossref={test}, title={Hello world}, "
                "journal={My Journal}, year={2009}, url={}}")
        self.assertRaises(exceptions.BrokenCrossReferences, bib.validate)

class QuotingTests(unittest.TestCase):
    """
    BibTeX offers some very strange quoting options. Some of them are tested
    here.
    """

    def test_bstring(self):
        """
        Test nested bibtex strings.
        """
        inp = r'{{test} {{test2}}}'
        self.assertEquals('{test} {{test2}}', 
                parser.bstring.parseString(inp)[0])

    def test_quotedliteral_escapes(self):
        """
        Check if escap sequence for quote characters are removed from
        the result.
        """
        inp = r'@article{somename, author="Max \"Mustermann", ' \
                r'title={Hello world}}'
        bib = parse_bibliography(inp)
        self.assertEqual(1, len(bib))
        self.assertEqual('somename', bib['somename'].name)
        entry = bib['somename']
        self.assertEqual('Max "Mustermann', entry['author'])

    def test_multiline_quotedliteral(self):
        """
        Make sure that quoting works for multiple lines.
        """
        inp = """@article{somename, author="Max 
                Mustermann", title={Hello world}}"""
        entry = parse_entry(inp)
        self.assertEqual('Max Mustermann', entry.get('author'))
    
    def test_multiline_blockliteral(self):
        """
        Quoting with braces should also work for multiple lines.
        """
        inp = """@article{somename, author={Max 
                Mustermann}, title={Hello world}}"""
        entry = parse_entry(inp)
        self.assertEqual('Max Mustermann', entry.get('author'))

class SpecialFieldTests(unittest.TestCase):
    """
    Some fields can be converted Python types other than string.
    These tests should cover some of them.
    """

    def test_multiple_authors(self):
        """
        Make sure that multiple authors are converted into a list while
        a single author is still represented as a string.
        """
        inp = "@article{somename, author={Max Mustermann1 and Max " \
                "Mustermann2}, title={Hello world}}"
        entry = parse_entry(inp)
        self.assertEqual(['Max Mustermann1', 'Max Mustermann2'],
                entry['author'])
        entry = parse_entry('@article{somename, author={Max Mustermann}}')
        self.assertEqual('Max Mustermann', entry['author'])

class CustomizationTests(unittest.TestCase):
    """
    Tests for the customization features.
    """

    def test_global_typeregistry(self):
        """
        Check if it's possible to globally register a new Entry type.
        """

        class TestEntryType(structures.Entry):
            pass
        structures.TypeRegistry.register('test', TestEntryType)

        parse_entry('@test{name, title={test}}')

    def test_invalid_entryclass(self):
        """
        Make sure that the new Entry type is a subclass of Entry.
        """

        class TestEntryType(object):
            pass
        self.assertRaises(exceptions.InvalidEntryType,
                structures.TypeRegistry.register, 'test', TestEntryType)

