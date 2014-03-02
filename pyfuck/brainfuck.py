#!/usr/bin/env python3


import logging
import sys
# TODO use doctest and https://github.com/Feneric/doxypypy

class Brainfuck(object):
    """
    Represents a basic Brainfuck! interpreter.

    Brainfuck syntax:
    >   increment the data pointer (to point to the next cell to the right).
    <   decrement the data pointer (to point to the next cell to the left).
    +   increment (increase by one) the byte at the data pointer.
    -   decrement (decrease by one) the byte at the data pointer.
    .   output the byte at the data pointer.
    ,   accept one byte of input, storing its value in the byte at the data pointer.
    [   if the byte at the data pointer is zero, then instead of moving the instruction pointer forward to the next command, jump it forward to the command after the matching ] command.
    ]   if the byte at the data pointer is nonzero, then instead of moving the instruction pointer forward to the next command, jump it back to the command after the matching [ command.

    Author:
        Tomas Bedrich

    See:
        http://en.wikipedia.org/wiki/Brainfuck

    Examples:
        # TODO
    """

    COMMANDS = "<>+-.,[]!"

    def __init__(self):
        super(Brainfuck, self).__init__()
        self._getch = Brainfuck._find_getch()

    @staticmethod
    def _find_getch():
        """
        Returns platform specific implementation of C's getch() method.

        Author:
            Louis
        
        See:
            http://stackoverflow.com/questions/510357/python-read-a-single-character-from-the-user
        """
        try:
            import termios
        except ImportError:
            # Non-POSIX. Return msvcrt's (Windows') getch.
            import msvcrt
            return msvcrt.getch

        # POSIX system. Create and return a getch that manipulates the tty.
        import tty
        def _getch():
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch

        return _getch

    def _compile(self, program):
        """
        'Compiles' Brainfuck! code.

        Args:
            program: A string with Brainfuck! program.

        Returns:
            Two dimensional array with commands and possible jump destinations.

        Examples:
            >>> b = Brainfuck()
            >>> b._compile("+-.")
            [['+', 0], ['-', 0], ['.', 0]]
            >>> b._compile("comment.")
            [['.', 0]]
            >>> b._compile("print0:.[]")
            [['.', 0], ['[', 2], [']', 1]]
        """
        skipped = 0
        compiled = list()
        stack = list()

        for pos, command in enumerate(program):

            if command not in self.COMMANDS:
                skipped += 1
                continue

            # save while { pos to stack
            if command is "[":
                stack.append(pos - skipped)
                compiled.append([command, 0])

            # pair while { and }
            elif command is "]":
                _ = stack.pop()
                compiled.append([command, _])
                compiled[_][1] = pos - skipped

            else:
                compiled.append([command, 0])

        return compiled


    def eval(self, program, stdout=None, stdin=None):
        """
        Evaluates the Brainfuck! program.

        Args:
            program: A string with Brainfuck! program.
            stdout: Output destination. Passed as to print() function. Default is sys.stdout.
            stdin: Input source. Any iterator returning individual chars can be passed. Default is sys.stdin.

        Examples:
            >>> Brainfuck().eval("++++++++++[>+++++++>++++++++++>+++>+<<<<-]>++.>+.+++++++..+++.>++.<<+++++++++++++++.>.+++.------.--------.>+.>.")
            Hello World!
        """
        pc = 0 # = program counter
        cc = 0 # = cell counter
        cc_max = 0 # = cell counter max
        cells = bytearray(1)
        compiled = self._compile(program)

        if stdout is None:
            stdout = sys.stdout
        
        try:
            stdin = iter(stdin)
        except TypeError:
            stdin = None

        while True:

            try:
                command = compiled[pc][0]
            except IndexError:
                break

            logging.debug("Processing command: {}".format(compiled[pc]))

            # move one cell left
            if command is "<" and cc > 0:
                cc -= 1

            # move one cell right
            elif command is ">":
                cc += 1
                if cc > cc_max:
                    cells.append(0)
                    cc_max += 1

            # increment
            elif command is "+":
                cells[cc] += 1

            # decrement
            elif command is "-":
                cells[cc] -= 1

            # output current cc
            elif command is ".":
                print(chr(cells[cc]), end="", file=stdout)

            # input and save to current
            elif command is ",":
                if stdin:
                    try:
                        _ = next(stdin)
                    except StopIteration:
                        raise EOFError("More input required.")
                else:
                    _ = self._getch()
                cells[cc] = ord(_)

            # while current is not 0
            elif command is "[":
                if cells[cc] is 0:
                    pc = compiled[pc][1]

            # end while
            elif command is "]":
                if cells[cc] is not 0:
                    pc = compiled[pc][1]

            # data separator
            elif command is "!":
                # TODO
                pass

            pc += 1


def main():
    logging.basicConfig(level=logging.INFO)
    # TODO


if __name__ == '__main__':
    main()
