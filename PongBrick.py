import sys
import random
import textwrap
import time

try:
    import curses
except ImportError:
    if sys.platform.startswith('win'):
        import os
        os.system('pip install windows-curses')
        import curses
    else:
        raise

"""
打砖块游戏
"""

def main(stdscr):
    def start_game():
        nonlocal stdscr
        stdscr.clear()
        curses.curs_set(0)
        sh, sw = stdscr.getmaxyx()
        w = curses.newwin(sh, sw, 0, 0)
        w.keypad(1)
        w.nodelay(1)  # Make getch() non-blocking

        # Initialize colors
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_WHITE, -1)
        curses.init_pair(2, -1, -1)

        # Set the background color
        w.bkgd(' ', curses.color_pair(1))

        ball = [sh // 2, sw // 2]
        ball_direction = [1, random.choice([-1, 1])]
        ball_speed = 0.2  # Initial slow ball speed
        paddle_x = sw // 2 - 4  # Adjust initial position for the wider paddle
        paddle_width = 12  
        paddle_y = sh - 2
        bricks = []
        symbols = ['💀', '👽', '👻']
        scores = [1, 2, 3]
        score = 0
        game_started = False
        game_paused = False

        for i in range(1, sh // 2 - 1):
            for j in range(2, sw - 2, 4):
                symbol = random.choice(symbols)
                value = scores[symbols.index(symbol)]
                bricks.append([i, j, symbol, value])

        key = None

        def update_header():
            w.addstr(0, 0, "Press 'SPACE' to start/pause. Press 'q' to quit. Score: {}".format(score), curses.color_pair(1))

        update_header()

        while True:
            prev_key = key
            event = w.getch()
            if event != -1:
                key = event

            if key == ord('q'):
                w.clear()
                break

            if key == ord(' '):
                if not game_started:
                    game_started = True
                else:
                    game_paused = not game_paused
                key = None  # Reset key to avoid immediate movement after pause

            if not game_started:
                welcome_message = "Welcome to Pongbrick 🧱\nPress 'space' to start"
                for i, line in enumerate(welcome_message.split('\n')):
                    w.addstr(sh // 2 + i, sw // 2 - len(line) // 2, line, curses.color_pair(1))
                w.refresh()
                time.sleep(0.1)
                continue

            if game_paused:
                pause_message = "Paused"
                w.addstr(sh // 2, sw // 2 - len(pause_message) // 2, pause_message, curses.color_pair(1))
                w.refresh()
                time.sleep(0.1)
                continue

            w.clear()
            w.border(0)
            update_header()
            for brick in bricks:
                w.addstr(brick[0], brick[1], brick[2])
            
            for i in range(paddle_x, paddle_x + paddle_width):
                w.addstr(paddle_y, i, '=')

            if 0 < ball[0] < sh and 0 < ball[1] < sw:
                w.addstr(ball[0], ball[1], '🌔')
            
            if key == curses.KEY_LEFT:
                paddle_x = max(1, paddle_x - 2)  # Immediately move paddle left
            elif key == curses.KEY_RIGHT:
                paddle_x = min(sw - paddle_width - 1, paddle_x + 2)  # Immediately move paddle right
            
            # Update ball position
            ball[0] += ball_direction[0]
            ball[1] += ball_direction[1]
            
            # Ball collision with walls
            if ball[0] <= 1:
                ball_direction[0] = -ball_direction[0]
            if ball[1] in [1, sw - 2]:
                ball_direction[1] = -ball_direction[1]
            if ball[0] >= sh - 1:
                break

            # Ball collision with paddle (with extended range)
            if ball[0] == paddle_y - 1 and paddle_x - 1 <= ball[1] < paddle_x + paddle_width + 1:
                ball_direction[0] = -ball_direction[0]
                ball_speed = max(0.05, ball_speed - 0.01)  # Increase speed each hit

            # Ball collision with bricks
            hit_index = None
            for i, brick in enumerate(bricks):
                if [ball[0], ball[1]] == [brick[0], brick[1]] or [ball[0], ball[1]] == [brick[0], brick[1] + 1]:
                    hit_index = i
                    ball_direction[0] = -ball_direction[0]
                    score += brick[3]
                    break
            
            if hit_index is not None:
                del bricks[hit_index]
            
            # Check for game over
            if not bricks:
                w.clear()
                w.addstr(sh // 2, sw // 2 - len("YOU WIN!") // 2, "YOU WIN!", curses.color_pair(1))
                w.addstr(sh // 2 + 1, sw // 2 - len(f"Final Score: {score}") // 2, f"Final Score: {score}", curses.color_pair(1))
                w.addstr(sh // 2 + 2, sw // 2 - len("Press 'SPACE' to restart or 'q' to quit") // 2, "Press 'SPACE' to restart or 'q' to quit", curses.color_pair(1))
                w.refresh()
                time.sleep(2)
                while True:
                    restart_key = w.getch()
                    if restart_key == ord(' '):
                        return True
                    elif restart_key == ord('q'):
                        curses.endwin()
                        quit()
            
            w.refresh()
            time.sleep(ball_speed)

        w.clear()
        w.addstr(sh // 2, sw // 2 - len("GAME OVER") // 2, "GAME OVER", curses.color_pair(1))
        w.refresh()
        time.sleep(2)
    
    while start_game():
        pass

if __name__ == "__main__":
    curses.wrapper(main)
