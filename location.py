"""Locations for the simulation"""

from __future__ import annotations


class Location:
    """A two-dimensional location."""
    row: row
    column: column

    def __init__(self, row: int, column: int) -> None:
        """Initialize a location.

        """
        self.row = row
        self.column = column

    def __str__(self) -> str:
        """Return a string representation.

        """
        return f"({self.row}, {self.column})"

    def __eq__(self, other: Location) -> bool:
        """Return True if self equals other, and false otherwise.

        """
        return True if other.row == self.row and other.column == self.column \
            else False


def manhattan_distance(origin: Location, destination: Location) -> int:
    """Return the Manhattan distance between the origin and the destination.

    """
    return abs(origin.row - destination.row) + abs(origin.column - destination.
                                                   column)


def deserialize_location(location_str: str) -> Location:
    """Deserialize a location.

    location_str: A location in the format 'row,col'
    """
    row, col = location_str.split(',')
    return Location(int(row), int(col))


if __name__ == '__main__':
    import python_ta
    python_ta.check_all()
    