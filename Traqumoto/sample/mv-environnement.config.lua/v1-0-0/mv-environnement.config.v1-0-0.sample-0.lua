-- # Environnment # --
-- Torch path
config.torchLocation = "/home/user/traqumoto/Application/torch" -- UNUSED YET

-- Video de test --
-- (Chemin de la vidéo en entrée)
config.videoLocation = "/media/mvdata/test-videos/HeureDePointe.avi"

-- Fichier de réseau de neuronne --
-- Pour creationReseau (écriture):
config.networkDestionation = '/media/mvdata/networks/network.t7'
-- Étape de la création
config.torchAppDatasetFile = '/media/mvdata/torch-dataset-files/datasetApp.t7'
config.torchTestDataseFile = '/media/mvdata/torch-dataset-files/datasetTest.t7'

-- Pour prevision (lecture):
config.networkLocation = '/media/mvdata/networks/network.t7'

-- Fichier de destination des résultats --
config.resultDestination = '/media/mvdata/results/resultats.csv'
