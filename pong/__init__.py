import math
import os

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))


# Hard-coded URL values pointing to our sheet
def _url(gid: int) -> str:
    _spreadsheet_key = "1evcgUzJ5hO55RYshc3dH-EmzZfor58t0qPB-zp8iw4A"
    return (
        "https://docs.google.com/spreadsheet/ccc"
        f"?key={_spreadsheet_key}"
        f"&gid={gid}"
        "&output=csv"
    )


SINGLES_URL = _url(834797930)
DOUBLES_URL = _url(682349527)

# Constants
DRAW_PROB_DOUBLES = math.comb(20, 10) * (1 / 2) ** 20

# Fall back (cached CSV files, if sheets.google.com is unreachable)
CSV_GAMES_SINGLES = os.path.join(PROJECT_ROOT, "data", "games_singles.csv")
CSV_GAMES_DOUBLES = os.path.join(PROJECT_ROOT, "data", "games_doubles.csv")

# Persist ratings after main script for auxiliary calculations
CSV_RATINGS_SINGLES = os.path.join(PROJECT_ROOT, "data", "ratings_singles.csv")
CSV_RATINGS_DOUBLES = os.path.join(PROJECT_ROOT, "data", "ratings_doubles.csv")
