# Uber Simulator

An event-driven ride-sharing simulation built in Python. The system models interactions between riders and drivers, including ride requests, driver dispatching, pickups, cancellations, and drop-offs.
Features
- Processes simulation events using a priority queue.
- Coordinates ride requests and available drivers.
- Tracks rider and driver states throughout each trip.
- Calculates travel distances using Manhattan distance.
- Collects statistics about simulation activity.

## Files
simulation.py	Runs the simulation and processes events.
dispatcher.py	Coordinates drivers and ride requests.
event.py	Defines ride requests, pickups, cancellations, and drop-offs.
driver.py	Models drivers and their behaviour.
rider.py	Models riders and their requests.
location.py	Represents locations and calculates distances.
container.py	Implements the priority queue.
monitor.py	Tracks activity and reports statistics.
events.txt	Provides sample simulation events.
Python module names are preserved so existing imports continue to work.

## Background
Developed as a coursework project using provided starter code, with a focus on object-oriented programming, priority queues, and discrete-event simulation.

## Validation
Python source files pass syntax checks. Runtime behavior and the included tests have not yet been verified for this version.
