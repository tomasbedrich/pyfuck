# PyFuck: Brainfuck-family languages interpreter and converter

### Supported languages:

 - [Brainfuck](http://esolangs.org/wiki/Brainfuck) (extended syntax with `!`)
 - [Brainloller](http://esolangs.org/wiki/Brainloller)
 - [Braincopter](http://esolangs.org/wiki/Braincopter)

### Features:

 - interpret each langugage
 - convert between langugages


## Usage

    pyfuck [-h] {run,convert} ...

    pyfuck run [-h] [-t {auto,brainfuck,braincopter,brainloller}] [source]

    pyfuck convert [-h] [-t {auto,brainfuck,braincopter,brainloller}]
                         -o {brainfuck,braincopter,brainloller}
                        [-i <image>] [source] [destination]

### Positional arguments

 `source`  
  Source file to interpret (default: sys.stdin).

 `destination`  
  Destination filename (default: sys.stdout).

### Optional arguments

 `-t/--type {auto,brainfuck,braincopter,brainloller}`  
  Source type (default: auto).

 `-o/--output {brainfuck,braincopter,brainloller}`  
  Output type. Required for all conversions.

 `-i/--image <image>`  
  A PNG file where to encode the Braincopter data.
  Required for all conversions to Braincopter.


## Example usage

Run simple brainfuck file:

    python -m pyfuck run hello_world.bf
    python -m pyfuck run < hello_world.bf
    python -m pyfuck run -t brainfuck hello_world.bf

Run brainloller and braincopter:

    python -m pyfuck run hello_world.brainloller.png
    python -m pyfuck run hello_world.braincopter.png

Convert anything to brainfuck:

    python -m pyfuck convert -o brainfuck hello_world.brainloller.png result.bf

Convert brainfuck to braincopter:

    python -m pyfuck convert -o braincopter -i image.png hello_world.brainloller.png result.braincopter.png


## Author

Tomas Bedrich  
tbedrich.cz  
ja@tbedrich.cz