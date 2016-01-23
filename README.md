# RAYLEIGH 

[![Build Status](https://travis-ci.org/GuiltyDolphin/RAYLEIGH.svg?branch=master)](https://travis-ci.org/GuiltyDolphin/RAYLEIGH) [![Coverage Status](https://coveralls.io/repos/github/GuiltyDolphin/RAYLEIGH/badge.svg?branch=master)](https://coveralls.io/github/GuiltyDolphin/RAYLEIGH?branch=master)

A plotter and file converter for output files from TimePix chips.

# Installation

In the directory with `setup.py`, run `python3 setup.py install`. If the
script should only be installed for the current user, run
`python3 setup.py install --user`.



## Source
The source code can be found on
[Github](https://github.com/guiltydolphin/rayleigh).

## License

RAYLEIGH is licensed under GPLv3.
See the LICENSE file for more information.

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

`rayleigh [options] <command> {arguments}`

Use `rayleigh --help` for an overview of the commands.

## Examples:

With a directory called 'frames' that contains
two files, 'data00.txt' and 'data01.txt' (assume
the contents of these files is valid output data).

```
/toplevel <-- PWD
/frames
    data00.txt
    data01.txt
```

### Using the frame parser:

    rayleigh frame frames

Results in the same directory as before, but containing
an additional directory called 'output', that in turn contains
three files: 'data00.json', 'data01.json' and 'frames.json'.

```
/toplevel <-- PWD
  /frames
      data00.txt
      data01.txt
      /output
          data00.json
          data01.json
          frames.json
```

### Using the plotter:

After running the above example and moving into the output directory.

    rayleigh plot data00.json -w --no-view

Results in a directory called 'plots' that contains a file called
'data00.json.png'.

```
/toplevel
  /frames
      data00.txt
      data01.txt
      /output <-- PWD
          data00.json
          data01.json
          frames.json
          /plots
              data00.json.png
```


## Frame Parser

Usage: `rayleigh frame [options] frames..`

Use `rayleigh frame --help` for the option summary.

## Plotter

Usage: `rayleigh plot [options] frames..`

Use `rayleigh plot --help` for the option summary.
