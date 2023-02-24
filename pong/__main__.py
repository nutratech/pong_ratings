# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
"""
Created on Fri Feb 10 12:18:04 2023

@author: shane
"""
import argparse
import time
from typing import Any, List, Tuple, Union
from urllib.error import URLError

import argcomplete
import requests

from pong import CLI_CONFIG, __email__, __title__, __url__, __version__
from pong.argparser import build_subcommands


def build_arg_parser() -> argparse.ArgumentParser:
    """Adds all subparsers and parsing logic"""

    arg_parser = argparse.ArgumentParser(prog=__title__)
    arg_parser.add_argument(
        "-v",
        action="version",
        version=f"{__title__} version {__version__}",
    )

    arg_parser.add_argument(
        "-d", dest="debug", action="store_true", help="enable verbose logging (debug)"
    )

    # Subparsers
    build_subcommands(arg_parser)

    return arg_parser


def main(args: Union[None, List[str]] = None) -> int:
    """
    Main method for CLI

    @param args: List[str]
    """

    start_time = time.time()
    arg_parser = build_arg_parser()
    argcomplete.autocomplete(arg_parser)

    def parse_args() -> argparse.Namespace:
        """Returns parsed args"""
        if args is None:
            return arg_parser.parse_args()
        return arg_parser.parse_args(args=args)

    def func(parser: argparse.Namespace) -> Tuple[int, Any]:
        """Executes a function for a given argument call to the parser"""
        if hasattr(parser, "func"):
            # Print help for nested commands
            if parser.func.__name__ == "print_help":
                return 0, parser.func()  # pragma: no cover

            # Collect non-default args
            args_dict = dict(vars(parser))
            for expected_arg in ["func", "debug"]:
                args_dict.pop(expected_arg)

            # Run function
            if args_dict:
                # Make sure the parser.func() always returns: Tuple[Int, Any]
                return parser.func(args=parser)  # type: ignore
            return parser.func()  # type: ignore

        # Otherwise print help
        arg_parser.print_help()
        return 0, None

    # Build the parser, set flags
    _parser = parse_args()
    CLI_CONFIG.set_flags(_parser)

    # Try to run the function
    exit_code = 1
    conn_errs = (requests.exceptions.ConnectionError, requests.ReadTimeout, URLError)

    try:
        exit_code, *_results = func(_parser)
    except requests.exceptions.HTTPError as http_error:
        err_msg = f"{http_error.response.status_code}: {repr(http_error)}"
        print("Server response error, try again: " + err_msg)
        if CLI_CONFIG.debug:
            raise
    except conn_errs as conn_url_error:  # pragma: no cover
        print("Connection error, check your internet: " + repr(conn_url_error))
        if CLI_CONFIG.debug:
            raise
    except Exception as exception:  # pragma: no cover  # pylint: disable=broad-except
        print("Unforeseen error, run with -d for more info: " + repr(exception))
        print(f"You can open an issue here: {__url__}")
        print(f"Or send me an email with the debug output: {__email__}")
        if CLI_CONFIG.debug:
            raise
    finally:
        if CLI_CONFIG.debug:
            exc_time = time.time() - start_time
            print(f"\nExecuted in: {round(exc_time * 1000, 1)} ms")
            print(f"Exit code: {exit_code}")

    return exit_code
