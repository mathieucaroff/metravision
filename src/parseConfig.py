# Interaction
import os
import yaml

# Usual
import abc
import collections

# Internal
from util import Dotdict


class MvConfig(collections.namedtuple("AbstractMvConfig", "dataset, testVideoFileSets")):
    @staticmethod
    def fromConfigFile(configFile):
        """
        @param configFile: An opened metravision configuration file.
        @return MvConfig mvConfigObject: An MvConfig object.
        """
        configData = yaml.load(configFile)
        return MvConfig.fromConfigData(configData)
    
    @classmethod
    def fromConfigData(cls, configData):
        # dataset
        dataset = configData["dataset"]
        datasetFileSets = dict()
        for subdirname, dirDescription in dataset.items():
            
            dirname = dirDescription["dirname"]
            nameFormat = dataset["nameFormat"]
            firstImgIndex = dirDescription["first"]
            imgCount = dirDescription["count"]
            lFrac = dirDescription["learningFraction"]

            imgLearnCount = imgCount * lFrac[0] // lFrac[1]
            imgTestCount = imgCount - imgLearnCount

            datasetFileSets[(subdirname, "learn")] = generateFileIteratorFromRange(
                dataset["directoryLocation"], dirname, nameFormat, firstImgIndex,
                imgLearnCount
            )
            datasetFileSets[(subdirname, "test")] = generateFileIteratorFromRange(
                dataset["directoryLocation"], dirname, nameFormat, firstImgIndex,
                imgTestCount
            )

        # test-video
        testVideos = configData["test-videos"]
        testVideosDirectoryLocation = testVideos["directoryLocation"]
        testVideoFileSets = Dotdict()
        for videoKind in ("short", "medium", "long"):
            testVideoFileSets[videoKind] = set(generateFileIteratorFromSet(testVideosDirectoryLocation, testVideos[videoKind]))
        
        return cls(datasetFileSets, testVideoFileSets)


def joinpath(begining, end):
    if begining[-1] == "/" or end[0] == "/":
        pathformat = "%s%s"
        if begining[-1] == "/" and end[0] == "/":
            end = end[1:]
    else:
        pathformat = "%s/%s"
    dirpath = pathformat % (begining, end)
    return dirpath


def generateFileIteratorFromRange(directoryLocation, subdirname, nameFormat, first, count):
    dirpath = os.path.join(directoryLocation, subdirname)

    for index in range(first, first + count):
        yield os.path.join(dirpath, nameFormat % index)

def generateFileIteratorFromSet(directoryLocation, mvConfigDirectoryDescription):
    if directoryLocation[-1] != "/":
        pathformat = "%s/%s/"
    else:
        pathformat = "%s%s/"
    dirpath = pathformat % (directoryLocation, mvConfigDirectoryDescription["directoryName"])

    filepathset = mvConfigDirectoryDescription["files"]
    fileset = map(lambda filepath: dirpath + filepath, filepathset)
    return fileset