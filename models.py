DEFAULT_RATING = 1500


class Player:
    def __init__(self, username: str):
        """Model for storing username, rating"""

        self.username = username

        self.rating_singles = DEFAULT_RATING
        self.rating_doubles = DEFAULT_RATING

    def __str__(self):
        return f"{self.username} ({round(self.rating_singles)})"
