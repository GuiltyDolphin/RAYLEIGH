#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# frame.py


class Frame:
    """Frame object to represent the data contained within .dsc files"""
    def __init__(self, **kwargs):
        self._frame = kwargs.get("frame", None)
        self._acquisition_mode = kwargs.get("acquisition_mode", None)
        self._acquisition_time = kwargs.get("acquisition_time", None)
        self._chipboard_id = kwargs.get("chipboard_id", None)
        self._dacs = kwargs.get("dacs", None)
        self._firmware_version = kwargs.get("firmware_version", None)
        self._bias_voltage = kwargs.get("bias_voltage", None)
        self._hw_timer_mode = kwargs.get("hw_timer_mode", None)
        self._medipix_interface = kwargs.get("medipix_interface", None)
        self._medipix_clock = kwargs.get("medipix_clock", None)
        self._medipix_type = kwargs.get("medipix_type", None)
        self._name_and_serial_number = kwargs.get("name_and_serial_number", None)
        self._pixelman_version = kwargs.get("pixelman_version", None)
        self._detector_polarity = kwargs.get("detector_polarity", None)
        self._acquisition_start_time = kwargs.get("acquisition_start_time", None)
        self._acquisition_start_time_string = kwargs.get("acquisition_start_time_string", None)
        self._timepix_clock = kwargs.get("timepix_clock", None)
