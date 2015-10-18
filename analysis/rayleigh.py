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
            fname = args.frame
            if not os.path.dirname(fname):
                fname = "{}/{}".format(os.getcwd(), fname)
            frame_parser_._detect_input_and_write(fname)

        parser_frame = subparsers.add_parser(
            'frame',
            help="Frame parser for converting frame files to json")
        parser_frame.set_defaults(func=run_parser_frame)

        parser_frame.add_argument(
            "file",
            help="File to be converted",
            default=None)

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


if __name__ == '__main__':
    app = RayleighApp()
    app._run(sys.argv[1:])
