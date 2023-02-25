#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 10 13:26:27 2023

@author: shane
"""
from argparse import ArgumentParser

from pong.argparser.funcs import parser_func_download, parser_func_rank


def build_subcommands(arg_parser: ArgumentParser) -> None:
    """Build the arg parser sub commands"""

    subparsers = arg_parser.add_subparsers(title="actions")

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Download sub-parser
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    subparser_download = subparsers.add_parser(
        "fetch", help="Download the latest Sheet from Google"
    )
    subparser_download.set_defaults(func=parser_func_download)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Rank sub-parser
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    subparser_rank = subparsers.add_parser(
        "rank", help="Process CSV, output ratings or player detail"
    )
    subparser_rank.add_argument(
        "-s",
        dest="skip_dl",
        action="store_true",
        help="skip sheet download, use cached",
    )
    subparser_rank.add_argument(
        "-m", "--matches", action="store_true", help="include fairest match ups"
    )
    subparser_rank.add_argument(
        "-g", "--graph", action="store_true", help="include rating history charts"
    )
    subparser_rank.add_argument(
        "--no-abbrev-titles", action="store_true", help="don't abbreviate table titles"
    )
    subparser_rank.set_defaults(func=parser_func_rank)
