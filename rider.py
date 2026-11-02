"""
The rider module contains the Rider class. It also contains
constants that represent the status of the rider.

=== Constants ===
WAITING: A constant used for the waiting rider status.
CANCELLED: A constant used for the cancelled rider status.
SATISFIED: A constant used for the satisfied rider status
"""

from location import Location

WAITING = "waiting"
CANCELLED = "cancelled"
SATISFIED = "satisfied"


class Rider:

    """A rider for a ride-sharing service.

    """
    id: str
    patience: int
    origin: Location
    destination: Location
    status: str

    def __init__(self, identifier: str, patience: int, origin: Location,
                 destination: Location) -> None:
        """Initialize a Rider.

        """
        self.id = identifier
        self.patience = patience
        self.origin = origin
        self.destination = destination
        self.status = WAITING

    def __str__(self) -> str:
        """
        Return a string representation of the object.
        """
        return f"{self.id} wants to go from {self.origin} to " \
               f"{self.destination} and is {self.status} "

    def __eq__(self, other) -> bool:
        """Return True if self equals other, and false otherwise.
        """
        if not isinstance(other, Rider):
            return False

        return (
            self.origin == other.origin
            and self.id == other.id
            and self.destination == other.destination
            and self.patience == other.patience
            and self.status == other.status
        )

if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={'extra-imports': ['location']})
