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
    optional_fields = []

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

class Article(Entry): 
    required_fields = ('author', 'title', 'journal', 'year')
    optional_fields = ('value', 'number', 'pages', 'month', 'note')

class Booklet(Entry): pass
class Conference(Entry): pass
class Inbook(Entry): pass
class Incollection(Entry): pass
class Inproceedings(Entry): pass
class Manual(Entry): pass
class Masterthesis(Entry): pass
class Misc(Entry): pass
class Phdthesis(Entry): pass
class Proceedings(Entry): pass
class Techreport(Entry): pass
class Unpublished(Entry): pass
