#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# test_frame.py

import unittest
import tempfile
import os

from analysis import frame


class TestFrame(unittest.TestCase):

    """Tests for the Frame object"""

    def setUp(self):
        self.frame = frame.Frame(
            frame={
                'name': "A000000001",
                'unknown': ['F0'],
                'type': "i16 [X, Y, C]",
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

        def tearDown(self):
            pass

    def test_has_frame_class(self):
        self.assertIsInstance(self.frame, frame.Frame)


class TestDSCParser(unittest.TestCase):

    """Tests for the DSC Parser object"""

    def setUp(self):
        self.in_file = "testdata/frame_data.txt.dsc"
        self.out_file = tempfile.NamedTemporaryFile(delete=False)
        with open(self.in_file) as f:
            self.dsc_data = f.read()

    def tearDown(self):
        os.remove(self.out_file.name)

    def test_name(self):
        pass
