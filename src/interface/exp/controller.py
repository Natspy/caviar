import os
import datetime
import typing

from charts.informer import informer

def experiment(sim_info, **kwargs):

    penetration_list: list = kwargs["penetration_list"]
    num: int = kwargs['num']
    steps: int = kwargs['steps']
    skip: int = kwargs['skip']

    del sim_info["penetration"]
    length: int = sim_info['length']
    lanes: int = sim_info['lanes']
    emergency_lane: int = sim_info["emergency_lane"]
    max_speed: int = sim_info['max_speed']
    density: float = sim_info['density']
    dispatch: int = sim_info['dispatch']
    car_length: int = sim_info['car_length']
    emergency: int = sim_info['emergency']
    pslow: float = sim_info['pslow']
    pchange: float = sim_info['pchange']
    symmetry: str = "" if not sim_info["symmetry"] else "--symmetry"
    limit: int = sim_info['limit']

    if not sim_info["obstacles"]:
        obstacles: str = ""
    else:
        sim_info["obstacles"] = [f'{lane}:{begin}-{end}' for lane, begin, end in sim_info["obstacles"]]
        obstacles: str = f'--obstacles {", ".join(sim_info["obstacles"])}'
    seed: typing.Optional[int] = sim_info['seed'] if sim_info['seed'] is not None else ""


    if not os.path.isdir('./out'):
        os.mkdir('./out')

    date = datetime.datetime.now()
    name = str(date.date()) + '__' + str(datetime.time(date.hour, date.minute)).replace(':', '-')
    dir_name = os.path.join('out/', name)
    os.mkdir('./' + dir_name)

    informer(dir_name, steps = steps, skip = skip, num = num, penetration = penetration_list, **sim_info)

    for p in penetration_list:
        penetration = int(p * 100)
        prefix = f'p{penetration:02d}'
        for i in range(num):
            os.system(f'python src/main.py --penetration {p} --length {length} --lanes {lanes} --emergency-lane {emergency_lane} '
                      f'--max-speed {max_speed} {obstacles} --density {density} --dispatch {dispatch} '
                      f'--car-length {car_length} --emergency {emergency} --pslow {pslow} --pchange {pchange} '
                      f'{symmetry} --limit {limit} {seed} cli --steps {steps} --skip {skip} '
                      f'-o {dir_name} --prefix="{prefix}__{i:02d}" --no-charts --travel --heatmap')

        os.system(f'python src/charts/heatmap.py -o {dir_name}  -p {prefix}.traffic -s 5 {dir_name}/{prefix}__*_traffic.csv')
        os.system(f'python src/charts/travel.py -o {dir_name} -p {prefix}.travel'
                  f' {dir_name}/{prefix}__*_travel.csv')
        os.system(f'python src/charts/average.py -o {dir_name} -p {prefix}.average'
                  f' -x {penetration} {dir_name}/{prefix}__*_average.csv')

    os.system(f'python src/charts/average.py --output={dir_name} --prefix=average {dir_name}/*.average.csv')
    os.system(f'python src/charts/penetration.py --output={dir_name} --prefix=average {dir_name}/average.csv')
    if not emergency == 0:
        os.system(f'python src/charts/penetration_emergency.py --output={dir_name} --prefix=average_emergency {dir_name}/average.csv')
