Sondag Chloé

-Description du projet :
-
Développement d'une application de communication sécurisée entre 2 clients via un routage en oignon, telle l'architecture 'Tor'. 

-Exigences Environnement :
-
2 VM Linux + 1 VM Windows;
Interface graphique avec PyQt5 ou 6

dans ce projet :
VM1 -> 'Master' Debian 12 hébergeant le serveur mariadb;
VM2 -> 'Noeud' Debian 12;
VM3 -> 'GUI' Debian 12;
Interface PyQt5 pour plus de stabilité

-Modification du code nécessaire après "Configuration réseau fixe Host-Only" !
-
Les adresses ip du Master (VM Master) et des Routeurs et Client B (VM Noeud) sont enregistrées en dur dans noeud.py.

Puisqu'elles dépendent de l'adresse du réseau privé hôte de votre machine, elles sont actuellement sous la forme '192.168.x.10'. 

Alors, juste après l'étape "Configuration réseau fixe Host-Only", une fois l'adresse du réseau privé hôte de votre machine identifiée, modifiez noeud.py

-Avertissement (test) : 
-
Une fois un routeur enregistré dans la base de données, il est considéré comme utilisable par le client même s’il a été arrêté.
On considère que tous les routeurs enregistrés dans la base sont en cours d’execution.
Sinon, il faut supprimer les entrées de la table routeurs avec la commande sql 'DELETE FROM routeurs;'.