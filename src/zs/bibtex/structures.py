from .exceptions import InvalidStructure, BrokenCrossReferences


class Bibliography(dict):
    """
    A counter for all entries of a BibTeX file. It also contains the 
    cross-reference validator.
    """

    def __init__(self):
        self.crossrefs = []
        super(Bibliography, self).__init__()

    def validate(self, **kwargs):
        self.check_crossrefs()
        for k, v in self.items():
            v.validate(**kwargs)
        pass
    
    def check_crossrefs(self):
        broken = []
        for k, v in self.items():
            crossref = v.get('crossref')
            if crossref is not None:
                if crossref not in self:
                    broken.append(v)
        if len(broken):
            raise BrokenCrossReferences('One or more cross reference could not be resolved', broken)

    def add(self, entry):
        self[entry.name] = entry

class Entry(dict): 
    """
    A slightly enhanced dict structure that acts as representation of an entry
    within a bibliography. It also comes with a generic validator for required
    and potentially unsupported fields and acts as base-class for the actual
    entry-types commonly used in BibTeX.
    """

    required_fields = ('title',)
    optional_fields = ('key', )

    def __init__(self, name=None):
        self.name = name

    def validate(self, raise_unsupported=False):
        fields = set(self.keys())
        flattened_required_fields = set()
        required_errors = []
        for f in self.required_fields:
            found = False
            if isinstance(f, (list, tuple)):
                # Check all alternatives
                for real_f in f:
                    if real_f in fields:
                        flattened_required_fields.add(real_f)
                        found = True
            else:
                flattened_required_fields.add(f)
                if f in fields: 
                    found = True
            if not found:
                required_errors.append(f)
        unsupported_fields = fields - flattened_required_fields - set(self.optional_fields)
        if len(required_errors) or (raise_unsupported and len(unsupported_fields)):
            raise InvalidStructure("Missing or unsupported fields found", 
                    required_fields=required_errors, 
                    unsupported_fields=unsupported_fields)

# The following required_fields/optiona_fields attributes are based on 
# http://en.wikipedia.org/wiki/Bibtex
class Article(Entry): 
    required_fields = ('author', 'title', 'journal', 'year')
    optional_fields = ('value', 'number', 'pages', 'month', 'note') + Entry.optional_fields

class Book(Entry):
    required_fields = (('author', 'editor'), 'title', 'publisher', 'year')
    optional_fields = ('address', 'pages', 'volume', 'series', 'edition', 'month', 'note') + Entry.optional_fields

class Booklet(Entry): 
    required_fields = Entry.required_fields
    optional_fields = ('author', 'howpublished', 'address', 'month', 'year', 'note', 'key')

class Conference(Entry): 
    required_fields = ('author', 'title', 'booktitle', 'year')
    optional_fields = ('editor', 'pages', 'organization', 'publisher', 'address', 'month', 'note', 'key')

class Inbook(Entry): 
    required_fields = (('author', 'editor'), 'title', 'publisher', 'year', ('chapter', 'pages'))
    optional_fields = ('volume', 'series', 'address', 'edition', 'month', 'note', 'key')

class Incollection(Entry): 
    required_fields = ('author', 'title', 'year', 'booktitle'),
    optional_fields = ('editor', 'pages', 'organization', 'publisher', 'address', 'month', 'note', 'key')

class Inproceedings(Incollection): pass

class Manual(Entry): 
    required_fields = ('title',)
    optional_fields = ('author', 'organization', 'address', 'edition', 'year', 'month', 'note', 'key')

class Masterthesis(Entry): 
    required_fields = ('author', 'title', 'school', 'year')
    optional_fields = ('address', 'month', 'note', 'key')

class Misc(Entry):
    required_fields = []
    optional_fields = ('author', 'title', 'howpublished', 'month', 'year', 'note', 'key')

class Phdthesis(Masterthesis): pass

class Proceedings(Entry):
    required_fields = ('title', 'year')
    optional_fields = ('editor', 'publisher', 'organization', 'address', 'month', 'note', 'key')

class Techreport(Entry):
    required_fields = ('author', 'title', 'institution', 'year')
    optional_fields = ('type', 'number', 'address', 'month', 'note', 'key')

class Unpublished(Entry):
    required_fields = ('author', 'title', 'note',)
    optional_fields = ('month', 'year', 'key',)
