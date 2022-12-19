import json
import sys
from concurrent.futures.thread import ThreadPoolExecutor
from typing import List, Dict, Union, Any
import time
from transport_api import TransportAPI, dataset_le_havre

import WazeRouteCalculator
from WazeRouteCalculator import WRCError

import fct_aux

def get_stops(direction: int = -1) -> List[Dict[str, Union[str, Any]]]:
    api = TransportAPI(dataset_le_havre)
    api.get_response_file()
    last_file = api.download_latest_file()

    trips = fct_aux.get_lia_data(last_file)

    trips['service_id'] = trips['service_id'].apply(lambda x: "Semaine" if "Semaine" in x else "WE")

    fields = ['stop_name', 'stop_lat', 'stop_lon', 'direction_id']
    # Drop other columns
    trips = trips.drop(axis="columns",
                       labels=[col for col in trips.columns.tolist() if col not in fields]).drop_duplicates()
    trips = trips.sort_values(by=fields)

    # Group by
    trips = trips.drop(axis="columns",
                       labels=[col for col in trips.columns.tolist() if
                               col not in fields + ['stop_id']]).drop_duplicates()

    if direction < 0:
        retour = [{
                'adr': trip[0],
                'coord': f"{trip[1]}, {trip[2]}"
            } for trip in zip(trips['stop_name'], trips['stop_lat'], trips['stop_lon'], trips['direction_id'])]
    else:
        retour = [{
            'adr': trip[0],
            'coord': f"{trip[1]}, {trip[2]}"
        } for trip in zip(trips['stop_name'], trips['stop_lat'], trips['stop_lon'], trips['direction_id']) if trip[3] == direction]

    return retour

def get_travel_time(from_ad, to_ad):
    region = 'EU'
    route = WazeRouteCalculator.WazeRouteCalculator(from_ad["coord"], to_ad["coord"], region)
    t = None
    while t is None:
        try:
            t = route.calc_route_info(real_time=False)
        except WRCError:
            pass
    return t[0]

def thread_call(from_ad, to_ad):
    if from_ad == to_ad:
        tps = 0
    else:
        tps = get_travel_time(from_ad, to_ad)
    dist[from_ad['adr']][to_ad['adr']] = tps

def update(future):
    global i, total
    if future.cancelled():
        print('cancelled\n')
    elif future.exception():
        print('except\n')
    else:
        i += 1
        fct_aux.print_progress_bar(i, total, suffix=f"({total})")

if __name__ == '__main__':
    global i, total, dist
    with open('adresses.json') as f:
        adresses = json.load(f)

    if len(sys.argv) <= 1 or sys.argv[1] != "NOTRAM":
        adresses += get_stops(1)

    i = 0
    total = pow(len(adresses), 2)
    dist = {}
    start_time = time.time()
    fct_aux.print_progress_bar(i, total, suffix=f"({total})")
    with ThreadPoolExecutor() as executor:
        for ad in adresses:
            dist[ad['adr']] = {}
            for dest in adresses:
                future = executor.submit(thread_call, ad, dest)
                future.add_done_callback(update)
    print(f"Temps exec : {time.time() - start_time}")

    fct_aux.write_matrice_distance(dist, "output/waze_temps_trajets.txt")
    with open('output/matrice_waze.json', 'w') as outfile:
        json.dump(dist, outfile)