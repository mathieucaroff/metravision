# Interaction
import os
import yaml

# Usual
import abc
import collections
import itertools
# import pprint as Pprint

# pprint = Pprint.PrettyPrinter(indent = 2).pprint

# Internal
from util import Namespace
from util import Dotdict
from util import ReadOnlyDotdict


glob = Namespace()


def test_MvConfig():
    configData = yaml.load("""
networkDestination: /your/path
networkLocation: /your/path.t7
resultDestination: /your/path.csv
training:
    iterationCount: 1
    threashold: 0.60
network:
    imgWidth: 60
    imgHeight: 120 # Dimensions normalisées en entrée du réseau de neuronne.
activeWindows:
    nb: true # Vidéo en niveaux de gris avec prédictions effectuées (rectangles blancs)
    bcgSub: false # Masque Background Subtractor, fond en noir et pixels en mouvement en blanc
    mask: false # BS + Fonctions Eroder & Dilater
    blob: true # BS + E&D + détection blobs
    detection: true # Vidéo avec trackers + compteur + temps
image:
    directoryLocation: /path/to/image-dataset
    nameFormat: "%06d.png"
    categories:
        bike:
            dirname: bike
            first: 1
            count: 6
            learningFraction: [2, 3]
        notBike:
            dirname: not-bike
            first: 1
            count: 8
            learningFraction: [2, 3]
video:
    directoryLocation: /path/to/video
    short:
        directoryName: "short"
        files: !!set
            ? 8s.mp4
            ? bouchon-40s.mp4
            ? embouteillage-21s.mp4
            ? soleil-1m32.avi
            ? test-9s.avi
    medium:
        directoryName: "6min"
        files: !!set
            ? 1ereSequence.avi
            ? DerniereSequence.avi
            ? HeureDePointe.avi
    long: null
""")
    config = MvConfig.fromRawConfigData(configData)
    glob.config = config

    # Image dataset
    assert len(config.image) == 2
    for categoryName in ("bike", "notBike"):
        category = config.image[categoryName]
        for learnOrTest in ("learn", "test"):
            assert learnOrTest in category
    assert len(config.image.bike.learn.files) == 4
    assert len(config.image.notBike.test.files) == 3  # 8 / 3 = 2.66 -> ceil: 3

    # v Not working for some reason v
    assert "/path/to/image-dataset\\bike\\000006.png" in config.image["bike"]["test"].files
    assert "/path/to/image-dataset\\not-bike\\000001.png" in config.image.notBike.learn.files

    # Test video file sets
    assert len(config.video.short.files) == 5
    assert r"/path/to/video\short\8s.mp4" in config.video.short.files
    assert r"/path/to/video\6min\DerniereSequence.avi" in config.video.medium.files
    assert len(config.video.files) == 8


class MvDirectory(ReadOnlyDotdict):
    def __init__(self, filePathFormat = None, fileValues = None, subdirs = {}):
        
        # Verifications
        assert type(subdirs) == dict

        if subdirs != {} and (filePathFormat is not None or fileValues is not None):
            raise ValueError("Argument subdir can't be used with filePathFormat and fileValues.")

        if (filePathFormat is None) != (fileValues is None):
            raise ValueError("Arguments filePathFormat and fileValues must always be used together.")


        # Assignements
        for dirname, dirvalue in subdirs.items():
            self[dirname] = dirvalue
        
        self.__subdirs = subdirs
        if filePathFormat is not None:            
            self.__files = [ filePathFormat % val for val in fileValues ]
    
    @property
    def files(self):
        """
        List all own and subdirectory files.
        Returns them as a list if they are it's own files.
        Returns them as a tuple if they are from it's subdirectory.
        """
        try:
            files = self.__files
            assert(files is not None)
            return files
        except (AttributeError, AssertionError):
            subdirFileListList = map(lambda dir: dir.files, self.__subdirs.values())
            subFiles = tuple(itertools.chain(*subdirFileListList))
            return subFiles


class MvConfig(Dotdict):
    # collections.namedtuple("AbstractMvConfig", "imageDataset, testVideoFileSets"))
    @staticmethod
    def fromConfigFile(configFile):
        """
        @param configFile: An opened metravision yaml configuration file.
        @return MvConfig mvConfigObject: An MvConfig object, corresponding to the data.
        """
        rawConfigData = yaml.load(configFile)
        return MvConfig.fromRawConfigData(rawConfigData)
    
    @classmethod
    def fromRawConfigData(cls, rawConfigData):
        """
        @param rawConfigData: A hierchy of dict, list and sets containing the configuration informations
        @return MvConfig resultConfig: An MvConfig object, corresponding to the data.
        """
        
        resultConfig = MvConfig()

        resultConfig.raw = rawConfigData

        # image
        resultConfig.image = cls.__expandImage(rawConfigData["image"])

        # video
        resultConfig.video = cls.__expandVideo(rawConfigData["video"])

        return resultConfig

    @classmethod
    def __expandImage(cls, imageDatasetDescription):
        """
        @param imageDatasetDescription: A yaml-produced hierchy of dict, list and sets describing the image locations.
        @return MvDirectory imageDirectory: Lists of the available image files.
        """
        directoryLocation = imageDatasetDescription["directoryLocation"]
        categories = dict()
        nameFormat = imageDatasetDescription["nameFormat"]
        for subdirname, dirDescription in imageDatasetDescription["categories"].items():
            dirname = dirDescription["dirname"]
            firstImgIndex = dirDescription["first"]
            imgCount = dirDescription["count"]
            lFrac = dirDescription["learningFraction"]

            imgLearnCount = imgCount * lFrac[0] // lFrac[1]
            imgTestCount = imgCount - imgLearnCount

            subdirs = {}
            filePathFormat = os.path.join(directoryLocation, dirname, nameFormat)
            first = firstImgIndex
            subdirs["learn"] = MvDirectory(filePathFormat = filePathFormat, fileValues = range(first, first + imgLearnCount))
            first = firstImgIndex + imgLearnCount
            subdirs["test"] = MvDirectory(filePathFormat = filePathFormat, fileValues = range(first, first + imgTestCount))

            categories[subdirname] = MvDirectory(subdirs = subdirs)

        imageDirectory = MvDirectory(subdirs = categories)
        return imageDirectory


    @classmethod
    def __expandVideo(cls, videoDatasetDescription):
        """
        @param videoDatasetDescription: A yaml-produced hierchy of dict, list and sets describing the video locations.
        @return MvDirectory videoDirectory: Lists of the available video files.
        """
        # test-video
        directoryLocation = videoDatasetDescription["directoryLocation"]
        categories = dict()
        for videoKind in ("short", "medium", "long"):
            categoryDescription = videoDatasetDescription[videoKind]
            if categoryDescription is not None:
                directoryName = categoryDescription["directoryName"]
                filePathFormat = os.path.join(directoryLocation, directoryName, "%s")
                categories[videoKind] = MvDirectory(filePathFormat = filePathFormat, fileValues = categoryDescription["files"])

        videoDirectory = MvDirectory(subdirs = categories)
        return videoDirectory

if __name__ == "__main__":
    test_MvConfig()