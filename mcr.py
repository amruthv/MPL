import mcrGraph
import covercalculator
import numpy as np
import heapq

class MCRPlanner():
    # start and goal are both configurations
    def __init__(self, robot, world, start, goal):
        self.robot = robot
        self.world = world
        self.start = start
        self.goal = goal
        self.cc = covercalculator.CoverCalculator(robot, world)

    def discreteMCR(self, N_raise = 1000):
        #setup stuff
        startCover = self.cc.cover(self.start)
        goalCover = self.cc.cover(self.goal)
        startGoalEdgeCover = self.cc.edgeCover(self.start, self.goal)
        s_min =  startCover.mergeWith(startGoalEdgeCover).score
        k = startCover.score + goalCover.score
        G = initializeGraph()
        N = 1
        while True:
            self.expandRoadmap(G, k)
            self.computeMinExplanations(G)
            s_min = G.covers[goal].score
            if N % N_raise == 0:
                k += 1
            if k >= s_min:
                k = s_min - 1
            N += 1

    def initializeGraph(self):
        V = set()
        V.add(self.start)
        V.add(self.goal)
        E = {}
        E[start] = [self.goal]
        E[goal] = [self.start]
        graph = Graph(V,E)
        graph.covers[self.start] = self.cc.cover(start)
        graph.covers[self.goal] = graph.covers[self.start].mergeWith(self.cc.edgeCover(start, goal))  # do i need to set this
        return graph

    def expandRoadmap(self, G, k, delta = 1):
        sampleConfig = robot.generateRandomConfiguration()
        nearestConfig = self.closest(G,k,sampleConfig)
        q = self.extendToward(G, nearestConfig, sampleConfig, delta, k)
        neighborsOfQ = self.neighbors(G, q)
        G.addVertex(q)
        for neighbor in neighborsOfQ:
            if self.robot.distance(neighbor, q) < delta:
                G.addEdge(neighbor, q)

    def closest(self, G, k, sampleConfig):
        GKReachableNodes = []
        for node in G.V:
            if G.covers[node].score <= k:
                GKReachableNodes.append(node)
        minIndex = np.argmin([self.robot.distance(q, sampleConfig) for q in GKReachableNodes])
        return GKReachableNodes[minIndex]

    def extendToward(self, G, closest, sample, delta, k, bisectionLimit = 4):
        qPrime = tuple(np.array(closest) + 
                min(float(delta) / self.robot.distance(closest, sample), 1) * 
                    np.array(sample) - np.array(closest))
        bisectionCount = 0
        while True:
            closestCover = G.covers[closest]
            edgeCover = self.cc.edgeCover(closest, qPrime)
            qPrimeCover = closestCover.mergeWith(edgeCover)
            if qPrimeCover.score <= k:
                break
            elif bisectionCount < bisectionLimit:
                bisectionCount += 1 
                qPrime = 0.5 * (np.array(qPrime) + np.array(closest))
            else:
                break
        return qPrime

    def neighbors(self, G, q, m = 10):
        # we choose nearest 10 rather than the ball of radius r approach
        distances = [(self.robot.distance(q, v), v) for v in G.V]
        sortedDistances = sorted(distances)
        neighbors = [x[1] for x in sortedDistances[:min(m, len(sortedDistances))]]
        return neighbors

    def computeMinExplanations(self, G, start, useGreedy = True):
        if useGreedy:
            greedySearch(G, start)
        else:
            raise NotImplementedError()

    def greedySearch(self, G, start):
        def coverScore(entry):
            return entry[0]
        def coverObj(entry):
            return entry[1]
        def entryId(entry):
            return entry[2]
        def makeEntry(coverObj, entryId):
            return [coverObj.score, coverObj, entryId]

        finalCovers = {}
        cameFrom = {}
        heap = []

        startCover = self.cc.cover(start)
        startEntry = makeEntry(startCover, start)
        coversSoFar = {start : startEntry}
        heapq.heappush(heap, startEntry)
        while (len(finalCovers) < len(G.V)) {
            # find lowest unfinalized cover size node
            while True:
               entry = heapq.heappop(heap)
               vertexCoverSize = coverSize(entry)
               vertexCover = coverSet(entry)
               vertexName = entryId(entry)
               if vertexName !=  "REMOVED":
                    del coversSoFar[vertexName]
                    break
            #finalize this distance
            finalCovers[vertexName] = vertexCover
            # add neighbors
            for neighbor in G.E[vertexName]:
                # only manipulate those not in finalCovers
                if neighbor not in finalCovers:
                    # solve neighbor cover with edge cover from vertexName
                    neighborCover = vertexCover.mergeWith(self.cc.edgeCover(vertexName, neighbor))
                    neighborEntry = makeEntry(neighborCover, neighbor)
                    if neighbor not in coversSoFar:
                        coversSoFar[neighbor] = neighborEntry
                        heapq.heappush(heap, neighborEntry)
                        cameFrom[neighbor] = vertexName
                    elif neighborCover.score < coversSoFar[neighbor].score:
                        # mark existing entry in heap as removed. Can just use the reference to the entry in the hashmap
                        coversSoFar[neighbor][2] = "REMOVED"
                        # override the value in dict of neighbor to new one
                        coversSoFar[neighbor] = neighborEntry
                        heapq.heappush(heap, neighborEntry)
                        cameFrom[neighbor] = vertexName
        
        # now go back through and fill in G.Covers with the final covers
        G.covers = {}
        for node in finalCovers:
            G.covers[node] = finalCovers[node]

        return cameFrom
