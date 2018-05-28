import util

class AnalyseData:
    def __init__(self, timePerFrame, jumpEventSubscriber):
        self.timePerFrame = timePerFrame
        self._data = []

        jumpEventSubscriber.append(self.addJumpNotice)
    
    def addVehicle(self, veHistory):
        time = max(veHistory.keys()) * self.timePerFrame

        getRatio = lambda mvBbox: mvBbox[3] / mvBbox[2] # width / height
        ratios = map(getRatio, veHistory.values())
        medianRatio = util.median(ratios)
        vehicle = "Moto" if medianRatio > 1.6 else "Automobile"
        self._data.append((time, vehicle))
    
    def addJumpNotice(self, frameIndex, **_kwargs):
        time = frameIndex * self.timePerFrame
        self._data.append((time, "<Jumping>"))
    
    def getData(self):
        return self._data