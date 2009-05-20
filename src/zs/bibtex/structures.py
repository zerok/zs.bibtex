"""
This module holds all the structures produced by the parser. The main 
structures are the clases ``Bibliography`` and ``Entry``. Both are 
slightly enhanced subclasses of ``dict`` and offer some additional
field validation.

Entry also has a handful of subclasses; one for each common entry-type
in BibTeX.
"""

from ..bibtex import exceptions


class TypeRegistry(object):
    """
    Global registry for entry types.
    """
    _registry = {}

    @classmethod
    def register(cls, name, type_):
        """
        Register a new type for an entry-type. The 2nd argument has to be a
        subclass of structures.Entry.
        """

        if not issubclass(type_, Entry):
            raise exceptions.InvalidEntryType, "%s is not a subclass of Entry" % str(type_)
        cls._registry[name.lower()] = type_

    @classmethod
    def get_type(cls, name):
        """
        Retrieve a type from the registry using its name as used in a bibtex 
        file.
        """
        return cls._registry.get(name.lower())

class Bibliography(dict):
    """
    A counter for all entries of a BibTeX file. It also contains the 
    cross-reference validator.
    """

    def __init__(self):
        self.crossrefs = []
        super(Bibliography, self).__init__()

    def validate(self, **kwargs):
        """
        Validates each entry (passing the provided arguments down to them and
        also tries to resolve all cross-references between the entries.
        """
        self.check_crossrefs()
        for value in self.values():
            value.validate(**kwargs)
    
    def check_crossrefs(self):
        """
        Checks all crossreferences found in the bibliography. If one can not
        be resolved from *this* Bibliography instance, a BrokenCrossReferences
        exception is raised.
        """
        broken = []
        for value in self.values():
            crossref = value.get('crossref')
            if crossref is not None:
                if crossref not in self:
                    broken.append(value)
        if len(broken):
            raise exceptions.BrokenCrossReferences('One or more cross reference could not'
                    ' be resolved', broken)

    def add(self, entry):
        """
        Add an entry based on its ``name``-attribute to the Bibliography.
        """
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

    def __init__(self, name=None, **kwargs):
        super(Entry, self).__init__(**kwargs)
        self.name = name

    def validate(self, raise_unsupported=False):
        """
        Checks if the Entry instance includes all the required fields of its
        type. If ``raise_unsupported`` is set to ``True`` it will also check
        for potentially unsupported types.

        If a problem is found, an InvalidStructure exception is raised.
        """
        fields = set(self.keys())
        flattened_required_fields = set()
        required_errors = []
        for field in self.required_fields:
            found = False
            if isinstance(field, (list, tuple)):
                # Check all alternatives
                for real_f in field:
                    if real_f in fields:
                        flattened_required_fields.add(real_f)
                        found = True
            else:
                flattened_required_fields.add(field)
                if field in fields: 
                    found = True
            if not found:
                required_errors.append(field)
        unsupported_fields = fields - flattened_required_fields \
                - set(self.optional_fields)
        if len(required_errors) or (raise_unsupported 
                and len(unsupported_fields)):
            raise exceptions.InvalidStructure("Missing or unsupported fields found",
                    required_fields=required_errors, 
                    unsupported_fields=unsupported_fields)

# The following required_fields/optiona_fields attributes are based on 
# http://en.wikipedia.org/wiki/Bibtex

class Article(Entry): 
    """Article in a journal, magazine etc."""

    required_fields = ('author', 'title', 'journal', 'year')
    optional_fields = ('value', 'number', 'pages', 'month', 'note', 'key')

TypeRegistry.register('article', Article)


class Book(Entry):
    """A book that has already been published or at least has a publisher."""

    required_fields = (('author', 'editor'), 'title', 'publisher', 'year')
    optional_fields = ('address', 'pages', 'volume', 'series', 'edition', 
            'month', 'note', 'key')

TypeRegistry.register('book', Book)

class Booklet(Entry): 
    """
    Similar to a book in the sense that it is bound but without a "real"
    publisher.
    """

    required_fields = Entry.required_fields
    optional_fields = ('author', 'howpublished', 'address', 'month', 'year', 
            'note', 'key')

TypeRegistry.register('booklet', Booklet)


class Incollection(Entry): 
    """Part of a book but with its own title."""

    required_fields = ('author', 'title', 'year', 'booktitle'),
    optional_fields = ('editor', 'pages', 'organization', 'publisher', 
            'address', 'month', 'note', 'key')

TypeRegistry.register('incollection', Incollection)


class Inproceedings(Incollection): 
    """Article that is part of a conference proceedings."""

    pass

TypeRegistry.register('inproceedings', Inproceedings)


class Conference(Inproceedings): 
    """Similar to ``Inproceedings``."""

    required_fields = ('author', 'title', 'booktitle', 'year')
    optional_fields = ('editor', 'pages', 'organization', 'publisher', 
            'address', 'month', 'note', 'key')

TypeRegistry.register('conference', Conference)


class Inbook(Entry): 
    """Part of a book."""

    required_fields = (('author', 'editor'), 'title', 'publisher', 'year',
            ('chapter', 'pages'))
    optional_fields = ('volume', 'series', 'address', 'edition', 'month', 
            'note', 'key')

TypeRegistry.register('inbook', Inbook)


class Manual(Entry): 
    """A technical manual."""

    required_fields = ('title',)
    optional_fields = ('author', 'organization', 'address', 'edition', 'year',
            'month', 'note', 'key')

TypeRegistry.register('manual', Manual)


class Mastersthesis(Entry): 
    """A Master's thesis"""

    required_fields = ('author', 'title', 'school', 'year')
    optional_fields = ('address', 'month', 'note', 'key')

TypeRegistry.register('mastersthesis', Mastersthesis)


class Misc(Entry):
    """Type of document that doesn't fit into any of the other categories."""

    required_fields = []
    optional_fields = ('author', 'title', 'howpublished', 'month', 'year', 
            'note', 'key')

TypeRegistry.register('misc', Misc)


class Phdthesis(Mastersthesis): 
    """A Ph.D. thesis."""
    pass

TypeRegistry.register('phdthesis', Phdthesis)


class Proceedings(Entry):
    """Conference proceedings."""

    required_fields = ('title', 'year')
    optional_fields = ('editor', 'publisher', 'organization', 'address', 
            'month', 'note', 'key')

TypeRegistry.register('proceedings', Proceedings)


class Techreport(Entry):
    """A technical report published by an institution."""

    required_fields = ('author', 'title', 'institution', 'year')
    optional_fields = ('type', 'number', 'address', 'month', 'note', 'key')

TypeRegistry.register('techreport', Techreport)


class Unpublished(Entry):
    """A not yet published document that already has an author and a title."""
    required_fields = ('author', 'title', 'note',)
    optional_fields = ('month', 'year', 'key',)

TypeRegistry.register('unpublished', Unpublished)

