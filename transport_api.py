import datetime
from collections import OrderedDict
from pathlib import Path
from time import strptime, struct_time
from fct_aux import pairwise, static_logger

import requests
import simplejson as json

dataset_le_havre = 'https://transport.data.gouv.fr/api/datasets/617c12b7f9aaa6853cf6d303'
dataset_grenoble = "https://transport.data.gouv.fr/api/datasets/5af03701b595081c1880a8a4"

@static_logger
class TransportAPI:
	"""
	## TransportAPI
	Usage typique de la classe:
	>>> api = TransportAPI(url)
	>>> api.get_response_file()
	>>> gtfs_file = api.download_latest_file()
	"""
	response: str
	files: 'OrderedDict[str, str]' = None

	def __init__(self, api_url):
		self.api_url = api_url
		self.cwd = Path.cwd()
		self.cache_dir = self.cwd / 'cache/transport'
		dataset = api_url[api_url.rindex('/') + 1:]
		self.cache_file = self.cache_dir / f'{dataset}.json'
		self.output_dir = self.cwd / 'horaires'

	def get_response_file(self):
		""" Récupère les détails sur les données par un appel à l'API. """
		self.cache_dir.mkdir(parents=True, exist_ok=True)

		# retrieve from cache
		if self.is_response_outdated(self.cache_file):
			self.logger.info("Appel à l'API transport.data.gouv.fr")
			response = requests.get(self.api_url)
			with self.cache_file.open('wb') as output:
				output.write(response.content)
				self.response = response.json()
		else:
			self.logger.info(f"Lecture du fichier mis en cache {self.cache_file.relative_to(self.cwd)}")
			with self.cache_file.open('r') as input:
				self.response = json.load(input)

	def download_latest_file(self) -> str:
		""" Télécharge le fichier le plus récent et retourne le chemin où ce dernier est stocké. """
		current = self.response['resources'][0]
		url = current['original_url']
		output_file = self.output_dir / (url.split('/')[-1])
		self.logger.info(f"Fichier le plus récent : {output_file.relative_to(self.cwd)}")
		self.download_file(url, output_file)

		return output_file.absolute()
	
	def download_file(self, url: str, output_file: Path) -> None:
		""" Télécharge un fichier à l'url donnée et le stocke dans le fichier output_file. """
		if not output_file.exists():
			self.logger.info(f"Téléchargement de {url}")
			file = requests.get(url)
			with output_file.open( "wb") as f:
				f.write(file.content)
			self.logger.info(f"Données GTFS écrites dans {output_file.relative_to(self.cwd)}")

	def get_file_from_date(self, file_date: str) -> str:
		date = self.date_str_to_struct_time(file_date)
		""" Télécharge le fichier qui correspond à la date donnée, ou le plus récent si la date n'existe pas. """
		if not self.files:
			d = {f['payload']['download_datetime']: f['payload']['permanent_url'] for f in self.response['history']}
			self.files = OrderedDict(sorted(d.items()))

		for (dl_date1, file1), (dl_date2, file2) in pairwise(self.files.items()):
			dl = self.iso_str_to_struct_time(dl_date1)
			dl2 = self.iso_str_to_struct_time(dl_date2)
			# date in range ?
			if date >= dl and date < dl2:
				output_file = self.output_dir / (file1.split('/')[-1])
				self.logger.info(f"Récupération des données du {dl.tm_year}-{dl.tm_mon}-{dl.tm_mday}")
				self.download_file(file1, output_file)
				break
		else:
			output_file = self.output_dir / self.download_latest_file()
		
		return output_file.absolute()
		
	@staticmethod
	def is_response_outdated(cache_file: Path) -> bool:
		if not cache_file.exists():
			return True
		cache_mtime = cache_file.stat().st_mtime
		# cache expires after 24 hours
		next_mtime = cache_mtime + 60 * 60 * 24

		return datetime.datetime.now().timestamp() > next_mtime

	@staticmethod
	def iso_str_to_struct_time(str: str) -> struct_time:
		return strptime(str, '%Y-%m-%dT%H:%M:%S.%fZ')

	@staticmethod
	def date_str_to_struct_time(str: str) -> struct_time:
		return strptime(str, '%Y-%m-%d')

if __name__ == '__main__':
	# Tests
	dataset_grenoble = 'https://transport.data.gouv.fr/api/datasets/5af03701b595081c1880a8a4'
	api = TransportAPI(dataset_grenoble)
	latest_file = api.get_response_file()
	file_at_date = api.get_file_from_date('2022-01-01')
	print(file_at_date)
	print(api.files)
