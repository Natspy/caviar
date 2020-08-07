import typing

import pandas as pd
from more_itertools import ilen

from simulator.road.road import Road
from simulator.simulator import Hook, Simulator
from simulator.statistics.averageresult import AverageResult
from simulator.statistics.filters import Filter, combine
from simulator.statistics.vehicletype import VehicleType, getVehicleTypeFilter, getVehicleTypeName
from simulator.vehicle.car import Car
from simulator.vehicle.vehicle import Vehicle
from util.cumulativelist import CumulativeList
from util.dict import makeOrderedDict


class Tracker(Hook):
    steps: int
    velocity: typing.Dict[VehicleType, CumulativeList[AverageResult]]
    throughput: typing.Dict[VehicleType, CumulativeList[int]]
    decelerations: typing.Dict[VehicleType, CumulativeList[int]]
    lane_changes: typing.Dict[VehicleType, CumulativeList[int]]
    waiting: typing.Dict[VehicleType, CumulativeList[int]]

    def __init__(self, simulator: Simulator, buffer_size: int = 1):
        super().__init__(simulator=simulator)
        self.steps = 0
        self.velocity = {}
        self.throughput = {}
        self.decelerations = {}
        self.lane_changes = {}
        self.waiting = {}
        for vehicle_type in VehicleType:
            self.velocity[vehicle_type] = CumulativeList(buffer_size, AverageResult(0, 0))
            self.throughput[vehicle_type] = CumulativeList(buffer_size, 0)
            self.decelerations[vehicle_type] = CumulativeList(buffer_size, 0)
            self.lane_changes[vehicle_type] = CumulativeList(buffer_size, 0)
            self.waiting[vehicle_type] = CumulativeList(buffer_size, 0)

    @property
    def _road(self) -> Road:
        return self.simulator.road

    def run(self) -> None:
        self.steps += 1
        for vehicle_type in VehicleType:
            predicate = getVehicleTypeFilter(vehicle_type)
            self.velocity[vehicle_type].append(self._trackVelocity(predicate))
            self.throughput[vehicle_type].append(self._trackThroughput(predicate))
            self.decelerations[vehicle_type].append(self._trackDecelerations(predicate))
            self.lane_changes[vehicle_type].append(self._trackLaneChanges(predicate))
            self.waiting[vehicle_type].append(self._trackWaiting(predicate))

    def _trackVelocity(self, predicate: Filter) -> AverageResult:
        velocity, count = 0, 0
        for vehicle in filter(predicate, self._road.getAllActiveVehicles()):
            velocity += vehicle.velocity
            count += 1
        return AverageResult(value=velocity, count=count)

    def getAverageVelocity(self, vehicle_type: VehicleType) -> typing.Optional[float]:
        return self.velocity[vehicle_type].value().toMaybeFloat()

    def _trackThroughput(self, predicate: Filter) -> int:
        return ilen(filter(predicate, self._road.removed))

    def getAverageThroughput(self, vehicle_type: VehicleType) -> float:
        return self.throughput[vehicle_type].value() / len(self.throughput[vehicle_type])

    def _trackDecelerations(self, predicate: Filter) -> int:
        def isDeceleration(vehicle: Vehicle) -> bool:
            if not isinstance(vehicle, Car):
                return False
            _, last_velocity = vehicle.path[-1]
            return last_velocity - vehicle.velocity > 1

        return ilen(filter(combine(predicate, isDeceleration), self._road.getAllActiveVehicles()))

    def getAverageDecelerations(self, vehicle_type: VehicleType) -> float:
        return self.decelerations[vehicle_type].value() / len(self.decelerations[vehicle_type])

    def _trackLaneChanges(self, predicate: Filter) -> int:
        def isLaneChange(vehicle: Vehicle) -> bool:
            _, last_lane = vehicle.last_position
            _, lane = vehicle.position
            return last_lane != lane

        return ilen(filter(combine(predicate, isLaneChange), self._road.getAllActiveVehicles()))

    def getAverageLaneChanges(self, vehicle_type: VehicleType) -> float:
        return self.lane_changes[vehicle_type].value() / len(self.lane_changes[vehicle_type])

    def _trackWaiting(self, predicate: Filter) -> int:
        def isWaiting(vehicle: Vehicle) -> bool:
            return vehicle.position == vehicle.last_position

        return ilen(filter(combine(predicate, isWaiting), self._road.getAllActiveVehicles()))

    def getAverageWaiting(self, vehicle_type: VehicleType) -> float:
        return self.waiting[vehicle_type].value() / len(self.waiting[vehicle_type])

    def getAverageData(self) -> pd.DataFrame:
        statistics = {}
        for vehicle_type in VehicleType:
            name = getVehicleTypeName(vehicle_type)
            statistics[f'velocity_{name}'] = self.getAverageVelocity(vehicle_type)
            statistics[f'throughput_{name}'] = self.getAverageThroughput(vehicle_type)
            statistics[f'decelerations_{name}'] = self.getAverageDecelerations(vehicle_type)
            statistics[f'laneChanges_{name}'] = self.getAverageLaneChanges(vehicle_type)
            statistics[f'waiting_{name}'] = self.getAverageWaiting(vehicle_type)

        return pd.DataFrame(makeOrderedDict(statistics, AVERAGE_DATA_ORDER), index=[0])


# Order for the average statistics.
AVERAGE_DATA_KEYS = ['velocity', 'throughput', 'decelerations', 'laneChanges', 'waiting']
AVERAGE_DATA_ORDER = []
for key in AVERAGE_DATA_KEYS:
    for vehicle_type in VehicleType:
        name = getVehicleTypeName(vehicle_type)
        AVERAGE_DATA_ORDER.append(f'{key}_{name}')
