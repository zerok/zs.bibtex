from zs.bibtex import parser


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
