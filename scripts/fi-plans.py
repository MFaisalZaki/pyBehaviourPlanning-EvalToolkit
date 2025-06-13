plans = [
'(navigate rover0 waypoint1 waypoint2)\n(sample_soil rover0 rover0store waypoint2)\n(navigate rover1 waypoint3 waypoint0)\n(communicate_soil_data rover0 general waypoint2 waypoint2 waypoint0)\n(sample_rock rover1 rover1store waypoint0)\n(navigate rover1 waypoint0 waypoint1)\n(calibrate rover1 camera1 objective0 waypoint1)\n(take_image rover1 waypoint1 objective0 camera1 colour)\n(communicate_rock_data rover1 general waypoint0 waypoint1 waypoint0)\n(communicate_image_data rover1 general objective0 colour waypoint1 waypoint0)\n; cost = 10 (unit cost)\n', 
'(calibrate rover0 camera1 objective0 waypoint1)\n(navigate rover1 waypoint3 waypoint0)\n(take_image rover0 waypoint1 objective0 camera1 colour)\n(communicate_image_data rover0 general objective0 colour waypoint1 waypoint0)\n(navigate rover0 waypoint1 waypoint2)\n(sample_soil rover0 rover0store waypoint2)\n(communicate_soil_data rover0 general waypoint2 waypoint2 waypoint0)\n(sample_rock rover1 rover1store waypoint0)\n(navigate rover1 waypoint0 waypoint3)\n(communicate_rock_data rover1 general waypoint0 waypoint3 waypoint0)\n; cost = 10 (unit cost)\n', 
'(calibrate rover0 camera1 objective0 waypoint1)\n(navigate rover1 waypoint3 waypoint0)\n(sample_rock rover1 rover1store waypoint0)\n(navigate rover1 waypoint0 waypoint2)\n(take_image rover0 waypoint1 objective0 camera1 colour)\n(communicate_rock_data rover1 general waypoint0 waypoint2 waypoint0)\n(communicate_image_data rover0 general objective0 colour waypoint1 waypoint0)\n(drop rover1 rover1store)\n(sample_soil rover1 rover1store waypoint2)\n(communicate_soil_data rover1 general waypoint2 waypoint2 waypoint0)\n; cost = 10 (unit cost)\n',
'(navigate rover1 waypoint3 waypoint0)\n(calibrate rover1 camera1 objective0 waypoint0)\n(take_image rover1 waypoint0 objective0 camera1 colour)\n(sample_rock rover1 rover1store waypoint0)\n(navigate rover1 waypoint0 waypoint2)\n(drop rover1 rover1store)\n(communicate_rock_data rover1 general waypoint0 waypoint2 waypoint0)\n(communicate_image_data rover1 general objective0 colour waypoint2 waypoint0)\n(sample_soil rover1 rover1store waypoint2)\n(communicate_soil_data rover1 general waypoint2 waypoint2 waypoint0)\n; cost = 10 (unit cost)\n',
'(calibrate rover0 camera1 objective0 waypoint1)\n(navigate rover0 waypoint1 waypoint0)\n(sample_rock rover0 rover0store waypoint0)\n(take_image rover0 waypoint0 objective0 camera1 colour)\n(navigate rover0 waypoint0 waypoint2)\n(drop rover0 rover0store)\n(communicate_rock_data rover0 general waypoint0 waypoint2 waypoint0)\n(communicate_image_data rover0 general objective0 colour waypoint2 waypoint0)\n(sample_soil rover0 rover0store waypoint2)\n(communicate_soil_data rover0 general waypoint2 waypoint2 waypoint0)\n; cost = 10 (unit cost)\n'
]

plans = list(map(lambda p:p.split('\n')[:-2], plans))

distances = []

for l, plan in zip(['D', 'E', 'F', 'G', 'H'], plans):
    for l2, plan2 in zip(['D', 'E', 'F', 'G', 'H'], plans):
        if l == l2: continue
        distances.append(f'{l}-{l2}: {round(1-len(set.intersection(set(plan), set(plan2)))/len(set.union(set(plan), set(plan2))),2)}')
        pass


pass