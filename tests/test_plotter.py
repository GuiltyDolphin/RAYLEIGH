#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import tempfile
import os
import shutil
import json

import matplotlib

from analysis import plotter


class TestFrameGraphing(unittest.TestCase):

    """Tests for graph output from the Graph Plotter"""

    def setUp(self):
        self.xyz = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        self.xs = [1, 4, 7]
        self.ys = [2, 5, 8]
        self.zs = [3, 6, 9]
        self.plotter = plotter.GraphPlotter()
        self.fig, self.ax = self.plotter._generate_basic_figure()
        self.heatmap_data = self.plotter._generate_with_coordinates(self.xyz)

        self.dir = tempfile.mkdtemp()
        self.in_file_frame = tempfile.NamedTemporaryFile(delete=False, dir=self.dir)
        with open(self.in_file_frame.name, 'w') as f:
            f.write(json.dumps(self.xyz))

        def get_new_file_name(fname):
            base = os.path.basename(fname)
            new_name = os.path.splitext(base)[0] + ".png"
            return self.dir + "/plots/" + new_name
        self.out_name = get_new_file_name(self.in_file_frame.name)

    def tearDown(self):
        os.remove(self.in_file_frame.name)
        shutil.rmtree(self.dir)

    def test_inserts_elements_at_correct_indices(self):
        arr_vals = [self.heatmap_data[x, y] for (x, y) in zip(self.xs, self.ys)]
        self.assertEqual(self.zs, arr_vals)

    def test_basic_figure_correct_labels(self):
        self.assertEqual("Y coordinate", self.ax.get_ylabel())
        self.assertEqual("X coordinate", self.ax.get_xlabel())

    def test_basic_figure_correct_limits(self):
        expected = (0, 255)
        self.assertEqual(expected, self.ax.get_ylim())
        self.assertEqual(expected, self.ax.get_xlim())

    def test_basic_figure_correct_aspect(self):
        self.assertEqual('equal', self.ax.get_aspect())

    @unittest.skip
    def test_basic_heatmap_correct_data(self):
        heatmap = self.plotter._plot_heatmap(self.heatmap_data)
        self.fail("Need to implement test - Read below comment")
        # Retrieve the datapoints from the generated heatmap
        # and compare against the known points of the prevously
        # generated numpy array
        #self.assertEqual(self.heatmap_data,

    def test_can_write_output_file_to_directory(self):
        self.plotter._write_heatmap_from_file(self.in_file_frame.name)
        expected_contents = [os.path.basename(self.out_name)]
        actual = os.listdir(self.dir + "/plots")
        self.assertCountEqual(expected_contents, actual)
