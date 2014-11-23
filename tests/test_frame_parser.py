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
        self.cluster_text = """
        Frame 1: Frame 1 (1336049775.586539 s, 0.03 s) \n
        [6, 0, 200] [7, 0, 61]\n
        [44, 0, 119] \n
        [203, 0, 172] [204, 0, 81] \n
        [208, 0, 82] [209, 0, 117] [209, 1, 127] [208, 1, 2] \n
        [99, 1, 133] \n
        \n
        Frame 2 (1336049775.7117825 s, 0.03 s)\n
        [54, 0, 108] [54, 1, 43] [55, 1, 115] \n
        [123, 0, 76] [124, 0, 59] [124, 1, 142] [123, 1, 84] \n
        [156, 0, 24] \n"""
        self.frame_data = """77 56  28
        7   57  61
        7   58  74
        20  84  52
        21  84  4
        20  85  23
        21  85  60
        21  86  41"""

        self.parser = fp.FrameParser()
        self.in_file_calibration = tempfile.NamedTemporaryFile(delete=False)
        self.in_file_frame = tempfile.NamedTemporaryFile(delete=False)
        self.out_file = tempfile.NamedTemporaryFile(delete=False)
        with open(self.in_file_calibration.name, 'w') as f:
            f.write(self.cluster_text)
        with open(self.in_file_frame.name, 'w') as f:
            f.write(self.frame_data)

    def tearDown(self):
        os.remove(self.in_file_calibration.name)
        os.remove(self.out_file.name)
        os.remove(self.in_file_frame.name)

    def get_hits(self, text=None):
        """Helper - Get the hits from frame"""
        return self.parser._retrieve_frame(text or self.cluster_text)

    def test_can_correctly_retrieve_data_from_calibration_file(self):
        """Can retrieve data from calibration file"""
        expected = self.get_hits()
        actual = self.parser._get_frame_from_file(self.in_file_calibration.name)
        self.assertEqual(expected, actual)

    def test_can_convert_calibration_to_json(self):
        """Calibration data can be converted to JSON"""
        data = self.get_hits()
        expected_json_data = json.loads(json.dumps(data))
        actual_json_data = json.loads(self.parser._gen_output_data(data))
        self.assertEqual(expected_json_data, actual_json_data)

    def test_output_calibration_data_written_correctly_to_file(self):
        """Calibration data can be written to file"""
        clusters = self.get_hits()
        data = self.parser._gen_output_data(clusters)
        expected = json.loads(data)
        self.parser._write_data(data, self.out_file.name)
        with open(self.out_file.name) as f:
            self.assertEqual(expected, json.loads(f.read()))

    def test_can_recognise_calibration_data(self):
        """Calibration data and standard data can be recognized"""
        self.assertTrue(self.parser._is_calibration_data(self.cluster_text))
        self.assertFalse(self.parser._is_calibration_data(self.frame_data))

    def test_can_correctly_retrieve_data_from_file(self):
        """Data can be retrieved from standard data files"""
        expected = self.get_hits(self.frame_data)
        actual = self.parser._get_frame_from_file(self.in_file_frame.name)
        self.assertEqual(expected, actual)

    def test_can_convert_frame_data_to_json(self):
        """Standard input data can be converted to JSON"""
        data = self.get_hits(self.frame_data)
        expected_json_data = json.loads(json.dumps(data))
        actual_json_data = json.loads(self.parser._gen_output_data(data))
        self.assertEqual(expected_json_data, actual_json_data)

    def test_output_frame_data_written_correctly_to_file(self):
        """Standard data can be written to a file"""
        clusters = self.get_hits(self.frame_data)
        data = self.parser._gen_output_data(clusters)
        expected = json.loads(data)
        self.parser._write_data(data, self.out_file.name)
        with open(self.out_file.name) as f:
            self.assertEqual(expected, json.loads(f.read()))

    def test_can_recognise_file_input(self):
        """Can determine if the input string represents a filename"""
        self.assertEqual("file", self.parser._input_type(self.in_file_frame.name))


class TestDirectoryParsing(unittest.TestCase):
    """Tests regarding multiple files for the FrameParser"""

    def setUp(self):
        self.parser = fp.FrameParser()
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

    def test_creates_suitable_directory_structure(self):
        """Creates a suitable directory structure"""
        self.parser._write_output_directory(self.dir)
        name1, name2, name3 = get_base_names([self.in_file1, self.in_file2, self.dsc_file])
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
        self.parser._write_output_directory(self.dir)
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
        self.parser._write_output_directory(self.dir)
        self.assertCountEqual([exp1, exp2, "frames.json"], os.listdir(self.dir + "/output"))

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
        self.parser._write_output_directory(self.dir, ext)
        self.assertCountEqual([exp1, exp2, "frames.json"], os.listdir(self.dir + "/output"))
        os.rename(new1, self.in_file1.name)
        os.rename(new2, self.in_file2.name)

    def test_total_frame_output_has_correct_data(self):
        """The frames file contains the cumulative frame data"""
        expected = self.get_expected_data()
        self.parser._write_output_directory(self.dir)
        with open(self.dir + "/output/frames.json") as f:
            self.assertEqual(expected, json.loads(f.read()))

    def test_can_automatically_detect_directories(self):
        """Can determine that the input string represents a directory path"""
        self.assertEqual("directory", self.parser._input_type(self.dir))

    def test_can_detect_and_write_to_output_dir(self):
        """Given an input string can determine that it is a directory and parse it accordingly"""
        exp1, exp2 = get_expected_names([self.in_file1, self.in_file2])
        self.parser._detect_input_and_write(self.dir)
        self.assertCountEqual([exp1, exp2, "frames.json"], os.listdir(self.dir + "/output"))

class TestUserInteraction(unittest.TestCase):

    """Test the users' interface to the graph module"""

    def setUp(self):
        self.interface = fp.AppFrameParser()
        self.optparser = self.interface._option_parser
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

    def test_provides_explicit_file_name_option(self):
        """Provides the option to specify filename explicitly"""
        option = self.optparser.get_option('-f')
        self.assertEqual('--file-name', option.get_opt_string())
        self.assertIsNone(option.default)
        self.assertEqual('Provide the file name to be read explicitly', option.help)

    def test_provides_explicit_output_file_option(self):
        """Provides the option to specify output filename explicitly"""
        option = self.optparser.get_option('-o')
        self.assertEqual('--output-file', option.get_opt_string())
        self.assertIsNone(option.default)
        self.assertEqual('File to write output to or STDOUT', option.help)


    def test_can_parse_directory(self):
        """Can parse user file input and write"""
        exp1, exp2 = get_expected_names([self.in_file1, self.in_file2])
        self.interface._run_with_args(self.test_args + [self.dir])
        self.assertCountEqual([exp1, exp2, "frames.json"], os.listdir(self.dir + "/output"))

