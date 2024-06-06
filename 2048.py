import random
import os
import argparse
import readchar
"""
2048 Game
Author: AaronDuan
Date: June 2024
Description: MoYu version 2048， A command-line implementation of the 2048 game in Python .
"""

class Game2048:
    def __init__(self):
        self.board = [[0] * 4 for _ in range(4)]
        self.score = 0
        self.add_new_tile()
        self.add_new_tile()

    def add_new_tile(self):
        empty_tiles = [(r, c) for r in range(4) for c in range(4) if self.board[r][c] == 0]
        if empty_tiles:
            r, c = random.choice(empty_tiles)
            self.board[r][c] = random.choice([2, 4])

    def print_board(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"Score: {self.score}")
        for row in self.board:
            print('+----' * 4 + '+')
            print(''.join(f'|{num:^4}' if num > 0 else '|    ' for num in row) + '|')
        print('+----' * 4 + '+')

    def move_left(self):
        moved = False
        for row in self.board:
            compacted = [num for num in row if num != 0]
            new_row = []
            skip = False
            for i in range(len(compacted)):
                if skip:
                    skip = False
                    continue
                if i + 1 < len(compacted) and compacted[i] == compacted[i + 1]:
                    new_num = compacted[i] * 2
                    self.score += new_num
                    new_row.append(new_num)
                    skip = True
                    moved = True
                else:
                    new_row.append(compacted[i])
            new_row += [0] * (4 - len(new_row))
            if new_row != row:
                moved = True
            for i in range(4):
                row[i] = new_row[i]
        return moved

    def rotate_board(self):
        self.board = [[self.board[j][i] for j in range(4)] for i in range(4)]
        self.board.reverse()

    def move(self, direction):
        rotations = {'left': 0, 'up': 1, 'right': 2, 'down': 3}
        moved = False
        for _ in range(rotations[direction]):
            self.rotate_board()
        moved = self.move_left()
        for _ in range(4 - rotations[direction]):
            self.rotate_board()
        if moved:
            self.add_new_tile()
        return moved

    def can_move(self):
        for row in self.board:
            for i in range(3):
                if row[i] == row[i + 1] or row[i] == 0 or row[i + 1] == 0:
                    return True
        for col in range(4):
            for row in range(3):
                if self.board[row][col] == self.board[row + 1][col] or self.board[row][col] == 0 or self.board[row + 1][col] == 0:
                    return True
        return False

    def is_won(self):
        return any(any(num == 2048 for num in row) for row in self.board)

def main():
    parser = argparse.ArgumentParser(description='2048 Game')
    parser.add_argument('-c', '--continue_game', action='store_true', help='Continue playing after reaching 2048')
    parser.add_argument('-r', '--restart', action='store_true', help='Restart the game')
    parser.add_argument('-q', '--quit', action='store_true', help='Quit the game')
    args = parser.parse_args()

    if args.quit:
        return

    game = Game2048()

    if args.restart:
        game = Game2048()

    while True:
        game.print_board()
        if game.is_won() and not args.continue_game:
            print("Congratulations! You've reached 2048!")
            break
        if not game.can_move():
            print("Game Over! No more moves available.")
            break
        print("Use arrow keys to move. Commands:  -c (continue),  -r (restart),  -q (quit)")
        
        move = readchar.readkey()
        if move == '\x1b[A':  # Up arrow
            game.move('up')
        elif move == '\x1b[B':  # Down arrow
            game.move('down')
        elif move == '\x1b[C':  # Right arrow
            game.move('right')
        elif move == '\x1b[D':  # Left arrow
            game.move('left')
        elif move == 'c':
            args.continue_game = True
        elif move == 'r':
            game = Game2048()
        elif move == 'q':
            break
        else:
            print("Invalid input! Please use arrow keys for moves or 'c', 'r', 'q' for commands.")

if __name__ == "__main__":
    main()
