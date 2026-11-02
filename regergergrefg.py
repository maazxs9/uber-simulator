# monitor.notify(self.timestamp, DRIVER, PICKUP, self.driver.id,
#                self.driver.location)
# monitor.notify(self.timestamp, RIDER, PICKUP, self.rider.id,
#                self.rider.origin)
#
# events = []
# if self.rider.status == WAITING:
#     if self.timestamp < self.rider.patience:
#         self.driver.idle = False
#         self.driver.location = self.rider.origin
#         self.rider.status = SATISFIED
#         monitor.notify(self.timestamp, DRIVER, DROPOFF, self.driver.id,
#                        self.driver.location)
#         dropoff_time = self.timestamp + self.driver.get_travel_time(
#             self.rider.destination)
#         events.append(Dropoff(dropoff_time, self.rider, self.driver))
# else:
#     events.append(DriverRequest(self.timestamp, self.driver))
#
# return events


# total_d = 0
# count = 0
# l1 = None
# l2 = None
# prev = None
# for activities in self._activities[DRIVER].values():
#     if len(activities) >= 2:
#         for activity in activities:
#             prev = l2
#             if activity.description == PICKUP:
#                 l1 = activity.location
#             elif activity.description == DROPOFF:
#                 l2 = activity.location
#             if l1 is not None and l2 is not None and l2 != prev:
#                 total_d += manhattan_distance(l1, l2)
#         count += 1
#
# return total_d / count


# if self.available_l:
#     driver = self.available_l[0]
#     self.available_l = self.available_l[1:]
#     return driver
# else:
#     self.waiting_l.append(rider)
#     return None




import pytest
from container import PriorityQueue
from dispatcher import Dispatcher
from event import DriverRequest
from event import RiderRequest
from event import Pickup
from monitor import Monitor
from rider import Rider
from driver import Driver
from location import Location
from location import manhattan_distance


def test_dispatcher():
    # Rider, who cancels ride, is no longer available
    sponge = Rider('Sponge', 2, Location(2, 4), Location(3, 6))
    dispatcher1 = Dispatcher()
    dispatcher1.cancel_ride(sponge)
    assert sponge.status == 'cancelled'
    # request_driver returns None when no Drivers are available
    assert dispatcher1.request_driver(sponge) is None
    # Test that request_driver returns a Driver
    soap = Rider('Soap', 2, Location(2, 4), Location(3, 6))
    raw = Driver('Raw', Location(3, 5), 5)
    dispatcher2 = Dispatcher()
    dispatcher2.request_rider(raw)
    assert dispatcher2.request_driver(soap) == raw
    # returns a driver even when none would make it in time
    marc = Rider('Marc', 1, Location(20, 40), Location(3, 6))
    zuck = Driver('Zuck', Location(1, 1), 1)
    dispatcher3 = Dispatcher()
    dispatcher3.request_rider(zuck)
    assert dispatcher3.request_driver(marc) == zuck
    # request_driver returns one of the two tied drivers (not at front or
    # back of a list)
    soft = Rider('Soft', 2, Location(2, 4), Location(3, 6))
    raw = Driver('Raw', Location(3, 5), 1)
    squid = Driver('Squid', Location(2, 4), 5)
    crab = Driver('Crab', Location(2, 4), 5)
    penny = Driver('Penny', Location(3, 5), 1)
    dispatcher4 = Dispatcher()
    dispatcher4.request_rider(raw)
    dispatcher4.request_rider(squid)
    dispatcher4.request_rider(crab)
    dispatcher4.request_rider(penny)
    assert (dispatcher4.request_driver(soft) == crab or
            dispatcher4.request_driver(soft) == squid)
    # returns the longest waiting customer
    bee = Rider('Bee', 2, Location(2, 4), Location(3, 6))
    em = Rider('Em', 2, Location(2, 4), Location(3, 6))
    bb = Rider('Bb', 2, Location(2, 4), Location(3, 6))
    ryan = Driver('Ryan', Location(2, 4), 1)
    dispatcher5 = Dispatcher()
    dispatcher5.request_driver(bee)
    dispatcher5.request_driver(em)
    dispatcher5.request_driver(bb)
    assert dispatcher5.request_rider(ryan) == bee
    # returns None when no Rider
    ryan = Driver('Ryan', Location(2, 4), 1)
    dispatcher6 = Dispatcher()
    assert dispatcher6.request_rider(ryan) is None
    # returns a Rider when available
    r = Driver('Ryan', Location(2, 4), 1)
    b = Rider('Bee', 2, Location(2, 4), Location(3, 6))
    dispatcher7 = Dispatcher()
    dispatcher7.request_driver(b)
    assert dispatcher7.request_rider(r) == b
    # returns rider even when a driver can't make it in time
    r2 = Driver('Ryan', Location(2, 4), 1)
    b2 = Rider('Bee', 2, Location(50, 90), Location(3, 6))
    dispatcher8 = Dispatcher()
    dispatcher8.request_driver(b2)
    assert dispatcher8.request_rider(r2) == b2
    # __str__ returns a string
    dispatcher9 = Dispatcher()
    s4 = Rider('Sponge', 2, Location(2, 4), Location(3, 6))
    s5 = Rider('Soap', 2, Location(2, 4), Location(3, 6))
    s6 = Rider('Soft', 2, Location(2, 4), Location(3, 6))
    dispatcher9.request_driver(s4)
    dispatcher9.request_driver(s5)
    dispatcher9.request_driver(s6)
    assert type(dispatcher9.__str__()) is str


def test_driver():
    # test end_drive doesn't return anything
    driver1 = Driver('Ryan', Location(2, 4), 1)
    assert driver1.end_drive() is None
    # test end_ride doesn't return anything
    driver2 = Driver('Ryan', Location(2, 4), 1)
    assert driver2.end_ride() is None
    # test that the __eq__ method returns False when given
    # two different Drivers with different stats
    driver3 = Driver('Ryan', Location(2, 4), 1)
    driver4 = Driver('Bob', Location(2, 4), 1)
    assert driver3.__eq__(driver4) is False
    # test that the __eq__ method returns True when given
    # two different Drivers with the same stats
    driver5 = Driver('Bob', Location(2, 4), 1)
    driver6 = Driver('Bob', Location(2, 4), 1)
    assert driver5.__eq__(driver6) is True
    # test that get_travel_time returns the correct value
    driver7 = Driver('Bob', Location(2, 4), 1)
    travel = Location(1, 1)
    time = abs(travel.row - driver7.location.row) + \
           abs(travel.column - driver7.location.column)
    assert driver7.get_travel_time(travel) == time
    # test that get_travel_time rounds down correctly to the nearest integer
    driver8 = Driver('Bob', Location(2, 4), 10)
    travel2 = Location(1, 1)
    time2 = (abs(travel2.row - driver8.location.row) + \
             abs(travel2.column - driver8.location.column)) / driver8.speed
    assert driver8.get_travel_time(travel2) == round(time2)
    # test that the get_travel_time rounds up correctly to the nearest integer
    driver9 = Driver('Bob', Location(2, 4), 5)
    travel3 = Location(1, 1)
    time3 = (abs(travel3.row - driver9.location.row) + \
             abs(travel3.column - driver9.location.column)) / driver9.speed
    assert driver9.get_travel_time(travel3) == round(time3)
    # test that the start_drive returns int not float
    driver10 = Driver('Bob', Location(2, 4), 1)
    travel4 = Location(1, 1)
    time4 = abs(travel4.row - driver10.location.row) + \
            abs(travel4.column - driver10.location.column)
    assert type(driver10.start_drive(travel4)) is int
    # test that Driver.start_drive returns the travel time from the driver's
    # location to the rider's origin
    driver11 = Driver('Bob', Location(2, 4), 1)
    travel5 = Location(1, 1)
    rider1 = Rider('Ryan', 1, travel5, Location(2, 2))
    time5 = abs(travel5.row - driver11.location.row) + \
            abs(travel5.column - driver11.location.column)
    assert driver11.start_drive(rider1.origin) == time5
    # test that start_ride returns the travel time from the driver's location
    # /the rider's origin to the rider's destination
    driver12 = Driver('Bob', Location(2, 4), 1)
    travel6 = Location(1, 1)
    travel7 = Location(3, 3)
    rider2 = Rider('Ryan', 1, travel6, travel7)
    driver12.start_drive(rider2.origin)
    driver12.end_drive()
    distance = manhattan_distance(rider2.origin, rider2.destination)
    assert driver12.start_ride(rider2) == distance
    # test that the __str__ method returns a string
    driver13 = Driver('Bob', Location(2, 4), 1)
    assert type(driver13.__str__()) is str


def test_driver_request():
    # notified the monitor when multiple riders
    # riders are available
    monitor = Monitor()
    dispatcher = Dispatcher()
    driver1 = Driver('Ryan', Location(2, 4), 1)
    rider1 = Rider('Bob', 1, Location(2, 4), Location(3, 6))
    rider2 = Rider('Bob', 1, Location(2, 4), Location(3, 6))
    request1 = RiderRequest(1, rider1)
    request2 = RiderRequest(1, rider2)
    request1.do(dispatcher, monitor)
    request2.do(dispatcher, monitor)
    request3 = DriverRequest(1, driver1)
    request3.do(dispatcher, monitor)
    assert monitor._activities['driver']['Ryan'][0].description == 'request'
    # test that it returns a list with one pick
    # when multiple riders are available
    monitor2 = Monitor()
    dispatcher2 = Dispatcher()
    driver2 = Driver('Ryan', Location(2, 4), 1)
    rider3 = Rider('Bob', 1, Location(2, 4), Location(3, 6))
    rider4 = Rider('Bob', 1, Location(2, 4), Location(3, 6))
    request4 = RiderRequest(1, rider3)
    request5 = RiderRequest(1, rider4)
    request4.do(dispatcher2, monitor2)
    request5.do(dispatcher2, monitor2)
    request6 = DriverRequest(1, driver2)
    assert type(request6.do(dispatcher2, monitor2)[0]) is Pickup
    # test that it does notify the monitor when no riders are available
    monitor3 = Monitor()
    dispatcher3 = Dispatcher()
    driver3 = Driver('Ryan', Location(2, 4), 1)
    request7 = DriverRequest(1, driver3)
    request7.do(dispatcher3, monitor3)
    assert monitor3._activities['driver']['Ryan'][0].description == 'request'
    # test that it returns an empty list when no riders are available
    monitor4 = Monitor()
    dispatcher4 = Dispatcher()
    driver4 = Driver('Ryan', Location(2, 4), 1)
    request8 = DriverRequest(1, driver4)
    assert request8.do(dispatcher4, monitor4) == []
    # test that do returns a list with one pickup when one rider is available
    monitor5 = Monitor()
    dispatcher5 = Dispatcher()
    driver5 = Driver('Ryan', Location(2, 4), 1)
    rider5 = Rider('Bob', 1, Location(2, 4), Location(3, 6))
    request9 = RiderRequest(1, rider5)
    request9.do(dispatcher5, monitor5)
    request10 = DriverRequest(1, driver5)
    assert type(request10.do(dispatcher5, monitor5)[0]) is Pickup


def test_event():
    pass


def test_location():
    # test that the __eq__ method returns False when given two different
    # Locations with different stats
    location1 = Location(2, 4)
    location2 = Location(2, 5)
    assert location1.__eq__(location2) is False
    # test that the __eq__ method returns True when given two references to
    # the same object
    location3 = Location(2, 4)
    location4 = Location(2, 4)
    assert location3.__eq__(location4) is True
    # test that the __str__ method returns a string
    location5 = Location(2, 4)
    assert type(location5.__str__()) is str


def test_monitor():
    pass


def test_priority_queue():
    # test adding and removing multiple items
    pq = PriorityQueue()
    pq.add("red")
    assert pq.remove() == "red"
    pq.add("blue")
    assert pq.remove() == "blue"
    pq.add("yellow")
    assert pq.remove() == "yellow"
    pq.add("green")
    assert pq.remove() == "green"
    # test the order of items removed when priority
    # is FIFO anyway
    pq2 = PriorityQueue()
    pq2.add("a")
    pq2.add("b")
    pq2.add("c")
    pq2.add("d")
    assert pq2.remove() == "a"
    assert pq2.remove() == "b"
    assert pq2.remove() == "c"
    assert pq2.remove() == "d"
    # test the order of tiems removed when priority
    # is not FIFO
    pq3 = PriorityQueue()
    pq3.add("red")
    pq3.add("blue")
    pq3.add("yellow")
    pq3.add("green")
    assert pq3.remove() == "blue"
    assert pq3.remove() == "green"
    assert pq3.remove() == "red"
    assert pq3.remove() == "yellow"
    # test that items with tied priority are returned in
    # FIFO order
    pq4 = PriorityQueue()
    pq4.add("blue")
    pq4.add("blue")
    pq4.add("green")
    assert pq4.remove() == "blue"
    assert pq4.remove() == "blue"
    assert pq4.remove() == "green"
    # test tht adding and removing a single item
    # works correctly
    pq5 = PriorityQueue()
    pq5.add("red")
    assert pq5.remove() == "red"
    # test that priority is right when alternately adding
    # and removing items
    pq6 = PriorityQueue()
    pq6.add("red")
    pq6.add("blue")
    assert pq6.remove() == "blue"
    pq6.add("yellow")
    pq6.add("green")
    assert pq6.remove() == "green"
    assert pq6.remove() == "red"
    assert pq6.remove() == "yellow"


def test_simulation():
    pass


if __name__ == "__main__":
    pytest.main(['test.py'])
