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

require 'torch'		-- Utilisation du module torch
require 'nn'		-- Utilisation du module neural network
require 'math'		-- Utilisation du module math
cv = require 'cv'	-- Utilisation d'OpenCV
require 'cv.features2d'	-- Utilisation du module features2d d'OpenCV
require 'cv.highgui'	-- Utilisation du module highgui d'OpenCV
require 'cv.videoio'	-- Utilisation du module videoio d'OpenCV
require 'cv.imgproc'	-- Utilisation du module imgproc d'OpenCV
require 'cv.video'	-- Utilisation du module video d'OpenCV

-- fonction ecrire dans un fichier excel
function write(path, data, sep)	-- 
    sep = sep or ';'	-- separateur pour décaler d'une colonne à droite
    local file = assert(io.open(path, "w"))
    for i=1,#data do	-- #data = nombre de lignes
        for j=1,#data[i] do	-- #data[i] = nombre de colonnes
            if j>1 then file:write(sep) end
            file:write(data[i][j])	-- data[i][j] = donnée de la case ieme ligne et jeme colonne
        end
        file:write('\n') -- separateur pour descendre d'une ligne
    end
    file:close()
end

local l = 60		-- largeur normalisée des images en entrée du réseau de neurones
local L = 120		-- hauteur normalisée des images en entrée du réseau de neurones

local vid = cv.VideoCapture{vidname}	-- capture du chemin de la vidéo

if not vid:isOpened() then	-- ouverture de la vidéo
    print("Failed to open the video")
    os.exit(-1)
end

local fps = vid:get{cv.CAP_PROP_FPS} 	-- images par seconde
local cptframe = 0			-- compteur image
local oldtps = 0			-- temps début
local tps = 0				-- temps actuel
data ={{'Temps','Nombre de Motos'}}	-- données à écriture dans fichier résultats.xlsx

local pMOG2 = cv.BackgroundSubtractorMOG2{} 	-- Background Subtractor
local _, frame = vid:read{}			-- booléen , image actuelle
-- 30 premières images pour créer le fond fixe de l'image pour le BS
for i=1,30 do
	if not(vid:read{frame}) then
		break
	end
	cptframe = cptframe + 1
	fgMaskMOG2 = pMOG2:apply{frame} -- application du masque BS
end


local width = frame:size()[1]	-- largeur
local length = frame:size()[2]	-- longueur
local Img = torch.Tensor(width,length):zero() 
Img = cv.cvtColor{frame, nil, cv.COLOR_BGR2GRAY}  
local Imgpred = torch.Tensor(width,length):zero()
Imgpred = cv.cvtColor{frame, nil, cv.COLOR_BGR2GRAY}

local CoordTrack = {} 	-- Liste des coordonnées des trackers
local NTrack = 0	-- Nombre de trackers
local VTrack = 5	-- Vitesse du traquer (en pixels/image)
local TVTab = 5		-- Taille du tableau des 5 dernières vitesses
local VTab = {}		-- Liste des vitesses des trackers
for i=1,TVTab do VTab[i] = VTrack end
local cpt = 0		-- compteur de motos par 6 minutes
local cptglb = 0	-- compteur global (total)

-- création de 5 fenetres
cv.namedWindow{'win1'}
cv.setWindowTitle{'win1', 'N&B'}	

cv.namedWindow{'win2'}
cv.setWindowTitle{'win2', 'BcgSub'}

cv.namedWindow{'win3'}
cv.setWindowTitle{'win3', 'Mask'}

cv.namedWindow{'win4'}
cv.setWindowTitle{'win4', 'Blob'}

cv.namedWindow{'win5'}
cv.setWindowTitle{'win5', 'Detection'}

local pause = false 
local key = 0
local key_SPACE = 32  	-- touche Espace
local key_ESCAPE = 27 	-- touche Echap
local key_Q = 113	-- touche Q

while true do
	if key == key_SPACE then	-- mettre en pause avec la touche espace
		key = 0
		pause = not pause
		print("en pause")
		key=cv.waitKey{0}
	elseif key == key_ESCAPE or key == key_Q then -- quitter avec les touches Echap ou Q
		print("quitter")
		break
	end
	
	if not pause then

		if not(vid:read{frame}) then	-- fin de la vidéo
			print("Fin de la video")
			key=cv.waitKey{0}
			break
		end
		cptframe = cptframe + 1

		local Img = cv.cvtColor{frame, nil, cv.COLOR_BGR2GRAY}
		local Imgpred = cv.cvtColor{frame, nil, cv.COLOR_BGR2GRAY}

		local fgMaskMOG2 = pMOG2:apply{frame}								-- application du Background Subtractor
		local Mask = torch.ByteTensor(fgMaskMOG2:size()[1],fgMaskMOG2:size()[2]):copy(fgMaskMOG2)	-- image du Background Subtractor

		cv.threshold{Mask, Mask, 100, 255, cv.THRESH_BINARY} -- pixels entre 0 et 100 =0 (noir), pixels entre 100 et 255 =255 (blanc)

		local erodeElement = cv.getStructuringElement{ cv.MORPH_RECT, cv.Size{4,4}}
		cv.erode{Mask, Mask, erodeElement}	-- erode pixels blancs de 4 dans la longueur et la largeur
		local dilateElement = cv.getStructuringElement{ cv.MORPH_RECT, cv.Size{5,5}}
		cv.dilate{Mask, Mask, dilateElement}	-- dilate pixels blancs de 5 dans la longueur et la largeur

		-- Filtre negatif
		Mask = Mask:apply(function(x)
				x=255-x
				return x
			end)
		
		-- paramètres du détecteur de blobs
		local params = cv.SimpleBlobDetector_Params{}
		-- Change thresholds
		params.minThreshold = 0
		params.maxThreshold = 255
		-- Filter by Area
		params.filterByArea = true
		params.minArea = 500
		params.maxArea = 10000000000000
		-- Filter by Circularity
		params.filterByCircularity = false
		-- Filter by Convexity
		params.filterByConvexity = false
		-- Filter by Inertia
		params.filterByInertia = false
		local detector = cv.SimpleBlobDetector{params}		-- détecte blobs
		local keypoints = detector:detect{Mask}			-- liste des coordonnées des centres de blobs
		local ImgBlob = cv.drawKeypoints{Mask, keypoints}	-- Mask + keypoints

		local CoordPredicted = torch.Tensor(keypoints.size,2):zero() -- liste des coordonnées des centres de blobs
		local NPredicted = 0	-- nombre de prédictions

		for k=1,keypoints.size do
			local x = keypoints.data[k].pt.x	-- coordonnées des points clés
			local y = keypoints.data[k].pt.y
			if y+L/2-1<width and y-L/2>1 and x-l/2>1 and x+l/2-1<length then	-- pour ne pas dépasser du cadre de l'image
				local sub = torch.Tensor(1,L,l):copy(Imgpred:sub(y-L/2,y+L/2-1,x-l/2,x+l/2-1))	-- découpage de l'echantillon à prédire
				-- local tps = os.clock() -- calcul temps pour traverser le réseau
				local predicted = net:forward(sub:view(1,L,l))					-- prediction de l'echantillon
				-- tps = (os.clock() - tps)
				-- print(tps) -- durée d'une prédiction en seconde 
				if predicted[1]==1 then		-- si prédiction >= seuil
					NPredicted = NPredicted + 1
					CoordPredicted[NPredicted][1] = x
					CoordPredicted[NPredicted][2] = y
					-- dessine cercles rouges sur la moto predite
					for i=10,26,8 do
						cv.circle{frame, center={x, y-10}, radius= i, color = {0,0,255},1,8,0}
					end	
				end
				-- dessine un rectangle blanc à chaque prediction dans la fenetre en N&B
				cv.rectangle{Img, pt1={x-l/2, y-L/2}, pt2={x+l/2-1, y+L/2-1}, color = {255,255,255}}
			end
		end

		local Coordchange = {}
		for i=1,NTrack do Coordchange[i] = false end

		for i=1,NPredicted do
			local new = true	-- variable nouvelle moto
			for j=1,NTrack do
				-- si la distance entre l'ordonnée de l'ancienne prediction (traker) et le blob actuel < 50
				-- si la distance entre l'abscisse de l'ancienne prediction et le blob actuel < 30
				if math.abs(CoordTrack[j][1]-CoordPredicted[i][1])<50 and math.abs(CoordTrack[j][2]-CoordPredicted[i][2])<30 then
					new = false	-- ce n'est pas une nouvelle moto
					if math.abs(CoordTrack[j][2]-CoordPredicted[i][2])<15 then	-- si la vitesse (pixels/image) est <15
						table.remove(VTab,1)					-- on supprime la vitesse la plus ancienne du tableau
						table.insert(VTab,math.abs(CoordTrack[j][2]-CoordPredicted[i][2]))	-- on y ajoute la vitesse actuelle
						m=0	-- calcul vitesse moyenne
						for a=1,TVTab do
							m=m+VTab[a]
						end
						VTrack=m/TVTab
					end
					-- Actualisation des coordonnées : copie des coordonnées predites dans tracker
					CoordTrack[j][1] = CoordPredicted[i][1]
					CoordTrack[j][2] = CoordPredicted[i][2]
					CoordTrack[j][3] = CoordTrack[j][3] + 1
					Coordchange[j] = true
					--if CoordTrack[j][3] > 5 then	-- cercle bleu indique que la moto sera comptée
					--	cv.circle{frame, center={CoordTrack[j][1], CoordTrack[j][2]-10}, radius=5, color = {255,0,0},1,4,0}
					--end
				end
			end
			if new then	-- si nouvelle moto détectée
				NTrack = NTrack + 1	-- dessine cercle vert sur la moto predite
				cv.circle{frame, center={CoordPredicted[i][1], CoordPredicted[i][2]-10}, radius= 26, color = {0,255,0},1,8,0}
				table.insert(CoordTrack,{CoordPredicted[i][1],CoordPredicted[i][2],1})	-- ajoute coordonnées dans le tableau des coordonnées
			end
		end

		for j=1,NTrack do
			if not(Coordchange[i]) then	-- si les coordonnées n'ont pas été actualisées, on effectue une prediction à l'emplacement du tracker
				if CoordTrack[j][1]-l/2>1 and CoordTrack[j][2]-L/2>1 and CoordTrack[j][1]+l/2-1<length and CoordTrack[j][2]+L/2-1<width then
					local sub = torch.Tensor(1,L,l):copy(Imgpred:sub(CoordTrack[j][2]-L/2,CoordTrack[j][2]+L/2-1,CoordTrack[j][1]-l/2,CoordTrack[j][1]+l/2-1))
					local predicted = net:forward(sub:view(1,L,l))
					if predicted[1]==1 then	-- dessine un rectangle vert sur la moto traquee
						cv.rectangle{frame, pt1={CoordTrack[j][1]-l/2, CoordTrack[j][2]-L/2}, pt2={CoordTrack[j][1]+l/2-1, CoordTrack[j][2]+L/2-1}, color = {0,255,0}}
						CoordTrack[j][3] = CoordTrack[j][3] + 1
					end
				end
			end
		end

		local j = 1	-- permet d'effacer les doublons
		while j<=NTrack and j>0 do
			local k = 1
			while k<=NTrack and k>0 and j>0 do
				if k~=j then
					if CoordTrack[j][2] == CoordTrack[k][2] then
						table.remove(CoordTrack,k)
						NTrack = NTrack-1
						j = j-1
						k = k-1
					end
				end
				k = k+1
			end
			j = j+1
		end

		j=1
		while j<=NTrack and j>0 do	-- tous les trackers avancent de Vtrack pixels s'ils ne dépassent pas de l'image
			if CoordTrack[j][1]-l/2>1 and CoordTrack[j][2]-L/2>1 and CoordTrack[j][1]+l/2-1<length and CoordTrack[j][2]+L/2-1<width then
				local sub = torch.Tensor(1,L,l):copy(Imgpred:sub(CoordTrack[j][2]-L/2,CoordTrack[j][2]+L/2-1,CoordTrack[j][1]-l/2,CoordTrack[j][1]+l/2-1))
				local predicted = net:forward(sub:view(1,L,l))
				if predicted[1]>0.8 then
					cv.rectangle{frame, pt1={CoordTrack[j][1]-l/2-1, CoordTrack[j][2]-L/2-1}, pt2={CoordTrack[j][1]+l/2-1+1, CoordTrack[j][2]+L/2-1+1}, color = {255,0,0}}
				end
				CoordTrack[j][2] = CoordTrack[j][2]+VTrack
			else	-- si hors cadre
				if CoordTrack[j][3] > 5 then	-- om compte la moto si le compteur > 5
					cpt = cpt+1
					cptglb = cptglb+1
				end	-- supprime les données de la moto
				table.remove(CoordTrack,j)
				NTrack = NTrack-1
				j = j-1
			end
			j = j+1
		end

		if cptframe>=fps then	-- calcul du temps via compteur de frame
			cptframe = 0
			tps = tps + 1
			if tps%(6*60)==0 and tps~=0 then	-- découpage par tranche de 6 minutes
				table.insert(data,{math.floor(oldtps/60) .. ':00' .. '-' .. math.floor(tps/60) .. ':00',cpt})
				oldtps = tps
				cpt = 0
			end
		end
		-- affichage du temps et du compteur de motos en haut de la frame
		cv.rectangle{frame, pt1={0, 0}, pt2={60, 20}, color = {255,255,255},thickness=-1}
		cv.putText{frame,string.format('%02d',math.floor(tps/60)) .. ':' .. string.format('%02d',tps%60),{3,16},cv.FONT_HERSHEY_SIMPLEX,0.6,{0,0,0},2}
		cv.rectangle{frame, pt1={length-290, 0}, pt2={length, 20}, color = {255,255,255},thickness=-1}
		if cptglb>1 then
			cv.putText{frame,string.format('Traqumoto compte %d motos',cptglb),{length-290,16},cv.FONT_HERSHEY_SIMPLEX,0.6,{0,0,0},2}
		else
			cv.putText{frame,string.format('Traqumoto compte %d moto',cptglb),{length-290,16},cv.FONT_HERSHEY_SIMPLEX,0.6,{0,0,0},2}
		end

		-- affichage des fenetres
		cv.imshow{'win1', Img}		-- vidéo en niveaux de gris avec prédictions effectuées (rectangles blancs)		
		cv.imshow{'win2', fgMaskMOG2} 	-- Masque Background Subtractor, fond en noir et pixels en mouvement en blanc
		cv.imshow{'win3', Mask} 	-- BS + fonctions Eroder & Dilater
		cv.imshow{'win4', ImgBlob}	-- BS + E&D + détection blobs
		cv.imshow{'win5', frame}	-- vidéo avec trackers + compteur + temps 
		
		key=cv.waitKey{1} -- temps entre chaque image en ms
	end
end
-- écriture temps dans fichier excel
table.insert(data,{math.floor(oldtps/60) .. ':00' .. '-' .. math.floor(tps/60) .. ':' .. string.format('%02d',tps%60),cpt})

cv.destroyAllWindows{}
