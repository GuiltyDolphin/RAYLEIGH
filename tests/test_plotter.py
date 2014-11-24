#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import tempfile
import os
import shutil
import json

import matplotlib
import numpy as np

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
        """The coordinate array converter correctly places z values"""
        arr_vals = list(self.heatmap_data.take(2, axis=1))
        self.assertEqual(self.zs, arr_vals)

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
        outliers = 1
        frame = np.random.randint(0, 255, (20, 3))
        vals = frame.take(2, axis=1)
        d = np.abs(vals - np.median(vals))
        meds = np.median(d)
        s = d / meds if meds else 0
        new_frame = frame[s<outliers]
        arr = self.plotter._generate_with_coordinates(frame, outliers=outliers)
        np.testing.assert_array_equal(new_frame, arr)



class TestUserInteraction(unittest.TestCase):

    """Test the users' interface to the graph module"""

    def setUp(self):
        self.xyz = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        self.xs = [1, 4, 7]
        self.ys = [2, 5, 8]
        self.zs = [3, 6, 9]

        self.interface = plotter.AppGraphPlotter()
        self.optparser = self.interface._option_parser
        self.plotter = self.interface._plotter
        self.test_args = ['--no-view']

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

    def option_helper(self, option_name, option_string, default, help):
        option = self.optparser.get_option(option_name)
        self.assertEqual(option_string, option.get_opt_string())
        self.assertEqual(default, option.default)
        self.assertEqual(help, option.help)

    def test_provides_write_option(self):
        """Provides a write option"""
        self.option_helper(
            '-w', '--write',
            False, 'Write the graph to file')

    def test_provides_no_view_option(self):
        """Provides a --no-view option"""
        self.option_helper(
            '--no-view', '--no-view',
            False, 'Do not view the graph - only useful in conjunction with other flags')

    def test_provides_explicit_file_name_option(self):
        """Provides the option to specify filename explicitly"""
        self.option_helper(
            '-f', '--file-name',
            None, 'Provide the file name to be read explicitly')

    def test_provides_outliers_option(self):
        """Provides the option to specify the value to be used for finding outliers"""
        self.option_helper(
            '--outliers', '--outliers',
            None, 'Provide the value to be used when finding outliers')

    def test_accepts_single_files_and_writes(self):
        """The App can save the figure to a file when the write option is passed with a file name"""
        self.interface._run_with_args(self.test_args + [self.in_file_frame.name, '-w'])
        expected_contents = [os.path.basename(self.out_name)]
        actual = os.listdir(self.dir + "/plots")
        self.assertCountEqual(expected_contents, actual)
