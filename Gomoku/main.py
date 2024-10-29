from PyQt5 import QtWidgets, QtGui, QtCore
import sys
import random
from Gomoku import GomokuGame
  
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    game = GomokuGame()
    sys.exit(app.exec_())