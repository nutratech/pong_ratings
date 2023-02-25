#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 13 16:30:30 2018

@author: shane
"""
import os
import platform

from setuptools import find_packages, setup

from pong import __author__, __email__, __title__, __version__

os.chdir(os.path.dirname(os.path.realpath(__file__)))

PLATFORM_SYSTEM = platform.system()

CLASSIFIERS = [
    "Environment :: Console",
    "Intended Audience :: End Users/Desktop",
    "Intended Audience :: Science/Research",
    "Intended Audience :: Education",
    "Development Status :: 3 - Alpha",
    "Natural Language :: English",
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    "Framework :: Flake8",
    "Framework :: Pytest",
    "Operating System :: OS Independent",
    "Operating System :: Microsoft :: Windows :: Windows XP",
    "Operating System :: Microsoft :: Windows :: Windows 10",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: POSIX :: Linux",
    "Programming Language :: Python :: Implementation :: CPython",
    "Programming Language :: Python :: Implementation :: PyPy",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: SQL",
    "Programming Language :: Unix Shell",
]

# ReadMe
with open("README.rst", encoding="utf-8") as file:
    README = file.read()

# Requirements
with open("requirements.txt", encoding="utf-8") as file:
    REQUIREMENTS = file.read().split()

# Setup method
setup(
    name=__title__,
    author=__author__,
    author_email=__email__,
    classifiers=CLASSIFIERS,
    install_requires=REQUIREMENTS,
    python_requires=">=3.7",
    zip_safe=False,
    packages=find_packages(exclude=["tests", "pong.docs"]),
    include_package_data=True,
    entry_points={"console_scripts": ["pr=pong.__main__:main", "p=pong.__main__:main"]},
    platforms=["linux", "darwin", "win32"],
    description="Table tennis rating system for local clubs",
    long_description=README,
    long_description_content_type="text/x-rst",
    url="https://github.com/nutratech/pong_ratings",
    license="GPL v3",
    version=__version__,
)
