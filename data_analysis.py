#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# data_analysis.py

import re
import json
import sys
import getopt

cluster_matcher = re.compile("(\[(?:\d+, )+\d+\])")


def output_data(data, path=None):
    """Send a JSON representation of the data to an output stream"""
    if path is None:
        print(json.dumps(data))
    else:
        json.dump(data, path)

def parse_options(argv):
    input_file = None
    output_file = None

    try:
        opts, args = getopt.getopt(argv, "hi:o", ["input-file=", "output-file=", "help"])
    except getopt.GetoptError as e:
        print("Unknown option: {}".format(e.opt))
        print("Usage: {}".format(help_msg))
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(help_msg)
            sys.exit()
        elif opt in ("-i", "--input-file"):
            input_file = arg
        elif opt in ("-o", "--output-file"):
            output_file = arg


def retrieve_clusters(file_name):
    """Retrieve clusters from frame file"""
    with open(file_name) as f:
        contents = f.read()

    frames = re.split("Frame.*\n", contents)
    frames.remove('')
    clusters = [[]] * len(frames)

    for i, frame in enumerate(frames):
        frame = frame.splitlines()
        frame.remove('')
        for cluster in frame:
            clusters[i].append(
                    [eval(x) for x in cluster_matcher.findall(cluster)])
