#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

from analysis import plotter


class TestFrameGraphing(unittest.TestCase):

    """Tests for graph output from the Graph Plotter"""

    def setUp(self):
        self.xyz = [(1, 2, 3), (4, 5, 6), (7, 8, 9)]
        self.xs = [1, 4, 7]
        self.ys = [2, 5, 8]
        self.zs = [3, 6, 9]
        self.plotter = plotter.GraphPlotter()
        self.fig, self.ax = self.plotter._generate_basic_figure()
        self.heatmap_data = self.plotter._generate_with_coordinates(self.xs, self.ys, self.zs)

    def tearDown(self):
        pass

    def test_inserts_elements_at_correct_indices(self):
        arr_vals = [self.heatmap_data[x, y] for (x, y) in zip(self.xs, self.ys)]
        self.assertEqual(self.zs, arr_vals)

    def test_basic_figure_correct_labels(self):
        self.assertEqual("Y coordinates", self.ax.get_ylabel())
        self.assertEqual("X coordinates", self.ax.get_xlabel())

    def test_basic_figure_correct_limits(self):
        expected = (0, 255)
        self.assertEqual(expected, self.ax.get_ylim())
        self.assertEqual(expected, self.ax.get_xlim())

    @unittest.skip
    def test_basic_heatmap_correct_data(self):
        heatmap = self.plotter._plot_heatmap(self.heatmap_data)
        self.fail("Need to implement test - Read below comment")
        # Retrieve the datapoints from the generated heatmap
        # and compare against the known points of the prevously
        # generated numpy array
        #self.assertEqual(self.heatmap_data,

