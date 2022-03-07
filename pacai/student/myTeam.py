"""
This file contains all agents to be used in createTeam
Authors:
Henry Estberg (henrye1@outlook.com)
Jia Mei
"""

from pacai.util import reflection
from pacai.agents.capture.capture import CaptureAgent
from pacai.core.directions import Directions


def createTeam(firstIndex, secondIndex, isRed,
               first='pacai.agents.capture.dummy.DummyAgent',
               second='pacai.agents.capture.dummy.DummyAgent'):
    """
    This function should return a list of two agents that will form the capture team,
    initialized using firstIndex and secondIndex as their agent indexed.
    isRed is True if the red team is being created,
    and will be False if the blue team is being created.
    """

    firstAgent = reflection.qualifiedImport(first)
    secondAgent = reflection.qualifiedImport(second)

    return [
        firstAgent(firstIndex),
        secondAgent(secondIndex),
    ]


# This agent attempts to target the nearest pellet on the other side of the board
class OffensiveAgent(CaptureAgent):

    # I'm not incredibly sure where the gameState that this is called with is coming from,
    # so for now we just generate a new one with getCurrentObservation()
    def chooseAction(self, gameState):
        # First we look for the enemies that the agent can currently see
        agentState = self.getCurrentObservation()
        isRed = self.isOnRedTeam(self.index)
        enemies = [agentState.getAgentState(i) for i in self.getOpponents(agentState)]
        # Ghosts now contains a list of the enemy ghost agents that this agent can see
        ghosts = [a for a in enemies if not a.isPacman() and a.getPosition() is not None]
        currentPos = agentState.getPosition()
        # targetFood represents the coordinates of the nearest food item that we want to eat
        # foodDistance is the current maze distance to that food
        targetFood = self.getClosestFood(gameState, isRed)
        foodDistance = self.getMazeDistance(currentPos, targetFood)
        if len(ghosts) > 0:
            # ghostDistance is how far away the agent is from all visible ghosts
            ghostDistance = []
            for g in ghosts:
                ghostDistance.append(self.getMazeDistance(currentPos, g.getPosition()))

        actions = gameState.getLegalActions(self.index)
        # I'm assuming we want to avoid the agent just pausing, so I am not including stop
        bestScore = 0
        bestAction = Directions.STOP
        for action in actions:
            if action != Directions.STOP:
                successor = self.getSuccessor(gameState, action)
                successorPos = successor.getPosition()
                # newGhostDistance is a list of the new distance between the agent and any
                # visible ghosts, in their old positions, if pacman makes the given action
                if len(ghosts) > 0:
                    newGhostDistance = []
                    distanceChange = []
                    for g in ghosts:
                        newGhostDistance.append(self.getMazeDistance(successorPos, g.getPosition()))
                    # distanceChange shows how much closer/farther pacman gets to every ghost with
                    # the given action
                    for d, nd in ghostDistance, newGhostDistance:
                        distanceChange.append(nd - d)
                    # totalDistance represents the total distance change from visible ghosts, as
                    # ideally we would like pacman to run away from all ghosts at once
                    totalDistance = sum(distnceChange)
                else:
                    totalDistance = 0
                # newFoodDistance represents the new distance to the target food after a move
                newFoodDistance = self.getMazeDistance(successorPos, targetFood)
                foodDistanceChange = foodDistance - newFoodDistance

                actionScore = -1 * foodDistanceChange+ 5 * totalDistance
                if actionScore > bestScore:
                    bestAction = action
                    bestScore = actionScore
        return bestAction

    # Function that returns the coordinates to the closest food,
    # only checking the targeted food for the given team
    def getClosestFood(self, gameState, isRed):
        if isRed:
            foodList = self.getBlueFood(gameState)
        else:
            foodList = self.getRedFood(gameState)
        agentState = self.getCurrentObservation()
        currentPos = agentState.getPosition()
        if len(foodList) > 0:
            # sets the first food in the list as the closest
            closestFood = foodList[0]
            closestFoodDistance = self.getMazeDistance(currentPos, foodList[0])
            for food in foodList:
                # calculates distance from food
                nextFoodDistance = self.getMazeDistance(currentPos, food)
                # if distance is less than the current closest food we set food to new closest food
                if nextFoodDistance < closestFoodDistance:
                    closestFood = food
            # return the closest food at the end of the loop
            return closestFood

    # Function that returns the coordinates to the closest food,
    # only checking the targeted food for the given team
    def getClosestCapsule(self, gameState, isRed):
        if isRed:
            capList = self.getBlueCapsules(gameState)
        else:
            capList = self.getRedCapsules(gameState)
        agentState = self.getCurrentObservation()
        currentPos = agentState.getPosition()
        if len(capList) > 0:
            closestCap = capList[0]
            closestCapDist = self.getMazeDistance(currentPos, capList[0])
            for cap in capList:
                nextCapDist = self.getMazeDistance(currentPos, cap)
                if nextCapDist < closestCapDist:
                    closestCap = cap
                return closestCap



class DefensiveAgent(CaptureAgent):
    # I'm not incredibly sure where the gameState that this is called with is coming from,
    # so for now we just generate a new one with getCurrentObservation()
    def chooseAction(self, gameState):
        # First we look for the enemies that the agent can currently see
        agentState = self.getCurrentObservation()
        isRed = self.isOnRedTeam(self.index)
        enemies = [agentState.getAgentState(i) for i in self.getOpponents(agentState)]
        # Invaders now contains a list of the enemy pacman agents that this agent can see
        invaders = [a for a in enemies if a.isPacman() and a.getPosition() is not None]

        # closestInvader is the pacman that is closest to the agent
        currentPos = agentState.getPosition()
        if len(invaders) > 0:
            closestInvader = invaders[0]
            shortestDistance = self.getMazeDistance(currentPos, invaders[0].getPosition())
            for i in invaders:
                distance = self.getMazeDistance(currentPos, i.getPosition())
                if distance < shortestDistance:
                    shortestDistance = distance
                    closestInvader = i

        actions = gameState.getLegalActions(self.index)
        # I'm assuming we want to avoid the agent just pausing, so I am not including stop
        for action in actions:
            if action != Directions.STOP:
                successor = self.getSuccessor(gameState, action)
                successorPos = successor.getPosition()
                if len(invaders) > 0:
                    newDistanceToInvader = self.getMazeDistance(successorPos,
                                                                closestInvader.getPosition())
