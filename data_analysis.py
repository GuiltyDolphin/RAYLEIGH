#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# data_analysis.py

import re
import json
import sys
import getopt
from optparse import OptionParser

cluster_matcher = re.compile("(\[(?:\d+, )+\d+\])")


def output_data(data, path=None):
    """Send a JSON representation of the data to an output stream"""
    if path is None:
        print(json.dumps(data))
    else:
        json.dump(data, path)


def setup_parser():
    parser = OptionParser()
    parser.add_option("-i", "--input-file", dest="input_file",
                      help="File to read cluster data from", metavar="FILE")
    parser.add_option("-o", "--output-file", dest="output_file",
                      help="File to write output to, if not supplied will write to STDOUT",
                      default=None, metavar="FILE")
    parser.add_option("-v", "--verbose", dest="verbose",
                      help="Print status messages to STDOUT", default=False,
                      action="store_true")
    return parser


def parse_options(argv):
    """Parse command-line options for script"""

    options = {
        'input_file=': None,
        'output_file=': None,
        'verbose': False
        }

    short_options = "hvi:o:"
    long_options = [x.replace('_', '-') for x in options.keys()]
    other_options = ["help"]
    help_msg = "data_analysis [{}]".format(short_options)

    try:
        opts, args = getopt.getopt(
            argv, short_options, long_options.extend(other_options))
    except getopt.GetoptError as e:
        print("Unknown option: {}".format(e.opt))
        print("Usage: {}".format(help_msg))
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(help_msg)
            sys.exit()
        elif opt in ("-i", "--input-file"):
            options['input_file='] = arg
        elif opt in ("-o", "--output-file"):
            options['output_file='] = arg
        elif opt in ("-v", "--verbose"):
            options['verbose'] = True
    return options

def _safe_remove(ls, c):
    if ls.count(c):
        ls.remove(c)


def retrieve_clusters(file_name):
    """Retrieve clusters from frame file"""
    with open(file_name) as f:
        contents = f.read()

    frames = re.split("Frame.*\n", contents)
    _safe_remove(frames, '')
    clusters = [[]] * len(frames)

    for i, frame in enumerate(frames):
        frame = frame.splitlines()
        _safe_remove(frame, '')
        for cluster in frame:
            clusters[i].append(
                    [eval(x) for x in cluster_matcher.findall(cluster)])
    return clusters


def main(options):
    verbose = options['verbose']
    if verbose:
        print("Retrieving clusters...")
    clusters = retrieve_clusters(options['input_file='])

    if verbose:
        print("Found {} frames".format(len(clusters)))
        for i in range(len(clusters)):
            print("Frame {}:".format(i + 1))
            print("Clusters found: {}".format(len(clusters[i])))
    output_data(clusters, options['output_file='])


if __name__ == '__main__':
    main(parse_options(sys.argv[1:]))
