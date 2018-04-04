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
Dans ce ficher, le code crée une base de données constituée de
	10 (transformations) * Napp
images. Puis il crée le réseau de neurones et l'entraine avec la base
de données. Ensuite, il teste les Ntest images pour évaluer le réseau.
]]

require 'mv-header'

require 'cv.imgcodecs'
require 'cv.imgproc'

local cr = config.creationReseau

local n1 = cr.n1			-- Nombre d'images de motos
local n2 = cr.n2			-- Nombre d'images de pas motos
local N = n1 + n2			-- Nombre total d'images
local n1app = cr.n1app		-- Nombre d'images de motos pour l'apprentissage
local n2app = cr.n2app		-- Nombre d'images de pas motos pour l'apprentissage
local Napp = n1app + n2app	-- Nombre total d'images pour l'apprentissage
local n1test = n1 - n1app	-- Nombre d'images de motos pour le test
local n2test = n2 - n2app	-- Nombre d'images de pas motos pour le test
local Ntest = n1test + n2test	-- Nombre d'échantillons de tests

local nbiterations = cr.nbiterations -- nombre d'itérations
local seuil = cr.seuil		-- seuil pour comparer au résultat de la prédiction (moto=1, pasmoto=0)

local nt = cr.nt	-- nombre de transformations
local l = cr.l	-- largeur normalisée des images en entrée du réseau de neurones
local L = cr.L	-- hauteur normalisée des images en entrée du réseau de neurones

local datasetLocationFormat = cr.datasetLocationFormat
local bikeDirname = cr.bikeDirname
local notBikeDirname = cr.notBikeDirname

-- Creation de la base de données d'images
function creation_dataset()
	local imgsetMoto = torch.Tensor(n1,1,L,l):zero() 	-- tableau contenant les images de motos
	local imgsetPasMoto = torch.Tensor(n2,1,L,l):zero() 	-- tableau contenant les images de pas motos

	for i=1,N do
		local yesMoto = i <= n1
		local j = i - n1
		
		if yesMoto then
			imgname = string.format(datasetLocationFormat, bikeDirname, i)
		else
			imgname = string.format(datasetLocationFormat, notBikeDirname, j)
		end

		f = io.open(imgname)
		if f ~= nil then
			-- printTRM("File `" .. imgname .. "` exists")
			f:close()
		else
			printTRM("File `" .. imgname .. "` doesn't exist")
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

	local printTRM_debug = util.nope

	printTRM_debug("<Structure du réseau>")

	printTRM_debug("net = nn.Sequential")
	local net = nn.Sequential()										-- Réseau de neurones
	printTRM_debug("nn.SpatialConvolution--1")
	net:add(nn.SpatialConvolution(inputs,couche1,tailleConvolution,tailleConvolution))			-- Convolution
	printTRM_debug("nn.ReLU--1")
	net:add(nn.ReLU())											-- Application du ReLU 
	printTRM_debug("nn.SpatialMaxPooling--1")
	net:add(nn.SpatialMaxPooling(tailleMaxPooling,tailleMaxPooling,tailleMaxPooling,tailleMaxPooling))	-- Max Pooling pour réduire les images
	printTRM_debug("nn.SpatialConvolution--2")
	net:add(nn.SpatialConvolution(couche1,couche2,tailleConvolution,tailleConvolution))			-- 6 input image channels, 16 output channels, 5x5 convolution kernel
	printTRM_debug("nn.ReLU--2")
	net:add(nn.ReLU())											-- Application du ReLU 
	printTRM_debug("nn.SpatialMaxPooling--2")
	net:add(nn.SpatialMaxPooling(tailleMaxPooling,tailleMaxPooling,tailleMaxPooling,tailleMaxPooling))	-- Max Pooling pour réduire les images
	printTRM_debug("nn.View")
	net:add(nn.View(couche2*27*12))										-- redimmensionnement en un seul tableau
	printTRM_debug("nn.Linear--1")
	net:add(nn.Linear(couche2*27*12,couche3))								-- Liens entre la deuxième et troisième couche
	printTRM_debug("nn.ReLU--3")
	net:add(nn.ReLU())											-- Application du ReLU
	printTRM_debug("nn.Linear--2")
	net:add(nn.Linear(couche3,outputs))									-- Liens entre la  troisième couche et la couche de sortie
	printTRM_debug("nn.Sigmoid")
	net:add(nn.Sigmoid())											-- Sigmoid pour que les résultats soient entre 0 et 1
	
	printTRM("nn.BCECriterion")
	local criterion = nn.BCECriterion()				-- Choix du critère d'entrainement, BCE adapté à deux classes
	printTRM("nn.StochasticGradient")
	local trainer = nn.StochasticGradient(net, criterion)		-- Création de l'entraineur avec le reseau et le critère
	trainer.learningRate = 0.0005		-- paramètre vitesse d'apprentissage
	trainer.maxIteration = nbiterations	-- paramètre nombre d'itérations
	printTRM("trainer:train(dataset)")
	trainer:train(dataset)			-- lance l'entrainement du reseau de neurones avec la base de données

	printTRM("torch.save('network.t7', net)")
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
	printTRM('[Résultat] ' .. cptVP/n1test*100 .. '% de Vrai-Positifs pour le seuil de ' .. seuil)
	printTRM('[Résultat] ' .. cptFN/n2test*100 .. '% de Faux-Negatifs pour le seuil de ' .. seuil)
end

-- Main
printTRM("[Main] Prétraitement et création de la base de données")
datasetApp,datasetTest = creation_dataset()
printTRM("[Main] Prétraitement et entrainement du réseau de neurones")
local tps = os.time()
net = entrainement(datasetApp)
printTRM("[Main] Réseau sauvegardé")
tps = (os.time() - tps)	-- durée de l'entrainement
printTRM("[Main] Temps d'entrainement : " .. math.floor(tps/86400) .. "d " .. math.floor(tps/3600)%86400 .. "h " .. math.floor(tps/60)%60 .. "m " .. tps%60 .. "s")
printTRM("[Main] Test du réseau")
testNetwork(net,datasetTest,seuil)
