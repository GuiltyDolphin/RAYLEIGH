#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from matplotlib import pyplot as plt

import numpy as np
import numpy.ma as ma

import json
import math
import os


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
        xs, ys, zs = arr.transpose()
        zeros = np.zeros((256, 256))
        zeros[(xs, ys)] = zs
        zmask = ma.masked_array(zeros, mask=zeros == 0)

        # Use Chauvenet's criterion to find the outliers
        if outliers is not None:
            d_max = np.abs(zmask - zmask.mean()) / zmask.std()
            return ma.masked_array(zmask, mask=d_max >= outliers)
        return zmask

    def _generate_basic_figure(self, num=1):
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
        def get_shape(num):
            x = round(math.sqrt(num))
            y = math.ceil(num / x)
            return (x, y)

        rows, cols = get_shape(num)
        if cols > 1 and rows == 1:
            rows = 2
        fig, ax = plt.subplots(rows, cols)

        def set_limits_aspect(axis):
            axis.set_ylim((0, 255))
            axis.set_xlim((0, 255))
            axis.set_aspect('equal')

        if type(ax) == np.ndarray:
            base_axis = ax[0][0]
            for axis in ax.flatten():
                set_limits_aspect(axis)
            fig.subplots_adjust(hspace=0.45, wspace=0.45)
            num_to_turn_off = (rows * cols) - num
            for x in range(1, num_to_turn_off+1):
                ax[-1][-x].axis('off')
        else:
            base_axis = ax

        base_axis.set_ylabel("Y coordinate")
        base_axis.set_xlabel("X coordinate")
        set_limits_aspect(base_axis)
        return fig, ax

    def _gen_multi_plots(self, frames):
        fig, axes = self._generate_basic_figure(len(frames))
        heatmaps = []
        x, y = axes.shape
        c = 0
        for i in range(x):
            for j in range(y):
                ax = axes[i][j]
                if ax.axison:
                    heatmaps.append(
                        ax.pcolormesh(frames[c], cmap='Reds'))
                    c += 1
        return fig, axes, heatmaps

    def _gen_multi_from_files(self, file_names, outliers=None):
        data = []

        def fltint(x):
            return int(float(x))

        for file_name in file_names:
            with open(file_name) as f:
                loaded_data = json.load(f, parse_float=fltint)
                data.append(
                    self._generate_with_coordinates(
                        loaded_data, outliers=outliers))
        return np.array(data)

    def _read_and_generate_heatmaps(self, file_names, outliers=None):
        """Read multiple files and generate subplots

        Parameters
        ----------
        file_names : (list (string))
             The paths of the files to be read
        outliers   : (float)
             The value to be used in outlier calculations

        Returns
        -------
        (Figure, [Axes], [heatmap])
        The figure and associated subplot axes, along with
        the list of heatmaps generated.
        """
        frames = self._gen_multi_from_files(file_names, outliers=outliers)
        return self._gen_multi_plots(frames)

    def _write_multi(self, files, output=None):
        fig, ax, heatmap = self._read_and_generate_heatmaps(files)
        dname = os.path.dirname(files[0]) + "/plots"
        if not os.path.exists(dname):
            os.mkdir(dname)
        self._write_heatmap(output or "{}/plots/{}.png".format(
            os.path.dirname(files[0]), os.path.basename(files[0])),
            (fig, ax, heatmap))

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
        """Read a file and write a heatmap image

        Parameters
        ----------
        input_file : (string)
             The name of the file to be read
        output     : (string)
             The path to write the heatmap to - will save to a plots folder
             if not specified

        Returns
        -------
        Nothing - Used for side effects
        """
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
