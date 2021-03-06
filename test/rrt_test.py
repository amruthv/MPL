from drawCommon import *
from testWorlds import *
import packagehelper

import math
from Tkinter import *
from mpl.common import searcher
from mpl.algorithms.rrt_variants.rrt.new_rrt import RRTSearcher
from mpl.common.movableLinkRobot import MovableLinkRobot
from mpl.common.world import World, SimpleObstacle
from mpl.common.MPLHelper import MPLHelper

pi = math.pi
piOver2 = math.pi / 2

def testOneObstacleMiddle():
    
    world, obstacles = getWorldMiddleObstacle()

    links = []
    links.append([0, [(50,50), (90,50), (90,70), (50,70)]])
    links.append([0, [(90,50), (130,50), (130,70), (90,70)]])
    links.append([0, [(130,50), (170,50), (170,70), (130,70)]])
    start = (50,50, 0, 0, 0)
    goal = (320, 50, 0, piOver2, -piOver2)
    linkRobot = MovableLinkRobot(links, world)

    helper = MPLHelper(linkRobot, world, goal, 50)
    rrt = RRTSearcher(start, goal, helper)
    
    sim = makeSim(world)
    drawProblemAndWait(sim, linkRobot, obstacles, start, goal)

    if rrt.run():
        path = searcher.reconstructPath(rrt.cameFrom, goal)
        sim.drawPath(obstacles, linkRobot, path)


if __name__ == '__main__':
    testOneObstacleMiddle()
