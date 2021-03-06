from polygonhelper import *
from robotpolygon import *
import numpy as np
from heapq import * 
import math
import random

class LinkRobot():
    #polygonArr is an array of tuples (angle, array of points -- not polygon objects or point objects) e.g [(0,[([1,2],[3,4]]), (20,[[5,5],[6,6]]]) 
    def __init__(self, polygonInfoArray, world, goal):
        self.polygons = self.movePolygonsToOrigin(polygonInfoArray)
        self.numJoints = len(polygonInfoArray)
        referenceTransforms, inverseReferenceTransforms = self.makeInitialTransforms(polygonInfoArray)
        self.referenceTransforms = referenceTransforms
        self.inverseReferenceTransforms = inverseReferenceTransforms
        self.moveToConfiguration([0] * self.numJoints)
        self.world = world
        self.goal = goal

    def movePolygonsToOrigin(self, polygonInfoArray):
        polygons = []
        for (_, polygonPoints) in polygonInfoArray:
            pointsMovedToOrigin = []
            deltaX, deltaY = polygonPoints[0]
            for (x,y) in polygonPoints:
                pointsMovedToOrigin.append((x - deltaX, y - deltaY))
            polygons.append(pointsMovedToOrigin)
        return polygons

    def makeInitialTransforms(self, polygonInfoArray):
        referenceTransforms = []
        inverseReferenceTransforms = []
        for polygonAngle, polygonPoints in polygonInfoArray:
            polygonRotationPoint = polygonPoints[0]
            radians = math.radians(polygonAngle)
            cosTheta = math.cos(radians)
            sinTheta = math.sin(radians)
            transform = np.array([[cosTheta, -sinTheta, polygonRotationPoint[0]], 
                [sinTheta, cosTheta, polygonRotationPoint[1]],
                [0, 0, 1]])
            referenceTransforms.append(transform)
            inverseReferenceTransforms.append(np.linalg.inv(transform))
        return referenceTransforms, inverseReferenceTransforms

    def findTransformsForConfiguration(self, configuration):
        transforms = []
        for jointNum, jointAngle in enumerate(configuration):
            radians = math.radians(jointAngle)
            cosTheta = math.cos(radians)
            sinTheta = math.sin(radians)
            rotationMatrix = np.array([[cosTheta, -sinTheta, 0],
                                [sinTheta, cosTheta, 0],
                                [0, 0, 1]])
            if jointNum == 0:
                transform = self.referenceTransforms[jointNum].dot(rotationMatrix)
            else:
                previousJointTransform = transforms[jointNum - 1]
                transformToPreviousFrame = self.inverseReferenceTransforms[jointNum - 1].dot(self.referenceTransforms[jointNum])
                transform = previousJointTransform.dot(transformToPreviousFrame).dot(rotationMatrix)
            transforms.append(transform)
        return transforms


    # list of joint angles
    def moveToConfiguration(self, q):
        transforms = self.findTransformsForConfiguration(q)
        positionOfRobot = []
        for polygonNumber, polygonPosition in enumerate(self.polygons):
            transformedPolygonPoints = []
            for xPoint, yPoint in polygonPosition:
                transformedPoint = transforms[polygonNumber].dot(np.array([xPoint, yPoint, 1]))
                transformedPolygonPoints.append(Point(transformedPoint[0], transformedPoint[1]))
            positionOfRobot.append(Polygon(transformedPolygonPoints))
        self.position = positionOfRobot

    def generateRandomConfiguration(self, goalBias):
        if random.random() < goalBias:
            q_rand = self.goal
        else:
            q_rand = [random.randint(-180,180) for i in range(self.numJoints)]
        return q_rand

    def makeRotationMatrix(self, rotationAngle):
        radians = math.radians(rotationAngle)
        cosTheta = math.cos(radians)
        sinTheta = math.sin(radians)
        return np.array([[cosTheta, -sinTheta, 0], [sinTheta, cosTheta, 0], [0, 0, 1]])

    def inBounds(self):
        for polygon in self.position:
            for point in polygon.points:
                if not self.world.inRange(point.x, point.y):
                    return False
        return True
