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

from analysis import frame

data_frame = frame.Frame(
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
        self.assertIsInstance(data_frame, frame.Frame)


class TestDSCParser(unittest.TestCase):

    """Tests for the DSC Parser object"""

    def setUp(self):
        self.frame = copy.deepcopy(data_frame)
        self.pickled_frame = pk.dumps(self.frame, pk_protocol)
        self.parser = frame.DSCParser()
        self.in_file = "testdata/frame_data.txt.dsc"
        self.out_file = tempfile.NamedTemporaryFile(delete=False)
        with open(self.in_file) as f:
            self.dsc_data = f.read()

    def tearDown(self):
        os.remove(self.out_file.name)

    def test_can_match_title(self):
        title_matcher = self.parser._dsc_reg['title']
        title = '"Acq time" ("Acquisition time [s]"):'
        matches = title_matcher.match(title).groupdict()
        short = matches['short_name']
        self.assertEqual('Acq time', short)
        long_name = matches['long_name']
        self.assertEqual('Acquisition time ', long_name)

    def test_can_match_data_type(self):
        type_matcher = self.parser._dsc_reg['data_type']
        data_type = "double[1]"
        matches = type_matcher.match(data_type).groupdict()
        type_ = matches['type']
        self.assertEqual(type_, 'double')
        num = matches['num']
        self.assertEqual(num, '1')

    def test_can_match_value(self):
        value_matcher = self.parser._dsc_reg['value']
        value = "60.000000"
        matches = value_matcher.match(value).groupdict()
        val = matches['value']
        self.assertEqual(val, '60.000000')

    def test_can_match_header(self):
        header_matcher = self.parser._dsc_reg['header']
        header_type = "Type=i16 [X,Y,C] width=256 height=256"
        matches = header_matcher.match(header_type).groupdict()
        type_ = matches['type']
        self.assertEqual(type_, "i16 [X,Y,C]")
        width = matches['width']
        self.assertEqual(width, "256")
        height = matches['height']
        self.assertEqual(height, "256")

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
        self.assertEqual(expected, self.parser._parse_config(config, use_alternate=config_alternate))


    def test_can_create_frame_from_dsc(self):
        self.assertIsInstance(
            self.parser._frame_from_dsc(self.dsc_data), frame.Frame)

    def test_creates_correct_frame_from_dsc(self):
        other = self.parser._frame_from_dsc(self.dsc_data)
        self.assertEqual(self.frame.__dict__, other.__dict__)

    def creates_correct_frame_from_pickle(self):
        other = pk.loads(self.parser._pickle_from_dsc(self.dsc_data))
        self.assertEqual(self.frame.__dict__, other.__dict__)
