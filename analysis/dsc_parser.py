#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# frame.py

import pickle as pk
import re
from collections import deque

pk_protocol = 4

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


class DSCParser:
    """Parser for DSC files"""
    def __init__(self):
        self._blank_frame = Frame()
        self._dsc_reg = {
                'title': re.compile('"?(?P<short_name>(?:\w\s?)+)[^"]*"?(?:\s+\("(?P<long_name>(?:\w\s?)+)(?:[\[(].+[)\]])?"\):)?'),
                'data_type': re.compile("(?P<type>\w*)\[(?P<num>\w*)\]"),
                'value': re.compile("(?P<value>.+)"),
                'header': re.compile("Type=(?P<type>.+) width=(?P<width>\d+) height=(?P<height>\d+)")
                }

    def _pickle_from_dsc(self, dsc_data):
        """Produce a pickled Frame object from a .dsc file"""
        frame = self._frame_from_dsc(dsc_data)
        return pk.dumps(frame, pk_protocol)

    def _frame_from_dsc(self, dsc_data):
        """Parse a .dsc file and create a frame object"""
        config = deque([s.splitlines() for s in dsc_data.split("\n\n")])
        config.remove([])

        header = config.popleft()

        frame, header_rest = self._analyse_dsc_header(header)
        if header_rest:
            config.appendleft(header_rest)
        kvs = {'frame': frame}
        use_short_names = ["DACs values of all chips",
                           "Medipix or chipboard ID"]
        expect_list = [("DACs", " ")]
        use_alternate = [('[Ss]tart time \(string\)', "acquisition start time string"),
                ('ChipboardID', 'chipboard id')]
        for conf in config:
            kvs.update(self._parse_config(conf, use_short_names, expect_list, use_alternate))

        return Frame(**kvs)

    def _analyse_dsc_header(self, header):
        """Analyse a .dsc header. Return a dictionary for
        header values and the header attachment if any"""
        header_type = self._dsc_reg['header'].match(header[2]).groupdict()
        header_type['name'] = self._dsc_reg['title'].match(header[0]).groupdict()['short_name']
        for entry in ['height', 'width']:
            header_type[entry] = int(header_type[entry])
        return (header_type, header[3:])

    def _parse_config(
            self, config,
            use_short=[], expect_list=[], use_alternate=[]):
        """Retrieve name and value of a config section"""
        def match_dict(name, pos):
            return self._dsc_reg[name].match(config[pos]).groupdict()
        title = match_dict('title', 0)
        str_value = match_dict('value', 2)['value']

        def try_str_to_num(s):
            """Attemp to convert a string to an int or float"""
            try:
                value = int(s)
            except ValueError:
                try:
                    value = float(s)
                except ValueError:
                    value = s
            return value

        def first(x):
            return x[0]
        exps = map(first, expect_list)
        for name in expect_list:
            if first(name) in title.values():
                value = str_value.split(name[1])
                value = list(map(try_str_to_num, value))
                if ('') in value:
                    value.remove('')
                break
        else:
            value = try_str_to_num(str_value)

        for a in use_alternate:
            if re.findall(first(a), first(config)):
                title['short_name'] = a[1]
                title['long_name'] = a[1]
                break

        def format_title(title):
            return title.strip().replace(" ", "_").lower()

        def return_hash(name):
            return {format_title(title[name]): value}

        if title['long_name'] in use_short:
            return return_hash('short_name')
        else:
            return return_hash('long_name')



