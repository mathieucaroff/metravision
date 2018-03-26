--[[ Copyright
Copyright Manuel MATILDE, contact: mtld.manu@gmail.com,
Copyright Maxime LEIBER, contact: leibermaxime@gmail.com,
Copyright Antoine SOUSTELLE, contact: antoine.soustelle@wanadoo.fr.
Programme crée le 6 mars 2017.]]

--[[ Licence
Ce logiciel est régi par la licence CeCILL soumise au droit français et
respectant les principes de diffusion des logiciels libres. Vous pouvez
utiliser, modifier et/ou redistribuer ce programme sous les conditions
de la licence CeCILL telle que diffusée par le CEA, le CNRS et l'INRIA 
sur le site "http://www.cecill.info".]]

--[[ Logiciel
Ce fichier fait parti du logiciel Traqu'moto, servant à la détection
des deux roues motorisés sur autoroute. Il a été réalisé sur commande
du Cerema.]]

--[[ Description du ficher
Ce fichier permet d'executer le promgramme Traqu'moto par commandes via
le terminal (>> th predictionVideo.lua).
On charge le réseau de neurones, choisit le chemin de la vidéo, execute
le programme de prédiction puis enregistre les résultats dans un fichier
excel. ]]

require 'torch'		-- Utilisation du module torch
require 'nn'		-- Utilisation du module neural network
require 'math'		-- Utilisation du module math
cv = require 'cv'	-- Utilisation d'OpenCV
require 'cv.features2d'	-- Utilisation du module features2d d'OpenCV
require 'cv.highgui'	-- Utilisation du module highgui d'OpenCV
require 'cv.videoio'	-- Utilisation du module videoio d'OpenCV
require 'cv.imgproc'	-- Utilisation du module imgproc d'OpenCV
require 'cv.video'	-- Utilisation du module video d'OpenCV

net = torch.load('network.t7')			-- Charge le réseau de neurones network.t7
vidname = '/home/user/traqumoto/sequence.mp4'	-- Chemin de la vidéo en entrée

dofile("prediction.lua")	-- Execute le fichier prediction.lua

write('../Resultat.csv',data,';')	-- Ecris le résultat dans un fichier excel
