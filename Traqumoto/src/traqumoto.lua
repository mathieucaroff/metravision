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

require 'mv.globals'

require 'cv.features2d'
require 'cv.highgui'
require 'cv.videoio'
require 'cv.imgproc'
require 'cv.video'
require 'math'

net = torch.load('src/network.t7')	-- Charge le réseau de neurones network.t7
vidname = getFile()			-- Appel de la fonction getFile de traqumoto.cpp
vidname = vidname:gsub("\n", "")	-- retire le caractère \n à la fin du chemin de la vidéo
print(vidname)				-- Affiche le chemin

dofile("src/prediction.lua")		-- Execute le programme de prediction

write('Resultat.csv',data,';')		-- Ecris le résultat dans un fichier excel
