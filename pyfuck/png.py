#!/usr/bin/env python3



import zlib
from math import floor



BYTEORDER = "big" # PNG is big endian
RGB = 3 # 3 color components



class PNG(object):
    """
    Represents a simplified PNG image and it's operations.

    See:
        http://www.w3.org/TR/PNG/

    Author:
        Tomas Bedrich

    Examples:
        >>> PNG("test/assets/squares.png").pixels #doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        [[(255, 0, 0), (0, 255, 0), (0, 0, 255)],
         [(255, 255, 255), (127, 127, 127), (0, 0, 0)],
         [(255, 255, 0), (255, 0, 255), (0, 255, 255)]]

        >>> PNG("test/assets/hello_world.png").pixels #doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        [[(255, 0, 0), (0, 255, 0), (0, 255, 0),
         ...
         (0, 128, 0), (0, 128, 0), (0, 255, 255)]]

        >>> PNG("test/assets/not.found") #doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        FileNotFoundError: ...

        >>> PNG("test/assets/bad.png") #doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        pyfuck.png.ValidationException: ...
    """


    SIGNATURE = b'\x89PNG\r\n\x1a\n'
    CHUNK_LEN = 4 # bytes
    CHUNK_TYPE = 4 # bytes
    CHUNK_CRC = 4 # bytes


    def __init__(self, filename):
        """
        Args:
            filename: PNG file to load
        """
        super(PNG, self).__init__()
        self.filename = filename
        self._parse()


    # TODO refactoring: too long method
    def _parse(self):
        """
        Parses the PNG and saves data in readable form for further manipulations.

        Raises:
            pyfuck.png.ValidationException
        """

        def err(msg):
            raise ValidationException("'{}': ".format(self.filename) + msg)

        # initiate generator
        reader = self._reader()
        next(reader)

        # validate header
        if reader.send(len(PNG.SIGNATURE)) != PNG.SIGNATURE:
            err("The file is not a valid PNG image (signature doesn't match).")

        self.chunks = list()
        while True:

            # read length
            try:
                length = int.from_bytes(reader.send(PNG.CHUNK_LEN), BYTEORDER)
            except StopIteration:
                err("Unexpected file end.")

            # read type
            type = reader.send(PNG.CHUNK_TYPE)

            # read data
            if length > 0:
                data = reader.send(length)
            else:
                data = b""

            # read CRC
            crc = reader.send(PNG.CHUNK_CRC)

            # create chunk object or end
            if type == b"IHDR":
                self.header = IHDR(data, crc)
            elif type == b"PLTE":
                self.palette = PLTE(length, data, crc)
            elif type == b"IEND":
                break
            else:
                self.chunks.append(Chunk(length, type, data, crc))

        if not self.header.isSimplified():
            err("The file is not a simplified PNG:\n" + str(self.header) + \
                "\nSupported values are: bit depth: 1, 2, 4, 8; colour type: 2, 3; compression: 0; filter: 0; interlace: 0.")

        # decompress
        try:
            self.decompressed = zlib.decompress(b"".join(chunk.data for chunk in self.chunks if chunk.type == b"IDAT"))
        except zlib.error:
            err("PNG data cannot be decompressed.")

        # scanline extraction
        if self.header.colour == 2: # truecolour
            # one line length = (filter + width * (R, G, B) * depth / 8 (in bytes)
            lineLength = 1 + self.header.width * RGB * self.header.depth // 8
        elif self.header.colour == 3: # indexed-colour
            lineLength = 1 + self.header.width * self.header.depth // 8

        self.scanlines = [[self.decompressed[y * lineLength + x] for x in range(0, lineLength)] for y in range(self.header.height)]

        # filter reconstruction
        self.bytes = list()
        for y, scanline in enumerate(self.scanlines):
            res = list()
            for x, byte in enumerate(scanline):
                if x == 0: # set filter for each scanline
                    fil = byte
                    continue
                if fil:
                    if fil == 1: # sub
                        byte = self._filterSub(x, y)
                    elif fil == 2: # up
                        byte = self._filterUp(x, y)
                    elif fil == 3: # average
                        byte = self._filterAverage(x, y)
                    elif fil == 4: # paeth
                        byte = self._filterPaeth(x, y)
                self.scanlines[y][x] = byte
                res.append(byte)
            self.bytes.append(res)

        # group bytes to pixels
        if self.header.colour == 2: # truecolour
            self.pixels = [[tuple(row[x:x+RGB]) for x in range(0, len(row), RGB)] for row in self.bytes]
        elif self.header.colour == 3: # indexed-colour
            def getColour(index):
                return self.palette.palette[index]
            shifts = list(reversed(range(0, 8, self.header.depth)))
            self.pixels = [[getColour(row[i // len(shifts)] >> shift & 2 ** self.header.depth - 1) for i, shift in enumerate(len(row) * shifts)] for row in self.bytes]


    def _getA(self, x, y):
        if x > RGB:
            return self.scanlines[y][x - RGB]
        else:
            return 0


    def _getB(self, x, y):
        if y > 0:
            return self.scanlines[y - 1][x]
        else:
            return 0


    def _getC(self, x, y):
        if x > RGB and y > 0:
            return self.scanlines[y - 1][x - RGB]
        else:
            return 0


    def _filterSub(self, x, y):
        """
        Sub filter reconstruction function.

        See:
            http://www.w3.org/TR/PNG/#9-table91

        Examples:
            >>> PNG("test/assets/filterSub.png").pixels[-2][-1]
            (8, 70, 255)
        """
        return (self.scanlines[y][x] + self._getA(x, y)) % 256


    def _filterUp(self, x, y):
        """
        Up filter reconstruction function.

        See:
            http://www.w3.org/TR/PNG/#9-table91

        Examples:
            >>> PNG("test/assets/filterUp.png").pixels[-2][-1]
            (8, 70, 255)
        """
        return (self.scanlines[y][x] + self._getB(x, y)) % 256


    def _filterAverage(self, x, y):
        """
        Average filter reconstruction function.

        See:
            http://www.w3.org/TR/PNG/#9-table91

        Examples:
            >>> PNG("test/assets/filterAverage.png").pixels[-2][-1]
            (8, 70, 255)
        """
        return (self.scanlines[y][x] + floor((self._getA(x, y) + self._getB(x, y)) / 2)) % 256


    def _filterPaeth(self, x, y):
        """
        Paeth filter reconstruction function.

        See:
            http://www.w3.org/TR/PNG/#9-table91

        Examples:
            >>> PNG("test/assets/filterPaeth.png").pixels[-2][-1]
            (8, 70, 255)
        """
        a, b, c = self._getA(x, y), self._getB(x, y), self._getC(x, y)
        p = a + b - c
        pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
        if pa <= pb and pa <= pc:
            pr = a
        elif pb <= pc:
            pr = b
        else:
            pr = c
        return (self.scanlines[y][x] + pr) % 256


    def _reader(self):
        """
        Binary file reader.

        This is generator object which recieves number of bytes to read.

        Returns:
            A generator object.
        """
        with open(self.filename, "rb") as f:
            howMuch = yield
            byte = f.read(howMuch)
            while byte != b"":
                howMuch = yield byte
                if not howMuch:
                    howMuch = 1
                byte = f.read(howMuch)


    def __str__(self):
        super(PNG, self).__str__() + "\n" + \
            "filename: {}".format(self.filename)



class Chunk(object):
    """
    Represents a PNG chunk.
    
    Author:
        Tomas Bedrich

    Examples:
        >>> len = 28
        >>> data = (12701710363046137946869161245835418579410248820780388934922353642866).to_bytes(len, 'big')
        >>> crc = b'\\xa6|\\xffu'
        >>> ch = Chunk(len, b"IDAT", data, crc)
        >>> ch.isValid()
        True
    """


    def __init__(self, len, type, data, crc):
        """
        Args:
            len: int, max 4 byte long - chunk data length (in bytes)
            type: byte array, 4 byte long - chunk type (ASCII string)
            data: byte array, `len` byte long - raw data
            crc: byte array, 4 byte long - CRC checksum of type + data
        """
        super(Chunk, self).__init__()
        self.len = len
        self.type = type
        self.data = data
        self.crc = parseInt(crc, 0, 4)
        if not self.isValid():
            raise ValidationException("The chunk is not valid:\n" + str(self))


    def isValid(self):
        """
        Computes CRC on this chunk and validates chunk's attributes.

        Returns:
            True if this chunk is valid.
        """
        return len(self.type) == 4 and float(self.len).is_integer() and self.crc == zlib.crc32(self.type + self.data)


    def __str__(self):
        return super(Chunk, self).__str__() + "\n" + \
            "len: {}\n".format(self.len) + \
            "type: {}\n".format(self.type) + \
            "data: {}\n".format(self.data) + \
            "crc: {}\n".format(self.crc) + \
            "valid: {}".format(self.isValid())



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
        >>> ch = IHDR(b'\\x00\\x00\\x00\\x03\\x00\\x00\\x00\\x03\\x08\\x02\\x00\\x00\\x00', b'\\xd9J"\\xe8')
        >>> ch.isSimplified()
        True
        >>> ch.width
        3
        >>> ch.height
        3
        >>> ch.depth
        8
        >>> ch.colour
        2
    """


    def __init__(self, data, crc):
        def get(start, len):
            return parseInt(data, start, len)
        self.width = get(0, 4)
        self.height = get(4, 4)
        self.depth = get(8, 1)
        self.colour = get(9, 1)
        self.compression = get(10, 1)
        self.filter = get(11, 1)
        self.interlace = get(12, 1)
        super(IHDR, self).__init__(13, b"IHDR", data, crc)


    def isValid(self):
        return super(IHDR, self).isValid() and self.width != 0 and self.height != 0


    def isSimplified(self):
        """
        Returns:
            True if this IHDR describes simplified PNG image.
        """
        return self.depth in (1, 2, 4, 8) and self.colour in (2, 3) \
            and not self.compression and not self.filter and not self.interlace


    def __str__(self):
        return super(IHDR, self).__str__() + "\n" + \
            "width: {}\n".format(self.width) + \
            "height: {}\n".format(self.height) + \
            "bit depth: {}\n".format(self.depth) + \
            "colour type: {}\n".format(self.colour) + \
            "compression method: {}\n".format(self.compression) + \
            "filter method: {}\n".format(self.filter) + \
            "interlace method: {}".format(self.interlace)



class PLTE(Chunk):
    """
    Represents an PLTE chunk.

    This chunk contains 1 to 256 palette entries each:
    - red: 1 byte
    - green: 1 byte
    - blue: 1 byte

    See:
        http://www.w3.org/TR/PNG/#11PLTE

    Author:
        Tomas Bedrich

    Examples:
        >>> len = 12
        >>> data = b'\\x00\\xff\\x00\\xff\\x00\\x00\\xff\\xff\\x00\\x00\\x00\\xff'
        >>> PLTE(len, data, (1698638778).to_bytes(4, 'big')).palette
        [(0, 255, 0), (255, 0, 0), (255, 255, 0), (0, 0, 255)]
    """


    def __init__(self, len, data, crc):
        super(PLTE, self).__init__(len, b"PLTE", data, crc)
        RGB = 3 # 3 color components
        self.palette = [ tuple(parseInt(data, 3 * i + j) for j in range(RGB)) for i in range(self.len // RGB)]


    def isValid(self):
        return super(PLTE, self).isValid() and (0 < self.len <= 256 * 3) and (self.len % 3 == 0)


    def __str__(self):
        return super(PLTE, self).__str__() + "\n" + \
            "palette: {}".format(self.palette)



class ValidationException(BaseException):
    """
    Raised in case of invalid PNG file.
    
    Author:
        Tomas Bedrich
    """
    pass



def parseInt(data, start=0, len=1):
    """
    Args:
        data: bytes to create integer from
        start: where to start
        len: how many bytes to parse

    Returns:
        Integer parsed from bytes.

    Examples:
        >>> parseInt(b"\\xa6")
        166
        >>> parseInt(b"\\xa6\\xffu", 0, 2)
        42751
    """
    return int.from_bytes(data[start:start+len], BYTEORDER)



def bitReader(data):
    """
    A bit reader.

    This is generator object which recieves number of bit to read.
    Aligns the data to 8 bits!

    Args:
        data: bytes to read from

    Returns:
        Array of integers (0 or 1) read from data.

    Examples:
        >>> reader = bitReader(b'\\x03')
        >>> next(reader) # initiate generator
        >>> reader.send(8)
        [0, 0, 0, 0, 0, 0, 1, 1]
    """
    if not isinstance(data, bytes):
        return

    def bit():
        for byte in data:
            for i in reversed(range(8)):
                yield (byte >> i) & 1

    howMuch = yield
    bit = bit()
    while True:
        howMuch = yield [next(bit) for _ in range(howMuch)]
