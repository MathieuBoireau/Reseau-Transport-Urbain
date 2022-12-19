from zipfile import ZipFile

import pandas as pd
import fct_aux

class GTFSParser:
    gtfs_file: str
    route_ids: 'list[str]'
    service_id: str
    date_debut: str
    date_fin: str

    def __init__(self, file: str, route_ids: 'list[str]', default_service_id: int = None):
        self.gtfs_file = file
        self.route_ids = route_ids
        self.default_service_id = default_service_id

    # Récupère le service_id en fonction des routes données puis renvoie les trips associés
    def parse_data(self):
        self.get_service_ids()
        routes = "','".join(self.route_ids)
        query = f"route_id in ('{routes}') and service_id in ('{self.service_id}')"

        trips = GTFSParser.get_trips(self.gtfs_file, query)
        return trips

    # En fonction de la disponibilité de calendar et calendar_date, récupère les service_ids possibles par rapport aux routes puis demande à l'utilisateur lequel garder
    def get_service_ids(self):
        service_id = None
        with ZipFile(self.gtfs_file, "r") as zip_file:
            # Lecture des fichiers
            # Récupère les service_ids correspondant aux jours de la semaine
            calendar = pd.read_csv(zip_file.open("calendar.txt")).query(
                "monday == 1 and tuesday == 1 and wednesday == 1 and thursday == 1 and friday == 1 and saturday == 0 and sunday == 0"
            )
            # Si calendar est vide, on récupère les service_ids depuis calendar_dates
            if calendar.empty:
                calendar_dates = pd.read_csv(zip_file.open("calendar_dates.txt"))
                # On convertie les dates au format YYmmdd
                calendar_dates['date'] = pd.to_datetime(calendar_dates['date'], format='%Y%m%d')

                calendar = calendar_dates[calendar_dates['date'].dt.weekday < 5] # Monday to Friday
                # On supprime les service_ids des weekends
                calendar = calendar_dates[calendar_dates['date'].dt.weekday < 5]  # Monday to Friday

                # On récupère les noms des service_ids sans duplicat
                service_ids = set(calendar['service_id'])

                #Dictionnaire contenant tous les service_ids avec leurs dates de début et fin
                result = {"service_id": [], "start_date": [], "end_date": []}
                for service in service_ids:
                    result["service_id"].append(service)
                    # Récupération de toutes les dates du service_id
                    tmp = calendar.query(f"service_id in ('{service}')")
                    dates = tmp['date']
                    result["start_date"].append(min(dates))
                    result["end_date"].append(max(dates))
                # Convertion du dictionnaire en un DataFrame
                calendar = pd.DataFrame.from_records(data=result)

            # S'il y a plusieurs service_ids possibles
            if len(calendar) > 1:
                trips = pd.read_csv(zip_file.open("trips.txt")).query(
                    "route_id in ('" + "','".join(self.route_ids) + "') and service_id in ('" + "','".join(
                        calendar['service_id']) + "')"
                )
                service_ids = set(trips['service_id'])
                calendar = calendar.query("service_id in ('" + "','".join(service_ids) + "')")
                possibles = sorted([x for x in zip(calendar['service_id'], calendar['start_date'], calendar['end_date'])], key=lambda x: x[1])
                if len(possibles) > 1:
                    service_id = possibles[(self.default_service_id or self.ask_user(possibles)) - 1][0]
                else:
                    service_id = possibles[0][0]
        self.service_id = service_id

    # Demande à l'utilisateur quel service_id choisir
    def ask_user(self, service_ids: 'list[tuple]') -> int:
        print("Plusieurs service_id sont disponibles, veuillez en choisir un pour la récupération des horaires : ")
        for i, (service_id, date_debut, date_fin) in enumerate(service_ids):
            print(
                f"[{i + 1}] {service_id}, date de début : {date_debut}, date de fin : {date_fin}")
        return fct_aux.get_int_input()

    @staticmethod
    def get_trips(gtfs_file: str, query: str):
        with ZipFile(gtfs_file, "r") as zip_file:
            # Lecture des fichiers
            trips = pd.read_csv(zip_file.open("trips.txt")).query(query)
            stops = pd.read_csv(zip_file.open("stops.txt"), na_filter=False)
            stop_times = pd.read_csv(zip_file.open("stop_times.txt"))

        # Join on trip_id
        trips = pd.merge(trips, stop_times, on="trip_id")
        # Join on stop_id
        trips['stop_id'] = trips['stop_id'].astype(str)
        trips = pd.merge(trips, stops, on="stop_id")

        return trips
