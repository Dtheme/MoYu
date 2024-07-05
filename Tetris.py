import curses
import random

"""
俄罗斯方块
Author: AaronDuan
Date: June 2024
"""

# Tetrimino shapes
shapes = [
    [[1, 1, 1],
     [0, 1, 0]],

    [[0, 1, 1],
     [1, 1, 0]],

    [[1, 1, 0],
     [0, 1, 1]],

    [[1, 1, 1, 1]],

    [[1, 1],
     [1, 1]],

    [[1, 1, 1],
     [1, 0, 0]],

    [[1, 1, 1],
     [0, 0, 1]]
]

class Tetris:
    def __init__(self, screen):
        self.screen = screen
        self.height, self.width = 20, (curses.COLS - 20) // 2  # Adjust width to fit within window
        self.board = [[0] * self.width for _ in range(self.height)]
        self.score = 0
        self.game_over = False
        self.paused = False

        self.update_speed()

        self.current_shape = self.get_new_shape()
        self.current_x = self.width // 2 - len(self.current_shape[0]) // 2
        self.current_y = 0

        self.next_shape = self.get_new_shape()
        self.draw_next_shape = False
        
        curses.start_color()
        curses.use_default_colors()  # Use terminal default colors
        curses.init_pair(1, curses.COLOR_WHITE, -1)  # -1 for default background color
        curses.init_pair(2, -1, -1)  # Same as background color

    def update_speed(self):
        # 动态调整速度：初始值为1000毫秒，每增加100分，速度增加50毫秒
        self.speed = max(100, 1000 - (self.score // 100) * 50)
        self.screen.timeout(self.speed)

    def get_new_shape(self):
        return random.choice(shapes)

    def draw_board(self):
        for y in range(self.height):
            self.screen.addstr(y + 1, 1, '|')
            self.screen.addstr(y + 1, self.width * 2 + 1, '|')
        for x in range(self.width):
            self.screen.addstr(self.height + 1, x * 2 + 1, '-')
        for y, row in enumerate(self.board):
            for x, cell in enumerate(row):
                if cell:
                    self.screen.addstr(y + 1, x * 2 + 2, '回')

    def draw_shape(self, shape, y, x):
        for row_y, row in enumerate(shape):
            for col_x, cell in enumerate(row):
                if cell:
                    self.screen.addstr(y + row_y + 1, (x + col_x) * 2 + 2, '回')

    def draw_next_shape_preview(self):
        preview_y = 2
        preview_x = self.width * 2 + 5
        if preview_x + 10 < curses.COLS:  # Ensure it fits in the screen
            self.screen.addstr(preview_y, preview_x, 'Next Shape:')
            for row_y, row in enumerate(self.next_shape):
                for col_x, cell in enumerate(row):
                    if cell:
                        self.screen.addstr(preview_y + row_y + 1, preview_x + col_x * 2, '回')
            self.screen.addstr(preview_y + 5, preview_x, f'Score: {self.score}')

    def can_move(self, shape, y, x):
        for row_y, row in enumerate(shape):
            for col_x, cell in enumerate(row):
                if cell:
                    new_y, new_x = y + row_y, x + col_x
                    if (new_x < 0 or new_x >= self.width or
                        new_y >= self.height or self.board[new_y][new_x]):
                        return False
        return True

    def freeze_shape(self):
        for row_y, row in enumerate(self.current_shape):
            for col_x, cell in enumerate(row):
                if cell:
                    self.board[self.current_y + row_y][self.current_x + col_x] = 1
        self.remove_completed_lines()

    def remove_completed_lines(self):
        new_board = [row for row in self.board if not all(row)]
        completed_lines = self.height - len(new_board)
        self.board = [[0] * self.width for _ in range(completed_lines)] + new_board
        self.score += completed_lines
        self.update_speed()

    def rotate_shape(self):
        new_shape = list(zip(*self.current_shape[::-1]))
        if self.can_move(new_shape, self.current_y, self.current_x):
            self.current_shape = new_shape

    def drop_shape(self):
        while self.can_move(self.current_shape, self.current_y + 1, self.current_x):
            self.current_y += 1
        self.freeze_shape()
        self.current_shape = self.next_shape
        self.next_shape = self.get_new_shape()
        self.current_x = self.width // 2 - len(self.current_shape[0]) // 2
        self.current_y = 0
        self.draw_next_shape = True
        if not self.can_move(self.current_shape, self.current_y, self.current_x):
            self.game_over = True

    def play(self):
        while not self.game_over:
            if not self.paused:
                self.screen.clear()
                self.screen.refresh()
                self.draw_board()
                self.draw_shape(self.current_shape, self.current_y, self.current_x)
                self.draw_next_shape_preview()
                self.screen.addstr(0, 2, 'Use arrow keys to move, UP to rotate, DOWN to drop, SPACE to pause, Q to quit')

                self.screen.refresh()

                key = self.screen.getch()

                # Handle lateral movement separately
                if key == curses.KEY_LEFT and self.can_move(self.current_shape, self.current_y, self.current_x - 1):
                    self.current_x -= 1
                elif key == curses.KEY_RIGHT and self.can_move(self.current_shape, self.current_y, self.current_x + 1):
                    self.current_x += 1

                # Handle rotation
                elif key == curses.KEY_UP:
                    self.rotate_shape()

                # Handle drop
                elif key == curses.KEY_DOWN:
                    self.drop_shape()

                # Handle pause
                elif key == ord(' '):
                    self.paused = not self.paused
                elif key == ord('q'):
                    break

                # Continue falling
                if not self.can_move(self.current_shape, self.current_y + 1, self.current_x):
                    self.freeze_shape()
                    self.current_shape = self.next_shape
                    self.next_shape = self.get_new_shape()
                    self.current_x = self.width // 2 - len(self.current_shape[0]) // 2
                    self.current_y = 0
                    self.draw_next_shape = True
                    if not self.can_move(self.current_shape, self.current_y, self.current_x):
                        self.game_over = True
                else:
                    self.current_y += 1
            else:
                self.screen.clear()
                self.screen.addstr(self.height // 2, self.width, 'PAUSED', curses.A_BOLD)
                self.screen.refresh()
                while self.paused:
                    key = self.screen.getch()
                    if key == ord(' '):
                        self.paused = not self.paused
                    elif key == ord('q'):
                        self.game_over = True
                        break

        self.screen.clear()
        game_over_message = "Amidst mountains and rivers, when paths seem lost, a village suddenly appears through shaded willows. Not all those who wander are lost."
        max_y, max_x = self.screen.getmaxyx()
        max_width = max_x * 2 // 3
        lines = self.wrap_text(game_over_message, max_width)
        for i, line in enumerate(lines):
            self.screen.addstr(max_y // 2 - len(lines) + i, (max_x - len(line)) // 2, line, curses.color_pair(2))
        self.screen.addstr(max_y // 2 + len(lines), (max_x - len('Game Over')) // 2, 'Game Over')
        self.screen.addstr(max_y // 2 + len(lines) + 1, (max_x - len(f'Score: {self.score}')) // 2, f'Score: {self.score}')
        self.screen.refresh()
        self.screen.nodelay(0)
        self.screen.getch()

    def wrap_text(self, text, max_width):
        words = text.split(' ')
        lines = []
        current_line = ""
        for word in words:
            if len(current_line) + len(word) + 1 > max_width:
                lines.append(current_line)
                current_line = word
            else:
                if current_line:
                    current_line += " " + word
                else:
                    current_line = word
        if current_line:
            lines.append(current_line)
        return lines

def main(screen):
    curses.curs_set(0)
    screen.clear()
    screen.refresh()
    game = Tetris(screen)
    game.play()

curses.wrapper(main)
