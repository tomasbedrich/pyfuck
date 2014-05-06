#!/usr/bin/env python3



import zlib
from math import floor
from io import IOBase



BYTEORDER = "big" # PNG is big endian
RGB = 3 # 3 colour components



class PNG(object):
    """
    Represents a simplified PNG image and it's operations.

    See:
        http://www.w3.org/TR/PNG/

    Author:
        Tomas Bedrich
    """


    SIGNATURE = b"\x89PNG\r\n\x1a\n"
    CHUNK_LEN = 4 # bytes
    CHUNK_TYPE = 4 # bytes
    CHUNK_CRC = 4 # bytes


    def __init__(self):
        super(PNG, self).__init__()
        PNG.IEND = Chunk(0, b"IEND", b"", b"\xaeB`\x82")

        self.header = None
        self.close = False


    def __del__(self):
        if self.close:
            self.file.close()


    def _open(self, target, mode="rb"):
        if issubclass(type(target), IOBase):
            self.filename = target.name
            self.file = target
        else:
            self.filename = target
            self.file = open(self.filename, mode)
            self.close = True


    def load(self, target):
        """
        Loads a PNG file to actual instance.

        Args:
            target: source

        Raises:
            pyfuck.png.ValidationException, IOError

        Examples:
            >>> PNG().load("test/assets/squares.png").pixels #doctest: +NORMALIZE_WHITESPACE
            [[(255, 0, 0), (0, 255, 0), (0, 0, 255)],
             [(255, 255, 255), (127, 127, 127), (0, 0, 0)],
             [(255, 255, 0), (255, 0, 255), (0, 255, 255)]]

            >>> f = open("test/assets/squares.png", "rb") # use with statement instead
            >>> PNG().load(f).pixels #doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
            [[(255, 0, 0), ... (0, 255, 255)]]
            >>> f.close()

            >>> PNG().load("test/assets/bad.png") #doctest: +ELLIPSIS
            Traceback (most recent call last):
            pyfuck.png.ValidationException: ...

            >>> PNG().load("test/assets/not.found") #doctest: +ELLIPSIS
            Traceback (most recent call last):
            FileNotFoundError: ...
        """
        self._open(target, "rb")
        self._read()
        return self


    def save(self, target):
        """
        Saves an instance as a PNG file.

        Args:
            target: destination

        Raises:
            IOError

        Examples:
            >>> p = PNG()
            >>> colours = (255, 0, 0), (0, 255, 0), (0, 0, 255)
            >>> p.pixels = [[random.choice(colours) for x in range(3)] for y in range(3)]
            >>> p.save("test/assets/saved.png")
        """
        self._open(target, "wb")
        self._write()


    def _read(self):
        """
        Parses the PNG and saves data to self for further manipulations.

        Raises:
            pyfuck.png.ValidationException, IOError
        """

        # init generator
        reader = self._reader()
        next(reader)

        # validate header
        if reader.send(len(PNG.SIGNATURE)) != PNG.SIGNATURE:
            self._err("The file is not a valid PNG image (signature doesn't match).")

        chunks = []
        while True:

            # read length
            try:
                length = int.from_bytes(reader.send(PNG.CHUNK_LEN), BYTEORDER)
            except StopIteration:
                self._err("Unexpected file end.")

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
                # raises exception if not valid
                chunks.append(Chunk(length, type, data, crc))

        if not self.header:
            self._err("Missing PNG header.")

        if not self.header.isSimplified():
            self._err("The file is not a simplified PNG:\n" + str(self.header) + \
                "\nSupported values are: bit depth: 1, 2, 4, 8; colour type: 2, 3; compression: 0; filter: 0; interlace: 0.")

        # decompress
        try:
            decompressed = zlib.decompress(b"".join(chunk.data for chunk in chunks if chunk.type == b"IDAT"))
        except zlib.error:
            self._err("PNG data cannot be decompressed.")

        # scanline extraction
        if self.header.colour == 2: # truecolour
            # one line length = (filter + width * (R, G, B) * depth / 8 (in bytes)
            lineLength = 1 + self.header.width * RGB * self.header.depth // 8
        elif self.header.colour == 3: # indexed-colour
            lineLength = 1 + self.header.width * self.header.depth // 8

        scanlines = [decompressed[y * lineLength : (y + 1) * lineLength] for y in range(self.header.height)]

        raw = [list(map(int, row)) for row in scanlines]

        # filter reconstruction
        for y, row in enumerate(scanlines):
            for x, byte in enumerate(row):
                if x == 0: # set filter for each scanline
                    fil = byte
                    continue

                if fil:
                    a = raw[y][x - RGB] if x > RGB else 0
                    
                    if fil == 1: # sub
                        byte += a
                    
                    else:
                        b = raw[y - 1][x] if y > 0 else 0

                        if fil == 2: # up
                            byte += b
                        
                        elif fil == 3: # average
                            byte += floor((a + b) / 2)

                        elif fil == 4: # paeth
                            c = raw[y - 1][x - RGB] if x > RGB and y > 0 else 0
                            _ = a + b - c
                            pa, pb, pc = abs(_ - a), abs(_ - b), abs(_ - c)
                            if pa <= pb and pa <= pc:
                                byte += a
                            elif pb <= pc:
                                byte += b
                            else:
                                byte += c

                    byte %= 256

                raw[y][x] = byte

        for y, row in enumerate(raw):
            raw[y] = row[1:]

        # group bytes to pixels
        if self.header.colour == 2: # truecolour
            self._pixels = [[tuple(row[x:x+RGB]) for x in range(0, len(row), RGB)] for row in raw]
        elif self.header.colour == 3: # indexed-colour
            def getColour(index):
                return self.palette.palette[index]
            shifts = list(reversed(range(0, 8, self.header.depth)))
            self._pixels = [[getColour(row[i // len(shifts)] >> shift & 2 ** self.header.depth - 1) for i, shift in enumerate(len(row) * shifts)] for row in raw]


    def _write(self):
        """
        Outputs data from self to file - aka writes the PNG file.
        """

        # init generator
        writer = self._writer()
        next(writer)

        writer.send(PNG.SIGNATURE)

        # generate raw bytes
        raw = bytearray()
        for row in self._pixels:
            raw.append(0) # filter 0
            for pixel in row:
                raw.extend(pixel)

        # write header
        writer.send(self.header)

        # write data
        type = b"IDAT"
        compressed = zlib.compress(raw)
        crc = zlib.crc32(type + compressed).to_bytes(4, BYTEORDER)
        length = len(compressed)
        writer.send(Chunk(length, type, compressed, crc))

        writer.send(PNG.IEND)


    def _reader(self):
        """
        Binary file reader.

        This is generator object which recieves number of bytes to read.

        Returns:
            A generator object.
        """
        howMuch = yield
        byte = self.file.read(howMuch)
        while byte != b"":
            howMuch = yield byte
            if not howMuch:
                howMuch = 1
            byte = self.file.read(howMuch)


    def _writer(self):
        """
        Binary file writer.

        This is generator object which recieves bytes to write.

        Returns:
            A generator object.
        """
        data = True
        while data:
            data = yield
            self.file.write(bytes(data))


    @property
    def pixels(self):
        return self._pixels


    @pixels.setter
    def pixels(self, value):
        """
        Image data (pixels) setter.

        Raises:
            pyfuck.png.ValidationException
        """

        # validation
        prevLen = len(value[0])

        # for each line
        for row in value:
            if len(row) != prevLen:
                raise ValidationException("The image is not rectangular.")
            prevLen = len(row)

            # for each pixel
            for pixel in row:
                if len(pixel) != RGB:
                    raise ValidationException("Does your RGB display really have {} colour components?".format(len(pixel)))

                # for each colour component
                for component in pixel:
                    if not 0 <= component <= 255:
                        raise ValidationException("Invalid colour value.")

        # seems ok
        self._pixels = value
        self.header = IHDR.initSimplified(prevLen, len(value))


    def _err(self, msg):
        raise ValidationException("'{}': ".format(self.filename) + msg)


    def __eq__(self, other):
        return self.pixels == other.pixels


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


    def __bytes__(self):
        res = bytes()
        res += self.len.to_bytes(4, BYTEORDER)
        res += self.type
        res += self.data
        res += self.crc.to_bytes(4, BYTEORDER)
        return res


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


    TYPE = b"IHDR"


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
        super(IHDR, self).__init__(13, IHDR.TYPE, data, crc)


    @classmethod
    def initSimplified(cls, width, height):
        def get(data, len):
            return data.to_bytes(len, BYTEORDER)
        
        data = bytes()
        data += get(width, 4) # width
        data += get(height, 4) # height
        data += get(8, 1) # depth
        data += get(2, 1) # colour
        data += get(0, 1) # compression
        data += get(0, 1) # filter
        data += get(0, 1) # interlace
        return cls(data, get(zlib.crc32(cls.TYPE + data), 4))


    def isValid(self):
        return super(IHDR, self).isValid() and self.width and self.height


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


    TYPE = b"PLTE"


    def __init__(self, len, data, crc):
        super(PLTE, self).__init__(len, PLTE.TYPE, data, crc)
        RGB = 3 # 3 colour components
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



if __name__ == '__main__':
    # TODO
    pass
