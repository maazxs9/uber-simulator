"""Dispatcher for the simulation"""

from typing import Optional
from driver import Driver
from rider import Rider


class Dispatcher:
    """A dispatcher fulfills requests from riders and drivers for a
    ride-sharing service.

    When a rider requests a driver, the dispatcher assigns a driver to the
    rider. If no driver is available, the rider is placed on a waiting
    list for the next available driver. A rider that has not yet been
    picked up by a driver may cancel their request.

    When a driver requests a rider, the dispatcher assigns a rider from
    the waiting list to the driver. If there is no rider on the waiting list
    the dispatcher does nothing. Once a driver requests a rider, the driver
    is registered with the dispatcher, and will be used to fulfill future
    rider requests.
    """
    wait_t: list
    avail_t: list

    def __init__(self) -> None:
        """Initialize a Dispatcher.

        """
        self.wait_t = []
        self.avail_t = []

    def __str__(self) -> str:
        """Return a string representation.

        """
        wait_t = f"Waiting: {len(self.wait_t)} riders"
        dr_t = f"Registered: {len(self.avail_t)} drivers"
        return f"Dispatcher\n{wait_t}\n{dr_t}"

    def request_driver(self, rider: Rider) -> Optional[Driver]:
        """Return a driver for the rider, or None if no driver is available.

        Add the rider to the waiting list if there is no available driver.

        """
        if self.avail_t:
            fastest = self.avail_t[0]
            fast = self.avail_t[0].get_travel_time(rider.origin)
            for driver in self.avail_t:
                drive_d = driver.get_travel_time(rider.origin)
                if drive_d < fast and driver.is_idle:
                    fastest = driver
                    fast = drive_d
            return fastest
        else:
            self.wait_t.append(rider)
            return None

    def request_rider(self, driver: Driver) -> Optional[Rider]:
        """Return a rider for the driver, or None if no rider is available.

        If this is a new driver, register the driver for future rider requests.

        """
        if driver not in self.avail_t:
            self.avail_t.append(driver)
        if self.wait_t:
            rider = self.wait_t.pop(0)
            return rider
        return None

    def cancel_ride(self, rider: Rider) -> None:
        """Cancel the ride for rider.

        """
        if rider in self.wait_t:
            self.wait_t.remove(rider)


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={'extra-imports': ['typing', 'driver', 'rider']})
