#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# cluster_parser.py

import re
import json
import sys
from optparse import OptionParser
import logging
from collections import deque
import os


class FrameParser(object):

    """Parser for frame files (calibration and standard)"""

    def __init__(self):
        """TODO: to be defined1. """

    def _retrieve_frame(self, data):
        """Retrieve frame from raw string"""

        ## Might want to sort out the below two methods
        ## - Might not be wise to have two unknown paths
        ## within one function
        def retrieve_from_standard_data(frame):
            """Retrieve the frame from a standard data file"""
            hits = deque()
            hit_matcher = re.compile("(\d+)\s+(\d+)\s+(\d+)")
            for hit in frame.splitlines():
                hits.append(list(map(int, hit_matcher.search(hit).groups())))
            return list(hits)

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
        """Generate the JSON representation of the data"""
        json_format = {'indent': 2}
        return json.dumps(data, **json_format)

    def _write_data(self, data, path=None):
        """Write the JSON data to a file or stdout"""
        if path is None:
            print("Writing to STDOUT currently disabled due to large datasets")
        else:
            with open(path, 'w') as f:
                f.write(data)

    def _is_calibration_data(self, data):
        """Determine whether some data is valid calibration data"""
        return "Frame" in data

    def _write_output_directory(self, directory, extension=".txt"):
        """Write output to specified directory"""

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
        frame = self._get_frame_from_file(in_file)
        output_data = self._gen_output_data(frame)
        self._write_data(output_data, out_file)
        return output_data


#### COMMAND-LINE ####

## Perhaps the CLI section should be moved into it's own class?
## Also - Add better testing for this section - maybe even rewrite
## it in TDD style
def _setup_parser(usage=None):
    parser = OptionParser(usage) if usage else OptionParser()
    #parser.add_option("-f", "--input-file", dest="input_file",
    #                  help="File to read cluster data from", metavar="FILE")
    parser.add_option("-o", "--output-file", dest="output_file",
                      help="File to write output to or STDOUT",
                      default=None, metavar="FILE")
    parser.add_option("-v", "--verbose", dest="verbose",
                      help="Print status messages to STDOUT", default=False,
                      action="store_true")
    parser.add_option("-i", "--info", dest="info",
                      help="Print additional information about process",
                      default=False, action="store_true")
    parser.add_option("--no-log", dest="log",
                      action="store_false", default=False,
                      help="Don't write to a log file")
    parser.add_option("--log", dest="log_level", default="ERROR",
                      help="Set the logging level")
    parser.add_option("--log-file", dest="log_file",
                      default="frame_parser.log",
                      help="Specify the file to send log messages to")
    return parser


def _main(args=sys.argv[1:]):
    option_parser = _setup_parser()
    (options, args) = option_parser.parse_args(args)

    if len(args) != 1:
        print("wrong number of arguments: {}".format(len(args)))
        sys.exit(2)
    else:
        options.input_file = args[0]

    def _set_logger():
        """Return a configured logger"""
        time_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        log_level = getattr(logging, options.log_level.upper(), None)
        if not isinstance(log_level, int):
            raise ValueError("Invalid log level: {}".format(options.log_level))

        logging.basicConfig(level=log_level,
                            filename=options.log_file,
                            format=time_format)

        logger = logging.getLogger('cluster_parser')
        logger.setLevel(log_level)

        stream_level = getattr(
            logging, "DEBUG" if options.verbose
            else ("INFO" if options.info else "ERROR"),
            None)
        log_stdout = logging.StreamHandler()
        log_stdout.setLevel(stream_level)
        logger.addHandler(log_stdout)
        return logger

    ## Fix the logging section below
    ## - The Debug may be removed until needed
    ## - This section should probably be written in TDD
    ##   style later on, to remove any UI bugs.
    ##   - Figure out a good way to test the user's interaction
    ##     with the application (and the graphing)
    logger = _set_logger()
    logger.setLevel(logging.DEBUG)  # This appears to fix logging?

    parser = FrameParser()

    logger.debug("Retrieving clusters...")
    frame = parser._get_frame_from_file(options.input_file)

    logger.debug("Converting data to JSON format...")
    output_data = parser._gen_output_data(frame)
    logger.debug("Conversion complete")

    if options.output_file:
        logger.debug("Writing to {}".format(options.output_file))
    else:
        logger.debug("Writing to stdout...")

    parser._write_data(output_data, options.output_file)


if __name__ == '__main__':
    _main()
