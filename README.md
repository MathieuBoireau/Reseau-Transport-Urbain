Projet étudiant - 5 mai 2022

# TPE Extraction de donnees pour un réseau de Transport Urbain

## Auteurs

|Nom|Prénom|login|email|
|--|--|--|--|
| BOIREAU | Mathieu | bm180551 | mathieu.boireau@etu.univ-lehavre.fr |
| COUFOURIER | Guillaume | cg180730 | guillaume.coufourier@etu.univ-lehavre.fr |
| PRUNIER | Sébastien | ps180437 | sebastien.prunier@etu.univ-lehavre.fr |

## Modélisation d'une ville

Le programme `modelisation.py` permet la modélisation d'une ville, en affichant ses routes et lignes de trams, si elles sont disponibles.

### Utilisation

Exécuter le programme avec Python. Lors de l'exécution, il sera demandé à l'utilisateur d'entrer le nom de la ville désirée. Si plusieurs villes doivent être modélisées, les noms doivent être séparés par des virgules.
Ex : 

```
Le Havre, Octeville-Sur-Mer
```

Il est possible de directement modéliser toute l'agglomération du Havre. Pour se faire, exécuter le programme avec le paramètre DEBUG

```
python ./modelisation.py DEBUG
```

A la fin de l'exécution, le programme affichera la modélisation de la ou les villes, selon les précisions du fichier de configuration.

### Modification de l'affichage

Il est possible d'ajouter ou supprimer des transports en commun, ainsi que de modifier leur couleur/agencement.
Pour ce faire, il faut modifier le fichier `configuration.json`. Ce fichier contient un dictionnaire composé de 2 sous-dictionnaires :

#### edge_color

Ce dictionnaire répertorie la couleur des arcs générés par OSMnx. La couleur est indiquée par sa première lettre (en anglais).
"highway" est la couleur des routes de l'arc, "default" est la couleur de tous les autres arcs.

#### transports

Ce dictionnaire répertorie tous les transports en communs désirés.
Il est possible d'ajouter un nouveau transport en commun en respectant ce format : 

```
"{nom du transport}": {
	"geometry": {
		"{key}": "{tag}"
	},
	"color": "{couleur}",
	"zorder": {index}
}
```

- nom du transport : nom du transport en commun voulu. Ce nom ne sert qu'à distinguer chaque transport et son choix est donc laissé à l'utilisateur.
- key et tag : clé et tag du transport, défini par OpenStreetMap. Ils peuvent être trouvés depuis [la documentation OpenStreetMap](https://wiki.openstreetmap.org/wiki/Features). Par exemple, [pour le tramway](https://wiki.openstreetmap.org/wiki/Key:railway#railway-tram).
- couleur : couleur du transport lors de l'affichage, le format est en héxadécimal.
- index : Position Z du transport. Plus il est élevé, plus le transport est en premier plan.

Il est également possible d'importer des données géométrique. Pour ce faire, remplacer la partie "geometry" par "file", en indiquant le lien vers le fichier
Ex :

```json
{
	"{nom du transport}": {
		"file": "extensions/fichier.geojson",
		"color": "{couleur}",
		"zorder": "{index}"
	}
}
```

## Horaires de tram

Le fichier `horaires.py` permet la récupération automatique des données de tram de LiA, ainsi que la création d'une matrice de temps de trajet entre chaque arrêt de tram.

### Utilisation

Exécuter le fichier `horaires.py` avec Python. Un fichier `horaires_output.txt`, indiquant les horaires de tous les trams pour chaque arrêt, est créé dans le dossier `output`. La moyenne ainsi que les quartiles des temps de trajet sont indiqués dans la console.
Egalement, la matrice des temps de trajet entre chaque arrêt est sauvegardée dans un fichier `matrice_dist.txt` dans le dossier `output`. 

### Modification

La source des données peut être modifiée en passant avec le paramètre `--config` un fichier JSON.

```json
{
	"dataset": "{URL de l'api transport.data.gouv.fr}",
	"dataset_file_date": "{date au format YYYY-MM-DD | latest}",
	"route_ids": ["{route_id présents dans trips.txt du fichier GTFS}"],
	"station_freq": "{nom de la station pour laquelle la matrice des temps est créée}",
	"service_id": "optionnel: un entier qui indique l'id du service_id à choisir lorsqu'il y en a plusieurs"
}
```

## Temps de trajet Waze

Le programme `waze_trajet.py` permet le calcul d'une matrice des temps de trajet entre plusieurs adresses et les arrêts de tram, en utilisant l'API Waze.

### Utilisation

Exécuter le fichier `waze_trajet.py`. Le programme est un peu long (environs 10min, en fonction de la machine), et sauvegarde la matrice calculée dans 2 fichiers différents dans le dossier `output` : `waze_temps_trajets.txt`, contenant la matrice formatée pour être lu, et `matrice_waze.json` contenant la matrice au format JSON, afin de faciliter l'importation dans un autre programme.

### Modification

Il est possible d'ajouter ou d'enlever des adresses à utiliser en modifiant le fichier `adresses.json`, contenant un tableau d'objets représentant chacun une adresse.
Pour ajouter une adresse, ajouter un objet au tableau en respectant ce format :

```json
{
	"adr": "{adresse à afficher dans la matrice}",
	"coord": "{latitude}, {longitude}"
}
```

Il est également possible de ne pas ajouter les arrêts de tram dans la matrice à calculer. Pour ce faire, exécuter `waze_trajet.py` avec le paramètre `NOTRAM`.
