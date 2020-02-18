import typing

from simulator.position import Position
from simulator.road.speedcontroller import SpeedController
from simulator.vehicle.vehicle import Vehicle


class Road:
    controller: SpeedController

    # Road options.
    length: int
    lanes_count: int

    def __init__(self, length: int, lanes_count: int,
                 controller: typing.Optional[SpeedController] = None):
        self.length = length
        self.lanes_count = lanes_count
        self.controller = controller if controller is not None else SpeedController()

    def addVehicle(self, position: Position, vehicle: Vehicle) -> None:
        '''
        Adds a new vehicle to the road.
        :param position: position on the road.
        :param vehicle: vehicle to add.
        :return: None.
        '''
        raise NotImplementedError()

    def getVehicle(self, position: Position) -> typing.Optional[Vehicle]:
        '''
        Gets a vehicle from the road.
        :param position: position on the road.
        :return: a vehicle currently at the given position or None.
        '''
        raise NotImplementedError()

    def getAllVehicles(self) -> typing.Generator[Vehicle, None, None]:
        '''
        Gets all the vehicles on the road.
        :return: generator yielding all the vehicles.
        '''
        raise NotImplementedError()

    def addPendingVehicle(self, position: Position, vehicle: Vehicle) -> None:
        '''
        Adds the vehicle to the road which will be added on the next commit.
        :param position: position on the road.
        :param vehicle: vehicle to add.
        :return: None.
        '''
        raise NotImplementedError

    def getNextVehicle(self, position: Position) -> typing.Tuple[int, typing.Optional[Vehicle]]:
        '''
        Gets the vehicle in front of a given position.
        :param position: position on the road.
        :return: position and the vehicle or None.
        '''
        raise NotImplementedError()

    def getMaxSpeed(self, position: Position) -> int:
        '''
        Gets maximum speed at the given position of the road.
        :param position: position on the road.
        :return: maximum allowed speed.
        '''
        next, vehicle = self.getNextVehicle(position=position)
        if vehicle is None:
            return self.controller.getMaxSpeed(position)
        else:
            return min(self.controller.getMaxSpeed(position), next - position[0])

    def isProperPosition(self, position: Position) -> bool:
        '''
        Checks if a position is a proper position on the road.
        :param position: position on the road.
        :return: if a position is on the road.
        '''
        x, lane = position
        return lane >= 0 and lane < self.lanes_count and x >= 0 and x < self.length

    def _commitLanes(self) -> None:
        '''
        Moves the pending vehicles to the actual road and clears the pending road.
        :return: None.
        '''
        raise NotImplementedError()

    def _updateLanes(self, f: typing.Callable[[Vehicle], Position]) -> None:
        '''
        Performs an update function on each of the vehicles on the road. Actions are
        performed at the same time on each of the vehicles and the road gets committed.
        :param f: update function.
        :return: None.
        '''
        for vehicle in self.getAllVehicles():
            x, i = f(vehicle)
            if x < self.length:
                self.addPendingVehicle(position=(x, i), vehicle=vehicle)
        self._commitLanes()

    def step(self) -> None:
        '''
        Performs a single simulation step moving all the vehicles.
        :return: None.
        '''
        self._updateLanes(lambda vehicle: vehicle.beforeMove())
        self._updateLanes(lambda vehicle: vehicle.move())

    # Statistics
    def getAverageVelocity(self) -> float:
        velocity, count = 0, 0
        for vehicle in self.getAllVehicles():
            velocity += vehicle.velocity
            count += 1
        return float(velocity) / count if count > 0 else 0.