import simplejson as json

from dataclasses import dataclass

class Configuration:
	@classmethod
	def read(cls, filename: str):
		with open(filename, 'r') as file:
			json_data = json.load(file)
			configuration = cls(**json_data)
		return configuration


@dataclass
class ConfigurationModelisation(Configuration):
	edge_color: "dict[str, str]"
	transports: "dict[str, dict]"

@dataclass
class ConfigurationHoraires(Configuration):
	dataset: str
	dataset_file_date: str
	route_ids: 'list[str]'
	station_freq: str
	service_id: int = None