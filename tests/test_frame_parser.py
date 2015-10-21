#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import tempfile
import os
import json
import shutil

import analysis.frame_parser as fp


# Helper functions
def get_base_names(files):
    return [os.path.basename(f.name) for f in files]


def get_expected_names(files):
    names = get_base_names(files)
    return [os.path.splitext(n)[0] + ".json" for n in names]


class TestFrameParser(unittest.TestCase):

    """Tests for the frame_parser module"""

    def setUp(self):
        self.frame_data = """77 56  28
        7   57  61
        7   58  74
        20  84  52
        21  84  4
        20  85  23
        21  85  60
        21  86  41"""

        self.in_file_frame = tempfile.NamedTemporaryFile(delete=False)
        self.out_file = tempfile.NamedTemporaryFile(delete=False)
        with open(self.in_file_frame.name, 'w') as f:
            f.write(self.frame_data)

    def tearDown(self):
        os.remove(self.out_file.name)
        os.remove(self.in_file_frame.name)

    def get_hits(self, text=None):
        """Helper - Get the hits from frame"""
        return fp._retrieve_frame(text or self.cluster_text)

    def test_can_correctly_retrieve_data_from_file(self):
        """Data can be retrieved from standard data files"""
        expected = self.get_hits(self.frame_data)
        actual = fp._get_frame_from_file(self.in_file_frame.name)
        self.assertEqual(expected, actual)

    def test_can_convert_frame_data_to_json(self):
        """Standard input data can be converted to JSON"""
        data = self.get_hits(self.frame_data)
        expected_json_data = json.loads(json.dumps(data))
        actual_json_data = json.loads(fp._gen_output_data(data))
        self.assertEqual(expected_json_data, actual_json_data)

    def test_output_frame_data_written_correctly_to_file(self):
        """Standard data can be written to a file"""
        clusters = self.get_hits(self.frame_data)
        data = fp._gen_output_data(clusters)
        expected = json.loads(data)
        fp._write_data(data, self.out_file.name)
        with open(self.out_file.name) as f:
            self.assertEqual(expected, json.loads(f.read()))


class TestDirectoryParsing(unittest.TestCase):
    """Tests regarding multiple files for the FrameParser"""

    def setUp(self):
        self.text1 = """1 2 3
        4 5 6
        7 8 9"""
        self.text2 = """10 11 12
        13 14 15
        16 17 18"""
        self.dir = tempfile.mkdtemp()
        file_options = {'delete': False, 'dir': self.dir}
        self.in_file1 = tempfile.NamedTemporaryFile(
            suffix="d00.txt", **file_options)
        self.in_file2 = tempfile.NamedTemporaryFile(
            suffix="d01.txt", **file_options)
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

    def test_creates_suitable_directory_structure(self):
        """Creates a suitable directory structure"""
        fp._write_output_directory(self.dir)
        name1, name2, name3 = get_base_names(
            [self.in_file1, self.in_file2, self.dsc_file])
        exp1, exp2 = get_expected_names([self.in_file1, self.in_file2])
        actual = os.listdir(self.dir)
        expected_contents = [name1, name2, name3, "output"]
        self.assertCountEqual(expected_contents, actual)

    def get_expected_data(self):
        """Helper - Data expected to be (retrievable) written to frames"""
        expect1 = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        expect2 = [[10, 11, 12], [13, 14, 15], [16, 17, 18]]
        return [expect1, expect2]

    def test_creates_files_with_correct_contents(self):
        """The output files have the correct contents"""
        fp._write_output_directory(self.dir)
        expect1, expect2 = self.get_expected_data()
        with open(self.out_name1) as f:
            actual1 = json.loads(f.read())
        with open(self.out_name2) as f:
            actual2 = json.loads(f.read())
        self.assertEqual(expect1, actual1)
        self.assertEqual(expect2, actual2)

    def test_only_converts_files_with_specified_extension(self):
        """Only the files with the given extension are parsed"""
        exp1, exp2 = get_expected_names([self.in_file1, self.in_file2])
        fp._write_output_directory(self.dir)
        self.assertCountEqual(
            [exp1, exp2, "frames.json"], os.listdir(self.dir + "/output"))

    def replace_extension(self, file, ext):
        return os.path.splitext(file)[0] + ext

    def test_allows_conversion_file_extension_to_be_specified(self):
        """Output file extension can be specified"""
        ext = ".sometext"
        new1 = self.replace_extension(self.in_file1.name, ext)
        new2 = self.replace_extension(self.in_file2.name, ext)
        os.rename(self.in_file1.name, new1)
        os.rename(self.in_file2.name, new2)
        exp1 = os.path.basename(self.replace_extension(new1, ".json"))
        exp2 = os.path.basename(self.replace_extension(new2, ".json"))
        fp._write_output_directory(self.dir, ext)
        self.assertCountEqual(
            [exp1, exp2, "frames.json"], os.listdir(self.dir + "/output"))
        os.rename(new1, self.in_file1.name)
        os.rename(new2, self.in_file2.name)

    def test_total_frame_output_has_correct_data(self):
        """The frames file contains the cumulative frame data"""
        expected = self.get_expected_data()
        fp._write_output_directory(self.dir)
        with open(self.dir + "/output/frames.json") as f:
            self.assertEqual(expected, json.loads(f.read()))

    def test_can_detect_and_write_to_output_dir(self):
        """Can detect and write to directories"""
        exp1, exp2 = get_expected_names([self.in_file1, self.in_file2])
        fp._detect_input_and_write(self.dir)
        self.assertCountEqual(
            [exp1, exp2, "frames.json"], os.listdir(self.dir + "/output"))
