import unittest
import StringIO
import pyparsing

from ..bibtex import structures, parser
from .exceptions import InvalidStructure, BrokenCrossReferences


class ParserTests(unittest.TestCase):

    def parse_entry(self, string):
        for k, v in parser.parse_string(string).items():
            return v

    def parse_bibliography(self, string):
        return parser.parse_string(string)

    def test_basic(self):
        input = """@article{somename, author={Max Mustermann}, title={Hello world}}"""
        bib = self.parse_bibliography(input)
        self.assertEqual(1, len(bib))
        self.assertEqual('somename', bib['somename'].name)
        entry = bib['somename']
        self.assertEqual('Max Mustermann', entry['author'])
        self.assertEqual('Hello world', entry['title'])

    def test_quotedliteral_escapes(self):
        input = r"""@article{somename, author="Max \"Mustermann", title={Hello world}}"""
        bib = self.parse_bibliography(input)
        self.assertEqual(1, len(bib))
        self.assertEqual('somename', bib['somename'].name)
        entry = bib['somename']
        self.assertEqual('Max "Mustermann', entry['author'])

    def test_multiline_quotedliteral(self):
        input = """@article{somename, author="Max 
                Mustermann", title={Hello world}}"""
        entry = self.parse_entry(input)
        self.assertEqual('Max Mustermann', entry.get('author'))
    
    def test_multiline_blockliteral(self):
        input = """@article{somename, author={Max 
                Mustermann}, title={Hello world}}"""
        entry = self.parse_entry(input)
        self.assertEqual('Max Mustermann', entry.get('author'))

    def test_single_author(self):
        input = """@article{somename, author={Max Mustermann}, title={Hello world}}"""
        entry = self.parse_entry(input)
        self.assertEqual('Max Mustermann', entry['author'])

    def test_multiple_authors(self):
        input = """@article{somename, author={Max Mustermann1 and Max Mustermann2}, title={Hello world}}"""
        entry = self.parse_entry(input)
        self.assertEqual(['Max Mustermann1', 'Max Mustermann2'], entry['author'])

    def test_regression_number_in_name(self):
        entry = self.parse_entry('''@article{mm09,
        author = {Max Mustermann},
        title = {The story of my life},
        year = {2009},
        journal = {Life Journale}
        }''')
        self.assertEqual('mm09', entry.name)

    def test_article_structure(self):
        entry = self.parse_entry("""@article{somename, author={Max Mustermann1}, title={Hello world}, journal={My Journal}, year={2009}, url={}}""")
        entry.validate()
        self.assertRaises(InvalidStructure, entry.validate, raise_unsupported=True)
        broken_article = self.parse_entry("""@article{somename, author={Max Mustermann1}, title={Hello world}, journal={My Journal}}""")
        self.assertRaises(InvalidStructure, broken_article.validate, raise_unsupported=True)

    def test_broken_crossref(self):
        bib = self.parse_bibliography("""@article{somename, author={Max Mustermann1}, crossref={test}, title={Hello world}, journal={My Journal}, year={2009}, url={}}""")
        self.assertRaises(BrokenCrossReferences, bib.validate)

    def test_uppercase_types_and_fieldnames(self):
        entry = self.parse_entry("""@ARTICLE{somename, AUTHOR={Max Mustermann1}, title={Hello world}, journal={My Journal}, year={2009}, url={}}""")
        self.assertEquals(structures.Article, type(entry))
        entry.validate()

    def test_syntaxerror(self):
        input = '@article{name}'
        self.assertRaises(pyparsing.ParseException, self.parse_entry, input)

    def test_bstring(self):
        input = r'{{test} {{test2}}}'
        self.assertEquals('{test} {{test2}}', parser.bstring.parseString(input)[0])

    def test_comments(self):
        bib = self.parse_bibliography('''% some comment
@article { name, % whatever
    title = {lala}
    }''')
        self.assertEquals(1, len(bib))
        self.assertEquals('lala', bib['name']['title'])

