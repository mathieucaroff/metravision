--[[
Copyright Maxime LEIBER,
Copyright Manuel MATILDE,
Copyright Antoine SOUSTELLE,
programme crée le 6 mars 2017.

Utilisation des bibliothèques libres suivantes :
Torch
Copyright (c) 2011-2014 Idiap Research Institute (Ronan Collobert)
Copyright (c) 2012-2014 Deepmind Technologies (Koray Kavukcuoglu)
Copyright (c) 2011-2012 NEC Laboratories America (Koray Kavukcuoglu)
Copyright (c) 2011-2013 NYU (Clement Farabet)
Copyright (c) 2006-2010 NEC Laboratories America (Ronan Collobert, Leon Bottou, Iain Melvin, Jason Weston)
Copyright (c) 2006           Idiap Research Institute (Samy Bengio)
Copyright (c) 2001-2004 Idiap Research Institute (Ronan Collobert, Samy Bengio, Johnny Mariethoz)
OpenCV
Copyright (C) 2000-2016, Intel Corporation, all rights reserved.
Copyright (C) 2009-2011, Willow Garage Inc., all rights reserved.
Copyright (C) 2009-2016, NVIDIA Corporation, all rights reserved.
Copyright (C) 2010-2013, Advanced Micro Devices, Inc., all rights reserved.
Copyright (C) 2015-2016, OpenCV Foundation, all rights reserved.
Copyright (C) 2015-2016, Itseez Inc., all rights reserved.
Autres
Copyright (c) 2015 Egor Burkov and other contributors

Contact :
leibermaxime@gmail.com
mtld.manu@gmail.com
antoine.soustelle@wanadoo.fr

Ce logiciel est un programme informatique servant à la détection
des deux roues motorisés sur l'autoroute. Le projet a été fait
par commande du Cerema.

Ce logiciel est régi par la licence CeCILL soumise au droit français et
respectant les principes de diffusion des logiciels libres. Vous pouvez
utiliser, modifier et/ou redistribuer ce programme sous les conditions
de la licence CeCILL telle que diffusée par le CEA, le CNRS et l'INRIA 
sur le site "http://www.cecill.info".

En contrepartie de l'accessibilité au code source et des droits de copie,
de modification et de redistribution accordés par cette licence, il n'est
offert aux utilisateurs qu'une garantie limitée.  Pour les mêmes raisons,
seule une responsabilité restreinte pèse sur l'auteur du programme,  le
titulaire des droits patrimoniaux et les concédants successifs.

A cet égard  l'attention de l'utilisateur est attirée sur les risques
associés au chargement,  à l'utilisation,  à la modification et/ou au
développement et à la reproduction du logiciel par l'utilisateur étant 
donné sa spécificité de logiciel libre, qui peut le rendre complexe à 
manipuler et qui le réserve donc à des développeurs et des professionnels
avertis possédant  des  connaissances  informatiques approfondies.  Les
utilisateurs sont donc invités à charger  et  tester  l'adéquation  du
logiciel à leurs besoins dans des conditions permettant d'assurer la
sécurité de leurs systèmes et ou de leurs données et, plus généralement, 
à l'utiliser et l'exploiter dans les mêmes conditions de sécurité. 

Le fait que vous puissiez accéder à cet en-tête signifie que vous avez 
pris connaissance de la licence CeCILL, et que vous en avez accepté les
termes.]]

--[[ Ce programme charge le réseau de neurones puis le teste avec la base de données de tests.
Il renvoie les pourcentages de réussite des échantillons de motos et de pas motos ]]

require 'torch'			-- Utilisation du module torch
require 'nn'			-- Utilisation du module neural network
cv = require 'cv'		-- Utilisation d'OpenCV
require 'cv.imgproc'		-- Utilisation du module imgproc d'OpenCV
require 'cv.imgcodecs'		-- Utilisation du module imgcodecs d'OpenCV

local l = 60			-- largeur normalisée des images en entrée du réseau de neurone
local L = 120			-- hauteur normalisée des images en entrée du réseau de neurone
local n1test = 280		-- Nombre d'images de motos pour le test
local n2test = 320		-- Nombre d'images de pas motos pour le test
local Ntest = n1test + n2test	-- Nombre d'échantillons de tests
local seuil = 1			-- seuil pour comparer au résultat de la prédiction (moto=1, pasmoto=0)

local net = torch.load('network.t7')			-- Chargement du réseau de neurones
local datasetTest = torch.load('datasetTest.t7') 	-- Chargement de la base de données

print('Détails ? (y or n)')		-- Demande de détails
local key = io.read()			-- Lecture de la réponse

if key == 'y' or key == 'n' then	-- si touche y ou n appuyée
	local cptVP = 0 -- compteur Vrai Postif (signifie moto vue comme moto par le reseau)
	local cptFN = 0 -- compteur Faux Negatif (signifie pas moto vue comme pas moto par le reseau)
	for i = 1,Ntest do
		local predicted = net:forward(datasetTest[i][1])	-- prediction de l'echantillon
		if datasetTest[i][2]==1 then		-- si l'image est une moto
			if predicted[1] >= seuil then	-- si la prediction du reseau est >= au seuil
				cptVP = cptVP + 1	-- bonne prediction donc on incrémente le compteur
			end
		else					-- sinon l'image est une pas moto
			if predicted[1] < seuil then	-- et si la prediction est < au seuil 
				cptFN = cptFN + 1	-- bonne prediction donc on incrémente le compteur
			end
		end
		if key == 'y' then				-- si touche y appuyée, afficher
			print('n°' .. i)			-- n° image
			print('pred = ' .. predicted[1])	-- prediction du reseau de neurones
			print('cptVP = ' .. cptVP)		-- nombre vrai positif
			print('cptFN = ' .. cptFN)		-- nombre faux negatif
			print('\n')
		end
	end
	print('[Résultat] ' .. cptVP/n1test*100 .. '% de Vrai-Positifs pour le seuil de ' .. seuil)
	print('[Résultat] ' .. cptFN/n2test*100 .. '% de Faux-Negatifs pour le seuil de ' .. seuil)
else
	print('Mauvaise entrée')
end
