#!/usr/bin/env python3


BYTEORDER = "big"


class PNG(object):
    """
    Represents a simplified PNG image and it's operations.

    See:
        http://www.w3.org/TR/PNG/

    Author:
        Tomas Bedrich
    """


    def __init__(self, filename):
        super(PNG, self).__init__()
        self.filename = filename
        self.file = open(self.filename)


    def _parse(self):
        pass



class Chunk(object):
    """
    Represents a PNG chunk.
    """


    def __init__(self, len, type, data, crc):
        super(Chunk, self).__init__()
        self.len = len
        self.type = type
        self.data = data
        self.crc = crc


    def _parseBytes(self, bytes, start, len):
        return int.from_bytes(bytes[start:start+len], BYTEORDER)


    def __str__(self):
        return self.__repr__()



class IHDR(Chunk):
    """
    Represents an IHDR chunk.

    This chunk is first and exclusive in every PNG file and contains following basic informations:
    - width: 4 bytes
    - height: 4 bytes
    - bit depth: 1 byte
    - colour type: 1 byte
    - compression method: 1 byte
    - filter method: 1 byte
    - interlace method: 1 byte

    See:
        http://www.w3.org/TR/PNG/#11IHDR

    Author:
        Tomas Bedrich

    Examples:
        >>> ch = IHDR((14167099451941863817216).to_bytes(13, 'big'), (3645514472).to_bytes(4, 'big'))
        >>> print(ch) # doctest:+ELLIPSIS
        <pyfuck.png.IHDR object at ...>
        width: 3
        height: 3
        bit depth: 8
        colour type: 2
        compression method: 0
        filter method: 0
        interlace method: 0
    """


    def __init__(self, data, crc):
        super(IHDR, self).__init__((13).to_bytes(13, 'big'), b'IHDR', data, crc)
        def get(start, len):
            return self._parseBytes(data, start, len)
        self.width = get(0, 4)
        self.height = get(4, 4)
        self.depth = get(8, 1)
        self.colour = get(9, 1)
        self.compression = get(10, 1)
        self.filter = get(11, 1)
        self.interlace = get(12, 1)


    def __str__(self):
        return super(IHDR, self).__str__() + "\n" + \
            "width: {}\n".format(self.width) + \
            "height: {}\n".format(self.height) + \
            "bit depth: {}\n".format(self.depth) + \
            "colour type: {}\n".format(self.colour) + \
            "compression method: {}\n".format(self.compression) + \
            "filter method: {}\n".format(self.filter) + \
            "interlace method: {}".format(self.interlace)


    def isSimplified(self):
        """
        Returns:
            True if this IHDR describes simplified PNG image.
        """
        return self.depth is 8 and self.colour is 2 and self.compression is 0 and self.filter is 0 and self.interlace is 0
