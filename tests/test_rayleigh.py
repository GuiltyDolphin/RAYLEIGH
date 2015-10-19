#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# test_rayleigh.py

import unittest
import tempfile
import json
import os
import shutil

from analysis import plotter
from analysis import rayleigh
from analysis import frame_parser


def get_base_names(files):
    return [os.path.basename(f.name) for f in files]


def get_expected_names(files):
    names = get_base_names(files)
    return [os.path.splitext(n)[0] + ".json" for n in names]


class TestInterfacePlotter(unittest.TestCase):

    """Test the user interface for the plotting functionality"""

    def setUp(self):
        self.xyz = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        self.xs = [1, 4, 7]
        self.ys = [2, 5, 8]
        self.zs = [3, 6, 9]

        self.interface = rayleigh.RayleighApp()
        self.plotparser = self.interface._parser_plot
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

    # def option_helper(self, option_name, option_string, default, help):
    #     option = self.optparser.get_option(option_name)
    #     self.assertEqual(option_string, option.get_opt_string())
    #     self.assertEqual(default, option.default)
    #     self.assertEqual(help, option.help)

    def test_provides_write_option(self):
        """Provides a write option"""
        self.assertEqual(False, self.plotparser.get_default('write'))
        # self.option_helper(
        #     '-w', '--write',
        #     False, 'Write the graph to file')

    def test_sets_default_no_view_option(self):
        """Provides a --no-view option"""
        self.assertEqual(False, self.plotparser.get_default('no_view'))

    ## def test_provides_no_view_option(self):
    ##     """Provides a --no-view option"""
        # self.option_helper(
        #     '--no-view', '--no-view',
        #     False, 'Do not view the graph - only useful in conjunction with other flags')

    def test_provides_explicit_file_name_option(self):
        """Provides the option to specify filename explicitly"""
        self.assertEqual(None, self.plotparser.get_default('file_names'))
        # self.option_helper(
        #     '-f', '--file-name',
        #     None, 'Provide the file name to be read explicitly')

    def test_provides_outliers_option(self):
        """Provides the option to specify the value to be used for finding outliers"""
        self.assertEqual(None, self.plotparser.get_default('outliers'))
        # self.option_helper(
        #     '--outliers', '--outliers',
        #     None, 'Provide the value to be used when finding outliers')

    def test_provides_multi_plot_option(self):
        """Provides the option to specify multiple frames to be plotted on a single figure"""
        self.assertEqual(False, self.plotparser.get_default('single_figure'))
        # self.option_helper(
        #     '--single-figure', '--single-figure',
        #     True, 'Plot all the frames on a single figure')

    def test_accepts_single_files_and_writes(self):
        """The App can save the figure to a file when the write option is passed with a file name"""
        self.interface._run(['plot'] + self.test_args + [self.in_file_frame.name, '-w'])
        expected_contents = [os.path.basename(self.out_name)]
        actual = os.listdir(self.dir + "/plots")
        self.assertCountEqual(expected_contents, actual)


class TestInterfaceFrame(unittest.TestCase):

    """Test the users' interface to the frame_parser module"""

    def setUp(self):
        self.interface = rayleigh.RayleighApp()
        self.optparser = self.interface._parser_frame
        self.parser = self.interface._frame_parser
        self.test_args = []

        self.text1 = """1 2 3
        4 5 6
        7 8 9"""
        self.text2 = """10 11 12
        13 14 15
        16 17 18"""
        self.dir = tempfile.mkdtemp()
        file_options = {'delete': False, 'dir': self.dir}
        self.in_file1 = tempfile.NamedTemporaryFile(suffix="d00.txt", **file_options)
        self.in_file2 = tempfile.NamedTemporaryFile(suffix="d01.txt", **file_options)
        file_options.update(suffix='.txt.dsc')
        self.dsc_file = tempfile.NamedTemporaryFile(**file_options)

        with open(self.in_file1.name, 'w') as f:
            f.write(self.text1)
        with open(self.in_file2.name, 'w') as f:
            f.write(self.text2)

        def get_new_file_name(fname):
            base = os.path.basename(fname)
            new_name = os.path.splitext(base)[0] + ".json"
            return self.dir + "/output/" + new_name

        self.out_name1 = get_new_file_name(self.in_file1.name)
        self.out_name2 = get_new_file_name(self.in_file2.name)

    def tearDown(self):
        os.remove(self.in_file1.name)
        os.remove(self.in_file2.name)
        os.remove(self.dsc_file.name)
        shutil.rmtree(self.dir)

    def test_no_default_input_file(self):
        """There is no default input file"""
        self.assertEqual(None, self.optparser.get_default('file_name'))

    def test_no_default_output_file(self):
        """There is no default output file"""
        self.assertEqual(None, self.optparser.get_default('output_file'))

    def test_can_parse_directory(self):
        """Can parse user file input and write"""
        exp1, exp2 = get_expected_names([self.in_file1, self.in_file2])
        self.interface._run(['frame'] + self.test_args + [self.dir])
        self.assertCountEqual([exp1, exp2, "frames.json"], os.listdir(self.dir + "/output"))

