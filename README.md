Jeu du Prince Bleu (Blue Prince)

Ceci est une version simplifiée du jeu « Blue Prince », développée en Python avec pygame.

Structure du projet

```
blue_prince/
├── main.py                 # Point d’entrée du jeu
├── game.py                 # Classe principale Game
├── mansion.py              # Gestion de la grille du manoir
├── room.py                 # Classe Room (pièce)
├── player.py               # Classe Player (joueur)
├── inventory.py            # Classe Inventory (inventaire)
├── door.py                 # Classe Door (porte)
├── item.py                 # Classe Item (objet)
├── room_selector.py        # Logique de sélection des pièces
├── ui.py                   # Interface graphique
├── config.py               # Constantes de configuration
├── rooms_data.py           # Définition des types de pièces
├── requirements.txt        # Dépendances
└── README.md               # Ce fichier
```

Installation et exécution

1. Installation des dépendances (de préférence dans un environnement virtuel)

```bash
pip install -r requirements.txt
```

ou en installant directement pygame :

```bash
pip install pygame
```

2. Lancer le jeu

```bash
python main.py
```

ou :

```bash
python3 main.py
```

Commandes du jeu

Commandes de base

* WASD ou ZQSD : choisir la direction de déplacement
* Barre d’espace : valider le déplacement
* Échap (ESC) : annuler la sélection

Sélection des pièces

Lorsqu’une nouvelle porte est ouverte, 3 pièces possibles sont proposées :

* Flèches gauche/droite : choisir la pièce
* Entrée ou espace : valider le choix
* T : utiliser un dé pour relancer le tirage des pièces

Règles du jeu

Objectif

Le joueur commence dans le hall d’entrée et doit atteindre l’antichambre située sur la première ligne du manoir.

Conditions de défaite

1. Les pas sont épuisés
2. Le joueur ne peut plus progresser (aucune porte disponible ou manque de clés)

Système d’objets

Objets consommables

* Pas : 70 au départ, on perd 1 pas à chaque déplacement
* Pièces d’or : 0 au départ, servent à acheter des objets dans les boutiques
* Gemmes : 2 au départ, servent à choisir certaines pièces
* Clés : 0 au départ, servent à ouvrir les portes verrouillées
* Dés : 0 au départ, servent à relancer le tirage des pièces

Objets permanents

* Pelle : permet de fouiller les emplacements creusables
* Marteau : permet d’ouvrir (casser) les coffres
* Kit de crochetage : permet d’ouvrir les portes de niveau 1 sans consommer de clé
* Détecteur de métaux : augmente les chances de trouver des clés et des pièces d’or
* Patte de lapin porte-bonheur : augmente les chances de trouver des objets

Nourriture

* Pomme : rend 2 pas
* Banane : rend 3 pas
* Gâteau : rend 10 pas
* Sandwich : rend 15 pas
* Festin : rend 25 pas

Types de pièces

* Pièce jaune : boutique, permet d’acheter des objets avec des pièces d’or
* Pièce verte : jardin intérieur, forte probabilité de contenir des gemmes, des emplacements creusables et des objets permanents
* Pièce violette : chambre, permet de récupérer des pas
* Pièce orange : couloir, contient souvent beaucoup de portes
* Pièce rouge : pièce dangereuse, peut avoir des effets négatifs
* Pièce bleue : pièce la plus courante, avec des effets variés

Système de verrouillage des portes

* Niveau 0 : non verrouillée, s’ouvre directement
* Niveau 1 : verrouillée, nécessite une clé ou un kit de crochetage
* Niveau 2 : double verrouillage, nécessite obligatoirement une clé

Le niveau de verrouillage dépend de la ligne où se trouve la pièce :

* Première ligne : uniquement des portes de niveau 0
* Lignes intermédiaires : mélange de niveaux 0, 1 et 2
* Dernière ligne : uniquement des portes de niveau 2

Fonctionnalités implémentées

Selon le cahier des charges, les fonctionnalités suivantes sont implémentées :

1. Interface graphique de bonne qualité et facile à utiliser
2. Déplacement dans le manoir et ouverture des portes
3. Tirage et sélection des pièces
4. Gain de pas via la nourriture et perte de pas lors des déplacements
5. Fin de partie (victoire en atteignant l’antichambre, défaite si les pas tombent à zéro)
6. Ramassage de gemmes et consommation de gemmes pour choisir des pièces
7. Ramassage de clés et consommation de clés pour ouvrir les portes
8. Ramassage de dés et consommation de dés pour relancer le tirage des pièces
9. Aléa sur les objets disponibles dans les pièces
10. Tirage aléatoire des pièces en tenant compte de leur rareté
11. Aléa sur le niveau de verrouillage des portes
12. Détecteur de métaux et patte de lapin (et leurs effets associés)
13. Kit de crochetage et ouverture des portes de niveau 1

Description du code

Conception des classes

* Game : classe principale du jeu, gère l’état du jeu et la boucle principale
* Mansion : classe du manoir, gère la grille 5×9 et la disposition des pièces
* Room : classe représentant une pièce et ses propriétés
* Player : classe joueur, gère l’état du joueur et son inventaire
* Inventory : classe inventaire, gère les consommables et les objets permanents
* Door : classe porte, gère l’état de verrouillage des portes
* Item : classe de base des objets et ses sous-classes
* RoomSelector : sélecteur de pièces, gère le tirage et la sélection des pièces
* UI : classe interface graphique, gère l’affichage avec pygame

Choix de conception

1. Programmation orientée objet : utilisation de classes pour structurer le code, chaque classe ayant une responsabilité claire
2. Gestion des états : utilisation d’un enum GameState pour gérer les différents états du jeu
3. Aléatoire : utilisation du module random pour toutes les mécaniques de hasard
4. Modulaire : séparation des fonctionnalités dans différents modules pour faciliter la maintenance

Mode d’interaction

Dans config.py, on peut régler STRICT_MODE :

* True : mode strict (flèches pour choisir la direction, espace pour valider le déplacement), conforme au cahier des charges
* False : mode confortable (appuyer sur une direction déplace directement), plus rapide à jouer

Effets globaux de certaines pièces spéciales

* Salle avec cheminée : augmente la probabilité de tirage des pièces rouges
* Serre : augmente la probabilité de tirage des pièces vertes
* Salle de bronzage : augmente la probabilité de tirage des pièces bleues
* Balcon : augmente encore la probabilité de tirage des pièces vertes (effet cumulable)

Environnement de développement

* Python 3.7 ou plus
* pygame 2.5.0 ou plus

Licence

Ce projet est un projet de cours de Python.

