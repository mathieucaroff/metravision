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

--[[ Ce programme crée la base de données constituée de 10 (transformations) * Napp images.
Puis il crée le réseau de neurones et l'entraine avec la base de données.
Ensuite le programme teste les Ntest images pour évaluer le réseau. ]]

require 'torch'		-- Utilisation du module torch
require 'nn'		-- Utilisation du module neural network
cv = require 'cv'	-- Utilisation d'OpenCV
require 'cv.imgcodecs'	-- Utilisation du module imgcodecs d'OpenCV
require 'cv.imgproc'	-- Utilisation du module imgproc d'OpenCV

local n1 = 1300			-- Nombre d'images de motos
local n2 = 1800			-- Nombre d'images de pas motos
local N = n1 + n2		-- Nombre total d'images
local n1app = 1200		-- Nombre d'images de motos pour l'apprentissage
local n2app = 1700		-- Nombre d'images de pas motos pour l'apprentissage
local Napp = n1app + n2app	-- Nombre total d'images pour l'apprentissage
local n1test = n1 - n1app	-- Nombre d'images de motos pour le test
local n2test = n2 - n2app	-- Nombre d'images de pas motos pour le test
local Ntest = n1test + n2test	-- Nombre d'échantillons de tests

local nbiterations = 10 -- nombre d'itérations
local seuil = 1		-- seuil pour comparer au résultat de la prédiction (moto=1, pasmoto=0)

local nt = 10	-- nombre de transformations
local l = 60	-- largeur normalisée des images en entrée du réseau de neurones
local L = 120	-- hauteur normalisée des images en entrée du réseau de neurones

-- Creation de la base de données d'images
function creation_dataset()
	local imgsetMoto = torch.Tensor(n1,1,L,l):zero() 	-- tableau contenant les images de motos
	local imgsetPasMoto = torch.Tensor(n2,1,L,l):zero() 	-- tableau contenant les images de pas motos

	for i=1,N do
		if i <= n1 then
			if i<100 then
				imgname = string.format('../BDD/Motos/%02d.png', i)	-- images de 01 à 99
			else
				if i<1000 then
					imgname = string.format('../BDD/Motos/%03d.png', i)	-- images de 100 à 999
				else
					imgname = string.format('../BDD/Motos/%04d.png', i)	-- images de 1000 à 9999
				end
			end
			local Img = cv.imread{imgname,cv.IMREAD_GRAYSCALE} 	-- image en niveau de gris
			local Imgr = cv.resize{Img,{l,L}} 			-- redimensionnement 60x120
			imgsetMoto[i] = torch.Tensor(1,L,l):copy(Imgr) 		-- ajout image moto dans tableau de motos
		else
			if i-n1<100 then
				imgname = string.format('../BDD/Pas_Motos/%02d.png', i-n1)		--images de 01 à 99
			else
				if i-n1<1000 then
					imgname = string.format('../BDD/Pas_Motos/%03d.png', i-n1)		-- images de 100 à 999
				else
					imgname = string.format('../BDD/Pas_Motos/%04d.png', i-n1)		-- images de 1000 à 9999
				end
			end
			local Img = cv.imread{imgname,cv.IMREAD_GRAYSCALE}	-- image en niveau de gris
			local Imgr = cv.resize{Img,{l,L}}			-- redimensionnement 60x120
			imgsetPasMoto[i-n1] = torch.Tensor(1,L,l):copy(Imgr) 	-- ajout image moto dans tableau de motos
		end
	end

	-- associe le label de moto à 1
	local dataMoto = {}
	for i=1,n1 do
		local input = imgsetMoto[i]
	 	local target = 1
	  	dataMoto[i] = {input, target}
	end

	-- associe le label de pas moto à 0
	local dataPasMoto = {}
	for i=1,n2 do
		local input = imgsetPasMoto[i]
		local target = 0
		dataPasMoto[i] = {input, target}
	end
	
	local rand1 = torch.randperm(n1) -- génération d'une permutation aléatoire de taille n1
	local rand2 = torch.randperm(n2) -- génération d'une permutation aléatoire de taille n2

	-- change l'ordre du tableau dataMotoRand avec la permutation précédente
	local dataMotoRand = {}
	for i=1,n1 do
		dataMotoRand[i] = dataMoto[rand1[i]]
	end

	-- change l'ordre du tableau dataPasMotoRand avec la permutation précédente
	local dataPasMotoRand = {}
	for i=1,n2 do
		dataPasMotoRand[i] = dataPasMoto[rand2[i]]
	end

	
	local imgsetApp = torch.Tensor(Napp*nt,1,L,l):zero() -- initialisation du tableau des images pour l'apprentissage
	local labelsetApp = torch.Tensor(Napp*nt,1):zero() -- initialisation du tableau des labels des images

	
	local k=1
	for i = 1,Napp do
	-- Attirbution du label (moto ou pas moto) à chaque image de l'apprentissage dans le tableau labelsetApp
		if i <= n1app then
			for j=k,k+nt-1 do
				labelsetApp[j] = 1		-- label de moto
			end
			Imgr = torch.Tensor(1,L,l):copy(dataMotoRand[i][1])
		else
			for j=k,k+nt-1 do
				labelsetApp[j] = 0		-- label de pas moto
			end
			Imgr = torch.Tensor(1,L,l):copy(dataPasMotoRand[i-n1app][1])
		end

	-- A partir de chaque image, on obtient 10 images en effectuant des transformations (flip, décalage)
		local Imgs1 = torch.ByteTensor(1,L,l):copy(Imgr)
		local Imgs2 = torch.ByteTensor(1,L,l):copy(Imgr)
		for i=6,Imgr:size()[1] do
			Imgs1[i-5]=Imgr[i]:copy(Imgr[i]) -- décalage de 5 pixels à gauche
			Imgs2[i]=Imgr[i-5]:copy(Imgr[i-5]) -- décalage de 5 pixels à droite
		end
		local Imgs3 = torch.ByteTensor(1,L,l):copy(Imgr)
		local Imgs4 = torch.ByteTensor(1,L,l):copy(Imgr)
		for j=3,Imgr:size()[2] do
			for i=1,Imgr:size()[1] do
				Imgs3[i][j-2]=Imgr[i][j] -- décalage de 2 pixels en haut
				Imgs4[i][j]=Imgr[i][j-2] -- décalage de 2 pixels en bas
			end
		end
		imgsetApp[k] = torch.Tensor(1,L,l):copy(Imgr)	-- image originale
		k = k+1
		imgsetApp[k] = torch.Tensor(1,L,l):copy(Imgs1)	-- droite
		k = k+1
		imgsetApp[k] = torch.Tensor(1,L,l):copy(Imgs2)	-- gauche
		k = k+1
		imgsetApp[k] = torch.Tensor(1,L,l):copy(Imgs3) 	-- haut
		k = k+1
		imgsetApp[k] = torch.Tensor(1,L,l):copy(Imgs4)	-- bas
		k = k+1

		local Imgf = torch.ByteTensor(1,L,l):copy(Imgr)		-- image flip
		cv.flip{Imgr,Imgf,1}

		local Imgfs1 = torch.ByteTensor(1,L,l):copy(Imgf)	
		local Imgfs2 = torch.ByteTensor(1,L,l):copy(Imgf)
		for i=6,Imgf:size()[1] do
			Imgfs1[i-5]=Imgf[i]:copy(Imgf[i])	-- flip + décalage de 5 pixels à gauche
			Imgfs2[i]=Imgf[i-5]:copy(Imgf[i-5])	-- flip + décalage de 5 pixels à droite
		end
		local Imgfs3 = torch.ByteTensor(1,L,l):copy(Imgf)
		local Imgfs4 = torch.ByteTensor(1,L,l):copy(Imgf)
		for j=3,Imgf:size()[2] do
			for i=1,Imgf:size()[1] do
				Imgfs3[i][j-2]=Imgf[i][j]	-- flip + décalage de 2 pixels en haut
				Imgfs4[i][j]=Imgf[i][j-2]	-- flip + décalage de 2 pixels en bas
			end
		end
		imgsetApp[k] = torch.Tensor(1,L,l):copy(Imgf)	-- flip
		k = k+1
		imgsetApp[k] = torch.Tensor(1,L,l):copy(Imgfs1)	-- flip droite
		k = k+1
		imgsetApp[k] = torch.Tensor(1,L,l):copy(Imgfs2)	-- flip gauche
		k = k+1
		imgsetApp[k] = torch.Tensor(1,L,l):copy(Imgfs3)	-- flip haut
		k = k+1
		imgsetApp[k] = torch.Tensor(1,L,l):copy(Imgfs4)	-- flip bas
		k = k+1

		Img = nil
	end


	local mean = imgsetApp:mean() -- moyenne
	local stdv = imgsetApp:std()  -- ecart-type
	-- fonction qui met la moyenne des pixels de l'image à 127 avec une répartition uniforme (égalisation des niveaux de gris)
	imgsetApp = imgsetApp:apply(function(x) 
			x=x*(42/stdv)-mean+127
			x = math.max(math.min(x,255),0)
			return x
		end)

	-- création de la BDD des images pour l'apprentissage (image, label)
	local datasetApp = {}
	for i=1,Napp*nt do
		local input = imgsetApp[i]
		local target = labelsetApp[i]
		datasetApp[i] = {input, target}
	end
	-- création de la BDD des images de Test
	local datasetTest = {}
	for i=1,Ntest*nt do
		if i<=n1test then
			datasetTest[i] = dataMotoRand[n1app+i]
		else
			datasetTest[i] = dataPasMotoRand[n2app+i-n1test]
		end
	end

	-- Enregistre les datasets (BDD d'apprentissage et de test)
	torch.save('datasetApp.t7', datasetApp)		
	torch.save('datasetTest.t7', datasetTest)
	return datasetApp,datasetTest
end

-- Creation du reseau de neurones et entrainement
function entrainement(dataset)

	function dataset:size()
		return Napp*nt -- taille BDD (10*Napp)
	end

	local inputs = 1	-- une image en entrée du réseau
	local couche1 = 4	-- taille des couche intermédiaires(4, 16, 2000)
	local couche2 = 16	
	local couche3 = 2000	
	local outputs = 1	-- une prédiction en sortie du reseau (probabilité entre 0 et 1)

	local tailleConvolution = 5
	local tailleMaxPooling = 2

	local net = nn.Sequential()										-- Réseau de neurones
	net:add(nn.SpatialConvolution(inputs,couche1,tailleConvolution,tailleConvolution))			-- Convolution
	net:add(nn.ReLU())											-- Application du ReLU 
	net:add(nn.SpatialMaxPooling(tailleMaxPooling,tailleMaxPooling,tailleMaxPooling,tailleMaxPooling))	-- Max Pooling pour réduire les images
	net:add(nn.SpatialConvolution(couche1,couche2,tailleConvolution,tailleConvolution))			-- 6 input image channels, 16 output channels, 5x5 convolution kernel
	net:add(nn.ReLU())											-- Application du ReLU 
	net:add(nn.SpatialMaxPooling(tailleMaxPooling,tailleMaxPooling,tailleMaxPooling,tailleMaxPooling))	-- Max Pooling pour réduire les images
	net:add(nn.View(couche2*27*12))										-- redimmensionnement en un seul tableau 
	net:add(nn.Linear(couche2*27*12,couche3))								-- Liens entre la deuxième et troisième couche
	net:add(nn.ReLU())											-- Application du ReLU
	net:add(nn.Linear(couche3,outputs))									-- Liens entre la  troisième couche et la couche de sortie
	net:add(nn.Sigmoid())											-- Sigmoid pour que les résultats soient entre 0 et 1

	local criterion = nn.BCECriterion()				-- Choix du critère d'entrainement, BCE adapté à deux classes
	local trainer = nn.StochasticGradient(net, criterion)		-- Création de l'entraineur avec le reseau et le critère
	trainer.learningRate = 0.0005		-- paramètre vitesse d'apprentissage
	trainer.maxIteration = nbiterations	-- paramètre nombre d'itérations
	trainer:train(dataset)			-- lance l'entrainement du reseau de neurones avec la base de données

	torch.save('network.t7', net)		-- Sauvegarde du réseau de neurones en fichier .t7
	return net
end

-- Test du réseau de neurones
-- Cette fonction permet de tester la précision de la prédiction du réseau de neurones en fonction du seuil choisi, la fonction renvoie le pourcentage de réussite
function testNetwork(net,datasetTest,seuil)
	local cptVP=0 -- compteur Vrai Postif (signifie moto vue comme moto par le reseau)
	local cptFN=0 -- compteur Faux Negatif (signifie pas moto vue comme pas moto par le reseau)
	for i = 1,Ntest do
		local predicted = net:forward(datasetTest[i][1]) -- prediction de l'echantillon
		if datasetTest[i][2]==1 then 		-- si l'image est une moto
			if predicted[1] >= seuil then 	-- si la prediction du reseau est >= au seuil 
				cptVP = cptVP + 1	-- bonne prediction donc on incrémente le compteur
			end
		else 					-- sinon si l'image est une pas moto
			if predicted[1] < seuil then 	-- et si la prediction est < au seuil
				cptFN = cptFN + 1	-- bonne prediction donc on incrémente le compteur
			end
		end
	end
	print('[Résultat] ' .. cptVP/n1test*100 .. '% de Vrai-Positifs pour le seuil de ' .. seuil)
	print('[Résultat] ' .. cptFN/n2test*100 .. '% de Faux-Negatifs pour le seuil de ' .. seuil)
end

-- Main
print("[Main] Prétraitement et création de la base de données")
datasetApp,datasetTest = creation_dataset()
print("[Main] Prétraitement et entrainement du réseau de neurones")
local tps = os.time()
net = entrainement(datasetApp)
print("[Main] Réseau sauvegardé")
tps = (os.time() - tps)	-- durée de l'entrainement
print("[Main] Temps d'entrainement : " .. math.floor(tps/86400) .. "d " .. math.floor(tps/3600)%86400 .. "h " .. math.floor(tps/60)%60 .. "m " .. tps%60 .. "s")
print("[Main] Test du réseau")
testNetwork(net,datasetTest,seuil)
