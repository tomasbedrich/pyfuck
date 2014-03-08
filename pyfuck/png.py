#!/usr/bin/env python3



import zlib



BYTEORDER = "big" # PNG is big endian



class PNG(object):
    """
    Represents a simplified PNG image and it's operations.

    See:
        http://www.w3.org/TR/PNG/

    Author:
        Tomas Bedrich

    Examples:
        >>> image = PNG("test/assets/squares.png")
        >>> image.pixels #doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        [[(255, 0, 0), (0, 255, 0), (0, 0, 255)],
         [(255, 255, 255), (127, 127, 127), (0, 0, 0)],
         [(255, 255, 0), (255, 0, 255), (0, 255, 255)]]

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
    # TODO chunk len (and more) constants


    def __init__(self, filename):
        """
        Args:
            filename: PNG file to load
        """
        super(PNG, self).__init__()
        self.filename = filename
        self._parse()


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
        if reader.send(8) != PNG.SIGNATURE:
            err("The file is not a valid PNG image (signature doesn't match).")

        self.chunks = list()
        while True:

            # read len
            try:
                len = int.from_bytes(reader.send(4), BYTEORDER)
            except StopIteration:
                err("Unexpected file end.")

            # read type
            type = reader.send(4)

            # read data
            if len > 0:
                data = reader.send(len)
            else:
                data = b""

            # read CRC
            crc = reader.send(4)

            # create chunk object or end
            if type == b"IHDR":
                self.header = IHDR(data, crc)
            elif type == b"IEND":
                break
            else:
                self.chunks.append(Chunk(len, type, data, crc))

        if not self.header.isSimplified():
            err("The file is not a simplified PNG:\n" + str(self.header) + \
                "\nSupported bit depth: 8, colour type: 2. No compression, filter nor interlace.")

        # decompress
        try:
            self.decompressed = zlib.decompress(b"".join(chunk.data for chunk in self.chunks if chunk.type == b"IDAT"))
        except zlib.error:
            err("PNG data cannot be decompressed.")

        # scanline extraction
        # one line = filter + WIDTH * (R, G, B) bytes
        rgb = 3 # 3 color components
        lineLength = 1 + self.header.width * rgb
        self.scanlines = [[self.decompressed[y * lineLength + x] for x in range(0, lineLength)] for y in range(self.header.height)]

        # filter reconstruction
        self.bytes = list()
        for y, scanline in enumerate(self.scanlines):
            res = list()
            for x, byte in enumerate(scanline):
                if x == 0:
                    fil = byte
                    continue
                if fil:
                    a = x - rgb if x > rgb + 1 else 0
                    if a:
                        a = self.scanlines[y][a]
                    b = y - 1 if y > 1 else 0
                    if b:
                        b = self.scanlines[b][x]
                    c = b - rgb if b > rgb + 1 else 0
                    if c:
                        c = self.scanlines[b][c]
                    if fil == 1: # sub
                        byte = self.filterSub(byte, a)
                    elif fil == 2: # up
                        byte = self.filterUp(byte, b)
                    elif fil == 3: # average
                        byte = self.filterAverage(byte, a, b)
                    elif fil == 4: # paeth
                        byte = self.filterPaeth(byte, a, b, c)

                    # overflow and underflow detection
                    if byte > 255:
                        byte = 255
                    elif byte < 0:
                        byte = 0
                res.append(byte)
            self.bytes.append(res)

        # group bytes to pixels
        self.pixels = [[tuple(row[x:x+rgb]) for x in range(0, self.header.width * rgb, rgb)] for row in self.bytes]


    def filterSub(self, x, a):
        """
        Sub filter reconstruction function.

        See:
            http://www.w3.org/TR/PNG/#9-table91
        """
        return x + a


    def filterUp(self, x, b):
        """
        Up filter reconstruction function.

        See:
            http://www.w3.org/TR/PNG/#9-table91
        """
        return x + b


    def filterAverage(self, x, a, b):
        """
        Average filter reconstruction function.

        See:
            http://www.w3.org/TR/PNG/#9-table91
        """
        return x + floor((a + b) / 2)


    def filterPaeth(self, x, a, b, c):
        """
        Paeth filter reconstruction function.

        See:
            http://www.w3.org/TR/PNG/#9-table91
        """
        p = a + b - c
        pa = abs(p - a)
        pb = abs(p - b)
        pc = abs(p - c)
        if pa <= pb and pa <= pc:
            return a
        elif pb <= pc:
            return b
        else:
            return c


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
        self.crc = self._parseInt(crc, 0, 4)
        if not self.isValid():
            raise ValidationException("The chunk is not valid:\n" + str(self))


    def isValid(self):
        """
        Computes CRC on this chunk and validates chunk's attributes.

        Returns:
            True if this chunk is valid.
        """
        return len(self.type) == 4 and float(self.len).is_integer() and self.crc == zlib.crc32(self.type + self.data)


    def _parseInt(self, bytes, start=0, len=1):
        """
        Args:
            bytes: bytes to create integer from
            start: where to start
            len: how many bytes to parse

        Returns:
            Integer parsed from bytes.

        Examples:
            >>> Chunk._parseInt(None, b"\\xa6")
            166
            >>> Chunk._parseInt(None, b"\\xa6\\xffu", 0, 2)
            42751
        """
        return int.from_bytes(bytes[start:start+len], BYTEORDER)


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
        >>> ch.isValid()
        True
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
            return self._parseInt(data, start, len)
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
        return (self.depth == 8) and (self.colour == 2) and (not self.compression) and (not self.filter) and (not self.interlace)


    def __str__(self):
        return super(IHDR, self).__str__() + "\n" + \
            "width: {}\n".format(self.width) + \
            "height: {}\n".format(self.height) + \
            "bit depth: {}\n".format(self.depth) + \
            "colour type: {}\n".format(self.colour) + \
            "compression method: {}\n".format(self.compression) + \
            "filter method: {}\n".format(self.filter) + \
            "interlace method: {}".format(self.interlace)



class ValidationException(BaseException):
    """
    Raised in case of invalid PNG file.
    
    Author:
        Tomas Bedrich
    """
    pass
        