#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# test_frame.py

import unittest
import tempfile
import os
import json
import copy
import pickle as pk
import re

from analysis import dsc_parser as dscp

data_frame = dscp.Frame(
    frame={
        'name': "A000000001",
        'type': "i16 [X,Y,C]",
        'width': 256,
        'height': 256},
    acquisition_mode=1,
    acquisition_time=60.0,
    chipboard_id="B06-W0212",
    dacs=[1, 100, 255, 127, 127,
          0, 405, 7, 130, 128, 80,
          85, 128, 128],
    firmware_version="Firmware 3 (date: 28. 11. 2012)",
    bias_voltage=95.0,
    hw_timer_mode=2,
    medipix_interface="MX-10",
    medipix_clock=10.0,
    medipix_type=3,
    name_and_serial_number="MX-10 Particle Detector A",
    pixelman_version="2.2.2",
    detector_polarity=1,
    acquisition_start_time=1396447375.004957,
    acquisition_start_time_string="Wed Apr 02 15:02:55.004957 2014",
    timepix_clock=10.0)

pk_protocol = 4


class TestFrame(unittest.TestCase):

    """Tests for the Frame object"""

    def setUp(self):
        self.frame = copy.deepcopy(data_frame)

    def tearDown(self):
        pass

    def test_has_frame_class(self):
        self.assertIsInstance(data_frame, dscp.Frame)


class TestDSCParser(unittest.TestCase):

    """Tests for the DSC Parser object"""

    def setUp(self):
        self.frame = copy.deepcopy(data_frame)
        self.pickled_frame = pk.dumps(self.frame, pk_protocol)
        self.parser = dscp.DSCParser()
        self.in_file = "tests/dsc_data.txt.dsc"
        self.out_file = tempfile.NamedTemporaryFile(delete=False)
        with open(self.in_file) as f:
            self.dsc_data = f.read()

    def tearDown(self):
        os.remove(self.out_file.name)

    def get_matcher_dict(self, field, to_match):
        """Helper - Get the groupdict of parser regex"""
        matcher = self.parser._dsc_reg[field]
        return matcher.match(to_match).groupdict()

    def test_can_match_title(self):
        title = '"Acq time" ("Acquisition time [s]"):'
        matches = self.get_matcher_dict('title', title)
        self.assertEqual('Acq time', matches['short_name'])
        self.assertEqual('Acquisition time ', matches['long_name'])

    def test_can_match_data_type(self):
        data_type = "double[1]"
        matches = self.get_matcher_dict('data_type', data_type)
        self.assertEqual('double', matches['type'])
        self.assertEqual('1', matches['num'])

    def test_can_match_value(self):
        value = "60.000000"
        matches = self.get_matcher_dict('value', value)
        self.assertEqual('60.000000', matches['value'])

    def test_can_match_header(self):
        header_type = "Type=i16 [X,Y,C] width=256 height=256"
        matches = self.get_matcher_dict('header', header_type)
        self.assertEqual("i16 [X,Y,C]", matches['type'])
        self.assertEqual("256", matches['width'])
        self.assertEqual("256", matches['height'])

    def test_can_analyse_dsc_header(self):
        header = [
            "A0000001",
            "[F0]",
            "Type=i16 [X,Y,C] width=256 height=256",
            "\"Acq mode\" (\"Acquisition mode\")",
            "i32[1]",
            "1"]
        expected_dict = {
            'name': "A0000001",
            'type': "i16 [X,Y,C]",
            'width': 256,
            'height': 256}
        expected = (expected_dict, header[3:])
        self.assertEqual(expected, self.parser._analyse_dsc_header(header))

    def test_can_parse_config(self):
        config = ["\"Hw timer\" (\"Hw timer mode\"):",
                  "i32[1]",
                  "2"]
        expected = dict(hw_timer_mode=2)
        self.assertEqual(expected, self.parser._parse_config(config))
        config_list = config.copy()
        config_list.pop()
        config_list.append("1 2 3 4")
        expected = dict(hw_timer_mode=[1, 2, 3, 4])
        self.assertEqual(expected, self.parser._parse_config(
            config_list, expect_list=[("Hw timer", " ")]))
        config.pop(0)
        config_alternate = [('[sS]tart time \(string\)', "start time string")]
        config.insert(0, "Start time (string)")
        expected = dict(start_time_string=2)
        self.assertEqual(
            expected,
            self.parser._parse_config(config, use_alternate=config_alternate))

    def test_can_create_frame_from_dsc(self):
        frame = self.parser._frame_from_dsc(self.dsc_data)
        self.assertIsInstance(frame, dscp.Frame)

    def test_creates_correct_frame_from_dsc(self):
        other = self.parser._frame_from_dsc(self.dsc_data)
        self.assertDictEqual(self.frame.__dict__, other.__dict__)

    def test_creates_correct_frame_from_pickle(self):
        other = pk.loads(self.parser._pickle_from_dsc(self.dsc_data))
        self.assertDictEqual(self.frame.__dict__, other.__dict__)
