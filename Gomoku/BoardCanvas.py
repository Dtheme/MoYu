from PyQt5 import QtWidgets, QtGui, QtCore

class BoardCanvas(QtWidgets.QWidget):
    def __init__(self, board_size, cell_size, board, parent=None):
        super().__init__(parent)
        self.board_size = board_size
        self.cell_size = cell_size
        self.board = board  # 新增：通过参数传递棋盘状态
        self.setFixedSize(board_size * cell_size, board_size * cell_size)

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.draw_board(qp)
        self.draw_pieces(qp)
        qp.end()

    def draw_board(self, qp):
        qp.setPen(QtCore.Qt.black)
        for i in range(self.board_size):
            qp.drawLine(i * self.cell_size, 0, i * self.cell_size, self.board_size * self.cell_size)
            qp.drawLine(0, i * self.cell_size, self.board_size * self.cell_size, i * self.cell_size)

    def draw_pieces(self, qp):
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col] != 0:
                    color = QtCore.Qt.black if self.board[row][col] == 1 else QtCore.Qt.white
                    qp.setBrush(QtGui.QBrush(color))
                    x0 = col * self.cell_size + self.cell_size // 8  # 优化了棋子位置
                    y0 = row * self.cell_size + self.cell_size // 8
                    qp.drawEllipse(x0, y0, self.cell_size - self.cell_size // 4, self.cell_size - self.cell_size // 4)

    def update_board(self, board):
        self.board = board  # 新增：提供更新棋盘状态的方法
        self.update()
