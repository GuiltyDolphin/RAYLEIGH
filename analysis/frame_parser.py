#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# frame_parser.py

import re
import json
import sys
from collections import deque
import os
import csv


class FrameParser(object):

    """Parser for frame files (calibration and standard)"""

    def __init__(self):
        """TODO: to be defined1. """

    def _retrieve_frame(self, data):
        """Retrieve frame from a string of data

        Parameters
        ----------
        data : (string)
             The data to be parsed - this may
             be valid calibration or standard
             frame data.

        Returns
        -------
        frame : ([[Numeric, Numeric, Numeric]])
              The frame as a list of [x, y, c] hits, where
              x is the x-coordinate, y is the y-coordinate and
              c is the intensity of the hit.
        """

        def retrieve_from_standard_data(frame):
            """Retrieve the frame from a standard data file"""
            space_separated = type('space_sep', (),
                {'delimiter': ' ', 'skipinitialspace': True,
                 'quoting': csv.QUOTE_NONNUMERIC})
            frame = frame.replace('\t', ' ')
            vals = csv.reader(frame.splitlines(), dialect=space_separated)
            return list(vals)

        def retrieve_from_calibration(frames):
            """Retrieve the clusters from a calibration file"""
            hits = []
            hit_matcher = re.compile("(\[(?:\d+, )+\d+\])")
            for frame in frames:
                for hit_set in frame.splitlines():
                    hits.extend(
                        map(json.loads, hit_matcher.findall(hit_set)))
            return hits

        if self._is_calibration_data(data):
            def _safe_remove(ls, c):
                if c in ls:
                    ls.remove(c)

            frames = re.split("Frame.*\n", data)
            _safe_remove(frames, '')
            return retrieve_from_calibration(frames)
        else:
            return retrieve_from_standard_data(data)

    def _get_frame_from_file(self, file_name):
        """Retrieve frame from a file object"""
        with open(file_name) as f:
            contents = f.read()
        return self._retrieve_frame(contents)

    def _gen_output_data(self, data):
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

    def _write_data(self, data, path):
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

    def _is_calibration_data(self, data):
        """Determine whether some data is valid calibration data

        Parameters
        ----------
        data : (string)
             The data that may be calibration or standard.

        Returns
        -------
        result : (Boolean)
             Whether or not the data is calibration data.
        """
        return "Frame" in data

    def _write_output_directory(self, directory, extension=".txt"):
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
                    self._parse_file_and_write(f, gen_output_path(f))))

        write_to_frames_list()
        with open(directory + "/output/frames.json", 'w') as f:
            f.write(json.dumps(frames, indent=2))

    def _parse_file_and_write(self, in_file, out_file=None):
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
        frame = self._get_frame_from_file(in_file)
        output_data = self._gen_output_data(frame)
        self._write_data(output_data, to_write)
        return output_data

    def _input_type(self, input_):
        if os.path.isdir(input_):
            return "directory"
        elif os.path.isfile(input_):
            return "file"
        raise FileError("Could not recognize input type")

    def _detect_input_and_write(self, input_, out_file=None):
        type_ = self._input_type(input_)
        if type_ == "directory":
            self._write_output_directory(input_)
        elif type_ == "file":
            self._parse_file_and_write(input_, out_file)
