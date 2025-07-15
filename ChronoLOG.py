from PySide6.QtWidgets import QApplication
from src.DB.db_creator import create_database, create_tables
from src.DB.db_manager import DBManager
from src.CORE.auth_system import AuthSystem, AuthUI
import sys

def main():
    create_database()
    create_tables()

    app = QApplication(sys.argv)

    auth = AuthSystem(DBManager())
    login_window = AuthUI(auth)
    login_window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
