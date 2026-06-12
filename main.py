import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont

import database as db
from ui.auth_window import AuthWindow


def main():
    db.init_db()

    app = QApplication(sys.argv)
    app.setApplicationName("VetSync Pro")
    app.setOrganizationName("VetSync")
    app.setFont(QFont("Segoe UI", 10))

    window = AuthWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()