import heapq
import numpy as np
import math
from scipy.spatial import KDTree
from new_rrt import RRTSearcher
from mpl.common import covercalculator
from mpl.common.cover import Cover
from mpl.common import searcher
from mpl.common import tlpObstacles
import mpl.mplGlobals as mplGlob
import pdb

#bi rrt implementation that determines obstacles with interest of removing.
class BiRRTIgnoreObstaclesSearcher(object):
    def __init__(self, start, goal, helper, useTLPObstacles):
        self.start = start
        self.goal = goal
        self.helper = helper
        self.RRT1 = RRTSearcher(start, goal, helper, useTLPObstacles, extendBackwards = False)
        self.RRT2 = RRTSearcher(goal, start, helper, useTLPObstacles, extendBackwards = True)
        self.meetingPoint = None
        self.useTLPObstacles = useTLPObstacles

    def run(self):
        for i in range(mplGlob.rrtIterFailLimit):
            success = self.search()
            if success:
                self.foundPath = True
                return True
        self.foundPath = False
        return False


    # want memoryFactor <= 1 used to discount previous weights since removing an obstacle opens up new space
    def search(self):
        for iterNum in range(mplGlob.iterCount):
            qExtended = self.RRT1.runIteration()
            if qExtended is not None:
                self.RRT2.rebuildTreeIfNecessary()
                qNearest = self.RRT2.nearestConfig(qExtended)
                if qNearest == qExtended:
                    self.meetingPoint = qExtended
                    return True 
                qExtendedTree2 = self.RRT2.extendToward(qNearest, qExtended)
                if qExtendedTree2 is not None:
                    self.RRT2.updateRRTWithNewNode(qNearest, qExtendedTree2)
                    if qExtendedTree2 == qExtended:
                        self.meetingPoint = qExtended
                        return True
            if self.RRT1.treeSize() > self.RRT2.treeSize():
                self.RRT1, self.RRT2 = self.RRT2, self.RRT1
        return False

    def getPath(self):
        if not self.foundPath:
            return []
        if self.RRT1.goal == self.goal:
            tree1 = self.RRT1
            tree2 = self.RRT2
        else:
            tree1 = self.RRT2
            tree2 = self.RRT1

        pathFromStart = searcher.reconstructPath(tree1.cameFrom, self.meetingPoint)
        pathFromGoal = searcher.reconstructPath(tree2.cameFrom, self.meetingPoint)
        if self.meetingPoint == self.goal:
            pathToReturn = pathFromStart
        elif self.meetingPoint == self.start:
            pathToReturn = pathFromGoal[::-1]
        else:
            pathFromMeetingToGoal = pathFromGoal[:-1][::-1]
            pathFromMeetingToGoal = pathFromMeetingToGoal[:-1] + [self.goal]   
            pathToReturn = pathFromStart + pathFromMeetingToGoal
        pathToReturn = [self.start] + pathToReturn[1:-1] + [self.goal]
        return pathToReturn

    def getCover(self):
        trajectory = self.getPath()
        cc = covercalculator.CoverCalculator(self.helper, self.useTLPObstacles)
        pathCover = Cover(set(), self.useTLPObstacles)
        for i in range(len(trajectory) - 1):
            edgeCoverInclusive = cc.edgeCover(trajectory[i], trajectory[i+1])
            pathCover = pathCover.mergeWith(edgeCoverInclusive)
        return list(pathCover.cover)