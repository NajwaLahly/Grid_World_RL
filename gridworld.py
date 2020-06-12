import sys
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.table import Table
import pygame
import pdb
from pprint import pprint

# # feature1

# global variables
BOARD_ROWS = 3
BOARD_COLS = 4
WIN_STATE = (0, 3)
LOSE_STATE = (1, 3)
WALL_STATE = (1, 1)
START = (2, 0)
DETERMINISTIC = True
discount = 0.9
WHITE = (200, 200, 200)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GREEN = (0, 100, 0)


class State:

    def __init__(self, state=START):
        self.end = False
        self.state = state

    def isEnd(self):
        if self.state == WIN_STATE or self.state == LOSE_STATE:
            self.end = True

    def giveReward(self, state):
        if state == WIN_STATE:
            return 1
        elif state == LOSE_STATE:
            return -1
        else:
            return 0

    def nextPosition(self, action):
        if not self.end:
            if action == "up":
                nxtState = (self.state[0] - 1, self.state[1])
            elif action == "down":
                nxtState = (self.state[0] + 1, self.state[1])
            elif action == "left":
                nxtState = (self.state[0], self.state[1] - 1)
            else:
                nxtState = (self.state[0], self.state[1] + 1)
            # if next state legal
            if (nxtState[0] >= 0) and (nxtState[0] <= BOARD_ROWS - 1):
                if (nxtState[1] >= 0) and (nxtState[1] <= BOARD_COLS - 1):
                    if nxtState != WALL_STATE:
                        return nxtState
                    return self.state
            return self.state

        else:
            # TODO
            pass

    def actionIsLegal(self, action):
        if self.nextPosition(action) == self.state:
            return False
        return True


class Agent:

    def __init__(self):
        self.State = State()
        self.actions = ["up", "down", "left", "right"]
        self.exp_rate = 0.2
        self.state_values = {}
        self.initializeRewards()  # initializing rewards

    def initializeRewards(self):
        for i in range(BOARD_ROWS):
            for j in range(BOARD_COLS):
                self.state_values[(i, j)] = 0

    def giveprobabilities(self, action, otheractions):
        if not self.State.actionIsLegal(action):
            return 0
        else:
            if otheractions == action:
                return 0.8
            else:
                return 0.1

    def getvalue(self):

        if self.State.state == WIN_STATE or self.State.state == LOSE_STATE or self.State.state == WALL_STATE:
            value = self.State.giveReward(self.State.state)

        else:
            nxt_value = []
            for a in self.actions:
                E = 0
                for act in self.actions:
                    E += self.giveprobabilities(act, a) * self.state_values[self.State.nextPosition(act)]
                nxt_value.append(self.State.giveReward(self.State.state) + discount * E)
                max_value_idx = nxt_value.index(max(nxt_value))
                value = max(nxt_value)
        return value

    def takeAction(self, action):
        position = self.State.nextPosition(action)
        return State(state=position)


class World:

    def __init__(self):
        self.board = np.zeros([BOARD_ROWS, BOARD_COLS])
        self.newWorld = np.zeros([BOARD_ROWS, BOARD_COLS])
        self.agent = Agent()
        self.states = []
        self.values = []
        self.running = True
        self.blockSize = 200
        self.SCREEN = pygame.display.set_mode((self.blockSize * BOARD_COLS, self.blockSize * BOARD_ROWS))
        self.init_game()

    def init_game(self):
        pygame.init()
        pygame.display.set_caption("GridWorld")
        self.drawGrid()

    def reset(self):
        self.states = []
        self.agent.State = State()

    def drawGrid(self):

        for i in range(BOARD_ROWS):
            for j in range(BOARD_COLS):
                # pdb.set_trace()
                rect = pygame.Rect(j * self.blockSize, i * self.blockSize, self.blockSize, self.blockSize)
                if (i, j) == LOSE_STATE:
                    pygame.draw.rect(self.SCREEN, RED, rect, 0)
                elif (i, j) == WIN_STATE:
                    pygame.draw.rect(self.SCREEN, GREEN, rect, 0)
                elif (i, j) == WALL_STATE:
                    pygame.draw.rect(self.SCREEN, WHITE, rect, 0)
                pygame.draw.rect(self.SCREEN, WHITE, rect, 1)

    def start_game(self):

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    sys.exit()
            pygame.display.update()

    # def draw_image(self):
    #     fig, ax = plt.subplots()
    #     ax.set_axis_off()
    #     tb = Table(ax, bbox=[0, 0, 1, 1])
    #     width, height = 1.0 / BOARD_COLS, 1.0 / BOARD_ROWS
    #     # Add cells
    #
    #     for (i, j), val in np.ndenumerate(self.board):
    #
    #         if (i, j) == LOSE_STATE:
    #             tb.add_cell(i, j, width, height, facecolor="RED", text=self.board[i, j])
    #         elif (i, j) == WIN_STATE:
    #             tb.add_cell(i, j, width, height, facecolor="GREEN", text=self.board[i, j])
    #         elif (i, j) == WALL_STATE:
    #             tb.add_cell(i, j, width, height, facecolor="GREY", text=self.board[i, j])
    #         else:
    #             tb.add_cell(i, j, width, height, facecolor="WHITE", text=self.board[i, j])
    #
    #     ax.add_table(tb)
    #     plt.show()

    def play(self, rounds=100):

        k = 0
        while True:
            values = {}
            newWorld = np.zeros([BOARD_ROWS, BOARD_COLS])
            for (i, j), val in np.ndenumerate(self.board):
                self.agent.State.state = (i, j)
                newWorld[i, j] = self.agent.getvalue()
                values[(i, j)] = newWorld[i, j]

            self.agent.state_values = values
            if np.sum(np.abs(self.board - newWorld)) < 1e-3:
                self.agent.State.end = True
                break

            self.board = newWorld
            k += 1


if __name__ == "__main__":
    world = World()
    world.start_game()
