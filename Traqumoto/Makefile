# Création de l'executable
# Le Makefile est appelé après l'installation des librairies par le fichier install.sh

Traqumoto:	src/traqumoto.cpp
	g++ src/traqumoto.cpp -IApplications/torch/install/include -LApplications/torch/install/lib -lluajit -ldl -o Traqumoto
