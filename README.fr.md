# Metravision

Detection et comptage des véhicules légés (moto et similaires) sur
autoroute, basé sur le traitement vidéo.

## Installation et lancement

### Utilisation basique

Ce projet dépends de packages Anaconda. Pour les récupérer, vous devez
installer Miniconda ou Anaconda, puis les installer en utilisant:

```sh
conda install -c conda-forge opencv pyyaml ipython openpyxl
```

Si vous êtes sur Windows, ces commandes doivent être copiée dans la
fenêtre "Anaconda Prompt".

Il vous faudra aussi copier la dernière version du fichier de
configuration depuis
`sample/metravision.config.yml.d/v*/metravision.config.*.yml` à la
racine du projet, et l'appeler `metravision.config.yml`. Il peut être
utile de vérifier que les valeurs par défaut vous conviennent.

Pour lancer le programme, il faut utiliser se placer à la racine du
projet et appeler `src/main.py` avec le python fourni par Conda. Passez
en paramètre du script les fichiers vidéos que vous souhaitez traiter.
Si vous n'avez pas changé le fichier de configuration, les résultats
seront placé dans un fichier `.xlsx`, dans un dossier nommé
`mv-results`.

Le fichier `launch-metravision.py` est un script d'aide qui trouve votre
installation Conda en cherchant aux endroits d'installation habituelles.
Si vous êtes sur Windows, il peut être intéressant de le packager en
fichier .exe, en utilisant PyInstaller, comme nous l'avons fait pour
livrer le logiciel. Si oui, référez vous à la section PyInstaller du
fichier README.md, en anglais.

La suite du fichier README.md n'est pas traduite. Voici un extrait la
liste des titres traduits qu'elle contient (au 2018-06-26) :

* Metravision
  * Installation et lancement
    * Utilisation basique
    * Environnement de dévloppement
    * PyInstaller
    * "Compillation" (packetage) du lanceur Metravision, avec
      PyInstaller
  * Contribuer
  * Utiliser git
    * (...)