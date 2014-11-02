#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import tempfile
import os
import json

import analysis.cluster_parser as cp

class TestClusterParser(unittest.TestCase):

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
        self.in_file = tempfile.NamedTemporaryFile(delete=False)
        self.out_file = tempfile.NamedTemporaryFile(delete=False)
        with open(self.in_file.name, 'w') as f:
            f.write(self.cluster_text)


    def tearDown(self):
        os.remove(self.in_file.name)
        os.remove(self.out_file.name)

    def test_can_correctly_retrieve_data_from_file(self):
        expected = cp._retrieve_clusters(self.cluster_text)
        actual = cp._get_clusters_from_file(self.in_file.name)
        self.assertEqual(expected, actual)

    def test_can_convert_to_json(self):
        data = cp._retrieve_clusters(self.cluster_text)
        expected_json_data = json.loads(json.dumps(data))
        actual_json_data = json.loads(cp._gen_output_data(data))

        self.assertEqual(expected_json_data, actual_json_data)

    def test_output_data_written_correctly_to_file(self):
        clusters = cp._retrieve_clusters(self.cluster_text)
        data = cp._gen_output_data(clusters)
        expected = json.loads(data)
        cp._write_data(data, self.out_file.name)
        with open(self.out_file.name) as f:
            self.assertEqual(expected, json.loads(f.read()))
