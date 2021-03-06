#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# rayleigh.py

import argparse
import os
import sys

from matplotlib import pyplot as plt

from analysis import frame_parser as fp
from analysis import plotter

import analysis


class RayleighApp():
    def __init__(self):

        self._parser = argparse.ArgumentParser(
            description="Perform operations on framedata from TimePix chips",
            prog='rayleigh')

        # self._parser.set_defaults(func=no_func)

        self._parser.add_argument(
            '--version',
            action='version',
            version="rayleigh {}".format(analysis.__version__))

        subparsers = self._parser.add_subparsers(
            title="commands")

        def run_parser_frame(args):
            fname = args.file
            outname = args.output_file
            out_file = os.path.realpath(outname) if outname else None
            file_name = os.path.realpath(fname)
            if not os.path.exists(file_name):
                print("No such file or directory: {}".format(fname))
                sys.exit(1)
            fp._detect_input_and_write(file_name, out_file)

        self._parser_frame = subparsers.add_parser(
            'frame',
            help="Frame parser for converting frame files to json")
        self._parser_frame.set_defaults(func=run_parser_frame)

        self._parser_frame.add_argument(
            "file",
            help="File or directory to be converted",
            default=None)

        self._parser_frame.add_argument(
            "-o", "--output-file", dest="output_file",
            help="File to write output to",
            default=None, metavar="FILE")

        def run_parser_plot(args):
            files = args.files

            def check_file(fname):
                full = os.path.realpath(fname)
                if not os.path.exists(full):
                    print("No such file or directory {}".format(fname))
                    sys.exit(1)
                if os.path.isdir(full):
                    print("{} is a directory")
                    sys.exit(1)
                return full
            file_names = list(map(check_file, files))

            if len(file_names) > 1:
                if args.single_figure:
                    plotter._read_and_generate_heatmaps(
                        file_names, outliers=args.outliers)

                if args.write:
                    plotter._write_multi(file_names)
            else:
                file_name = file_names[0]
                # Assume heatmap for the moment
                figmap = plotter._gen_heatmap_from_file(
                    file_name, outliers=args.outliers)

                if args.write:
                    plotter._write_heatmap_from_file(file_name)

            if not args.no_view:
                plt.show()
            else:
                plt.close()

        self._parser_plot = subparsers.add_parser(
            'plot',
            help="Plot json representations of frames")
        self._parser_plot.set_defaults(func=run_parser_plot)

        self._parser_plot.add_argument(
            '-w', '--write',
            help="Write the graph to file",
            default=False, action='store_true')

        self._parser_plot.add_argument(
            '--no-view',
            help=("Do not view the graph - "
                  "only useful in conjunction with other flags"),
            default=False, action='store_true', dest='no_view')

        self._parser_plot.add_argument(
            'files',
            help="Files to be read",
            default=None,
            nargs='*')

        self._parser_plot.add_argument(
            '--outliers',
            help="Provide the value to be used when finding outliers",
            default=None, type=float, metavar='FLOAT')

        self._parser_plot.add_argument(
            '--single-figure',
            help="Plot all the frames on a single figure",
            default=False, action='store_true')

    def _run(self, args):
        args_ = self._parser.parse_args(args)
        try:
            args_.func(args_)
        except AttributeError:
            print(
                "No command specified, "
                + "use 'rayleigh --help' to see a complete list")
            sys.exit(1)


def main():
    app = RayleighApp()
    app._run(sys.argv[1:])

if __name__ == '__main__':
    main()
