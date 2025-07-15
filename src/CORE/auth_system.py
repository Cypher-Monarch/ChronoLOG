from PySide6.QtWidgets import (QWidget, QStackedWidget, QLineEdit, QLabel, 
                              QPushButton, QVBoxLayout, QHBoxLayout, 
                              QFormLayout, QMessageBox)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, Signal
import sys
from src.DB.db_manager import DBManager
from PySide6.QtWidgets import QApplication
import hashlib
import logging
import os
from datetime import datetime

# Create 'logs' directory if it doesn't exist
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)

# Create log file with date stamp
log_filename = datetime.now().strftime("%Y-%m-%d") + ".log"
log_path = os.path.join(log_dir, log_filename)

# Configure logging
logging.basicConfig(
    filename=log_path,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class AuthSystem:
    def __init__(self, db_manager):
        self.db = db_manager
        self.current_user = None
    
    def register_user(self, username, password):
        """Register a new user with password hashing"""
        if self.user_exists(username):
            return False, "Username already exists"
        
        hashed_pw = self._hash_password(password)
        try:
            self.db.execute_query(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                (username, hashed_pw)
            )
            id = self.db.fetch_one(
                "SELECT id FROM users WHERE username = %s", (username,)
            )['id']
            
            # Initialize default settings
            self.db.execute_query(
                "INSERT INTO user_settings (id) VALUES (%s)", (id,)
            )
            return True, "Registration successful"
        except Exception as e:
            return False, f"Registration failed: {str(e)}"
    
    def login_user(self, username, password):
        """Authenticate a user"""
        user = self.db.fetch_one(
            "SELECT id, password_hash FROM users WHERE username = %s", 
            (username,)
        )
        
        if not user:
            return False, "User not found"
        
        if self._verify_password(password, user['password_hash']):
            self.current_user = user['id']
            return True, "Login successful"
        return False, "Incorrect password"
    
    def change_password(self, id, old_pw, new_pw):
        """Change user password with verification"""
        current_hash = self.db.fetch_one(
            "SELECT password_hash FROM users WHERE id = %s", (id,)
        )['password_hash']
        
        if not self._verify_password(old_pw, current_hash):
            return False, "Current password is incorrect"
        
        new_hash = self._hash_password(new_pw)
        self.db.execute_query(
            "UPDATE users SET password_hash = %s WHERE id = %s",
            (new_hash, id)
        )
        return True, "Password changed successfully"
    
    def delete_account(self, id):
        """Permanently delete user account"""
        try:
            self.db.execute_query("DELETE FROM user_settings WHERE id = %s", (id,))
            self.db.execute_query("DELETE FROM users WHERE id = %s", (id,))
            if self.current_user == id:
                self.current_user = None
            return True, "Account deleted successfully"
        except Exception as e:
            return False, f"Failed to delete account: {str(e)}"
    
    def user_exists(self, username):
        """Check if username exists"""
        return bool(self.db.fetch_one(
            "SELECT 1 FROM users WHERE username = %s", (username,))
        )
    
    def get_user_settings(self, id):
        """Get all user settings"""
        return self.db.fetch_one(
            "SELECT * FROM user_settings WHERE id = %s", (id,)
        )
    
    def update_setting(self, id, setting, value):
        """Update a specific user setting"""
        try:
            self.db.execute_query(
                f"UPDATE user_settings SET {setting} = %s WHERE id = %s",
                (value, id)
            )
            return True
        except Exception as e:
            logging.error(f"Error updating setting: {e}")
            return False
    
    @staticmethod
    def _hash_password(password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def _verify_password(password, stored_hash):
        """Verify password against stored hash"""
        return AuthSystem._hash_password(password) == stored_hash
class AuthUI(QWidget):
    """UI components for authentication"""
    
    login_success = Signal(int)  # Emits id on successful login
    
    def __init__(self, auth_system):
        super().__init__()
        self.auth = auth_system
        self.setWindowTitle("Authentication")
        self.setMinimumSize(400, 500)
        self.setup_ui()
        self._apply_styles()
    
    def setup_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(20)
        self.setLayout(self.layout)
        
        # Add title
        title = QLabel("Study Planner")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        self.layout.addWidget(title)
        
        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget)
        
        self._create_login_screen()
        self._create_register_screen()
        self._create_account_screen()
        self.stacked_widget.setCurrentIndex(0)
    
    def _apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #000000;
                font-family: Arial;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #343a40;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
                border: 1px solid transparent;
            }
            QLabel {
                font-size: 14px;
            }
            QFormLayout {
                margin-bottom: 15px;
            }
        """)
    
    def _create_login_screen(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Form
        form = QFormLayout()
        form.setVerticalSpacing(15)
        form.setHorizontalSpacing(10)
        
        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("Enter username")
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Enter password")
        self.login_password.setEchoMode(QLineEdit.Password)
        
        form.addRow("Username:", self.login_username)
        form.addRow("Password:", self.login_password)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        login_btn = QPushButton("Login")
        login_btn.setStyleSheet("background-color: #28a745; color: black;")
        login_btn.clicked.connect(self._handle_login)
        
        register_btn = QPushButton("Register")
        register_btn.setStyleSheet("background-color: #17a2b8; color: black;")
        register_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        
        btn_layout.addWidget(login_btn)
        btn_layout.addWidget(register_btn)
        
        layout.addLayout(form)
        layout.addLayout(btn_layout)
        widget.setLayout(layout)
        self.stacked_widget.addWidget(widget)
    
    def _create_register_screen(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Form
        form = QFormLayout()
        form.setVerticalSpacing(15)
        form.setHorizontalSpacing(10)
        
        self.register_username = QLineEdit()
        self.register_username.setPlaceholderText("Choose username")
        self.register_password = QLineEdit()
        self.register_password.setPlaceholderText("Create password")
        self.register_password.setEchoMode(QLineEdit.Password)
        self.register_confirm = QLineEdit()
        self.register_confirm.setPlaceholderText("Confirm password")
        self.register_confirm.setEchoMode(QLineEdit.Password)
        
        form.addRow("Username:", self.register_username)
        form.addRow("Password:", self.register_password)
        form.addRow("Confirm Password:", self.register_confirm)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        register_btn = QPushButton("Create Account")
        register_btn.setStyleSheet("background-color: #28a745; color: black;")
        register_btn.clicked.connect(self._handle_register)
        
        back_btn = QPushButton("Back")
        back_btn.setStyleSheet("background-color: #6c757d; color: black;")
        back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        
        btn_layout.addWidget(register_btn)
        btn_layout.addWidget(back_btn)
        
        layout.addLayout(form)
        layout.addLayout(btn_layout)
        widget.setLayout(layout)
        self.stacked_widget.addWidget(widget)
    
    def _create_account_screen(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        self.account_info = QLabel()
        self.account_info.setAlignment(Qt.AlignCenter)
        self.account_info.setStyleSheet("font-weight: bold; margin-bottom: 15px;")
        layout.addWidget(self.account_info)
        
        # Form
        form = QFormLayout()
        form.setVerticalSpacing(15)
        form.setHorizontalSpacing(10)
        
        self.current_password = QLineEdit()
        self.current_password.setPlaceholderText("Current password")
        self.current_password.setEchoMode(QLineEdit.Password)
        self.new_password = QLineEdit()
        self.new_password.setPlaceholderText("New password")
        self.new_password.setEchoMode(QLineEdit.Password)
        self.confirm_password = QLineEdit()
        self.confirm_password.setPlaceholderText("Confirm new password")
        self.confirm_password.setEchoMode(QLineEdit.Password)
        
        form.addRow("Current Password:", self.current_password)
        form.addRow("New Password:", self.new_password)
        form.addRow("Confirm New Password:", self.confirm_password)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        change_btn = QPushButton("Change Password")
        change_btn.setStyleSheet("background-color: #17a2b8; color: black;")
        change_btn.clicked.connect(self._handle_password_change)
        
        delete_btn = QPushButton("Delete Account")
        delete_btn.setStyleSheet("background-color: #dc3545; color: black;")
        delete_btn.clicked.connect(self._handle_account_deletion)
        
        logout_btn = QPushButton("Logout")
        logout_btn.setStyleSheet("background-color: #6c757d; color: black;")
        logout_btn.clicked.connect(self._handle_logout)
        
        btn_layout.addWidget(change_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(logout_btn)
        
        layout.addLayout(form)
        layout.addLayout(btn_layout)
        widget.setLayout(layout)
        self.stacked_widget.addWidget(widget)
    
    # All the original handler methods remain exactly the same
    def _handle_login(self):
        username = self.login_username.text()
        password = self.login_password.text()
        
        success, message = self.auth.login_user(username, password)
        if success:
            self.login_success.emit(self.auth.current_user)
            self._show_account_screen()

            from src.GUI.main_window import MainWindow  # or StudyPlanner, whichever is your entry
            self.main = MainWindow.StudyPlanner(user_id=self.auth.current_user)
            self.main.show()
            self.close()  # or hide() if you want to come back later
        else:
            QMessageBox.warning(self, "Login Failed", message)
    
    def _handle_register(self):
        if self.register_password.text() != self.register_confirm.text():
            QMessageBox.warning(self, "Error", "Passwords don't match")
            return
            
        success, message = self.auth.register_user(
            self.register_username.text(),
            self.register_password.text()
        )
        
        if success:
            QMessageBox.information(self, "Success", message)
            self.stacked_widget.setCurrentIndex(0)
        else:
            QMessageBox.warning(self, "Registration Failed", message)
    
    def _handle_password_change(self):
        if self.new_password.text() != self.confirm_password.text():
            QMessageBox.warning(self, "Error", "New passwords don't match")
            return
            
        success, message = self.auth.change_password(
            self.auth.current_user,
            self.current_password.text(),
            self.new_password.text()
        )
        
        QMessageBox.information(self, "Password Change", message)
        if success:
            self.current_password.clear()
            self.new_password.clear()
            self.confirm_password.clear()
    
    def _handle_account_deletion(self):
        confirm = QMessageBox.question(
            self, 
            "Confirm Deletion", 
            "Are you sure you want to delete your account? This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            success, message = self.auth.delete_account(self.auth.current_user)
            QMessageBox.information(self, "Account Deletion", message)
            if success:
                self._handle_logout()
    
    def _handle_logout(self):
        self.auth.current_user = None
        self.stacked_widget.setCurrentIndex(0)
        self.login_username.clear()
        self.login_password.clear()
    
    def _show_account_screen(self):
        user_data = self.auth.db.fetch_one(
            "SELECT username FROM users WHERE id = %s",
            (self.auth.current_user,)
        )
        self.account_info.setText(
            f"Username: {user_data['username']}\n"
        )
        self.stacked_widget.setCurrentIndex(2)