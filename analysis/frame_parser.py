#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# frame_parser.py

import re
import json
import sys
from collections import deque
import os
import csv


def _detect_input_and_write(input_, out_file=None):
    type_ = _input_type(input_)
    if type_ == "directory":
        _write_output_directory(input_)
    elif type_ == "file":
        _parse_file_and_write(input_, out_file)


def _write_data(data, path):
    """Write the JSON data to a file or stdout

    Parameters
    ----------
    data : (string)
            The data to be written to a file.
    path : (string), optional
            The path that the data will be written to.
            The default (None) causes the data to be written
            to STDOUT.

    Returns
    -------
    Nothing - Used for side-effects.
    """
    with open(path, 'w') as f:
        f.write(data)


def _input_type(input_):
    if os.path.isdir(input_):
        return "directory"
    elif os.path.isfile(input_):
        return "file"
    raise FileError("Could not recognize input type")


def _gen_output_data(data):
    """Generate the JSON representation of the data

    Parameters
    ----------
    data : (JSON serializable array)
            The data to be serialised

    Returns
    -------
    result : (String)
            The JSON serialised string
    """
    json_format = {'indent': 2}
    return json.dumps(data, **json_format)


def _retrieve_frame(data):
    """Retrieve frame from a string of data

    Parameters
    ----------
    data : (string)
            The data to be parsed.

    Returns
    -------
    frame : ([[Numeric, Numeric, Numeric]])
            The frame as a list of [x, y, c] hits, where
            x is the x-coordinate, y is the y-coordinate and
            c is the intensity of the hit.
    """

    space_separated = type(
        'space_sep', (),
        {
            'delimiter': ' ',
            'skipinitialspace': True,
            'quoting': csv.QUOTE_NONNUMERIC})
    frame = data.replace('\t', ' ')
    vals = csv.reader(frame.splitlines(), dialect=space_separated)
    return list(vals)


def _get_frame_from_file(file_name):
    """Retrieve frame from a file object"""
    with open(file_name) as f:
        contents = f.read()
    return _retrieve_frame(contents)


def _parse_file_and_write(in_file, out_file=None):
    """Perform the JSON conversion on a single file

    Parameters
    ----------
    in_file : (string)
            Path to the file to be read
    out_file : (string), optional
            The path to write the output data to.
            The default (None) will cause the output to be written to STDOUT.

    Returns
    -------
    output_data (string)
        The resulting parsed data as a JSON string.
    """
    to_write = out_file or os.path.splitext(in_file)[0] + '.json'
    frame = _get_frame_from_file(in_file)
    output_data = _gen_output_data(frame)
    _write_data(output_data, to_write)
    return output_data


def _write_output_directory(directory, extension=".txt"):
    """Parse a directory and write to output directory

    Parameters
    ----------
    directory : (string)
            Path to a directory that the datafiles will be read from
    extension : (string), optional
            The file extension that determines the files to be read.
            The default (".txt") causes files within the directory that
            have the extension '.txt' to be parsed.

    Returns
    -------
    Nothing - Used for side-effects.
    """

    def add_extension(fname, extension):
        """Append the extension to the file name"""
        return fname + extension

    def gen_output_path(fname):
        """Generate the expected path that the file will be written to"""
        new_name = add_extension(
            os.path.splitext(os.path.basename(fname))[0], ".json")
        new_dir = os.path.dirname(fname) + "/output/"
        return new_dir + new_name

    def get_valid_files(directory, ext):
        """Get a list of the (files) that match the extension in directory"""
        def with_dir(files):
            """Prepend the directory path to each of the files in file"""
            return map(lambda x: directory + "/" + x, files)

        def with_extension(files):
            """Get a filtered list of files matching the file extension"""
            return filter(lambda x: os.path.splitext(x)[1] == ext, files)

        return with_extension(
            filter(os.path.isfile, with_dir(os.listdir(directory))))

    os.mkdir(directory + "/output/")

    frames = []
    frame_number_matcher = re.compile("(\d+)\D*\.{}".format(extension.partition(".")[2]))

    def frame_compare():
        def cmp_func(x):
            return int(frame_number_matcher.findall(x)[0])
        return sorted(get_valid_files(directory, extension), key=cmp_func)

    def write_to_frames_list():
        """Append the contents of each frame
        (sorted by frame number) to the total frames"""
        for f in frame_compare():
            frames.append(json.loads(
                _parse_file_and_write(f, gen_output_path(f))))

    write_to_frames_list()
    with open(directory + "/output/frames.json", 'w') as f:
        f.write(json.dumps(frames, indent=2))
