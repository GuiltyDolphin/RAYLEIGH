#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# cluster_parser.py

import re
import json
import sys
from optparse import OptionParser
import logging
from collections import deque



#### DATA TRANSFER ####

def _gen_output_data(data):
    """Generate the JSON representation of the data"""
    json_format = {'indent': 2}
    return json.dumps(data, **json_format)


def _write_data(data, path=None):
    """Write the JSON data to a file or stdout"""

    if path is None:
        print("Writing to STDOUT currently disabled due to large datasets")
        #print(data)
        #print(json.dumps(data, **json_format))
    else:
        with open(path, 'w') as f:
            f.write(data)


def _is_calibration_data(data):
    return "Frame" in data


def _get_clusters_from_file(file_name):
    with open(file_name) as f:
        contents = f.read()
    return _retrieve_clusters(contents)

def _retrieve_clusters(data):
    """Retrieve clusters from frame string"""

    def retrieve_from_standard_data(frame):
        """Retrieve the clusters from a standard data file"""
        hits = deque()
        cluster_matcher = re.compile("(\d+)\s+(\d+)\s+(\d+)")
        for hit in frame.splitlines():
            x, y, c = map(int, cluster_matcher.search(hit).groups())
            hits.append((x, y, c))
        return list(hits)

    def retrieve_from_calibration(frames):
        """Retrieve the clusters from a calibration file"""
        clusters = [[]] * len(frames)
        cluster_matcher = re.compile("(\[(?:\d+, )+\d+\])")
        for i, frame in enumerate(frames):
            frame = frame.splitlines()
            _safe_remove(frame, '')
            for cluster in frame:
                clusters[i].append(
                        [json.loads(x) for x in cluster_matcher.findall(cluster)])
        return clusters

    if _is_calibration_data(data):
        frames = re.split("Frame.*\n", data)
        _safe_remove(frames, '')
        clusters = retrieve_from_calibration(frames)
    else:
        clusters = retrieve_from_standard_data(data)

    return clusters


#### COMMAND-LINE ####

def _setup_parser(usage=None):
    if usage is None:
        parser = OptionParser()
    else:
        parser = OptionParser(usage)

    parser.add_option("-f", "--input-file", dest="input_file",
                      help="File to read cluster data from", metavar="FILE")
    parser.add_option("-o", "--output-file", dest="output_file",
                      help="File to write output to, if not supplied will write to STDOUT",
                      default=None, metavar="FILE")
    parser.add_option("-v", "--verbose", dest="verbose",
                      help="Print status messages to STDOUT", default=False,
                      action="store_true")
    parser.add_option("-i", "--info", dest="info",
                      help="Print additional information about process",
                      default=False, action="store_true")
    parser.add_option("--no-log", dest="log", action="store_false", default=False,
                      help="Don't write to a log file")
    parser.add_option("--log", dest="log_level", default="ERROR",
                      help="Set the logging level")
    parser.add_option("--log-file", dest="log_file", default="cluster_parser.log",
                      help="Specify the file to send log messages to")
    return parser


def _safe_remove(ls, c):
    if ls.count(c):
        ls.remove(c)


def _main(args=sys.argv[1:]):
    parser = _setup_parser()
    (options, args) = parser.parse_args(args)

    if len(args) != 1:
        print("wrong number of arguments: {}".format(len(args)))
        sys.exit(2)
    else:
        options.input_file = args[0]

    def set_logger():

        time_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        log_level = getattr(logging, options.log_level.upper(), None)
        if not isinstance(log_level, int):
            raise ValueError("Invalid log level: {}".format(options.log_level))
        logging.basicConfig(level=log_level, filename=options.log_file, format=time_format)

        logger = logging.getLogger('cluster_parser')
        logger.setLevel(log_level)

        stream_level = getattr(
            logging,
            "DEBUG" if options.verbose else ("INFO" if options.info else "ERROR"),
            None)
        log_stdout = logging.StreamHandler()
        log_stdout.setLevel(stream_level)
        logger.addHandler(log_stdout)
        return logger

    logger = set_logger()
    logger.setLevel(logging.DEBUG)  # This appears to fix logging?

    logger.debug("Retrieving clusters...")
    clusters = _get_clusters_from_file(options.input_file)

    logger.info("Found {} frames".format(len(clusters)))
    if options.info:
        for i in range(len(clusters)):
            logger.info("Frame {}:".format(i + 1))
            logger.info("Clusters found: {}".format(len(clusters[i])))

    logger.debug("Converting data to JSON format...")
    output_data = _gen_output_data(clusters)
    logger.debug("Conversion complete")

    if options.output_file:
        logger.debug("Writing to {}".format(options.output_file))
    else:
        logger.debug("Writing to stdout...")

    _write_data(output_data, options.output_file)

    if options.output_file:
        expected = len(output_data.splitlines())
        #logger.debug("Expected to write {} lines to {}".format(
        #    expected, options.output_file))
        with open(options.output_file) as f:
            actual = len(f.readlines())
            if expected == actual:
                logger.debug("Okay, wrote {} lines".format(expected))
            else:
                logger.warning("Expected to write {} lines but could only find {}, something may have gone wrong.".format(
                    expected, actual))
            logger.debug("{}: Wrote {} lines".format(
                "Okay" if expected == actual else "Line mismatch", actual))

if __name__ == '__main__':
    _main()
