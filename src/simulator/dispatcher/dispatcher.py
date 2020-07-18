import random

from simulator.position import Position
from simulator.road.road import Road
from simulator.vehicle.vehicle import Vehicle
from util.rand import shuffled


class Dispatcher:
    road: Road
    count: int
    remaining: int
    length: int

    def __init__(self, road: Road, count: int, length: int = 1):
        self.road = road
        self.count = count
        self.remaining = 0
        self.length = length

    def dispatch(self) -> None:
        '''
        Adds vehicles to the road.
        :return: None.
        '''
        self.remaining += random.randint(0, self.count)
        for lane in shuffled(range(self.road.lanes_count)):
            if self.remaining <= 0:
                return
            # Check if position is not occupied.
            position = (self.length - 1, lane * self.road.lane_width + self.road.lane_width // 2)
            if self.road.getVehicle(position=position) is not None:
                continue
            # Add the vehicle.
            self.road.addVehicle(vehicle=self._newVehicle(position=position))
            self.remaining -= 1

    def _newVehicle(self, position: Position) -> Vehicle:
        '''
        Generates new vehicle at a given position.
        :param position: vehicle position.
        :return: new vehicle.
        '''
        raise NotImplementedError
