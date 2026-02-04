# Politiscales Analyzer

## Présentation

Politiscales Analyzer est un outil d’analyse et de visualisation du positionnement politique basé sur les résultats du test Politiscales.

L’application permet d’importer, d’analyser et de comparer plusieurs profils politiques à partir de résultats individuels, en utilisant un modèle mathématique multi-axes et une projection graphique bidimensionnelle.

Le projet combine data science, modélisation politique et visualisation interactive.

---

## Objectifs

Le projet vise à fournir un outil permettant :

- L’import automatique des résultats Politiscales via reconnaissance d’image
- La modélisation mathématique des positions politiques
- La comparaison simultanée de plusieurs individus
- La visualisation graphique du positionnement idéologique
- L’intégration de personnalités politiques historiques et contemporaines
- L’analyse comparative des proximités idéologiques

---

## Modèle politique

Le modèle repose sur huit axes idéologiques comprenant chacun deux pôles opposés.

### Axes analysés

| Axe | Pôle A | Pôle B |
|----------|----------------------|----------------|
| Anthropologie politique | Constructivisme | Essentialisme |
| Justice pénale | Justice réhabilitative | Justice punitive |
| Valeurs sociétales | Progressisme | Conservatisme |
| Politique internationale | Internationalisme | Nationalisme |
| Économie | Communisme | Capitalisme |
| Organisation du marché | Régulation | Laissez-faire |
| Environnement | Écologie | Productivisme |
| Transformation sociale | Révolution | Réformisme |

Chaque utilisateur obtient un score entre 0 et 100 sur chaque variable.

---

## Projection graphique

Les seize variables sont transformées en coordonnées bidimensionnelles.

### Axe économique (X)

Représente l’opposition entre :

Gauche économique et Droite économique.

### Axe sociétal (Y)

Représente l’opposition entre :

Libertaire et Autoritaire.

---

## Méthodologie mathématique

Les scores subissent plusieurs transformations afin d’améliorer la stabilité du modèle.

### Normalisation

Tous les scores sont ramenés dans l’intervalle [0,1].

### Transformations non linéaires

#### Transformation logarithmique
Réduit l’influence des valeurs extrêmes.

#### Transformation sigmoïde
Lisse les transitions idéologiques modérées.

#### Ratio pondéré
Empêche une variable dominante de fausser la projection globale.

#### Distance absolue
Mesure les écarts idéologiques entre concepts opposés.

---

## Reconnaissance automatique des résultats

Le projet inclut un module OCR permettant d’extraire automatiquement les scores depuis une capture d’écran Politiscales.

### Méthode utilisée

- Analyse OCR via Tesseract
- Détection géométrique des barres de scores
- Extraction automatique des pourcentages
- Attribution aux axes idéologiques

### Technologies utilisées

- Tesseract OCR
- Pillow
- Analyse spatiale des éléments graphiques

---

## Interface utilisateur

L’application propose une interface graphique développée en Tkinter.

### Fonctionnalités principales

#### Assistant multi-personnes
Permet la comparaison simultanée de plusieurs profils.

#### Import OCR
Permet l’import automatique depuis une capture Politiscales.

#### Visualisation graphique
Affiche les individus sur un plan politique bidimensionnel.

#### Superposition de références politiques
Permet la comparaison avec des personnalités historiques et contemporaines.

---

## Base de données de personnalités politiques

Le projet inclut une base de positionnements estimés pour :

- Philosophes politiques
- Dirigeants historiques
- Chefs d’État contemporains
- Théoriciens économiques

Ces positionnements sont établis à partir d’analyses académiques, historiques et bibliographiques.

Ces estimations sont fournies à titre pédagogique et analytique.

---

## Architecture du projet

politiscales-analyzer/
│
├── main.py # Point d’entrée de l’application
├── ui.py # Interface graphique Tkinter
├── model.py # Calcul des coordonnées politiques
├── ocr.py # Extraction OCR des scores Politiscales
│
├── personalities/
│ └── personalities_data.py # Base de données des personnalités politiques
│
├── plotting/
│ └── plot_engine.py # Moteur de génération du graphique
│
├── utils/
│ └── transformations.py # Fonctions mathématiques et normalisations
│
├── requirements.txt # Dépendances Python
└── README.md # Documentation du projet

## Installation des dépendances

```bash
pip install -r requirements.txt
```

## Installation de Tesseract OCR

Télécharger et installer Tesseract :

https://github.com/tesseract-ocr/tesseract

Si nécessaire, configurer le chemin vers l’exécutable dans ocr.py.

## Lancer l’application
```bash
python main.py
```
## Exemple d’utilisation

1- Lancer l’application
2- Indiquer le nombre de personnes à comparer
3- Importer les résultats Politiscales via OCR ou saisie manuelle
4- Visualiser le positionnement politique
5- Comparer avec les références idéologiques

## Auteur

Kenzi Lali

Étudiant ingénieur en Data Science et Intelligence Artificielle

ECE Paris

## Motivation du projet

Ce projet vise à explorer l’intersection entre :

- Science politique
- Data science
- Visualisation interactive
- Modélisation mathématique des idéologies

L’objectif est de transformer un test politique en outil analytique exploitable.


