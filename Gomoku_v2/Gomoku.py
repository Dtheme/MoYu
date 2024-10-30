from PyQt5 import QtWidgets, QtGui, QtCore
from GomokuAI import GomokuAI
from GomokuAI_v2 import GomokuAI_v2  # 引入新的大模型AI
from BoardCanvas import BoardCanvas

class GomokuGame(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MoYu-五子棋")

        self.board_size = 15
        self.cell_size = 40
        self.board = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_player = 1
        self.ai_enabled = False
        self.model_ai_enabled = False  # 新增：标识是否启用大模型AI
        self.black_steps = 0
        self.white_steps = 0
        self.ai_agent = GomokuAI()  # 初始化本地AI agent
        self.model_ai_agent = GomokuAI_v2()  # 初始化大模型AI agent

        self.main_widget = QtWidgets.QWidget()
        self.main_layout = QtWidgets.QVBoxLayout(self.main_widget)

        self.init_ui()
        self.setLayout(self.main_layout)
        self.show()

    def init_ui(self):
        self.mode_selection = QtWidgets.QHBoxLayout()
        self.human_vs_human_button = QtWidgets.QPushButton("人人对战")
        self.human_vs_ai_button = QtWidgets.QPushButton("本地AI对战")
        self.model_vs_ai_button = QtWidgets.QPushButton("大模型AI对战")  # 新增按钮

        self.human_vs_human_button.clicked.connect(self.set_human_vs_human)
        self.human_vs_ai_button.clicked.connect(self.set_human_vs_ai)
        self.model_vs_ai_button.clicked.connect(self.set_model_vs_ai)  # 新增按钮事件

        self.mode_selection.addWidget(self.human_vs_human_button)
        self.mode_selection.addWidget(self.human_vs_ai_button)
        self.mode_selection.addWidget(self.model_vs_ai_button)  # 将按钮添加到布局中
        self.main_layout.addLayout(self.mode_selection)

        self.game_info = QtWidgets.QHBoxLayout()
        self.current_turn_label = QtWidgets.QLabel("当前轮次：黑棋（先手）")
        self.black_steps_label = QtWidgets.QLabel("黑棋步数: 0")
        self.white_steps_label = QtWidgets.QLabel("白棋步数: 0")
        self.game_info.addWidget(self.current_turn_label)
        self.game_info.addWidget(self.black_steps_label)
        self.game_info.addWidget(self.white_steps_label)
        self.main_layout.addLayout(self.game_info)

        self.board_container = QtWidgets.QWidget()
        self.board_layout = QtWidgets.QVBoxLayout(self.board_container)
        self.board_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.board_container, alignment=QtCore.Qt.AlignCenter)

        self.show_board()

    def set_human_vs_human(self):
        self.ai_enabled = False
        self.model_ai_enabled = False
        self.reset_board()

    def set_human_vs_ai(self):
        self.ai_enabled = True
        self.model_ai_enabled = False
        self.reset_board()

    def set_model_vs_ai(self):
        self.ai_enabled = False
        self.model_ai_enabled = True
        self.reset_board()

    def show_board(self):
        for i in reversed(range(self.board_layout.count())):
            self.board_layout.itemAt(i).widget().setParent(None)
        self.canvas = BoardCanvas(self.board_size, self.cell_size, self.board, self)
        self.board_layout.addWidget(self.canvas)
        self.setFixedSize(self.board_size * self.cell_size + 100, self.board_size * self.cell_size + 200)

    def reset_board(self):
        self.board = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_player = 1
        self.black_steps = 0
        self.white_steps = 0
        self.update_labels()
        self.canvas.update_board(self.board)

    def update_labels(self):
        self.current_turn_label.setText(f"当前轮次：{'黑棋' if self.current_player == 1 else '白棋'}")
        self.black_steps_label.setText(f"黑棋步数: {self.black_steps}")
        self.white_steps_label.setText(f"白棋步数: {self.white_steps}")

    def mousePressEvent(self, event):
        if hasattr(self, 'canvas'):
            board_pos = self.canvas.mapFrom(self, event.pos())
            col = board_pos.x() // self.cell_size
            row = board_pos.y() // self.cell_size
            if 0 <= row < self.board_size and 0 <= col < self.board_size and self.board[row][col] == 0:
                self.place_piece(row, col)

    def place_piece(self, row, col):
        self.board[row][col] = self.current_player
        if self.current_player == 1:
            self.black_steps += 1
        else:
            self.white_steps += 1
        if self.check_winner(row, col):
            winner = "黑棋" if self.current_player == 1 else "白棋"
            QtWidgets.QMessageBox.information(self, "游戏结束", f"{winner}获胜！")
            self.reset_board()
        else:
            if self.model_ai_enabled and self.current_player == 1:
                self.current_player = 3 - self.current_player
                self.model_ai_move()  # 调用大模型AI对弈方法
            elif self.ai_enabled and self.current_player == 1:
                self.current_player = 3 - self.current_player
                self.ai_move()
            else:
                self.current_player = 3 - self.current_player
            self.update_labels()
            self.canvas.update_board(self.board)

    def ai_move(self):
        row, col = self.ai_agent.get_best_move(self.board, self.current_player)
        if row is not None and col is not None:
            self.place_piece(row, col)

    def model_ai_move(self):
        row, col = self.model_ai_agent.get_best_move(self.board, self.current_player)
        if row is not None and col is not None:
            self.place_piece(row, col)

    def check_winner(self, row, col):
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 1
            count += self.count_direction(row, col, dr, dc)
            count += self.count_direction(row, col, -dr, -dc)
            if count >= 5:
                return True
        return False

    def count_direction(self, row, col, dr, dc):
        r, c = row + dr, col + dc
        count = 0
        while 0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r][c] == self.current_player:
            count += 1
            r += dr
            c += dc
        return count
