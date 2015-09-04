This package for now only includes a quite basic parser for BibTeX which
converts a bibliography and its entries into simple dict-like data structures
and also checks crossreferences if used.

.. warning::

    The parser does not (and probably never will) support some of the more
    advanced BibTeX-features like preambles.

A simple example on how to use it::

    from zs.bibtex.parser import parse_string
    from StringIO import StringIO

    data = '''@article{mm09,
        author = {Max Mustermann},
        title = {The story of my life},
        year = {2009},
        journal = {Life Journale}
    }'''

    bibliography = parse_string(data)
    article = bibliography['mm09']

A bibliography as well as each entry in it offers a ``validate()`` method
which checks aspects like cross-references on the bibliography and fields on
the entries. It also supports an optional ``raise_unsupported``
keyword-argument which raises an exception once a possibly unsupported field
is used in an entry.

The information about what fields are required and optional for what kind of
entry is based on the `BibTeX article`_ on Wikipedia.

.. _BibTeX article: http://en.wikipedia.org/wiki/Bibtex
