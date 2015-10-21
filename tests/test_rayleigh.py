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
        self.test_args = ['--no-view']

        self.fig, self.ax = plotter._generate_basic_figure()
        self.heatmap_data = plotter._generate_with_coordinates(self.xyz)

        self.dir = tempfile.mkdtemp()
        self.in_file_frame = tempfile.NamedTemporaryFile(
            delete=False, dir=self.dir)
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

    def test_default_write_option(self):
        """Writing will not be performed by default"""
        self.assertEqual(False, self.plotparser.get_default('write'))

    def test_no_view_default(self):
        """By default the plot will be displayed"""
        self.assertEqual(False, self.plotparser.get_default('no_view'))

    def test_no_default_input_file(self):
        """There is no default input file"""
        self.assertEqual(None, self.plotparser.get_default('file_names'))

    def test_no_default_outliers(self):
        """By default there is no outlier boundary"""
        self.assertEqual(None, self.plotparser.get_default('outliers'))

    def test_default_multi_plot_option(self):
        """By default will not plot on single figure"""
        self.assertEqual(False, self.plotparser.get_default('single_figure'))

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

