#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# rayleigh.py

import sys
import argparse


class RayleighApp():
    def __init__(self):
        self._parser = argparse.ArgumentParser(
            description="Perform operations on framedata from TimePix chips",
            prog='rayleigh')

        self._parser.add_argument('command')

    def _run(self, args):
        args_ = self._parser.parse_args(args)
        subp = args_.command
        if subp == 'frame':
            print("Frame")
        elif subp == 'plot':
            print("Plotter")


if __name__ == '__main__':
    app = RayleighApp()
    app._run(sys.argv[1:])
