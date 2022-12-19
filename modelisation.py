# coding=utf-8
import os.path
import sys

import geopandas as gpd
import matplotlib.pyplot as plt
import networkx as nx
import osmnx as ox

from configuration import ConfigurationModelisation


def get_location(arg: str = '') -> 'list[str]':
	# Définition de la ville
	if arg == "DEBUG":
		nom_villes = "Cauville-sur-Mer, Épouville, Fontaine-la-Mallet, Fontenay, Gainneville, Gonfreville-l'Orcher, Harfleur, Le Havre, Manéglise, Mannevillette, Montivilliers, Notre-Dame-du-Bec, Octeville-sur-Mer, Rogerville, Rolleville, Sainte-Adresse, Saint-Martin-du-Manoir"
	else:
		nom_villes = input("Saisissez le nom de la ou des villes : ")

	villes = []
	for ville in nom_villes.split(","):
		villes.append(ville.strip() + ", France")
	return villes

def load_settings() -> None:
	global configuration
	configuration = ConfigurationModelisation.read(
		'configuration_modelisation.json')
	
	ox.config(use_cache=True,
			  log_console= True,
			  useful_tags_way= ox.settings.useful_tags_way + ['railway', "public_transport"])

def load_data(city: 'list[str]') -> "dict[str, object]":
	# Récupération du graph de la ville (tous les éléments)
	G1 = ox.graph_from_place(city, network_type="drive")
	G2 = ox.graph_from_place(city, network_type="all")
	G = nx.compose(G1, G2)

	# Récupère la liste des edges du graph, insère la couleur voulue à l'emplacement de l'edge
	default_color = configuration.edge_color.pop("default")
	colors = configuration.edge_color.items()
	edge_color = [value if key in d else default_color for key, value in colors for _, _, d in G.edges(data=True)]

	transports_en_commun = {}
	for key, value in configuration.transports.items():
		transports_en_commun[key] = {
			"graph": ox.geometries_from_place(city, value["geometry"]) if "geometry" in value
				else gpd.read_file(value["file"]),
			"color": value["color"],
			"zorder": value["zorder"]
		}

	return {
		"city": G,
		"edges_color": edge_color,
		"transports": transports_en_commun
	}

def check_data(data: "dict[str, object]") -> None:
	data_to_delete= []
	for key, transport in data["transports"].items():
		if transport["graph"].size == 0:
			data_to_delete.append(key)

	for key in data_to_delete:
		del data["transports"][key]

def display_data(data: "dict[str, object]") -> None:
	fig, ax = ox.plot_graph(data["city"], bgcolor='k', edge_color=data["edges_color"],
						node_size=0, edge_linewidth=0.5,
						show=False, close=False)

	for transport in data["transports"].values():
		test = next(transport["graph"].iterfeatures())
		transport["graph"].plot(ax=ax, color=transport["color"], zorder=transport["zorder"])

	plt.show()

def export(data: "dict[str, object]") -> None:
	#Creation du dossier d'exports
	export_folder = os.path.join(os.getcwd(), "exports")
	if not os.path.exists(export_folder):
		os.mkdir(export_folder)

	#export de la ville en geojson
	G = data["city"]
	filenames = ["city_nodes.geojson", "city_edges.geojson"]

	#Conversion du MultiDiGraph en GeoDataFrame, la méthode renvoie un tuple que l'on fusionne
	gdfs = ox.utils_graph.graph_to_gdfs(G)
	for i in range(2):
		with open(os.path.join(export_folder, filenames[i]), "w") as f:
			f.write(gdfs[i].to_json())

	#export des transports
	for key, transport in data["transports"].items():
		geojson = transport["graph"].to_json()
		filename = key + ".geojson"
		with open(os.path.join(export_folder, filename), "w") as f:
			f.write(geojson)

if __name__ == '__main__':
	#"traitement global"
	if len(sys.argv) > 1:
		city = get_location(sys.argv[1])
	else:
		city = get_location()
	load_settings()
	data = load_data(city)
	check_data(data)
	display_data(data)
	#export(data)
