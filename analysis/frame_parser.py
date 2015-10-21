#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# frame_parser.py

import csv
import glob
import json
import os
import re


def _detect_input_and_write(input_, out_file=None):
    if os.path.isdir(input_):
        _write_output_directory(input_)
    elif os.path.isfile(input_):
        _parse_file_and_write(input_, out_file)
    else:
        raise FileNotFoundError(
            "Not a valid file or directory: {}".format(input_))


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
    with open(file_name) as file:
        contents = file.read()
    return _retrieve_frame(contents)


def _parse_file_and_write(in_file, out_file=None):
    """Perform the JSON conversion on a single file

    Parameters
    ----------
    in_file : (string)
            Path to the file to be read
    out_file : (string), optional
            The path to write the output data to.
            The default (None) will automatically generate a filename based on
            the input file.

    Returns
    -------
    Nothing - used for side effects.
    """
    data = _get_output_data_from_file(in_file)
    _write_data(data, out_file)


def _write_data(data, file_name=None):
    to_write = file_name or os.path.splitext(in_file)[0] + '.json'
    with open(to_write, 'w') as fname:
        fname.write(data)


def _get_output_data_from_file(file_name):
    """Generate the JSON data from a frame file

    Parameters
    ----------
    file_name : (string)
              Path to the file to read

    Returns
    -------
    result : (String)
            The JSON serialised string
    """
    frame = _get_frame_from_file(file_name)
    return _gen_output_data(frame)


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

    def gen_output_path(fname):
        """Generate the expected path that the file will be written to"""
        base = os.path.basename(fname)
        without_ext = os.path.splitext(base)[0]
        with_ext = without_ext + '.json'
        new_dir = os.path.dirname(fname) + "/output/"
        return new_dir + with_ext

    def get_valid_files(directory, ext):
        """Get a list of the (files) that match the extension in directory"""
        files = os.listdir(directory)
        matches = glob.fnmatch.filter(files, '*{}'.format(ext))
        full_matches = [os.path.join(directory, file) for file in matches]
        return [file for file in full_matches if os.path.isfile(file)]

    os.mkdir(directory + "/output/")

    frames = []
    frame_number_matcher = re.compile(
        "(\d+)\D*\.{}".format(extension.partition(".")[2]))

    def frame_compare():
        def cmp_func(x):
            return int(frame_number_matcher.findall(x)[0])
        return sorted(get_valid_files(directory, extension), key=cmp_func)

    def write_to_frames_list():
        """Append the contents of each frame
        (sorted by frame number) to the total frames"""
        for file in frame_compare():
            curr_frame_data = _get_output_data_from_file(file)
            frames.append(json.loads(curr_frame_data))
            _write_data(curr_frame_data, gen_output_path(file))

    write_to_frames_list()
    with open(directory + "/output/frames.json", 'w') as file:
        file.write(json.dumps(frames, indent=2))
