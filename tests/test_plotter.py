#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import tempfile
import os
import shutil
import json

import matplotlib
import numpy as np
import numpy.ma as ma

from analysis import plotter


class TestFrameGraphing(unittest.TestCase):

    """Tests for graph output from the Graph Plotter"""

    def setUp(self):
        self.xyz = np.random.random_integers(1, 255, (10, 3))
        self.xs, self.ys, self.zs = self.xyz.transpose()
        self.plotter = plotter.GraphPlotter()
        self.fig, self.ax = self.plotter._generate_basic_figure()
        self.heatmap_data = self.plotter._generate_with_coordinates(self.xyz)

        self.dir = tempfile.mkdtemp()
        self.in_file_frame = tempfile.NamedTemporaryFile(delete=False, dir=self.dir)
        self.in_file_frame2 = tempfile.NamedTemporaryFile(delete=False, dir=self.dir)
        with open(self.in_file_frame.name, 'w') as f:
            f.write(json.dumps(self.xyz.tolist()))
        with open(self.in_file_frame2.name, 'w') as f:
            f.write(json.dumps(self.xyz.tolist()))

        def get_new_file_name(fname):
            base = os.path.basename(fname)
            new_name = os.path.splitext(base)[0] + ".png"
            return self.dir + "/plots/" + new_name
        self.out_name = get_new_file_name(self.in_file_frame.name)
        self.out_name2 = get_new_file_name(self.in_file_frame2.name)

    def tearDown(self):
        os.remove(self.in_file_frame.name)
        os.remove(self.in_file_frame2.name)
        shutil.rmtree(self.dir)

    def test_inserts_elements_at_correct_indices(self):
        """The coordinate array converter correctly places z values"""
        arr_vals = self.heatmap_data.compressed()
        np.testing.assert_array_equal(self.zs.sort(), arr_vals.sort())

    def test_basic_figure_correct_labels(self):
        """The x and y labels are properly configured for the basic figure"""
        self.assertEqual("Y coordinate", self.ax.get_ylabel())
        self.assertEqual("X coordinate", self.ax.get_xlabel())

    def test_basic_figure_correct_limits(self):
        """The x and y limit are properly configured for the basic figure"""
        expected = (0, 255)
        self.assertEqual(expected, self.ax.get_ylim())
        self.assertEqual(expected, self.ax.get_xlim())

    def test_write_to_file_heatmap_provided(self):
        """Can save a figure to the specified path if a heatmap is provided"""
        figmap = self.plotter._gen_heatmap_from_file(self.in_file_frame.name)
        os.mkdir(self.dir + "/plots")
        out_dir = self.dir + "/plots"
        with tempfile.NamedTemporaryFile(dir=self.dir) as f:
            new_name = out_dir + "/{}.png".format(os.path.basename(f.name))
            self.plotter._write_heatmap(new_name, figmap)
            expected_contents = [new_name]
        actual = os.listdir(out_dir)
        self.assertIn(os.path.basename(new_name), os.listdir(out_dir))

    def test_basic_figure_correct_aspect(self):
        """The aspect ratio for the basic figure is correctly configured"""
        self.assertEqual('equal', self.ax.get_aspect())

    def test_can_write_output_file_to_directory(self):
        """The plotter can create and write to a plots directory"""
        self.plotter._write_heatmap_from_file(self.in_file_frame.name)
        expected_contents = [os.path.basename(self.out_name)]
        actual = os.listdir(self.dir + "/plots")
        self.assertCountEqual(expected_contents, actual)

    def test_can_determine_outliers(self):
        """The coordinate array converter can correcly determine outliers given the outlier value"""
        frame = np.random.randint(0, 255, (20, 3))
        vals = frame.take(2, axis=1)
        outliers = 1
        d_max = np.abs(vals - vals.mean()) / vals.std()
        new_frame = ma.masked_array(vals, mask=d_max>=outliers)
        arr = self.plotter._generate_with_coordinates(frame, outliers=outliers)
        np.testing.assert_array_equal(new_frame.compressed().sort(), arr.compressed().sort())

    def test_basic_figure_correct_number_axes(self):
        fig, axes = self.plotter._generate_basic_figure(5)
        self.assertEqual((2, 3), axes.shape)

    def test_basic_figure_hides_correct_axes(self):
        fig, axes = self.plotter._generate_basic_figure(10)
        for x in [(-1, -1), (-1, -2)]:
            self.assertFalse(axes[x].axison)

    def test_can_read_multiple_files(self):
        file_names = [self.in_file_frame.name, self.in_file_frame2.name]
        exp_data = np.array([self.heatmap_data, self.heatmap_data])
        data = self.plotter._gen_multi_from_files(file_names)
        np.testing.assert_array_equal(exp_data, data)
