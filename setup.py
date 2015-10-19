#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# setup.py

from setuptools import setup, find_packages

import analysis

setup(
    name='RAYLEIGH',
    version=analysis.__version__,
    packages=find_packages(),
    # scripts=['analysis/rayleigh.py'],
    entry_points={'console_scripts': ['rayleigh = analysis.rayleigh:main']},
    install_requires=[
        'matplotlib>=1.4.2', 'nose>=1.3.4',
        'numpy>=1.9.0', 'setuptools>=6.0.2'],

    author="GuiltyDolphin",
    author_email="GuiltyDolphin@gmail.com",
    description="A basic plotter and converter for output files from"
    + " TimePix chips.",
    license="GPLv3",
    keywords="plotter ray rayleigh json converter",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux"],
    url="https://www.github.com/GuiltyDolphin/RAYLEIGH",
    download_url="https://github.com/GuiltyDolphin/RAYLEIGH/tarball/0.2.0",

    test_suite='nose.collector'
    )
