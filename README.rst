#########
zs.bibtex
#########

.. image:: https://travis-ci.org/zerok/zs.bibtex.svg?branch=master
    :target: https://travis-ci.org/zerok/zs.bibtex

This package for now only includes a quite basic parser for BibTeX which
converts a bibliography and its entries into simple dict-like data structures
and also checks crossreferences if used.

.. warning::

    The parser does not (and probably never will) support some of the more
    advanced BibTeX-features like preambles.

    It also doesn't convert things like accented characters into unicode but
    leaves them as they were in the original input.


Usage
=====

A simple example on how to use it::

    from zs.bibtex.parser import parse_string

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

If you're working with a file you can also use a small helper function called
``parse_file(file_or_path, encoding='utf-8', validate=False)`` which works on a
given filepath or file-like object and returns a bibliography object for the
content of that file.


Custom entry types
==================

Out of the box zs.bibtex supports following entry types for validation:

- article
- book
- booklet
- incollection
- inproceedings
- conference
- inbook
- manual
- masterthesis
- misc
- phdthesis
- proceedings
- techreport
- unpublished

For details on which of these requires what fields please take a look at the
``zs.bibtex.structures`` module.

But if you are in a situation where you need a different entry type, you can
also easily register your own.

First you have to create a subclass of the ``zs.bibtex.structures.Entry``
class::

  from zs.bibtex import structures


  class MyEntryType(structures.Entry):
      required_fields = ('required_field_1', ('either_this', 'or_that', ), )
      optional_fields = ('optional_field_1', )


and then simply register it::

  structures.TypeRegistry.register('mytype', MyEntryType')


.. _BibTeX article: http://en.wikipedia.org/wiki/Bibtex
