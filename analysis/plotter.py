#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from matplotlib import pyplot as plt

import numpy as np
import json
import os


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
        fig = plt.Figure()
        ax = fig.add_axes([0, 0, 256, 256])
        ax.set_ylabel("Y coordinates")
        ax.set_xlabel("X coordinates")
        ax.set_ylim((0, 255))
        ax.set_xlim((0, 255))
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
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        heatmap = ax.pcolormesh(data, cmap=plt.cm.Reds)
        ax.xaxis.set_label("X coordinate")
        ax.yaxis.set_label("Y coordinate")
        return fig, ax, heatmap

    def _gen_heatmap_from_file(self, file_name):
        with open(file_name) as f:
            frame = json.load(f)
        data = self._generate_with_coordinates(frame)
        return self._gen_heatmap(data)

    def _write_heatmap_from_file(self, input_file, output=None):
        fig, _, _ = self._gen_heatmap_from_file(input_file)
        print(os.listdir(os.path.dirname(input_file)))
        os.mkdir(os.path.dirname(input_file) + "/plots")
        fig.savefig(output or "{}/plots/{}.png".format(
            os.path.dirname(input_file), os.path.basename(input_file)))
        print(os.listdir(os.path.dirname(input_file) + "/plots"))
