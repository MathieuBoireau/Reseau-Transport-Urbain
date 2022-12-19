import logging
from itertools import tee
from typing import TypeVar
from zipfile import ZipFile

import pandas as pd


T = TypeVar('T')
def pairwise(iterable: T) -> 'tuple[T, T]':
	""" pairwise() from Itertools Recipes """
	a, b = tee(iterable)
	next(b, None)
	return zip(a, b)


def static_logger(cls, level='INFO', formatter=logging.Formatter('[%(asctime)s] [%(name)s/%(levelname)s]: %(message)s', '%H:%M:%S')):
	""" Met à disposition un objet logger. """
	def init_logger(cls):
		cls.logger = logging.getLogger(cls.__name__)
		cls.logger.setLevel(level)
		handler = logging.StreamHandler()
		handler.setFormatter(formatter)
		cls.logger.addHandler(handler)

	init_logger(cls)
	return cls

def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
	"""
	Call in a loop to create terminal progress bar
	@params:
		iteration   - Required  : current iteration (Int)
		total       - Required  : total iterations (Int)
		prefix      - Optional  : prefix string (Str)
		suffix      - Optional  : suffix string (Str)
		decimals    - Optional  : positive number of decimals in percent complete (Int)
		length      - Optional  : character length of bar (Int)
		fill        - Optional  : bar fill character (Str)
		printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
	"""
	percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
	filledLength = int(length * iteration // total)
	bar = fill * filledLength + '-' * (length - filledLength)
	print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
	# Print New Line on Complete
	if iteration == total:
		print()

def get_int_input() -> int:
	while True:
		try:
			s = int(input('choix : '))
		except ValueError:
			pass
		else:
			break
	return s

def write_matrice_distance(paths, output_file="tmp.txt"):
	maxLen = 0
	for source in paths:
		maxLen = max(maxLen, len(source))
	result = ""
	result += "---- Matrice des temps des trajet ----\n"
	result += ("{space:" + str(maxLen + 1) + "s}").format(space='')
	for target in paths:
		result += target + " "
	result += "\n"
	for source in paths:
		result += ("{name:" + str(maxLen) + "s}").format(name=source) + " "
		for target in paths:
			path = paths[source][target]
			path = ("{value:" + str(len(target)) + ".0f}").format(value=path * 60)
			result += path + " "
		result += "\n"
	result += "\n"

	with open(output_file, "w") as output:
		output.write(result)

def get_lia_data(gtfs_file: str) -> pd.DataFrame:
	with ZipFile(gtfs_file, "r") as zip_file:
		# Lecture des fichiers
		trips: pd.DataFrame = pd.read_csv(zip_file.open("trips.txt")).query(
			"service_id in ('2021-22-GSemHTra-Semaine-00')")
		# "route_id in ('T-1406') and service_id in ('2021-22-GPVSTra-Semaine-00')")
		stops: pd.DataFrame = pd.read_csv(zip_file.open("stops.txt"), na_filter=False).drop(
			axis="columns", labels=["stop_desc", "zone_id", "stop_url", "location_type"])
		stop_times: pd.DataFrame = pd.read_csv(zip_file.open("stop_times.txt")).drop(
			axis="columns", labels=["pickup_type", "drop_off_type", "shape_dist_traveled", "timepoint"])

	# Join on trip_id
	trips = pd.merge(trips, stop_times, on="trip_id")
	# Join on stop_id
	trips['stop_id'] = trips['stop_id'].astype(str)
	trips = pd.merge(trips, stops, on="stop_id")

	return trips
