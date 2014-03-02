#!/usr/bin/env python3


import logging


class Brainfuck(object):

    COMMANDS = "<>+-.,[]!"

    def __init__(self):
        super(Brainfuck, self).__init__()


    def _compile(self, program):
        compiled = list()
        stack = list()

        for pos, command in enumerate(program):

            if command not in self.COMMANDS:
                continue

            # save while { pos to stack
            if command is "[":
                stack.append(pos)
                compiled.append([command, 0])

            # pair while { and }
            elif command is "]":
                _ = stack.pop()
                compiled.append([command, _])
                compiled[_][1] = pos

            else:
                compiled.append([command, 0])

        return compiled


    def eval(self, program):
        pc = 0 # = program counter
        cc = 0 # = cell counter
        cc_max = 0 # = cell counter max
        cells = bytearray(1)

        compiled = self._compile(program)

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
                print(chr(cells[cc]), end="")

            # input and save to current
            elif command is ",":
                # TODO
                pass

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
