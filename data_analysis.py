#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# data_analysis.py

import re
import json
import sys
import getopt
from optparse import OptionParser

_cluster_matcher = re.compile("(\[(?:\d+, )+\d+\])")


#### ANALYSIS ####

def _output_data(data, path=None):
    """Send a JSON representation of the data to an output stream"""
    json_format = {
            'indent': 2
            }

    if path is None:
        print("Writing to STDOUT currently disabled due to large datasets")
        #print(json.dumps(data, **json_format))
    else:
        with open(path, 'w') as f:
            json.dump(data, f, **json_format)


def _retrieve_clusters(file_name):
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
                    [eval(x) for x in _cluster_matcher.findall(cluster)])
    return clusters


#### COMMAND-LINE ####

def _setup_parser(usage=None):
    if usage is None:
        parser = OptionParser()
    else:
        parser = OptionParser(usage)

    parser.add_option("-i", "--input-file", dest="input_file",
                      help="File to read cluster data from", metavar="FILE")
    parser.add_option("-o", "--output-file", dest="output_file",
                      help="File to write output to, if not supplied will write to STDOUT",
                      default=None, metavar="FILE")
    parser.add_option("-v", "--verbose", dest="verbose",
                      help="Print status messages to STDOUT", default=False,
                      action="store_true")
    return parser


def _parse_options(argv):
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


def _main(args=sys.argv[1:]):
    parser = _setup_parser()
    (options, args) = parser.parse_args(args)
    if len(args) != 1:
        print("wrong number of arguments: {}".format(len(args)))
        sys.exit(2)
    else:
        options.input_file = args[0]
    verbose = options.verbose
    if verbose:
        print("Retrieving clusters...")
    clusters = _retrieve_clusters(options.input_file)

    if verbose:
        print("Found {} frames".format(len(clusters)))
        for i in range(len(clusters)):
            print("Frame {}:".format(i + 1))
            print("Clusters found: {}".format(len(clusters[i])))
    _output_data(clusters, options.output_file)


if __name__ == '__main__':
    _main()
