from robot import *
import numpy as np
import math
import random
from shapely.geometry import Polygon

class MovableLinkRobot(Robot):
    #polygonArr is an array of tuples (angle, array of points -- not polygon objects or point objects) e.g [(0,[([1,2],[3,4]]), (20,[[5,5],[6,6]]]) 
    def __init__(self, polygonInfoArray, world):
        self.polygons = self.movePolygonsToOrigin(polygonInfoArray)
        self.numJoints = len(polygonInfoArray)
        referenceTransforms, inverseReferenceTransforms = self.makeInitialTransforms(polygonInfoArray)
        self.referenceTransforms = referenceTransforms
        self.inverseReferenceTransforms = inverseReferenceTransforms
        # extract the x,y coordinate of the first leg from the provided points
        firstCoordinate = list(polygonInfoArray[0][1][0])   
        self.initialOrigin = firstCoordinate
        self.moveToConfiguration(firstCoordinate + [0] * self.numJoints)
        self.world = world

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
            cosTheta = math.cos(polygonAngle)
            sinTheta = math.sin(polygonAngle)
            transform = np.array([[cosTheta, -sinTheta, polygonRotationPoint[0]], 
                [sinTheta, cosTheta, polygonRotationPoint[1]],
                [0, 0, 1]])
            referenceTransforms.append(transform)
            inverseReferenceTransforms.append(np.linalg.inv(transform))
        return referenceTransforms, inverseReferenceTransforms

    def findTransformsForConfiguration(self, configuration):
        transforms = []
        for jointNum, jointAngle in enumerate(configuration):
            cosTheta = math.cos(jointAngle)
            sinTheta = math.sin(jointAngle)
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


    # [x,y, joint angles]
    def moveToConfiguration(self, q):
        transforms = self.findTransformsForConfiguration(q[2:])
        positionOfRobot = []
        for polygonNumber, polygonPosition in enumerate(self.polygons):
            transformedPolygonPoints = []
            for xPoint, yPoint in polygonPosition:
                transformedPoint = transforms[polygonNumber].dot(np.array([xPoint, yPoint, 1]))
                # transformedPolygonPoints.append(Point(transformedPoint[0], transformedPoint[1]))
                transformedPolygonPoints.append((transformedPoint[0] + q[0] - self.initialOrigin[0], transformedPoint[1] + q[1] - self.initialOrigin[1]))
                positionOfRobot.append(transformedPolygonPoints)
        self.position = positionOfRobot

    # keep generating them until one is valid
    def generateRandomConfiguration(self):
        # [x, y, joint_angles]
        originalPosition = self.position
        while True:
            q_rand = [random.uniform(0,self.world.width - 1), random.uniform(0, self.world.height -1)] + [random.uniform(-math.pi, math.pi) for i in range(self.numJoints)]
            self.moveToConfiguration(q_rand)
            if self.inBounds():
                # reset position
                self.position = originalPosition
                return tuple(q_rand)

    def makeRotationMatrix(self, rotationAngle):
        cosTheta = math.cos(rotationAngle)
        sinTheta = math.sin(rotationAngle)
        return np.array([[cosTheta, -sinTheta, 0], [sinTheta, cosTheta, 0], [0, 0, 1]])

    def inBounds(self):
        for polygon in self.position:
            for point in polygon:
                if not self.world.inRange(point[0], point[1]):
                    return False
        return True

    def distance(self, q1, q2):
        # return self.angleDiscount(q1, q2)
        # return self.forwardKinDistance(q1, q2)
        return self.l2Norm(q1, q2)

    def forwardKinDistance(self, q1, q2):
        self.moveToConfiguration(q1)
        q1Position = self.position
        self.moveToConfiguration(q2)
        q2Position = self.position
        distance = 0.0
        for i in range(len(q1Position)):
            q1Point = q1Position[i][0]
            q2Point = q2Position[i][0]
            distance += math.sqrt((q1Point[0] - q2Point[0]) ** 2 + (q1Point[1] - q2Point[1]) ** 2)
        return distance

    def l2Norm(self, q1, q2):
        return np.linalg.norm(np.array(q2) - np.array(q1))

    def angleDiscount(self, q1, q2):
        assert(len(q1) == len(q2))
        angleFactor = 0.2
        # get euclidean distance for the origin of the two configurations
        euclideanDistance = math.sqrt((q1[0] - q2[0]) ** 2 + (q1[1] - q2[1]) ** 2)
        # get angle distance for the joint angles 
        jointAngleSum = 0
        for i in range(2, len(q1)):
            jointAngleSum += (q1[i] - q2[i]) ** 2
        jointAngleDistance = math.sqrt(jointAngleSum)
        distance = euclideanDistance + jointAngleDistance * angleFactor
        return distance

    def coverAtQ(self, q):
        return self.coverWithBBox(q)

    def coverWithBBox(self, q):
        self.robot.moveToConfiguration(q)
        collisions = set()
        allRobotPoints = [pt for polyPoints in self.robot.position for pt in polyPoints]
        allRobotBBox = BBox(allRobotPoints)
        for obstacle in self.world.obstacles:
            collisionFree = True
            for obstacle in self.world.obstacles:
                if allRobotBBox.intersectsBBox(obstacle.bbox):
                    collisionFree = False
                    break
            if collisionFree:
                return collisions

            #else check each robot polygon bbox
            for polygonPts in self.robot.position:
                bboxRobotPoly = BBox(polygonPts)
                polygon = Polygon(polygonPts)
                for obstacle in self.world.obstacles:
                    if bboxRobotPoly.intersectsBBox(obstacle.bbox):
                        if polygon.intersects(obstacle.polygon):
                            collisions.add(obstacle)
        return collisions

    def naiiveCover(self, q):
        self.robot.moveToConfiguration(q)
        collisions = set()
        for polygon in self.robot.position:
            poly = Polygon(polygon)
            for obstacle in self.world.obstacles:
                if poly.intersects(obstacle.polygon):
                    collisions.add(obstacle)
        return collisions

