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
Ce script charge le réseau de neurones puis le teste avec la base de
données de tests. Il renvoie les pourcentages de réussite des
échantillons de motos et de pas motos ]]

package.path = package.path .. ";src/?.lua"
require 'mv-header'

require 'cv.imgproc'
require 'cv.imgcodecs'

local l = 60			-- largeur normalisée des images en entrée du réseau de neurone
local L = 120			-- hauteur normalisée des images en entrée du réseau de neurone
local n1test = 280		-- Nombre d'images de motos pour le test
local n2test = 320		-- Nombre d'images de pas motos pour le test
local Ntest = n1test + n2test	-- Nombre d'échantillons de tests
local seuil = 1			-- seuil pour comparer au résultat de la prédiction (moto=1, pasmoto=0)

local net = torch.load('network.t7')			-- Chargement du réseau de neurones
local datasetTest = torch.load('datasetTest.t7') 	-- Chargement de la base de données

printTRM('Détails ? (y or n)')		-- Demande de détails
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
			printTRM('n°' .. i)			-- n° image
			printTRM('pred = ' .. predicted[1])	-- prediction du reseau de neurones
			printTRM('cptVP = ' .. cptVP)		-- nombre vrai positif
			printTRM('cptFN = ' .. cptFN)		-- nombre faux negatif
			printTRM('\n')
		end
	end
	printTRM('[Résultat] ' .. cptVP/n1test*100 .. '% de Vrai-Positifs pour le seuil de ' .. seuil)
	printTRM('[Résultat] ' .. cptFN/n2test*100 .. '% de Faux-Negatifs pour le seuil de ' .. seuil)
else
	printTRM('Mauvaise entrée')
end
