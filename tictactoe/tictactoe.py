"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    # Counts empty squares to determine who has played
    turn_counter = 0
    for row in board:
        for square in row:
            if square == EMPTY:
                turn_counter += 1
    # 1st turn has 9 squares, X starts first.
    if turn_counter % 2 == 0:
        return "O"
    else:
        return "X"


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    action = []
    # numbers row and columns, and if square is empty, add to actions list
    for row_index, row in enumerate(board):
        for col_index, square in enumerate(row):
            if square == None:
                action.append(tuple((row_index, col_index)))
    return set(action)


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    # Don't allow invalid (occupied) squares
    if action not in actions(board):
        raise ValueError
    # returns deepcopy of board to avoid changing original board
    else:
        result_board = copy.deepcopy(board)
        result_board[action[0]][action[1]] = player(board)
    return result_board

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    current_player = "O" if player(board) == "X" else "X"

    # Break down board positions
    pos_row = []
    pos_col = []
    for row_index, row in enumerate(board):
        for col_index, square in enumerate(row):
            if square == current_player:
                pos_row.append(row_index)
                pos_col.append(col_index)

    # Resolving row/col win condition
    for i in range(0,3):
        if pos_row.count(i) == 3 or pos_col.count(i) == 3:
            return current_player

    # Resolving diagonal and anti-diagonal win condition
    diag_count = 0
    adiag_count = 0
    for i in range(0, len(pos_row)):
        if pos_row[i] == pos_col[i]:
            diag_count += 1
            if diag_count == 3:
                return current_player
        if (pos_row[i] + pos_col[i]) == 2:
            adiag_count += 1
            if adiag_count == 3:
                return current_player
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) != None or actions(board) == set():
        return True
    else:
        return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == "X":
        return 1
    elif winner(board) == "O":
        return -1
    else:
        return 0

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
         return None
    # determine current player, and calculates minimax for that player (max for X, and min for O)
    current_player = player(board)
    if current_player == "X":
        # set baseline value (X win == 1)
        v = -2
        outcomes = []
        # takes min of each possible action, returns best(max) action possible
        for action in actions(board):
            x = min_val(result(board, action), 0)
            v = max(v, x[0])
            outcomes.append(tuple((action, v,  x[1])))
        return best_action(outcomes, current_player)
    elif current_player == "O":
        v = 2
        outcomes = []
        # takes max of each possible action, returns best(min) action possible
        for action in actions(board):
            x = max_val(result(board, action), 0)
            v = min(v, x[0])
            outcomes.append(tuple((action, v,  x[1])))
        return best_action(outcomes, current_player)

def best_action(outcomes, current_player):
    # determines what the max v is in list of actions
    if current_player == "X":
        x = 1 if 1 in [outcome[1] for outcome in outcomes] else 0
    else:
        x = -1 if -1 in [outcome[1] for outcome in outcomes] else 0
    max_v = [i for i in outcomes if i[1] == x]
    # determines better action based on depth
    best = min(max_v, key=lambda x: x[2]) # key takes all 3rd value (depth) in tuple
    return best[0]

def max_val(board, depth):
    if terminal(board):
        return(utility(board), depth)
    v = -2
    for action in actions(board):
        # takes max of all nodes for opponents(min) action
        v = max(v, min_val(result(board, action), depth + 1)[0])
        if v == 1:
            break
    return(v, depth)

def min_val(board, depth):
    if terminal(board):
        return(utility(board), depth)
    v = 2
    for action in actions(board):
        # takes min of all nodes for opponents(max) action
        v = min(v, max_val(result(board, action), depth + 1)[0])
        if v == -1:
            break
    return(v, depth)
