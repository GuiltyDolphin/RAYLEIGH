#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from matplotlib import pyplot as plt

import numpy as np
import numpy.ma as ma
import json
import os
import sys
from optparse import OptionParser


class GraphPlotter():
    def _generate_with_coordinates(self, frame, outliers=None):
        """Generate a numpy array to be used for coordinate plotting.

        Parameters
        ----------
        frame : (list-like (x, y, z))
             The (x, y, z) values to be used in the array
        outliers : (number)
        Default : None
             The value to be used when calculating outliers.
             If the value is None then outliers will not be calculated.

        Returns
        -------
        arr : (ndarray)
            The generated numpy array
        """
        arr = np.vstack(frame)
        xs, ys, zs  = arr.transpose()
        zeros = np.zeros((256, 256))
        zeros[(xs, ys)] = zs
        zmask = ma.masked_array(zeros, mask=zeros == 0)

        # Use Chauvenet's criterion to find the outliers
        if outliers is not None:
            d_max = np.abs(zmask - zmask.mean()) / zmask.std()
            return ma.masked_array(zmask, mask=d_max>=outliers)
        return zmask

    def _generate_basic_figure(self):
        """Create a basic pre-configured figure for use with frame heatmaps

        Parameters
        ----------
        None

        Returns
        -------
        fig : (Figure)
            The figure on which the axes lie
        ax  : (Axes)
            The axes associated with the plot
        """
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

    def _gen_heatmap_from_file(self, file_name, **kwargs):
        """Generate heatmap figure from a file

        Parameters
        ----------
        file_name : (string)
             The name of the file to be read

        Returns
        -------
        fig : (Figure)
            The figure object
        ax  : (Axes)
            The axes object
        heatmap : (Todo: Unknown)
            The actual heatmap object
        """
        def fltint(x):
            return int(float(x))
        with open(file_name) as f:
            frame = json.load(f, parse_float=fltint)
        data = self._generate_with_coordinates(frame, **kwargs)
        return self._gen_heatmap(data)

    def _write_heatmap_from_file(self, input_file, output=None):
        fig, ax, heatmap = self._gen_heatmap_from_file(input_file)
        dname = os.path.dirname(input_file) + "/plots"
        if not os.path.exists(dname):
            os.mkdir(dname)
        self._write_heatmap(output or "{}/plots/{}.png".format(
            os.path.dirname(input_file), os.path.basename(input_file)),
            (fig, ax, heatmap))

    def _write_heatmap(self, output_path, heatmap):
        """Write the heatmap to the specified path

        Parameters
        ----------
        output_path : (string)
             The path for the heatmap to be saved to
        heatmap : (Figure, Axes, heatmap)
             The heatmap to be used for writing

        Returns
        -------
        This function does not return
        It is only useful for its side effects.
        """
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

        self._option_parser.add_option('--outliers',
                help="Provide the value to be used when finding outliers",
                default=None, type='float')

    def _run_with_args(self, args):
        """Carry out the sequence of IO actions that define the graph plotter.

        Parameters
        ----------
        args : (list)
             The arguments to be used for the run

        Returns
        -------
        Nothing, this function is only useful for its side effects.
        """
        options, args = self._option_parser.parse_args(args)
        file_name = options.file_name or args[0]

        if not os.path.dirname(file_name):
            file_name = "{}/{}".format(os.getcwd(), file_name)
        # Assume heatmap for the moment
        figmap = self._plotter._gen_heatmap_from_file(file_name, outliers=options.outliers)

        if not options.no_view:
            plt.show()
            #figmap[0].show()

        if options.write:
            self._plotter._write_heatmap_from_file(file_name)


if __name__ == '__main__':
    app = AppGraphPlotter()
    app._run_with_args(sys.argv[1:])
