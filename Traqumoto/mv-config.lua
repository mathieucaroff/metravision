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
cr.seuil = 0.60		-- seuil pour comparer au résultat de la prédiction (moto=1, pasmoto=0)

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

return config