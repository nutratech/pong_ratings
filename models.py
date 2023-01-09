from glicko2 import glicko2

DEFAULT_RATING = 1500


class Player:
    def __init__(self, username: str):
        """Model for storing username, rating"""

        self.username = username

        self.rating_singles = glicko2.Glicko2()

    def __str__(self):
        _rating = round(self.rating_singles.mu)
        _two_deviations = round(self.rating_singles.phi * 2)
        # TODO: return this as a tuple, and tabulate it (rather than format as string)?
        return f"{self.username} ({_rating} ± {_two_deviations})"
