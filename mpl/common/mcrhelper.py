class MCRHelper():
    # return back list of obstacles that are in collision when robot is at configuration q
    def collisionsAtQ(self, q):
        raise NotImplementedError()

    # return a configuration represented as a list, can use the passed goal to do goal biasing in random sampling
    def sampleConfig(self, goal):
        raise NotImplementedError()

    # return a list of configurations (as defined above that exclude qFrom and qTo ie (qFrom... qTo) )
    def generateInBetweenConfigs(self, qFrom, qTo):
        raise NotImplementedError()

    # scalar representation of the distance between these configurations
    def distance(self, q1, q2):
        raise NotImplementedError()

    # get configuration that is in the direction (qFrom -> qTo) with max stepSize = stepSize
    def stepTowards(self, qFrom, qTo, stepSize):
        raise NotImplementedError()

    def getStepSize(self):
        raise NotImplementedError()