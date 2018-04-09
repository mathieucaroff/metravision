import yaml
import abc
import collections

class Dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

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
        dataset = configData["dataset"]
        datasetDirectoryLocation = dataset["directoryLocation"]
        datasetFileSets = Dotdict()
        for subdirname, dirDescription in dataset.items():
            datasetFileSets[subdirname] = generateFileIteratorFromRange(datasetDirectoryLocation, subdirname, dataset["nameFormat"], dirDescription["first"], dirDescription["count"])

        testVideos = configData["test-videos"]
        testVideosDirectoryLocation = testVideos["directoryLocation"]
        testVideoFileSets = Dotdict()
        for videoKind in ("short", "medium", "long"):
            testVideoFileSets[videoKind] = set(generateFileIteratorFromSet(testVideosDirectoryLocation, testVideos[videoKind]))
        
        return cls(datasetFileSets, testVideoFileSets)


def getSubDirpath(directoryLocation, subdirname):
    if directoryLocation[-1] != "/":
        pathformat = "%s/%s/"
    else:
        pathformat = "%s%s/"
    dirpath = pathformat % (directoryLocation, subdirname)
    return dirpath


def generateFileIteratorFromRange(directoryLocation, subdirname, nameFormat, first, count):
    dirpath = getSubDirpath(directoryLocation, subdirname)

    for index in range(first, first + count):
        yield dirpath + nameFormat % index

def generateFileIteratorFromSet(directoryLocation, mvConfigDirectoryDescription):
    if directoryLocation[-1] != "/":
        pathformat = "%s/%s/"
    else:
        pathformat = "%s%s/"
    dirpath = pathformat % (directoryLocation, mvConfigDirectoryDescription["directoryName"])

    filepathset = mvConfigDirectoryDescription["files"]
    fileset = map(lambda filepath: dirpath + filepath, filepathset)
    return fileset