# MKP - Projet de Résolution du Problème du Sac à Dos

Ce projet vise à résoudre le Problème du Sac à Dos (Knapsack Problem) en utilisant différents algorithmes d'optimisation, tels que DFS, BFS, A*,BSO et génétique, dans le cadre d'une application Django.

## Aperçu

Le Problème du Sac à Dos est un problème d'optimisation combinatoire où l'objectif est de maximiser la valeur totale des objets placés dans un sac à dos, sous contrainte de capacité. Cette application permet de résoudre ce problème en fournissant différents algorithmes et en visualisant les résultats.

## Installation

1. Cloner ce dépôt : `git clone https://github.com/felladib/MKP.git`
2. Accéder au répertoire du projet : `cd votre-projet`
3. Créer un environnement virtuel : `python -m venv venv`
4. Activer l'environnement virtuel :
   - Sur Windows : `venv\Scripts\activate`
   - Sur macOS/Linux : `source venv/bin/activate`
5. Installer les dépendances : `pip install -r requirements.txt`
6. Appliquer les migrations : `python manage.py migrate`
7. Lancer le serveur de développement : `python manage.py runserver`

## Utilisation

Une fois le serveur lancé, accédez à l'interface web de l'application à l'adresse `http://localhost:8000`. Sélectionnez l'algorithme que vous souhaitez utiliser, entrez le nombre de sacs et d'objets, puis cliquez sur le bouton "Run" pour résoudre le Problème du Sac à Dos.

## Fonctionnalités

- Résolution du Problème du Sac à Dos avec différents algorithmes.
- Visualisation des résultats, y compris le temps d'exécution, le nombre de nœuds générés et les objets placés dans chaque sac avec leur valeur respective.

## Technologies utilisées

- **Python**
- **Django**
- **HTML/CSS**
- **JavaScript**

## Contributeurs
- [Fella DIB](github.com/felladib)
- [Lina IGHILAZA](github.com/liAghZn)


## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

