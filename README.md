# **decp-couverture** : Couverture géographique des Données Essentielles de la Commande Publique (DECP). 

![Actions badge](https://github.com/139bercy/decp-couverture/actions/workflows/tests.yaml/badge.svg)
![Actions badge](https://github.com/139bercy/decp-couverture/actions/workflows/run.yaml/badge.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Ce projet permet d'analyser la couverture des données essentielles de la commande publique augmentées publiées quotidiennement sur [data.economie.gouv.fr](https://data.economie.gouv.fr/explore/dataset/decp_augmente/). Les résultats sont affichés dans une application Web interactive.

Pré-requis :
* [pipenv](https://pipenv-fork.readthedocs.io/en/latest/)
* [python 3.8](https://www.python.org/downloads/release/python-3810/)

### Utilisation

Installer les dépendances  :
```shell
pipenv install --python 3.8
```

Utiliser l'interface en ligne de commande  :
```
pipenv run python . [-h] {download,coverage,web} ...

positional arguments:
  {download,coverage,web}
    download            télécharger les DECP (economie.gouv.fr), la base Sirene (INSEE) et les contours de cartes
    coverage            calcule les statistiques de couverture des DECP
    web                 lancer l'application web de présentation de la couverture

optional arguments:
  -h, --help            show this help message and exit
```

Pour la commande `web` les variables d'environnements `GITHUB_USERNAME` et `GITHUB_TOKEN` doivent être définies. Le jeton d'accès doit avoir au moins le scope `public_repo` (accès aux projets publics).

```shell
# macOS ou Linux
export GITHUB_USERNAME="<Nom d'utilisateur GitHub>"
export GITHUB_TOKEN="<Jeton d'accès>"
# Windows
SET GITHUB_USERNAME=<Nom d'utilisateur GitHub>
SET GITHUB_TOKEN=<Jeton d'accès>
# PowerShell
$Env:GITHUB_USERNAME="<Nom d'utilisateur GitHub>"
$Env:GITHUB_TOKEN="<Jeton d'accès>"
```

### Guide du développeur

Installer les dépendances, y compris celles de développement  :
```shell
pipenv install --dev --python 3.8
```

Un [*workflow*](.github/workflows/tests.yaml) se déclenche à chaque *push* sur la branche *main*. Il est composé de deux *jobs* :
* `pylint-score` vérifie la conformité du code au standard PEP-8, à l'aide du module *pylint*. Le *job* échoue si le score de conformité est inférieur à 8/10.
* `pipfile-lock-check` vérifie que les dépendances du projet sont correctement vérouillées dans le fichier *Pipfile.lock*. Il s'agit d'une pratique recommandée dans la documentation de l'outil *pipenv*. Le *job* échoue si ce n'est pas le cas.

### Fonctionnement opérationnel

Deux systèmes fonctionnent en parallèle. Ils utilisent tous les deux la branche *main* du projet.

* Un [*workflow*](.github/workflows/run.yaml) automatisé analyse chaque lundi la couverture des DECP en exécutant les commandes `download` puis `coverage`. Ce workflow s'exécute sur le service GitHub Actions. Deux *artifacts* au format JSON sont générés par ce *workflow* puis stockés par GitHub :
  * Le fichier original des DECP augmentées, issu de la commande `download --decp-only`
  * Le fichier d'analyse de couverture par année/commune/département/région, issu de la commande `coverage`, au format CSV

* L'application Web de présentation des résultats est hébergée sur le service streamlit.io. Elle peut aussi être exécutée sur un poste avec la commande `web`. L'application récupère les résultats d'analyse (stockés sous forme d'*artifacts*) et les affiche sur la page sous forme de carte.
