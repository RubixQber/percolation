import random
import itertools
import copy
import sys
import traceback
import math
import time
import signal
import errno
from util import Vertex
from util import Edge
from util import Graph
"""
does assorted crackhead things.
todo: add state file logging and reading for faster endgame computation
problem: need to find a way to *quickly* match 2 graphs if index labels are different

funny things in this program:
- lots of if-else with magic numbers
- plenty more if-else with magic numbers
- lazy minimax endgame computation bashing
    - probably non-optimal non-functional minimax
- broken attempt at beta-prune alphing
- lots of "hecc"s when the endgame computation does approximately 3
  diagnostic runs to determine the optimal starting search depth
- no comments other than the ones that were stolen along with code from website
- citations! geeksforgeeks for minimax thing (pseudocode and python3 implementation)
- apologies if this is incomprehensible, it was completed circa 3 am on the due date
"""
class TimeoutError(Exception):
    pass

class Timeout:
    def __init__(self, seconds=0.5, error_message="Timeout of {0} seconds hit"):
        self.seconds = seconds
        self.error_message = error_message.format(seconds)
    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)
    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.setitimer(signal.ITIMER_REAL, self.seconds)
    def __exit__(self, type, value, traceback):
        signal.alarm(0)

class PercolationPlayer:
    MINI_THRESHOLD = 12
    def ChooseVertexToColor(graph, player):
        valid = [v for v in graph.V if v.color == -1]
        return max(valid, key = lambda vertex: PercolationPlayer.colorEval(graph, player, vertex))
        #return random.choice([v for v in graph.V if v.color == -1])

    def colorEval(graph, player, vertex):
        connectors = [edge.a if edge.b == vertex else edge.b for edge in PercolationPlayer.IncidentEdges(graph, vertex)]
        total = 0
        for vertex in connectors:
            if vertex.color == player:
                total += 3
            elif vertex.color == 1 - player:
                total += 1
            else:
                total += 2
        return total

    def ChooseVertexToRemove(graph, player):
        valid = [v for v in graph.V if v.color == player]
        try:
            with Timeout():
                if len(graph.V) <= PercolationPlayer.MINI_THRESHOLD:
                    val, vertex = PercolationPlayer.endgameEval(graph, player, True)
                    return vertex
        except TimeoutError as e:
            print("hecc")
            PercolationPlayer.MINI_THRESHOLD -= 1
        dict = {}
        if not valid:
            return None
        for v in valid:
            dict[v] = PercolationPlayer.removeEval(graph, v, player)
        return max(dict, key = lambda x: dict[x])

    def removeEval(graph, vertex, player):
        # remove = PercolationPlayer.numRemoved(graph, vertex)
        degree = PercolationPlayer.Degree(graph, vertex)
        connectors = [edge.a if edge.b == vertex else edge.b for edge in PercolationPlayer.IncidentEdges(graph, vertex)]
        total = 0
        for vertex in connectors:
            if vertex.color != player:
                total += 2
                deg = PercolationPlayer.Degree(graph, vertex)
                total += (max(4 - deg, 0) ** 2)

            elif vertex.color == player:
                total -= 1
                deg = PercolationPlayer.Degree(graph, vertex)
                total -= (max(2 - deg, 0) ** 2)
        return total - degree

    def numRemoved(graph, vertex):
        copied_graph = copy.deepcopy(graph)
        PercolationPlayer.Percolate(copied_graph, PercolationPlayer.GetVertex(copied_graph, vertex.index))
        return len(graph.V) - len(copied_graph.V) - 1

    def countPlayer(graph, player):
        return sum([1 for v in graph.V if v.color == player])

    def countTotalDegree(graph, player):
        return sum([PercolationPlayer.Degree(v) for v in graph.V if v.color == player])

    def Degree(graph, vertex):
        return len(PercolationPlayer.IncidentEdges(graph, vertex))

    def invertGraph(graph):
        for v in g.V:
            v.color = 1 - v.color

    def evaluate(graph, player):
        oppo = PercolationPlayer.countPlayer(graph, 1 - player)
        player = PercolationPlayer.countPlayer(graph, player)
        if not oppo:
            return 1000
        elif not player:
            return -1000
        else:
            oppoDegree = PercolationPlayer.countTotalDegree(graph, 1 - player)
            playerDegree = PercolationPlayer.countTotalDegree(graph, player)
            return 3 * (player - oppo) + playerDegree - oppoDegree

    def endgameEval(graph, player, isMinimizing):
        valid = [v for v in graph.V if v.color == player]
        if not valid:
            if isMinimizing:
                return 1000, None
            return -1000, None
        if isMinimizing:
            best = 2000
            best_tex = None
            # Recur for left and right children
            for vertex in valid:
                copied_graph = copy.deepcopy(graph)
                PercolationPlayer.Percolate(copied_graph, PercolationPlayer.GetVertex(copied_graph, vertex.index))
                val, tex = PercolationPlayer.endgameEval(copied_graph, 1 - player,
                              False)
                if val <= best:
                    best = val
                    best_tex = vertex
            return best, best_tex
        else:
            best = -2000
            best_tex = None
            # Recur for left and right children
            for vertex in valid:
                copied_graph = copy.deepcopy(graph)
                PercolationPlayer.Percolate(copied_graph, PercolationPlayer.GetVertex(copied_graph, vertex.index))
                val, tex = PercolationPlayer.endgameEval(copied_graph, 1 - player,
                              True)
                if val >= best:
                    best = val
                    best_tex = vertex
            return best, best_tex

    # Nonfunctional minimax algorithm plus alpha-beta pruning
    # 1 or more logic errors
    # probably an inversion on one of the constants or booleans
    # didn't have time to figure out how to properly fix

    # def minimax(graph, player, isMaximizing, target, index):
    #     print(player)
    #     print("~~~~~\n depth " + str(index))
    #     valid = [v for v in graph.V if v.color == player]
    #     if index == target or not valid:
    #         return PercolationPlayer.evaluate(graph, player), None
    #
    #     if isMaximizing:
    #         best = -1000
    #         best_tex = None
    #         # Recur for left and right children
    #         for vertex in valid:
    #             copied_graph = copy.deepcopy(graph)
    #             print("running copy on vertex " + str(vertex) + ":")
    #             print(copied_graph)
    #             PercolationPlayer.Percolate(copied_graph, PercolationPlayer.GetVertex(copied_graph, vertex.index))
    #             print(copied_graph.V)
    #             val, tex = PercolationPlayer.minimax(copied_graph, 1 - player,
    #                           False, target, index + 1)
    #             if val >= best:
    #                 print(val, best, vertex)
    #                 best = val
    #                 best_tex = vertex
    #             # alpha = max(alpha, best)
    #             #
    #             # # Alpha Beta Pruning
    #             # if beta <= alpha:
    #             #     break
    #         print(graph)
    #         print(best_tex)
    #         return best, best_tex
    #
    #     else:
    #         best = 1000
    #         best_tex = None
    #         # Recur for left and
    #         # right children
    #         for vertex in valid:
    #             copied_graph = copy.deepcopy(graph)
    #             PercolationPlayer.Percolate(copied_graph, PercolationPlayer.GetVertex(copied_graph, vertex.index))
    #             val, tex = PercolationPlayer.minimax(copied_graph, 1 - player,
    #                           True, target, index + 1)
    #             if val <= best:
    #                 best = val
    #                 best_tex = vertex
    #             # beta = min(beta, best)
    #             #
    #             # # Alpha Beta Pruning
    #             # if beta <= alpha:
    #             #     break
    #
    #         return best, best_tex

    # Gets a vertex with given index if it exists, else return None.
    def GetVertex(graph, i):
        for v in graph.V:
            if v.index == i:
                return v
        return None
    # Returns the incident edges on a vertex.
    def IncidentEdges(graph, v):
        return [e for e in graph.E if (e.a == v or e.b == v)]

    def Percolate(graph, v):
        # Get attached edges to this vertex, remove them.
        for e in PercolationPlayer.IncidentEdges(graph,v):
            graph.E.remove(e)
        # Remove this vertex.
        graph.V.remove(v)
        # Remove all isolated vertices.
        to_remove = {u for u in graph.V if len(PercolationPlayer.IncidentEdges(graph, u)) == 0}
        graph.V.difference_update(to_remove)
