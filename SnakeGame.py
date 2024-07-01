import sys
import random
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

def main(stdscr):
    # Function to start the game
    def start_game():
        nonlocal stdscr
        stdscr.clear()
        curses.curs_set(0)
        sh, sw = stdscr.getmaxyx()
        w = curses.newwin(sh, sw, 0, 0)
        w.keypad(1)

        # Initialize colors
        curses.start_color()
        curses.use_default_colors()  # Use terminal default colors
        curses.init_pair(1, curses.COLOR_WHITE, -1)  # -1 for default background color

        # Set the background color
        w.bkgd(' ', curses.color_pair(1))

        # Initial speed and level
        speed = 300
        level = 1
        w.timeout(speed)

        snk_x = sw // 4
        snk_y = sh // 2
        snake = [
            [snk_y, snk_x],
            [snk_y, snk_x - 1],
            [snk_y, snk_x - 2]
        ]

        food = [sh // 2, sw // 2]
        w.addch(int(food[0]), int(food[1]), curses.ACS_PI)

        key = curses.KEY_RIGHT
        score = 0
        paused = False

        # Instructions
        def update_header():
            w.addstr(0, 0, "Press 'SPACE' to pause/resume. Press 'q' to quit. Speed level: {} Score: {}".format(level, score), curses.color_pair(1))

        update_header()

        def update_speed_level(speed):
            if speed > 270:
                return 1
            elif speed > 240:
                return 2
            elif speed > 210:
                return 3
            elif speed > 180:
                return 4
            elif speed > 150:
                return 5
            elif speed > 120:
                return 6
            elif speed > 90:
                return 7
            elif speed > 60:
                return 8
            elif speed > 30:
                return 9
            else:
                return 10

        while True:
            next_key = w.getch()

            if next_key == ord('q'):
                w.clear()
                w.addstr(sh // 2, sw // 2 - len("Game Over!") // 2, "Game Over!", curses.color_pair(1))
                w.addstr(sh // 2 + 1, sw // 2 - len(f"Score: {score}") // 2, f"Score: {score}", curses.color_pair(1))
                w.refresh()
                time.sleep(2)
                curses.endwin()
                quit()

            if next_key == ord(' '):
                paused = not paused
                if paused:
                    w.addstr(sh // 2, sw // 2 - len("Paused") // 2, "Paused", curses.color_pair(1))
                else:
                    w.addstr(sh // 2, sw // 2 - len("Paused") // 2, " " * len("Paused"), curses.color_pair(1))
                continue

            if paused:
                continue

            # Prevent the snake from reversing direction
            if next_key in [curses.KEY_RIGHT, curses.KEY_LEFT, curses.KEY_UP, curses.KEY_DOWN]:
                if (key == curses.KEY_RIGHT and next_key != curses.KEY_LEFT) or \
                   (key == curses.KEY_LEFT and next_key != curses.KEY_RIGHT) or \
                   (key == curses.KEY_UP and next_key != curses.KEY_DOWN) or \
                   (key == curses.KEY_DOWN and next_key != curses.KEY_UP):
                    key = next_key

            if snake[0][0] in [0, sh] or \
               snake[0][1] in [0, sw] or \
               snake[0] in snake[1:]:
                w.clear()
                w.addstr(sh // 2, sw // 2 - len("Game Over!") // 2, "Game Over!", curses.color_pair(1))
                w.addstr(sh // 2 + 1, sw // 2 - len(f"Score: {score}") // 2, f"Score: {score}", curses.color_pair(1))
                w.addstr(sh // 2 + 2, sw // 2 - len("Press 'SPACE' to restart or 'q' to quit") // 2, "Press 'SPACE' to restart or 'q' to quit", curses.color_pair(1))
                w.refresh()
                while True:
                    restart_key = w.getch()
                    if restart_key == ord(' '):
                        return True
                    elif restart_key == ord('q'):
                        curses.endwin()
                        quit()

            new_head = [snake[0][0], snake[0][1]]

            if key == curses.KEY_DOWN:
                new_head[0] += 1
            if key == curses.KEY_UP:
                new_head[0] -= 1
            if key == curses.KEY_LEFT:
                new_head[1] -= 1
            if key == curses.KEY_RIGHT:
                new_head[1] += 1

            # Check if new head position is within bounds
            if new_head[0] >= sh or new_head[1] >= sw or new_head[0] < 0 or new_head[1] < 0:
                w.clear()
                w.addstr(sh // 2, sw // 2 - len("Game Over!") // 2, "Game Over!", curses.color_pair(1))
                w.addstr(sh // 2 + 1, sw // 2 - len(f"Score: {score}") // 2, f"Score: {score}", curses.color_pair(1))
                w.addstr(sh // 2 + 2, sw // 2 - len("Press 'SPACE' to restart or 'q' to quit") // 2, "Press 'SPACE' to restart or 'q' to quit", curses.color_pair(1))
                w.refresh()
                while True:
                    restart_key = w.getch()
                    if restart_key == ord(' '):
                        return True
                    elif restart_key == ord('q'):
                        curses.endwin()
                        quit()

            snake.insert(0, new_head)

            if snake[0] == food:
                score += 1
                food = None
                while food is None:
                    nf = [
                        random.randint(1, sh - 1),
                        random.randint(1, sw - 1)
                    ]
                    food = nf if nf not in snake else None
                w.addch(food[0], food[1], curses.ACS_PI)

                # Adjust speed based on score
                if speed > 200:
                    speed -= 5
                elif speed > 100:
                    speed -= 2
                elif speed > 1:
                    speed -= 1
                else:
                    # Victory condition
                    w.clear()
                    w.addstr(sh // 2, sw // 2 - len("🎉You Win! ヽ(･ω･´ﾒ)") // 2, "You Win!", curses.color_pair(1))
                    w.addstr(sh // 2 + 1, sw // 2 - len(f"Final Score: {score}") // 2, f"Final Score: {score}", curses.color_pair(1))
                    w.addstr(sh // 2 + 2, sw // 2 - len("Press 'SPACE' to restart or 'q' to quit") // 2, "Press 'SPACE' to restart or 'q' to quit", curses.color_pair(1))
                    w.refresh()
                    while True:
                        restart_key = w.getch()
                        if restart_key == ord(' '):
                            return True
                        elif restart_key == ord('q'):
                            curses.endwin()
                            quit()

                level = update_speed_level(speed)
                w.timeout(speed)
                update_header()
            else:
                tail = snake.pop()
                w.addch(int(tail[0]), int(tail[1]), ' ')

            w.addch(int(snake[0][0]), int(snake[0][1]), curses.ACS_CKBOARD)

        curses.endwin()

    while start_game():
        pass

if __name__ == "__main__":
    curses.wrapper(main)
