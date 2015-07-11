# segment.py is a module for creating EDI-compliant segments

# creates a segment using the 3-digit segment description and a list of
# elements. Returns a string based on input that can then be written to file.
def make_segment(desc,elements):
    elements.insert(0, desc)
    segment = '*'.join(map(str, elements))
    segment = segment+"~"
    return segment

