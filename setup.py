#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# setup.py

from setuptools import setup, find_packages

setup(
    name='RAYLEIGH',
    version="0.2.0",
    packages=find_packages(),
    scripts=[
        'analysis/frame_parser.py',
        'analysis/plotter.py',
        'analysis/dsc_parser.py'],

    install_requires=[
        'matplotlib>=1.4.2', 'nose>=1.3.4',
        'numpy>=1.9.0', 'setuptools>=6.0.2'],

    author="GuiltyDolphin",
    author_email="GuiltyDolphin@gmail.com",
    description="A basic plotter and converter for output files from"
    + " TimePix chips.",
    license="GPLv3",
    keywords="plotter ray rayleigh json converter",
    url="https://www.github.com/GuiltyDolphin/RAYLEIGH",
    download_url="https://github.com/GuiltyDolphin/RAYLEIGH/archive/master.zip",

    test_suite='nose.collector'
    )
