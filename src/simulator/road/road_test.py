import typing
import unittest
from unittest.mock import Mock

from simulator.road.road import Road, CollisionError
from simulator.vehicle.vehicle import Vehicle


def implementsRoad(cls):
    assert hasattr(cls, 'getRoad') and callable(getattr(cls, 'getRoad'))

    def test_addVehicle(self: cls):
        # Add a vehicle.
        road: Road = self.getRoad(length=100, lanes=1)
        vehicle: Vehicle = Mock()
        position = (0, 0)
        vehicle.position = position
        road.addVehicle(vehicle)
        # Try to add the vehicle outside the road length.
        road: Road = self.getRoad(length=100, lanes=1)
        vehicle: Vehicle = Mock()
        position = (100, 0)
        vehicle.position = position
        with self.assertRaises(IndexError):
            road.addVehicle(vehicle)
        # Try to add the vehicle outside the road lanes.
        road: Road = self.getRoad(length=100, lanes=1)
        vehicle: Vehicle = Mock()
        position = (0, 1)
        vehicle.position = position
        with self.assertRaises(IndexError):
            road.addVehicle(vehicle)
        # Try to add the vehicle to a nonempty road cell.
        road: Road = self.getRoad(length=100, lanes=1)
        vehicle: Vehicle = Mock()
        position = (0, 0)
        vehicle.position = position
        road.addVehicle(vehicle)
        another: Vehicle = Mock()
        another.position = position
        with self.assertRaises(CollisionError):
            road.addVehicle(another)

    def test_getVehicle(self: cls):
        # Add and retrieve the vehicle.
        road: Road = self.getRoad(length=100, lanes=1)
        vehicle: Vehicle = Mock()
        position = (0, 0)
        vehicle.position = position
        road.addVehicle(vehicle)
        result = road.getVehicle(position)
        self.assertEqual(result, vehicle, 'got invalid vehicle')
        # Get vehicle from an empty cell.
        road: Road = self.getRoad(length=100, lanes=1)
        position = (0, 0)
        result = road.getVehicle(position)
        self.assertIsNone(result, 'got unexpected vehicle')
        # Try to get vehicle from outside the road length.
        road: Road = self.getRoad(length=100, lanes=1)
        position = (100, 0)
        with self.assertRaises(IndexError):
            road.getVehicle(position)
        # Try to get the vehicle from outside the road lanes.
        road: Road = self.getRoad(length=100, lanes=1)
        position = (0, 1)
        with self.assertRaises(IndexError):
            road.getVehicle(position)

    def test_allVehicles(self: cls):
        # Add and retrieve all the vehicles from a single lane.
        road: Road = self.getRoad(length=100, lanes=1)
        vehicles: typing.List[Vehicle] = []
        for i in range(100):
            vehicle: Vehicle = Mock()
            vehicle.position = (i, 0)
            vehicles.append(vehicle)
            road.addVehicle(vehicle)
        result = list(road.getAllVehicles())
        self.assertEqual(len(result), len(vehicles), 'got invalid number of vehicles')
        self.assertListEqual(result, list(reversed(vehicles)), 'vehicle lists differ')
        # Add and retrieve all the vehicles from multiple lanes.
        road: Road = self.getRoad(length=100, lanes=2)
        vehicles: typing.List[Vehicle] = []
        for lane in range(2):
            for x in range(100):
                vehicle: Vehicle = Mock()
                vehicle.position = (x, 1 - lane)
                vehicles.append(vehicle)
                road.addVehicle(vehicle)
        result = list(road.getAllVehicles())
        self.assertEqual(len(result), len(vehicles), 'got invalid number of vehicles')
        self.assertListEqual(result, list(reversed(vehicles)), 'vehicle lists differ')
        # Get vehicles from an empty road.
        road: Road = self.getRoad(length=100, lanes=2)
        result = list(road.getAllVehicles())
        self.assertEqual(len(result), 0, 'got invalid number of vehicles')
        self.assertListEqual(result, [], 'vehicle lists differ')

    def test_addPendingVehicle(self: cls):
        # Add a vehicle.
        road: Road = self.getRoad(length=100, lanes=1)
        vehicle: Vehicle = Mock()
        position = (0, 0)
        vehicle.position = position
        road.addPendingVehicle(vehicle)
        # Try to add the vehicle outside the road length.
        road: Road = self.getRoad(length=100, lanes=1)
        vehicle: Vehicle = Mock()
        position = (100, 0)
        vehicle.position = position
        with self.assertRaises(IndexError):
            road.addPendingVehicle(vehicle)
        # Try to add the vehicle outside the road lanes.
        road: Road = self.getRoad(length=100, lanes=1)
        vehicle: Vehicle = Mock()
        position = (0, 1)
        vehicle.position = position
        with self.assertRaises(IndexError):
            road.addPendingVehicle(vehicle)
        # Try to add the vehicle to a nonempty road cell.
        road: Road = self.getRoad(length=100, lanes=1)
        vehicle: Vehicle = Mock()
        position = (0, 0)
        vehicle.position = position
        road.addPendingVehicle(vehicle)
        another: Vehicle = Mock()
        another.position = position
        with self.assertRaises(CollisionError):
            road.addPendingVehicle(another)

    def test_getNextVehicle(self: cls):
        # Single lane.
        road: Road = self.getRoad(length=100, lanes=1)
        vehicle: Vehicle = Mock()
        position = (10, 0)
        vehicle.position = position
        road.addVehicle(vehicle)
        # All positions < 10 should return the vehicle.
        for x in range(10):
            rx, result = road.getNextVehicle(position=(x, 0))
            self.assertEqual(rx, 10, 'got invalid next position')
            self.assertEqual(result, vehicle, 'got invalid next vehicle')
        # All positions >= 10 should return None.
        for x in range(10, 100):
            rx, result = road.getNextVehicle(position=(x, 0))
            self.assertEqual(rx, 100, 'got invalid next position')
            self.assertIsNone(result, 'got invalid next vehicle')
        # Multiple lanes.
        road: Road = self.getRoad(length=100, lanes=2)
        vehicle: Vehicle = Mock()
        position = (10, 0)
        vehicle.position = position
        road.addVehicle(vehicle)
        # All positions < 10 should return the vehicle.
        for x in range(10):
            rx, result = road.getNextVehicle(position=(x, 0))
            self.assertEqual(rx, 10, 'got invalid next position')
            self.assertEqual(result, vehicle, 'got invalid next vehicle')
        # All positions >= 10 should return None.
        for x in range(10, 100):
            rx, result = road.getNextVehicle(position=(x, 0))
            self.assertEqual(rx, 100, 'got invalid next position')
            self.assertIsNone(result, 'got invalid next vehicle')
        for x in range(100):
            rx, result = road.getNextVehicle(position=(x, 1))
            self.assertEqual(rx, 100, 'got invalid next position')
            self.assertIsNone(result, 'got invalid next vehicle')
        # Check errors.
        road: Road = self.getRoad(length=100, lanes=1)
        with self.assertRaises(IndexError):
            road.getNextVehicle(position=(-1, 0))
        with self.assertRaises(IndexError):
            road.getNextVehicle(position=(100, 0))
        with self.assertRaises(IndexError):
            road.getNextVehicle(position=(0, 1))
        with self.assertRaises(IndexError):
            road.getNextVehicle(position=(0, -1))

    cls.test_addVehicle = test_addVehicle
    cls.test_getVehicle = test_getVehicle
    cls.test_allVehicles = test_allVehicles
    cls.test_addPendingVehicle = test_addPendingVehicle
    cls.test_getNextVehicle = test_getNextVehicle
    return cls


class RoadTestCase(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
