"""Simulation Events

This file should contain all of the classes necessary to model the different
kinds of events in the simulation.
"""
from __future__ import annotations
from typing import List
from rider import Rider, WAITING, CANCELLED, SATISFIED
from dispatcher import Dispatcher
from driver import Driver
from location import deserialize_location
from monitor import Monitor, RIDER, DRIVER, REQUEST, CANCEL, PICKUP, DROPOFF


class Event:
    """An event.

    Events have an ordering that is based on the event timestamp: Events with
    older timestamps are less than those with newer timestamps.

    This class is abstract; subclasses must implement do().

    You may, if you wish, change the API of this class to add
    extra public methods or attributes. Make sure that anything
    you add makes sense for ALL events, and not just a particular
    event type.

    Document any such changes carefully!

    === Attributes ===
    timestamp: A timestamp for this event.
    """

    timestamp: int

    def __init__(self, timestamp: int) -> None:
        """Initialize an Event with a given timestamp.

        Precondition: timestamp must be a non-negative integer.

        >>> Event(7).timestamp
        7
        """
        self.timestamp = timestamp

    # The following six 'magic methods' are overridden to allow for easy
    # comparison of Event instances. All comparisons simply perform the
    # same comparison on the 'timestamp' attribute of the two events.
    def __eq__(self, other: Event) -> bool:
        """Return True iff this Event is equal to <other>.

        Two events are equal iff they have the same timestamp.

        >>> first = Event(1)
        >>> second = Event(2)
        >>> first == second
        False
        >>> second.timestamp = first.timestamp
        >>> first == second
        True
        """
        return self.timestamp == other.timestamp

    def __ne__(self, other: Event) -> bool:
        """Return True iff this Event is not equal to <other>.

        >>> first = Event(1)
        >>> second = Event(2)
        >>> first != second
        True
        >>> second.timestamp = first.timestamp
        >>> first != second
        False
        """
        return not self == other

    def __lt__(self, other: Event) -> bool:
        """Return True iff this Event is less than <other>.

        >>> first = Event(1)
        >>> second = Event(2)
        >>> first < second
        True
        >>> second < first
        False
        """
        return self.timestamp < other.timestamp

    def __le__(self, other: Event) -> bool:
        """Return True iff this Event is less than or equal to <other>.

        >>> first = Event(1)
        >>> second = Event(2)
        >>> first <= first
        True
        >>> first <= second
        True
        >>> second <= first
        False
        """
        return self.timestamp <= other.timestamp

    def __gt__(self, other: Event) -> bool:
        """Return True iff this Event is greater than <other>.

        >>> first = Event(1)
        >>> second = Event(2)
        >>> first > second
        False
        >>> second > first
        True
        """
        return not self <= other

    def __ge__(self, other: Event) -> bool:
        """Return True iff this Event is greater than or equal to <other>.

        >>> first = Event(1)
        >>> second = Event(2)
        >>> first >= first
        True
        >>> first >= second
        False
        >>> second >= first
        True
        """
        return not self < other

    def __str__(self) -> str:
        """Return a string representation of this event.

        """
        raise NotImplementedError("Implemented in a subclass")

    def do(self, dispatcher: Dispatcher, monitor: Monitor) -> List[Event]:
        """Do this Event.

        Update the state of the simulation, using the dispatcher, and any
        attributes according to the meaning of the event.

        Notify the monitor of any activities that have occurred during the
        event.

        Return a list of new events spawned by this event (making sure the
        timestamps are correct).

        Note: the "business logic" of what actually happens should not be
        handled in any Event classes.

        """
        raise NotImplementedError("Implemented in a subclass")


class RiderRequest(Event):
    """A rider requests a driver.

    === Attributes ===
    rider: The rider.
    """

    rider: Rider

    def __init__(self, timestamp: int, rider: Rider) -> None:
        """Initialize a RiderRequest event.

        """
        super().__init__(timestamp)
        self.rider = rider

    def do(self, dispatcher: Dispatcher, monitor: Monitor) -> List[Event]:
        """Assign the rider to a driver or add the rider to a waiting list.
        If the rider is assigned to a driver, the driver starts driving to
        the rider.

        Return a Cancellation event. If the rider is assigned to a driver,
        also return a Pickup event.

        """
        monitor.notify(self.timestamp, RIDER, REQUEST,
                       self.rider.id, self.rider.origin)
        events = []
        driver = dispatcher.request_driver(self.rider)
        if driver is not None:
            tot_ride_t = driver.start_drive(self.rider.origin)
            events.append(Pickup(self.timestamp + tot_ride_t,
                                 self.rider, driver))
        events.append(Cancellation(self.timestamp + self.rider.patience,
                                   self.rider))
        return events

    def __str__(self) -> str:
        """Return a string representation of this event.

        """
        return "{} -- {}: Get to request a driver".format(self.timestamp, self.rider)


class DriverRequest(Event):
    """A driver requests a rider.

    === Attributes ===
    driver: The driver.
    """

    driver: Driver

    def __init__(self, timestamp: int, driver: Driver) -> None:
        """Initialize a DriverRequest event.

        """
        super().__init__(timestamp)
        self.driver = driver

    def do(self, dispatcher: Dispatcher, monitor: Monitor) -> List[Event]:
        """Register the driver, if this is the first request, and
        assign a rider to the driver, if one is available.

        If a rider is available, return a Pickup event.

        """
        # Notify the monitor about the request.

        # Request a rider from the dispatcher.
        # If there is one available, the driver starts driving towards the
        # rider, and the method returns a Pickup event for when the driver
        # arrives at the riders location.
        monitor.notify(self.timestamp, RIDER, REQUEST,
                       self.driver.id, self.driver.location)
        events = []
        rider = dispatcher.request_rider(self.driver)
        if rider is None:
            return events
        else:
            tot_ride_t = self.driver.get_travel_time(self.driver.destination)
            self.driver.start_ride(self.driver.destination)
            p_u = self.timestamp + tot_ride_t
            events = []
            if p_u <= self.timestamp:
                events.append(Pickup(p_u, rider, self.driver))
                events.append(
                    Cancellation(self.timestamp + rider.patience, rider))
            return events

    def __str__(self) -> str:
        """Return a string representation of this event.

        """
        return "{} -- {}: Request a rider".format(self.timestamp, self.driver)


class Cancellation(Event):
    rider: Rider

    def __init__(self, timestamp: int, rider: Rider) -> None:
        """Initialize a DriverRequest event.

        """
        super().__init__(timestamp)
        self.rider = rider

    def do(self, dispatcher: Dispatcher, monitor: Monitor) -> List[Event]:
        """

        """
        events = []
        if self.rider.status == WAITING:
            monitor.notify(self.timestamp, RIDER, CANCEL,
                           self.rider.id, self.rider.origin)
            dispatcher.cancel_ride(self.rider)
        if self.rider.status == WAITING:
            self.rider.status = CANCELLED

        return events

    def __str__(self) -> str:
        """Return a string representation of this event.

        """
        return "{} -- {}: Cancel a ride".format(self.timestamp, self.rider)


class Pickup(Event):
    driver: Driver
    rider: Rider

    def __init__(self, timestamp: int, rider: Rider, driver: Driver) -> None:
        """Initialize a DriverRequest event.

        """
        super().__init__(timestamp)
        self.driver = driver
        self.rider = rider

    def do(self, dispatcher: Dispatcher, monitor: Monitor) -> List[Event]:
        """

        """
        events = []
        # Driver arrives at the destination
        self.driver.location = self.driver.destination
        if self.rider.status == CANCELLED and len(dispatcher.wait_t) == 0:
            print("Rider Now: None")
        elif self.rider.status == CANCELLED:
            # sample_rider = dispatcher.request_rider(self.driver)
            events.append(DriverRequest(self.timestamp, self.driver))
        else:
            if self.rider.status != CANCELLED:
                self.rider.status = SATISFIED
                monitor.notify(self.timestamp, DRIVER, PICKUP, self.driver.id,
                               self.driver.location)
                monitor.notify(self.timestamp, RIDER, PICKUP, self.rider.id,
                               self.rider.origin)
                tot_t = self.driver.start_ride(self.rider)
                tra_time = self.timestamp + tot_t
                events.append(Dropoff(tra_time, self.rider,
                                      self.driver))
        return events

    def __str__(self) -> str:
        """Return a string representation of this event.

        """
        return "{} -- {}: Pickup a ride".format(self.timestamp, self.driver)


class Dropoff(Event):
    def __init__(self, timestamp: int, rider: Rider, driver: Driver) -> None:
        """Initialize a DriverRequest event.

        """
        super().__init__(timestamp)
        self.rider = rider
        self.driver = driver

    def do(self, dispatcher: Dispatcher, monitor: Monitor) -> List[Event]:
        """

        """
        events = []
        monitor.notify(self.timestamp, RIDER, DROPOFF, self.rider.id,
                       self.rider.destination)

        monitor.notify(self.timestamp, DRIVER, DROPOFF, self.driver.id,
                       self.driver.location)
        if self.rider.status == SATISFIED:
            self.driver.end_ride()
            dispatcher.request_rider(self.driver)
            events.append(DriverRequest(self.timestamp, self.driver))
            return events

    def __str__(self):
        """Return a string representation of this event.
        @type self: Pickup
        @rtype: str
        """
        return "{} -- {}: Pick up".format(self.timestamp, self.driver)

def create_event_list(filename: str) -> List[Event]:
    """Return a list of Events based on raw list of events in <filename>.

    Precondition: the file stored at <filename> is in the format specified
    by the assignment handout.

    filename: The name of a file that contains the list of events.
    """
    events = []
    with open(filename, "r") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                # Skip lines that are blank or start with #.
                continue
            # Create a list of words in the line, e.g.
            # ['10', 'RiderRequest', 'Cerise', '4,2', '1,5', '15'].
            # Note that these are strings, and you'll need to convert some
            # of them to a different type.
            tokens = line.split()
            timestamp = int(tokens[0])
            event_type = tokens[1]
            # HINT: Use Location.deserialize to convert the location string to
            # a location.
            if event_type == "DriverRequest":
                # Create a DriverRequest event.
                driver_id, location_str, speed = tokens[2], tokens[3], int(
                    tokens[4])
                driver_location = deserialize_location(location_str)
                driver = Driver(driver_id, driver_location, speed)
                event = DriverRequest(timestamp, driver)
                events.append(event)
            elif event_type == "RiderRequest":
                # Create a RiderRequest event.
                rider_id, origin_str, destination_str, patience = tokens[2], \
                                                                  tokens[3], \
                                                                  tokens[
                                                                      4], int(
                    tokens[5])

                # Deserialize the location strings
                origin = deserialize_location(origin_str)
                destination = deserialize_location(destination_str)

                rider = Rider(rider_id, patience, destination, origin)
                event = RiderRequest(timestamp, rider)
            events.append(event)

    return events


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(
        config={
            'allowed-io': ['create_event_list'],
            'extra-imports': ['rider', 'dispatcher', 'driver',
                              'location', 'monitor']})
