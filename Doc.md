# Otelo v1.2

Otelo est developpé en Python 3, à l'aide du framework web Django

## Modules utilisés

- Django
- xlrd

## Arborescence d'Otelo - Premier niveau

- data : dossier contenant les fichiers de données utiles à Otelo,
- outil : dossier contenant l'application Django contenant Otelo,
- sauvegarde : dossier de stockage des fichiers de sauvegarde d'Otelo,
- static : dossier contenant les fichiers statiques d'Otelo,
- tpl_outil : dossier contenant les fichiers de paramètrage globaux d'Otelo.

## Application Otelo

Le dossier outil contient l'essentiel de l'application Django permettant le fonctionnement d'Otelo :

- calcul : dossier contenant les modules de calcul à la Zone d'Emploi et à l'EPCI,
- initialisation : dossier contenant les modules de chargement des données, d'initialisation de la base de données et les paramètrages vers les fichiers ressources,
- migrations : dossier contenant les modules générés par Django pour la construction de la base de données,
- templates : dossier contenant les templates HTML utilisés par Django,
- templatetags : dossier definissant quelques tags pour l'affichage dans les templates,
- views : dossier contenant les modules définissant les différentes vues (configurations et résultats).

La base de données est contenue dans le fichier db.sqlite3.

### Modèles de données

Le module models.py contient les différents modèles des tables associées dans la base de données:

- ParametreZE : comprend l'ensemble des paramétrages associés à une zone d'emploi,
- Commune : contient l'ensemble des informations relatives à une commune (notamment les coefficients correctifs).

Les classes Manager associées permettent des modifications ou la lecture de plusieurs objets de ces modèles.

### Modules d'initialisation

Le dossier initialisation contient les modules suivants:

#### charger_bdd.py : 

Ce module permet de réinitialiser le paramètrage pour l'ensemble des zones d'emploi dans la base de données, de réinitialiser les classes associées aux communes ou encore de réinitialiser les correspondances entre communes et EPCI.

#### charger_data.py :

Ce module permet de lire et stocker les données présentes dans les packs de données B1 et B2.

La classe ZEData contient l'ensemble des données associées à une zone d'emploi.

La classe ZEDatas permet d'importer les packs de données pour toutes les zones d'emploi. Elle a pour attribut le dictionnaire zones qui contient des instances ZEData pour chaque code ZE.

#### charger_ze.py :

Ce module permet de lire et stocker les zones d'emploi avec les communes associées.

#### outils_xls.py :

Ce module contient des fonctions facilitant la lecture de fichiers xls.

#### params.py :

Ce module contient les chemins d'accès aux différents fichiers de configuration de l'application.

### Modules de calcul

#### calculs_ze.py :

Ce module permet les différents calculs de besoin en logement à la zone d'emploi (ZE).

La classe ResultatZE permet de calculer les indicateurs de besoin en logement pour une zone d'emploi. Elle prend pour paramètre :

- les parametres de configuration de la ZE (instance de ParametreZE)
- les données des pack B1 et B2 associées à la ZE (instance de ZEData)

La classe ResultatInterZE permet de calculer les indicateurs relatifs à un ensemble de zones d'emploi (part d'une ZE, totaux, etc.). Elle prend pour paramètre la liste des instances ResultatZE de l'ensemble des ZE.

La classe CalculZE permet de renvoyer les résultats associés à une ou plusieurs ZE. 

#### calculs_epci.py :

La classe ResultatEPCI permet de calculer les indicateurs de besoin en logement pour un EPCI. Elle prend pour paramètre le code EPCI. Les methodes de calcul associées prennent en paramètre la liste des instances ResultatZE des zones d'emploi.

La classe CalculZE permet de renvoyer les résultats associés à un ou plusieurs EPCI. 

### Module des vues

Les fonctions de vue qui permettent de renvoyer les réponses et les contenus HTML (présents dans le dossier templates) sont définies dans les modules configuration.py et resultat.py du dossier views.

#### configuration.py :

Ce module contient les fonctions de vue relatives aux pages de configuration (b11, b12, etc.).

Ces fonctions permettent de récupérer les données de paramétrages présentes dans la base de données pour chaque ZE afin de les afficher et, si un formulaire a été validé sur la page, de prendre en compte, au préalable, les modifications de paramètrage demandées par l'utilisateur.

Pour la plupart de ces fonctions, une classe FormAnalyse est définie pour récupérer les informations issues du formulaire et intégrer les modifications dans la base de données (modification des ParametreZE correspondant).

Le traitement des modifications (lorsque la fonction de vue recoit une requete HTTP de type POST) s'effectue à l'aide de la fonction traitement_post qui prend pour paramètres la variable request.POST et la classe FormAnalyse associée à la fonction de vue.

#### resultat.py :

Ce module contient les fonctions de vue relatives aux pages de résultats.

Pour chaque fonction, les résultats sont calculés et récupérés pour les codes (ZE ou EPCI) selectionnés via une instance des classes CalculZE ou CalculEPCI. Ils permettent d'alimenter les templates de résultats sous forme HTML ou de générer le fichier csv lors d'une demande d'export en csv par l'utilisateur.





 



 


