#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import tempfile
import os
import json

import analysis.frame_parser as fp

# NOTES:
# * May want to move the cluster_parser into a class,
#   to allow for extra configuration (and not overload
#   the module)


class TestFrameParser(unittest.TestCase):

    """Tests for the cluster_parser module"""

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

    def test_can_correctly_retrieve_data_from_calibration_file(self):
        expected = self.parser._retrieve_frame(self.cluster_text)
        actual = self.parser._get_frame_from_file(self.in_file_calibration.name)
        self.assertEqual(expected, actual)

    def test_can_convert_calibration_to_json(self):
        data = self.parser._retrieve_frame(self.cluster_text)
        expected_json_data = json.loads(json.dumps(data))
        actual_json_data = json.loads(self.parser._gen_output_data(data))

        self.assertEqual(expected_json_data, actual_json_data)

    def test_output_calibration_data_written_correctly_to_file(self):
        clusters = self.parser._retrieve_frame(self.cluster_text)
        data = self.parser._gen_output_data(clusters)
        expected = json.loads(data)
        self.parser._write_data(data, self.out_file.name)
        with open(self.out_file.name) as f:
            self.assertEqual(expected, json.loads(f.read()))

    def test_can_recognise_calibration_data(self):
        self.assertTrue(self.parser._is_calibration_data(self.cluster_text))
        self.assertFalse(self.parser._is_calibration_data(self.frame_data))

    def test_can_correctly_retrieve_data_from_file(self):
        expected = self.parser._retrieve_frame(self.frame_data)
        actual = self.parser._get_frame_from_file(self.in_file_frame.name)
        self.assertEqual(expected, actual)

    def test_can_convert_frame_data_to_json(self):
        data = self.parser._retrieve_frame(self.frame_data)
        expected_json_data = json.loads(json.dumps(data))
        actual_json_data = json.loads(self.parser._gen_output_data(data))
        self.assertEqual(expected_json_data, actual_json_data)

    def test_output_frame_data_written_correctly_to_file(self):
        clusters = self.parser._retrieve_frame(self.frame_data)
        data = self.parser._gen_output_data(clusters)
        expected = json.loads(data)
        self.parser._write_data(data, self.out_file.name)
        with open(self.out_file.name) as f:
            self.assertEqual(expected, json.loads(f.read()))
