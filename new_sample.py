import pytest
from location import Location, deserialize_location, manhattan_distance
from monitor import Monitor
from dispatcher import Dispatcher
from simulation import Simulation
from event import create_event_list, RiderRequest, DriverRequest, Pickup, Dropoff, Cancellation
from driver import Driver
from rider import Rider


def test_location_print() -> None:
    """Tests for the correct implementation of creating and printing Location."""
    location = Location(1, 2)
    assert str(location) in ["(1,2)", "(1, 2)"]
    location2 = deserialize_location("3,4")
    assert str(location2) in ["(3,4)", "(3, 4)"]

def test_3_drivers_5_riders_reg_2() -> None:
    """Tests a scenario with multiple drivers and riders, where multiple pickups and dropoffs occur."""
    events = [
        DriverRequest(0, Driver("Driver1", Location(1, 1), 1)),
        DriverRequest(0, Driver("Driver2", Location(2, 2), 1)),
        DriverRequest(0, Driver("Driver3", Location(3, 3), 1)),
        RiderRequest(0, Rider("Rider1", 10, Location(1, 1), Location(2, 2))),
        RiderRequest(2, Rider("Rider2", 10, Location(3, 3), Location(4, 4))),
        RiderRequest(3, Rider("Rider3", 10, Location(2, 2), Location(3, 3))),
        RiderRequest(4, Rider("Rider4", 10, Location(1, 1), Location(3, 3))),
        RiderRequest(6, Rider("Rider5", 10, Location(4, 4), Location(1, 1))),
        RiderRequest(8, Rider("Rider6", 10, Location(3, 3), Location(1, 1))),
    ]

    sim = Simulation()
    report = sim.run(events)
    assert len(report) == 3
    assert report['rider_wait_time'] == pytest.approx(0.333333333333334)
    assert report['driver_total_distance'] == pytest.approx(7.33333333333)
    assert report['driver_ride_distance'] == pytest.approx(6.66666666667)


def test_event_creation() -> None:
    """Tests for the correct implementation of event creation."""
    events = create_event_list("events.txt")
    assert len(events) == 12
    for event in events:
        instance = isinstance(event, RiderRequest) or isinstance(event, DriverRequest)
        assert instance == True

    driverRequest = events[0]
    assert driverRequest.timestamp == 0
    riderRequest = events[-1]
    assert riderRequest.timestamp == 25

def test_special_events_pickup_and_dropoff() -> None:
    """Tests Pickup and Dropoff events on a basic set of events."""

    # Environment Setup
    events = create_event_list("events.txt")
    driver_request, passenger_request = events[0], events[-1]
    driver, rider = driver_request.driver, passenger_request.rider
    monitor = Monitor()
    dispatcher = Dispatcher()
    driver_request.do(dispatcher, monitor)
    passenger_request.do(dispatcher, monitor)

    # Testing
    pickup = Pickup(0, rider, driver)
    dropoff = pickup.do(dispatcher, monitor)

    assert isinstance(dropoff[0], Dropoff) == True
    assert rider.status == 'satisfied'

    # Environment Setup
    events = create_event_list("events.txt")
    driver_request, passenger_request = events[1], events[-2]
    driver, rider = driver_request.driver, passenger_request.rider
    monitor = Monitor()
    dispatcher = Dispatcher()
    driver_request.do(dispatcher, monitor)
    passenger_request.do(dispatcher, monitor)

    # Testing
    cancellation = Cancellation(0, rider)
    result = cancellation.do(dispatcher, monitor)
    assert result == []
    assert rider.status == 'cancelled'

def test_manhattan_distance() -> None:
    """Tests the calculation of Manhattan distance between two locations."""
    location1 = Location(1, 2)
    location2 = Location(4, 6)

    distance = manhattan_distance(location1, location2)
    assert distance == 7


def test_ride() -> None:
    """Tests that the driver correctly starts the ride."""
    rider = Rider('Eve', 100, Location(2, 4), Location(5, 7))
    driver = Driver('Abel', Location(2, 4), 3)

    travel_time = driver.start_ride(rider)
    assert travel_time == 2

def test_multiple_drivers_available() -> None:
    """Tests the scenario when there are multiple drivers available for a rider."""
    events = [
        DriverRequest(0, Driver('Driver1', Location(1, 1), 1)),
        DriverRequest(0, Driver('Driver2', Location(2, 2), 2)),
        RiderRequest(0, Rider('Alice', 5, Location(1, 1), Location(3, 3))),
    ]

    sim = Simulation()
    report = sim.run(events)

    assert report['rider_wait_time'] == 0
    assert report['driver_total_distance'] == 2
    assert report['driver_ride_distance'] == 2

def test_driver_cancels_ride() -> None:
    """Tests the scenario when a driver cancels the ride."""
    events = [
        DriverRequest(0, Driver('Driver1', Location(1, 1), 1)),
        RiderRequest(0, Rider('Alice', 5, Location(1, 1), Location(3, 3))),
        Cancellation(3, Rider('Alice', 5, Location(1, 1), Location(3, 3))),
    ]

    sim = Simulation()
    report = sim.run(events)

    assert report['rider_wait_time'] == 0
    assert report['driver_total_distance'] == 2
    assert report['driver_ride_distance'] == 0




# def test_simulation_run() -> None:
#     """Tests the simulation run on a basic set of events."""
#     events = create_event_list("events.txt")
#
#     assert len(events) == 12
#     sim = Simulation()
#     report = sim.run(events)
#     assert len(report) == 3
#     assert report['rider_wait_time'] == pytest.approx(0.5)
#     assert report['driver_total_distance'] == pytest.approx(4.5)
#     assert report['driver_ride_distance'] == pytest.approx(3.8333333333333335)


def test_special_events() -> None:
    """Tests Cancellation and Pickup on a basic set of events."""

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

    # Environment Setup
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

def test_multiple_pickups_and_dropoffs() -> None:
    """Tests a scenario with multiple drivers and riders, where multiple pickups and dropoffs occur."""
    events = [
        DriverRequest(0, Driver("Driver1", Location(1, 1), 1)),
        DriverRequest(0, Driver("Driver2", Location(2, 2), 1)),
        DriverRequest(0, Driver("Driver3", Location(3, 3), 1)),
        RiderRequest(0, Rider("Rider1", 10, Location(1, 1), Location(2, 2))),
        RiderRequest(2, Rider("Rider2", 10, Location(3, 3), Location(4, 4))),
        RiderRequest(3, Rider("Rider3", 10, Location(2, 2), Location(3, 3))),
        RiderRequest(4, Rider("Rider4", 10, Location(1, 1), Location(3, 3))),
        RiderRequest(6, Rider("Rider5", 10, Location(4, 4), Location(1, 1))),
        RiderRequest(8, Rider("Rider6", 10, Location(3, 3), Location(1, 1))),
    ]

    sim = Simulation()
    report = sim.run(events)
    assert len(report) == 3
    assert report['rider_wait_time'] == pytest.approx(3)
    assert report['driver_total_distance'] == pytest.approx(10)
    assert report['driver_ride_distance'] == pytest.approx(8.333333333333334)
    assert report['rider_wait_time'] == pytest.approx(1.0)



# Run the tests
if __name__ == '__main__':
    pytest.main(['-v'])