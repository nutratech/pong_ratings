import csv
import os
from io import StringIO

import requests

from pong.models import Player


# Hard-coded URL values pointing to our sheet
def _url(gid: int):
    _spreadsheet_key = "1evcgUzJ5hO55RYshc3dH-EmzZfor58t0qPB-zp8iw4A"
    return (
        "https://docs.google.com/spreadsheet/ccc"
        f"?key={_spreadsheet_key}"
        f"&gid={gid}"
        "&output=csv"
    )


SINGLES_URL = _url(834797930)
DOUBLES_URL = _url(682349527)


def get_google_sheet(url: str):
    """
    Returns a byte array (string)
    TODO:
      - Cache these on the filesystem, commit, and have the network latency be an
        optional step to "refresh" the data in real time.
        But also allow running instantly on old (cached) CSV files.
      - Support multiple sheets per document (e.g. separate "doubles games" sheet)?
    """

    response = requests.get(url, timeout=12)
    assert response.status_code == 200, "Wrong status code"

    return response.content


def build_csv_reader(url: str):
    """Returns a csv.reader() object"""
    _csv_bytes_output = get_google_sheet(url)
    _csv_file = StringIO(_csv_bytes_output.decode())
    return csv.reader(_csv_file)


def get_or_create_player_by_name(players: dict, username: str):
    """Adds a player"""
    if username in players:
        return players[username]

    _player = Player(username)
    players[username] = _player
    return _player


def print_title(title: str):
    """Prints a neat and visible header to separate tables"""
    print(os.linesep)
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print(title)
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print("")
