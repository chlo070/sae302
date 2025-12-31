Sondag Chloé

-Description du projet
Développement d'une application 

-Exigences Environnement 
2 VM Linux + 1 VM Windows
Interface graphique avec PyQt5 ou 6

dans ce projet :
VM1 -> 'Master' Debian 12 hébergeant le serveur mariadb
VM2 -> 'Noeud' Debian 12
VM3 -> 'GUI' Debian 12 
Interface PyQt5 pour plus de stabilité

Avertissement : une fois un routeur enregistré dans la base de données, il est considéré comme utilisable par le client même s’il a été arrêté.
On considère que tous les routeurs enregistrés dans la base sont en cours d’execution.
Sinon, il faut supprimer les entrées de la table routeurs avec la commande sql 'DELETE FROM routeurs;'.