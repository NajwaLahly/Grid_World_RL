import sys
import numpy as np
import pygame
import pdb

# global variables
BOARD_ROWS = 3
BOARD_COLS = 4
WIN_STATE = (0, 3)
LOSE_STATE = (1, 3)
WALL_STATE = (1, 1)
START = (2, 3)
DETERMINISTIC = True
discount = 0.9
WHITE = (200, 200, 200)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GREEN = (0, 100, 0)
YELLOW = (255, 255, 0)
FPS = 2


class State:

    def __init__(self, state=START):
        self.end = False
        self.state = state

    def isEnd(self):
        if self.state == WIN_STATE or self.state == LOSE_STATE:
            self.end = True

    def give_reward(self, state):
        if state == WIN_STATE:
            return 1
        elif state == LOSE_STATE:
            return -1
        else:
            return 0

    def next_position(self, action):
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
            return self.state

        else:
            return self.state

    def action_is_legal(self, action):
        if self.next_position(action) == self.state:
            return False
        return True


class Agent:

    def __init__(self):
        self.State = State()
        self.actions = ["up", "down", "left", "right"]
        self.exp_rate = 0.2
        self.state_values = {}
        self.initialize_rewards()  # initializing rewards

    def initialize_rewards(self):
        for i in range(BOARD_ROWS):
            for j in range(BOARD_COLS):
                self.state_values[(i, j)] = 0

    def give_probabilities(self, action, otheractions):
        if not self.State.action_is_legal(action):
            return 0
        else:
            if otheractions == action:
                return 0.8
            else:
                return 0.1

    def get_value(self):

        if self.State.state == WIN_STATE or self.State.state == LOSE_STATE or self.State.state == WALL_STATE:
            value = self.State.give_reward(self.State.state)

        else:
            nxt_value = []
            for a in self.actions:
                E = 0
                for act in self.actions:
                    E += self.give_probabilities(act, a) * self.state_values[self.State.next_position(act)]
                nxt_value.append(self.State.give_reward(self.State.state) + discount * E)
                max_value_idx = nxt_value.index(max(nxt_value))
                value = max(nxt_value)
        return value


class Player(pygame.sprite.Sprite):

    def __init__(self, world):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((30, 30))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        sub = tuple(sum(i) for i in zip(world.blockSize * np.array(START), (world.blockSize / 2, world.blockSize / 2)))
        self.rect.center = (sub[1], sub[0])
        self.position = START

    def update(self):
        new_move = world.agent.State.next_position(world.take_action(self.position))
        self.rect.center = (
            new_move[1] * world.blockSize + world.blockSize / 2, new_move[0] * world.blockSize + world.blockSize / 2)
        self.position = new_move


class World:

    def __init__(self):
        self.clock = pygame.time.Clock()
        self.board = np.zeros([BOARD_ROWS, BOARD_COLS])
        self.agent = Agent()
        self.states = []
        self.values = []
        self.running = True
        self.blockSize = 200
        self.SCREEN = pygame.display.set_mode((self.blockSize * BOARD_COLS, self.blockSize * BOARD_ROWS))
        self.all_sprites = pygame.sprite.Group()
        self.init_game()
        self.clock = pygame.time.Clock()

    def value_iteration_loop(self):

        k = 0
        while True:
            values = {}
            newWorld = np.zeros([BOARD_ROWS, BOARD_COLS])
            for (i, j), val in np.ndenumerate(self.board):
                self.agent.State.state = (i, j)
                newWorld[i, j] = self.agent.get_value()
                values[(i, j)] = newWorld[i, j]

            self.agent.state_values = values
            if np.sum(np.abs(self.board - newWorld)) < 1e-3:
                break

            self.board = newWorld
            k += 1
        return self.board

    def take_action(self, state):
        direction_values = []
        for a in self.agent.actions:
            self.agent.State.state = state
            potential_pos = self.agent.State.next_position(a)
            direction_values.append(self.board[potential_pos])
            idx_max_direction = np.argmax(direction_values)
            take_action = self.agent.actions[idx_max_direction]
        return take_action

    def init_game(self):
        pygame.init()
        pygame.display.set_caption("GridWorld")

    def draw_grid(self):

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
        return self.SCREEN

    def add_player(self, player):
        self.all_sprites.add(player)

    def start_game(self):

        while self.running:

            self.clock.tick(FPS)
            self.SCREEN.fill(BLACK)
            self.draw_grid()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    sys.exit()

            self.all_sprites.draw(self.SCREEN)
            self.all_sprites.update()
            pygame.display.flip()
        pygame.quit()


if __name__ == "__main__":
    world = World()
    world.value_iteration_loop()
    player = Player(world)
    world.add_player(player)
    world.start_game()
