import pytest

from zs.bibtex import structures, exceptions
from .helpers import parse_entry


def test_global_typeregistry():
    """
    Check if it's possible to globally register a new Entry type.
    """

    class TestEntryType(structures.Entry):
        pass
    structures.TypeRegistry.register('test', TestEntryType)

    parse_entry('@test{name, title={test}}')


def test_invalid_entryclass():
    """
    Make sure that the new Entry type is a subclass of Entry.
    """

    class TestEntryType(object):
        pass
    with pytest.raises(exceptions.InvalidEntryType):
            structures.TypeRegistry.register('test', TestEntryType)
