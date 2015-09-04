from .helpers import parse_entry

def test_multiple_authors():
    """
    Make sure that multiple authors are converted into a list while
    a single author is still represented as a string.
    """
    inp = "@article{somename, author={Max Mustermann1 and Max " \
            "Mustermann2}, title={Hello world}}"
    entry = parse_entry(inp)
    assert ['Max Mustermann1', 'Max Mustermann2'] == entry['author']
    entry = parse_entry('@article{somename, author={Max Mustermann}}')
    assert 'Max Mustermann' == entry['author']
