# Installation
Currently no installation is required, as long as the dependencies
have been fulfilled the scripts can be run as described in the 'usage'
section.

## Source
The source code can be found on [Github](https://github.com/guiltydolphin/rayleigh).

## Dependencies

All modules are dependent upon a version of Python
that is compatible with Python3.4.0

Installation of these dependencies can be
achieved via 'pip3 install (dependency)'.
If errors occur whilst attempting to install
the dependencies, try the same command prepended
with 'sudo'.

matplotlib >= 1.4.2

nose       >= 1.3.4

numpy      >= 1.9.0

setuptools >= 6.0.2

# Usage

Use 'python3 [command_name] [options]' to run the commands.

## Examples:

With a directory called 'frames' that contains
two files, 'data00.txt' and 'data01.txt' (assume
the contents of these files is valid output data).

### Using the frame parser:

    python3 path/to/frame_parser.py frames

Results in the same directory as before, but containing
an additional directory called 'output', that in turn contains
three files: 'data00.json', 'data01.json' and 'frames.json'.

### Using the plotter:

After running the above example and moving into the output directory.

    python3 path/to/plotter.py data00.json -w --no-view

Results in a directory called 'plots' that contains a file called
'data00.txt.png'.


## Frame Parser

    Usage: frame_parser.py [options]

    Options:
      -h, --help            show this help message and exit
      -f FILE_NAME, --file-name=FILE_NAME
                            Provide the file name to be read explicitly
      -o FILE, --output-file=FILE
                            File to write output to or STDOUT

## Plotter

    Usage: plotter.py [options]

    Options:
      -h, --help            show this help message and exit
      -w, --write           Write the graph to file
      --no-view             Do not view the graph - only useful in conjunction
                            with other flags
      -f FILE_NAME, --file-name=FILE_NAME
                            Provide the file name to be read explicitly
      --outliers=OUTLIERS   Provide the value to be used when finding outliers
