#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from matplotlib import pyplot as plt

import numpy as np
import json
import os
import sys
from optparse import OptionParser


class GraphPlotter():
    def _generate_with_coordinates(self, frame, size=(256, 256)):
        """Populate an empty numpy array of size with zs
        elements at xs and ys coordinates"""
        arr = np.zeros(size)
        for x, y, z in frame:
            arr.itemset((x, y), z)
        return arr

    def _generate_basic_figure(self):
        """Create a basic pre-configured figure for use with frame heatmaps"""
        fig, ax = plt.subplots()
        ax.set_ylabel("Y coordinate")
        ax.set_xlabel("X coordinate")
        ax.set_ylim((0, 255))
        ax.set_xlim((0, 255))
        ax.set_aspect('equal')
        return fig, ax

    def _gen_heatmap(self, data):
        """Generate a heatmap figure

        Parameters
        ----------
        data : (ndarray)
             The data to be plotted on the heatmap

        Returns
        -------
        fig : (Figure)
            The figure object
        ax  : (Axes)
            The axes object
        heatmap : (Todo: Unknown)
            The actual heatmap object
        """
        fig, ax = self._generate_basic_figure()
        heatmap = ax.pcolormesh(data, cmap=plt.cm.Reds)
        return fig, ax, heatmap

    def _gen_heatmap_from_file(self, file_name):
        with open(file_name) as f:
            frame = json.load(f)
        data = self._generate_with_coordinates(frame)
        return self._gen_heatmap(data)

    def _write_heatmap_from_file(self, input_file, output=None):
        fig, ax, heatmap = self._gen_heatmap_from_file(input_file)
        os.mkdir(os.path.dirname(input_file) + "/plots")
        self._write_heatmap(output or "{}/plots/{}.png".format(
            os.path.dirname(input_file), os.path.basename(input_file)),
            (fig, ax, heatmap))

    def _write_heatmap(self, output_path, heatmap):
        fig, _, _ = heatmap
        fig.savefig(output_path)


class AppGraphPlotter():
    def __init__(self):
        self._option_parser = OptionParser()
        self._plotter = GraphPlotter()

        self._option_parser.add_option('-w', '--write',
            help="Write the graph to file",
            default=False, action='store_true')

        self._option_parser.add_option('--no-view',
            help="Do not view the graph - only useful in conjunction with other flags",
            default=False, action='store_true')

        self._option_parser.add_option('-f', '--file-name',
            help="Provide the file name to be read explicitly",
            default=None)

    def _run_with_args(self, args):
        options, args = self._option_parser.parse_args(args)
        file_name = options.file_name or args[0]

        # Assume heatmap for the moment
        figmap = self._plotter._gen_heatmap_from_file(file_name)

        if not options.no_view:
            figmap[0].show()

        if options.write:
            self._plotter._write_heatmap_from_file(file_name)


if __name__ == '__main__':
    app = AppGraphPlotter()
    app._run_with_args(sys.argv[1:])
