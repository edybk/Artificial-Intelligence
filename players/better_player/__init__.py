
#===============================================================================
# Imports
#===============================================================================

import abstract
from utils import INFINITY, run_with_limited_time, ExceededTimeError
from Reversi.consts import EM, OPPONENT_COLOR, BOARD_COLS, BOARD_ROWS
import time
import copy
from collections import defaultdict

#===============================================================================
# Player
#===============================================================================

class Player(abstract.AbstractPlayer):
    def __init__(self, setup_time, player_color, time_per_k_turns, k):
        abstract.AbstractPlayer.__init__(self, setup_time, player_color, time_per_k_turns, k)
        self.clock = time.time()

        # We are simply providing (remaining time / remaining turns) for each turn in round.
        # Taking a spare time of 0.05 seconds.
        self.turns_remaining_in_round = self.k
        self.time_remaining_in_round = self.time_per_k_turns
        self.time_for_current_move = self.time_remaining_in_round / self.turns_remaining_in_round - 0.05

    def get_move(self, game_state, possible_moves):
        self.clock = time.time()
        self.time_for_current_move = self.time_remaining_in_round / self.turns_remaining_in_round - 0.05
        if len(possible_moves) == 1:
            return possible_moves[0]

        best_move = possible_moves[0]
        next_state = copy.deepcopy(game_state)
        next_state.perform_move(best_move[0],best_move[1])
        # Choosing an arbitrary move
        # Get the best move according the utility function
        for move in possible_moves:
            new_state = copy.deepcopy(game_state)
            new_state.perform_move(move[0],move[1])
            if self.utility(new_state) > self.utility(next_state):
                next_state = new_state
                best_move = move

        if self.turns_remaining_in_round == 1:
            self.turns_remaining_in_round = self.k
            self.time_remaining_in_round = self.time_per_k_turns
        else:
            self.turns_remaining_in_round -= 1
            self.time_remaining_in_round -= (time.time() - self.clock)

        return best_move

    def legalTile(self, x, y):
        if (x in range(BOARD_ROWS)) and (y in range(BOARD_COLS)):
            return True
        return False

    def getLegalTilesAround(self, x, y):
        aroundTile = {(0, 1), (1, 0), (0, -1), (-1, 0), (-1, -1), (1, 1), (-1, 1), (1, -1)}
        tiles = []
        for around in aroundTile:
            if self.legalTile(x+around[0], y+around[1]):
                tiles.append((x+around[0], y+around[1]))
        return tiles

    def cornerUtil(self, state):
        corners = {(0, 0), (0, BOARD_COLS-1), (BOARD_ROWS-1, 0), (BOARD_ROWS-1, BOARD_COLS-1)}

        my_corners = 0
        opp_corners = 0
        my_closeness = 0
        opp_closeness = 0

        for corner in corners:
            if state.board[corner[0]][corner[1]] == self.color:
                my_corners += 1
            elif state.board[corner[0]][corner[1]] == OPPONENT_COLOR[self.color]:
                opp_corners += 1
            else:
                for legalTile in self.getLegalTilesAround(corner[0], corner[1]):
                    if state.board[legalTile[0]][legalTile[1]] == self.color:
                        my_closeness += 1
                    elif state.board[legalTile[0]][legalTile[1]] == OPPONENT_COLOR[self.color]:
                        opp_closeness += 1
        corners_util = 25 * (my_corners - opp_corners)
        closeness_util = -12.5 * (my_closeness - opp_closeness)
        return corners_util, closeness_util

    def flipBoard(self, board):
        for x in range(BOARD_ROWS):
            for y in range(BOARD_COLS):
                if board[x][y] == self.color:
                    board[x][y] = OPPONENT_COLOR[self.color]
                elif board[x][y] == OPPONENT_COLOR[self.color]:
                    board[x][y] = self.color

    def mobilityUtil(self, state):
        my_moves = len(state.get_possible_moves())
        self.flipBoard(state.board)
        opp_moves = len(state.get_possible_moves())
        self.flipBoard(state.board)
        if my_moves > opp_moves :
            return (100.0 * my_moves) / (my_moves + opp_moves)
        elif my_moves < opp_moves:
            return -(100.0 * opp_moves) / (my_moves + opp_moves)
        else:
            return 0

    def stabilityUtil(self, state):
        scores = [[20, -3, 11, 8, 8, 11, -3, 20],
                  [-3, -7, -4, 1, 1, -4, -7, -3],
                  [11, -4, 2, 2, 2, 2, -4, 11],
                  [8, 1, 2, -3, -3, 2, 1, 8],
                  [8, 1, 2, -3, -3, 2, 1, 8],
                  [11, -4, 2, 2, 2, 2, -4, 11],
                  [-3, -7, -4, 1, 1, -4, -7, -3],
                  [20, -3, 11, 8, 8, 11, -3, 20]]
        d = 0
        my_tiles = 0
        opp_tiles = 0
        for x in range(BOARD_ROWS):
            for y in range(BOARD_COLS):
                if state.board[x][y] == self.color:
                    my_tiles += 1
                    d += scores[x][y]
                if state.board[x][y] == OPPONENT_COLOR[self.color]:
                    opp_tiles += 1
                    d -= scores[x][y]
        my_front_tiles = 0
        opp_front_tiles = 0

        for x in range(BOARD_ROWS):
            for y in range(BOARD_COLS):
                if state.board[x][y] != EM:
                    for tile in self.getLegalTilesAround(x, y):
                        if state.board[tile[0]][tile[1]] == EM:
                            if state.board[x][y] == self.color:
                                my_front_tiles += 1
                            else:
                                opp_front_tiles += 1
                            break
        if my_front_tiles > opp_front_tiles:
            front_util = -(100.0 * my_front_tiles) / (my_front_tiles + opp_front_tiles)
        elif my_front_tiles < opp_front_tiles:
            front_util = (100.0 * opp_front_tiles) / (my_front_tiles + opp_front_tiles)
        else:
            front_util = 0

        if my_tiles > opp_tiles:
            parity_util = (100.0 * my_tiles) / (my_tiles + opp_tiles)
        elif my_front_tiles < opp_front_tiles:
            parity_util = -(100.0 * opp_tiles) / (my_tiles + opp_tiles)
        else:
            parity_util = 0
        return d, front_util, parity_util

    def utility(self, state):
        corners_util, closeness_util = self.cornerUtil(state)
        mobility_util = self.mobilityUtil(state)
        scores_util, front_util, parity_util = self.stabilityUtil(state)
        return (10 * parity_util) + \
               (800 * corners_util) + \
               (380 * closeness_util) + \
               (80 * mobility_util) + \
               (75 * front_util) + \
               (10 * scores_util)
        
    def selective_deepening_criterion(self, state):
        # Simple player does not selectively deepen into certain nodes.
        return False

    def no_more_time(self):
        return (time.time() - self.clock) >= self.time_for_current_move

    def __repr__(self):
        return '{} {}'.format(abstract.AbstractPlayer.__repr__(self), 'simple')

# c:\python35\python.exe run_game.py 3 3 3 y simple_player random_player
