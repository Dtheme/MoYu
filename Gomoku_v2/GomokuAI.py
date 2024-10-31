class GomokuAI:
    def __init__(self):
        self.scores = {
            "活四": 10000,
            "死四": 5000,
            "活三": 1000,
            "死三": 500,
            "活二": 100,
            "死二": 50
        }

    def get_best_move(self, board, player):
        best_score = -float('inf')
        best_move = None
        search_depth = self.determine_depth(board)  # 动态调整深度
        
        # 提前优先评估能形成活四的落子点
        for r in range(len(board)):
            for c in range(len(board)):
                if board[r][c] == 0 and self.has_nearby_pieces(board, r, c):
                    board[r][c] = player
                    # 检查是否立即能形成活四
                    if self.is_immediate_threat(board, r, c, player):
                        board[r][c] = 0
                        return (r, c)
                    board[r][c] = 0

        # 继续常规搜索策略
        for r in range(len(board)):
            for c in range(len(board)):
                if board[r][c] == 0 and self.has_nearby_pieces(board, r, c):
                    board[r][c] = player
                    score = self.minimax(board, search_depth, -float('inf'), float('inf'), False, player)
                    board[r][c] = 0
                    if score > best_score:
                        best_score = score
                        best_move = (r, c)
        
        return best_move if best_move else (None, None)

    def is_immediate_threat(self, board, row, col, player):
        """检测此位置是否形成活四"""
        for dr, dc in [(1, 0), (0, 1), (1, 1), (1, -1)]:
            if self.evaluate_direction(board, row, col, dr, dc, player) == self.scores["活四"]:
                return True
        return False

    def determine_depth(self, board):
        empty_cells = sum(row.count(0) for row in board)
        if empty_cells < 15:
            return 4
        elif empty_cells < 30:
            return 3
        else:
            return 2

    def has_nearby_pieces(self, board, row, col):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            if 0 <= r < len(board) and 0 <= c < len(board) and board[r][c] != 0:
                return True
        return False

    def minimax(self, board, depth, alpha, beta, maximizing, player):
        opponent = 3 - player
        if depth == 0 or self.is_terminal_node(board):
            return self.evaluate_board(board, player)

        possible_moves = [
            (r, c) for r in range(len(board)) for c in range(len(board))
            if board[r][c] == 0 and self.has_nearby_pieces(board, r, c)
        ]

        if maximizing:
            max_eval = -float('inf')
            for r, c in possible_moves:
                board[r][c] = player
                eval = self.minimax(board, depth - 1, alpha, beta, False, player)
                board[r][c] = 0
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for r, c in possible_moves:
                board[r][c] = opponent
                eval = self.minimax(board, depth - 1, alpha, beta, True, player)
                board[r][c] = 0
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def is_terminal_node(self, board):
        for r in range(len(board)):
            for c in range(len(board)):
                if board[r][c] != 0 and self.check_winner(board, r, c):
                    return True
        return False

    def check_winner(self, board, row, col):
        player = board[row][col]
        if player == 0:
            return False
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 1
            count += self.count_direction(board, row, col, dr, dc, player)
            count += self.count_direction(board, row, col, -dr, -dc, player)
            if count >= 5:
                return True
        return False

    def count_direction(self, board, row, col, dr, dc, player):
        r, c = row + dr, col + dc
        count = 0
        while 0 <= r < len(board) and 0 <= c < len(board) and board[r][c] == player:
            count += 1
            r += dr
            c += dc
        return count

    def evaluate_board(self, board, player):
        opponent = 3 - player
        player_score = self.evaluate_player(board, player)
        opponent_score = self.evaluate_player(board, opponent)
        return player_score - opponent_score

    def evaluate_player(self, board, player):
        score = 0
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for r in range(len(board)):
            for c in range(len(board)):
                if board[r][c] == player:
                    for dr, dc in directions:
                        score += self.evaluate_direction(board, r, c, dr, dc, player)
        return score

    def evaluate_direction(self, board, row, col, dr, dc, player):
        opponent = 3 - player
        count = 0
        open_ends = 0
        for i in range(5):
            r, c = row + i * dr, col + i * dc
            if 0 <= r < len(board) and 0 <= c < len(board):
                if board[r][c] == player:
                    count += 1
                elif board[r][c] == 0:
                    open_ends += 1
                else:
                    break
            else:
                break
        if count == 4 and open_ends == 2:
            return self.scores["活四"]
        elif count == 4 and open_ends == 1:
            return self.scores["死四"]
        elif count == 3 and open_ends == 2:
            return self.scores["活三"]
        elif count == 3 and open_ends == 1:
            return self.scores["死三"]
        elif count == 2 and open_ends == 2:
            return self.scores["活二"]
        elif count == 2 and open_ends == 1:
            return self.scores["死二"]
        return 0
