import argparse
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

from GTFSParser import GTFSParser
from configuration import ConfigurationHoraires
from transport_api import TransportAPI

_stop_name = 0
_stop_code = 1
_arrival_time = 2
_trip_id = 3


def get_horaires_tries(gtfs_file: str, route_ids: 'list[str]' = ["T-1406"],
					   drop: bool = True) -> "list[tuple]":

	global configuration
	trips = GTFSParser(gtfs_file, route_ids, configuration.service_id).parse_data()

	fields = ['service_id', 'stop_code', 'stop_name', 'arrival_time']
	# Drop other columns
	if drop:
		trips = trips.drop(axis="columns",
						   labels=[col for col in trips.columns.tolist() if col not in fields]).drop_duplicates()
	else:
		fields.append('trip_id')
	trips = trips.sort_values(by=fields)

	if drop:
		return [x for x in zip(trips['stop_name'], trips['stop_code'], trips['arrival_time'])]
	else:
		return [x for x in zip(trips['stop_name'], trips['stop_code'], trips['arrival_time'],
							   trips['trip_id'])]


def write_horaires(horaires: "list[tuple]", output_file: str):
	result_str = '\n'.join(f"{x[0]} {x[1][-1]} {x[2]}" for x in horaires)
	with open(output_file, "w") as output:
		output.write(result_str)


def horaire_to_int(horaire: str) -> int:
	time = horaire.split(':')
	time = 3600 * int(time[0]) + 60 * int(time[1]) + int(time[2])
	return time


def int_to_horaire(time: int) -> str:
	hour = time // 3600
	minute = (time % 3600) // 60
	second = time % 60
	return f"{hour:02d}:{minute:02d}:{second:02d}"


def frequence_tram(horaires: "list[tuple]", station):
	print("Fréquence des tramway")
	horairesPlage = []
	for tuple in horaires:
		if tuple[_stop_name] == station and int(tuple[_stop_code][-1]) % 2 == 0:
			horairesPlage.append(horaire_to_int(tuple[_arrival_time]))

	freq = []
	freq2 = []
	mean = 0
	horairesPlage2 = []
	for i in range(len(horairesPlage) - 1):
		currentTime = horairesPlage[i]
		nextTime = horairesPlage[i + 1]
		difTime = nextTime - currentTime
		if difTime > 0:
			freq.append(difTime)
			freq2.append(difTime / 60)
			mean += difTime
			horairesPlage2.append(currentTime / 3600)
	mean /= len(freq)
	horairesPlage = horairesPlage2

	print("Moyenne   : " + str(mean))
	print("Minimum   : " + str(min(freq)))
	print("Maximum   : " + str(max(freq)))
	print("Quartiles :")
	print(pd.DataFrame(freq).quantile([0.25, 0.5, 0.75]))

	plt.plot(horairesPlage, freq2)
	plt.title("Fréquence de passage de tram ("+station+") au fil du temps")
	plt.xticks([i for i in range(4, 25)])
	plt.xlabel("Heure")
	plt.ylabel("Temps avant prochain départ en minute")
	plt.show()


def distances_voisins(horaires: "list[tuple]") -> "list[tuple]":
	horaires.sort(key=lambda x: (x[_trip_id], x[_arrival_time]))
	voisins = []
	last_trip = ''
	last_tuple = ''
	ligne = []
	for (stop_code, stop_name, arrival_time, trip_id) in horaires:
		if last_trip and last_trip != trip_id:
			doAppend = True
			for ligneVoisins in voisins:
				if set(ligneVoisins).issubset(set(ligne)):
					doAppend = False
					break
			if doAppend:
				voisins.append(ligne)
			ligne = []
		if last_trip != trip_id or stop_code != last_tuple and last_trip == trip_id:
			ligne.append(stop_code)
		last_trip = trip_id
		last_tuple = stop_code

	# Tableau associatif de distances entre stations voisines
	# De la forme : 'Station1---Station2' -> [sommeDistances, nbSommes]
	# Et sert à calculer ensuite les moyennes de distances entre stations voisines
	tabDistances = {}
	for idLigne in range(2):
		for idStation in range(len(voisins[idLigne]) - 1):
			key1 = voisins[idLigne][idStation] + \
				'---' + voisins[idLigne][idStation + 1]
			key2 = voisins[idLigne][idStation + 1] + \
				'---' + voisins[idLigne][idStation]
			tabDistances[key1] = [0, 0]
			tabDistances[key2] = [0, 0]

	horaires.sort(key=lambda x: (x[_trip_id], x[_arrival_time]))
	last_tuple = None
	for tuple in horaires:
		if last_tuple and last_tuple[_trip_id] == tuple[_trip_id] and not last_tuple == tuple:
			lastTime = horaire_to_int(last_tuple[_arrival_time])
			currentTime = horaire_to_int(tuple[_arrival_time])
			tabDistances[last_tuple[_stop_name] + '---' + tuple[_stop_name]][0] += currentTime - lastTime
			tabDistances[last_tuple[_stop_name] + '---' + tuple[_stop_name]][1] += 1
		last_tuple = tuple

	for keyDistance in tabDistances:
		tabDistances[keyDistance][0] = tabDistances[keyDistance][0] / \
			tabDistances[keyDistance][1]

	return tabDistances


def distances(horaires: "list[tuple]") -> "list[tuple]":
	tabDistancesVoisins = distances_voisins(horaires)
	tabStations = []
	for keyDistance in tabDistancesVoisins:
		station = keyDistance.split('---')[0]
		if not station in tabStations:
			tabStations.append(station)

	G = nx.DiGraph()
	for station in tabStations:
		G.add_node(station)
	for keyDistance in tabDistancesVoisins:
		stations = keyDistance.split('---')
		G.add_edge(stations[0], stations[1],
				   weight=tabDistancesVoisins[keyDistance][0])

	paths = nx.floyd_warshall(G)
	return paths


def write_matrice_distance(paths: "list[tuple]", output_file="output/matrice_dist.txt"):
	maxLen = 0
	for source in paths:
		maxLen = max(maxLen, len(source))
	result = "---- Matrice des temps ----\n"
	result += ("{space:" + str(maxLen + 1) + "s}").format(space='')
	for target in paths:
		result += target + " "
	result += "\n"
	for source in paths:
		result += ("{name:" + str(maxLen) + "s}").format(name=source) + " "
		for target in paths:
			path = paths[source][target]
			path = ("{value:" + str(len(target)) + ".0f}").format(value=path)
			result += path + " "
		result += "\n"
	result += "\n"

	with open(output_file, "w") as output:
		output.write(result)


if __name__ == '__main__':
	global configuration
	parser = argparse.ArgumentParser(description='script horaires')
	parser.add_argument('--config', type=str)
	args = parser.parse_args()
	configuration = ConfigurationHoraires.read(args.config or 'configuration_horaires.json')

	api = TransportAPI(configuration.dataset)
	api.get_response_file()
	gtfs_file = api.download_latest_file() if configuration.dataset_file_date == 'latest' \
		else api.get_file_from_date(configuration.dataset_file_date)

	horaires = get_horaires_tries(gtfs_file, configuration.route_ids, drop=False)
	write_horaires(horaires, "output/horaires_output.txt")
	frequence_tram(horaires, configuration.station_freq)
	print('')
	paths = distances(horaires)
	write_matrice_distance(paths)
