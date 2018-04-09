local config = {}
-- # Entrainement # --
-- CreationRéseau
local cr = {}
config.creationReseau = cr

cr.n1 = 1300			-- Nombre d'images de motos
cr.n2 = 1800			-- Nombre d'images de pas motos
cr.n1app = 800		-- Nombre d'images de motos pour l'apprentissage
cr.n2app = 1200		-- Nombre d'images de pas motos pour l'apprentissage
-- Les image qui ne sont pas attribuée à l'apprentissage sont utilisées pour le test

cr.nbiterations = 1 -- nombre d'itérations
cr.seuil = 0.60		-- seuil pour comparer au résultat de la prédiction (moto = 1, pasmoto = 0)

cr.nt = 10	-- nombre de transformations
cr.l = 60	-- largeur normalisée des images en entrée du réseau de neurones
cr.L = 120	-- hauteur normalisée des images en entrée du réseau de neurones

cr.datasetLocationFormat = "/media/mvdata/dataset/%s/%06d.png"
cr.bikeDirname = "bike"
cr.notBikeDirname = "not-bike"

-- Prédiction -- Traqumoto
local pr = {}
config.prediction = pr
pr.l = cr.l
pr.L = cr.L


-- # Environnment # --
-- Torch path
config.torchLocation = "/home/user/traqumoto/Application/torch" -- UNUSED YET

-- Video de test --
-- (Chemin de la vidéo en entrée)
config.videoLocation = "/media/mvdata/test-videos/HeureDePointe.avi"

-- Fichier de réseau de neuronne --
-- Pour creationReseau (écriture):
config.networkDestionation = '/media/mvdata/networks/mcgen-network.t7'
-- Étape de la création
config.torchAppDatasetFile = '/media/mvdata/torch-dataset-files/datasetApp.t7'
config.torchTestDataseFile = '/media/mvdata/torch-dataset-files/datasetTest.t7'

-- Pour prevision (lecture):
config.networkLocation = '/media/mvdata/networks/mcgen-network.t7'

-- Fichier de destination des résultats --
config.resultDestination = '/media/mvdata/results/resultats.csv'

-- # Interface # --
config.windows = {}
config.windows.nb = false -- vidéo en niveaux de gris avec prédictions effectuées (rectangles blancs)
config.windows.bcgSub = false -- Masque Background Subtractor, fond en noir et pixels en mouvement en blanc
config.windows.mask = false -- BS + fonctions Eroder & Dilater
config.windows.blob = true  -- BS + E&D + détection blobs
config.windows.detection = true -- vidéo avec trackers + compteur + temps

return config