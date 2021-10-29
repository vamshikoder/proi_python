import sys
from PyQt5.QtWidgets import QApplication
from editor.window import PWindow

if __name__ == "__main__":
    application = QApplication([])

    window = PWindow()

    sys.exit(application.exec_())
