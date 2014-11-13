#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from matplotlib import pyplot as plt

import numpy as np


class GraphPlotter():
    def _generate_with_coordinates(self, xs, ys, zs, size=(256, 256)):
        """Populate an empty numpy array of size with zs
        elements at xs and ys coordinates"""
        arr = np.zeros(size)
        for x, y, z in zip(xs, ys, zs):
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
