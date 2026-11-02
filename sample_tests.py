import pytest
from location import Location, deserialize_location
from monitor import Monitor
from dispatcher import Dispatcher
from simulation import Simulation
from event import create_event_list, RiderRequest, DriverRequest, Pickup, \
    Dropoff, Cancellation
from driver import Driver
from rider import Rider


def test_location_print() -> None:
    """ Tests for the currect implementation of the creating and print of the Location
    """
    location = Location(1, 2)
    assert str(location) in ["(1,2)", "(1, 2)"]
    location2 = deserialize_location("3,4")
    assert str(location2) in ["(3,4)", "(3, 4)"]


def test_event_creation() -> None:
    """ Tests for correct implementation of the event creations
    """
    events = create_event_list("events.txt")
    assert len(events) == 12
    for event in events:
        instance = isinstance(event, RiderRequest) or isinstance(event,
                                                                 DriverRequest)
        assert instance == True

    driverRequest = events[0]
    assert driverRequest.timestamp == 0
    riderRequest = events[-1]
    assert riderRequest.timestamp == 25


def test_ride() -> None:
    """ Tests that driver correctly starts its ride
    """
    rider = Rider('Eve', 100, Location(2, 4), Location(5, 7))
    driver = Driver('Abel', Location(2, 4), 3)

    travel_time = driver.start_ride(rider)
    assert travel_time == 2


def test_simulation_run() -> None:
    """Test simulation run on a basic set of events"""
    events = create_event_list("events.txt")

    assert len(events) == 12
    sim = Simulation()
    report = sim.run(events)
    assert len(report) == 3
    assert report['rider_wait_time'] == pytest.approx(0.5)
    assert report['driver_total_distance'] == pytest.approx(4.5)
    assert report['driver_ride_distance'] == pytest.approx(3.8333333333333335)


def test_random_order() -> None:
    """time stamp are random order + driver/rider requests also random"""
    events = create_event_list("1.txt")

    assert len(events) == 6
    sim = Simulation()
    report = sim.run(events)
    assert len(report) == 3
    assert report['rider_wait_time'] == pytest.approx(1.3333333333333333)
    assert report['driver_total_distance'] == pytest.approx(3.3333333333333335)
    assert report['driver_ride_distance'] == pytest.approx(1.666667)


def test_rider_request_first() -> None:
    """rider requests first then driver request"""
    events = create_event_list("2.txt")

    assert len(events) == 4
    sim = Simulation()
    report = sim.run(events)
    assert len(report) == 3
    assert report['rider_wait_time'] == pytest.approx(5)
    assert report['driver_total_distance'] == pytest.approx(1)
    assert report['driver_ride_distance'] == pytest.approx(0)


def test_two_same_drivers() -> None:
    """rider requests first then driver request"""
    events = create_event_list("4.txt")

    assert len(events) == 3
    sim = Simulation()
    report = sim.run(events)
    assert len(report) == 3
    assert report['rider_wait_time'] == pytest.approx(4)
    assert report['driver_total_distance'] == pytest.approx(2)
    assert report['driver_ride_distance'] == pytest.approx(1)


def test_special_events() -> None:
    """Test Cancellation and Pickup on a basic set of events"""

    # Environment Setup
    events = create_event_list("events.txt")
    dvr_request, psg_request = events[0], events[-1]
    driver, rider = dvr_request.driver, psg_request.rider
    monitor = Monitor()
    dispatcher = Dispatcher()
    dvr_request.do(dispatcher, monitor)
    psg_request.do(dispatcher, monitor)

    # Testing
    trip = Pickup(0, rider, driver)
    dropoff = trip.do(dispatcher, monitor)

    assert isinstance(dropoff[0], Dropoff) == True
    assert rider.status == 'satisfied'

    # ES
    events = create_event_list("events.txt")
    dvr_request, psg_request = events[1], events[-2]
    driver, rider = dvr_request.driver, psg_request.rider
    monitor = Monitor()
    dispatcher = Dispatcher()
    dvr_request.do(dispatcher, monitor)
    psg_request.do(dispatcher, monitor)

    # Testing
    cancel = Cancellation(0, rider)
    result = cancel.do(dispatcher, monitor)
    assert result == []
    assert rider.status == 'cancelled'


if __name__ == "__main__":
    pytest.main(['sample_tests.py'])
