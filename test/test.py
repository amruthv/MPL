import packagehelper

import math
from Tkinter import *
from mpl import algorithm_runner
from mpl.common.simplemcrhelper import SimpleMCRHelper
from mpl.common.world import World, SimpleObstacle
from mpl.common.movableLinkRobot import MovableLinkRobot
from mpl.common.simulator import Simulator


pi = math.pi
piOver2 = math.pi / 2

def testOneObstacleMiddle():
    master = Tk()
    canvas = Canvas(master, width=500, height=350)
    canvas.pack()
    sim = Simulator(canvas, 500, 350)

    obstacle1 = SimpleObstacle([(200,20), (300,20), (300,150), (200,150)])
    obstacles = [] 
    obstacles = [obstacle1]
    sim.drawObstacles(obstacles)
    world = World(500,350, obstacles)

    links = []
    links.append([0, [(50,50), (90,50), (90,70), (50,70)]])
    links.append([0, [(90,50), (130,50), (130,70), (90,70)]])
    links.append([0, [(130,50), (170,50), (170,70), (130,70)]])
    start = (50,50, 0, 0, 0)
    goal = (320, 50, 0, piOver2, -piOver2)
    linkRobot = MovableLinkRobot(links, world)
    sim.drawRobot(linkRobot)
    linkRobot.moveToConfiguration(goal)
    sim.drawRobot(linkRobot)
    raw_input()

    helper = SimpleMCRHelper(linkRobot, world, goal)
    path, cover = algorithm_runner.runAlgorithm(start, goal, helper, 1)
    sim.drawPoint((start[0], start[1]), fill = 'green')
    sim.drawPoint((goal[0], goal[1]), fill = 'blue')
    sim.drawPath(obstacles, linkRobot, path)


if __name__ == '__main__':
    testOneObstacleMiddle()