Les instances sont formées de plusieurs fichiers:
- Les matrices de temps:
	* Matrice M_door_door.txt: le temps en minutes d'aller d'une porte à une porte en voiture. La premiere ligne et colonne correspondent au depot.
	* Matrice M_door_station.txt: le temps d'aller d'une porte a une station en voiture
	* Matrice M_station_station.txt: le temps d'aller d'une station a une station en voiture
	* Matrice M_tram.txt: le temps d'aller d'une station a une station en transport en commun
 La matrice pour aller d'une station a une porte n'est pas incluse dans le projet pour le moment. Ca sera le meme temps de pour aller de cette porte a cette station.
- Un probleme qui contient:
	* Première ligne: le nombre de portes (toujours egal à 13: depot + 12 portes)
	* Seconde ligne: le nombre de stations (toujours egal à 23)
	* Troisième ligne: le nombre de vehicule et leur capacite.
	* Quatrieme ligne: le nombre de requetes
	* Lignes suivantes. Un requete par ligne avec 
		+ en argument 0 le pickup point
		+ en argument 1 et 2, la fenetre de temps associe au pickup point (l'utilisateur doit partir dans cette fenetre de temps)
		+ en argument 3 le delivery point
		+ en argument 4 et 5, la fenetre de temps associe au delivery point (l'utilisateur doit arriver dans cette fenetre de temps)
		+ en argument 6, le temps maximum de trajet.
		+ en dernier argument le nombre de voyageurs, toujours egale a 1.
- Une solution qui contient:
	* Premiere ligne: le nombre de requetes
	* Par paire de 2 lignes jusqu'a la fin du fichier:
		+ 0 si la requete n'utilise pas de transfert; 1 si elle en utilise un
		+ Si elle n'utilise pas de transfert: [temps au pickup point; vehicule en charge; temps au delivery point]
		  Si elle utilise un transfert: [temps au pickup point; vehicule en charge; temps a la premiere station; indice de la premiere station;
		  								 indice de la seconde station; temps a la seconde station; vehicule en charge; temps au delivery point]
		  								
Autres informations:
- Une route commence et finit au depot. Ce depot est l'arret Grand Hameau. Il a ete ajoute a M_door_door et M_door_station.
- Il y a un temps de chargement quand on prend les requetes de 1 minute. "temps au pickup point" est le temps d'arrive du vehicule au pickup point.
  Il repart a "temps au pickup point + 1 minute". "temps au delivery point" est le temps de depart du vehicule du delivery point.
  Il arrive donc a "temps au delivery point - 1 minute". Je ne sais pas si cette information va vous servir, je vous la donne au cas ou.
- Je vous ai donne beaucoup de donnees dont certaines qui me semblent inutiles pour vous (notament dans la description des requetes). 
  Vous n'etes pas oblige de tout exploiter. 
 
Il n'y a pas les routes ecrites dans le fichiers solutions. Ce sont juste des informations relatives aux requetes. 
Le fichier python lit le probleme, la solution et transforme les informations sur les requetes en routes.
Les structures de donnees sont expliquees dans le fichier python. N'hesitez pas a les changer ! J'ai juste traduit mon code C++ en python,
donc il existe surement mieux en python (et peut-etre en C++...).
Cependant, ca m'arrangerait que vous ne modifiez pas les fichiers txt, mis a part si vous avez une bonne idee et que vous voulez m'en faire part.
Je vous ai donne les fonctions python comme exemple. Libre a vous de ne pas les reutilisez/les modifier.

Je n'ai pas verifie mes solutions. Donc si vous observer des choses bizarres, comme des teleportations ou autres, envoyez-moi un mail !

Vous pouvez aussi m'envoyer un mail si des choses ne sont pas claires ou que vous voulez d'autres instances pour faire des tests.
