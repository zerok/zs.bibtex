class UnsupportedEntryType(RuntimeError): pass

class InvalidStructure(RuntimeError):
    """
    This exception is raised if a structure is missing any required fields
    or (if enabled in the validator) any potentially unsupported fields are
    present.
    """
    def __init__(self, value, required_fields=[], unsupported_fields=[]):
        self.required_fields = required_fields
        self.unsupported_fields = unsupported_fields
        super(InvalidStructure, self).__init__(value)

    def __str__(self):
        val = super(InvalidStructure, self).__str__()
        if len(self.required_fields):
            val += ' [Missing required fields: %s]' % str(self.required_fields)
        if len(self.unsupported_fields):
            val += ' [Unsupported fields: %s]' % str(self.unsupported_fields)
        return val

class BrokenCrossReferences(RuntimeError):
    """
    This exception is raised if the Bibliography's validator encounters a 
    cross-reference it cannot resolve.
    """
    def __init__(self, value, entries):
        super(BrokenCrossReferences, self).__init__(value)
        self.entries = entries

    def __str__(self):
        val = super(BrokenCrossReferences, self).__str__()
        return val + ' [Broken references: %s]' % str(['%s => %s' % (e.name, e['crossref']) for e in self.entries])

