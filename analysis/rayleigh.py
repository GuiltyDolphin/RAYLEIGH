#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# rayleigh.py

import argparse
import os
import sys

import frame_parser
import plotter


class RayleighApp():
    def __init__(self):
        frame_app = frame_parser.AppFrameParser()
        plot_app = plotter.AppGraphPlotter()

        self._parser = argparse.ArgumentParser(
            description="Perform operations on framedata from TimePix chips",
            prog='rayleigh')

        self._parser.add_argument(
            '--version',
            action='version',
            version='0.1.0')

        subparsers = self._parser.add_subparsers(
            title="commands")

        frame_parser_ = frame_parser.FrameParser()

        def run_parser_frame(args):
            fname = args.file
            outname = args.output_file
            out_file = os.path.realpath(outname) if outname else None
            file_name = os.path.realpath(fname)
            if not os.path.exists(file_name):
                print("No such file or directory: {}".format(fname))
                sys.exit(1)
            frame_parser_._detect_input_and_write(file_name, out_file)

        parser_frame = subparsers.add_parser(
            'frame',
            help="Frame parser for converting frame files to json")
        parser_frame.set_defaults(func=run_parser_frame)

        parser_frame.add_argument(
            "file",
            help="File or directory to be converted",
            default=None)

        parser_frame.add_argument(
            "-o", "--output-file", dest="output_file",
            help="File to write output to",
            default=None, metavar="FILE")

        parser_plot = subparsers.add_parser(
            'plot',
            help="Plot json representations of frames")
        parser_plot.set_defaults(func=plot_app._run_with_args)

        parser_help = subparsers.add_parser(
            'help',
            help="Display help for a command")

        parser_help.add_argument(
            'command',
            help="Command to show help for",
            choices=['plot', 'help', 'frame'])

    def _run(self, args):
        args_ = self._parser.parse_args(args)
        args_.func(args_)


if __name__ == '__main__':
    app = RayleighApp()
    app._run(sys.argv[1:])
