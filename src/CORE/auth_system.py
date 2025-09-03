from PySide6.QtWidgets import (QWidget, QStackedWidget, QLineEdit, QLabel, 
                              QPushButton, QVBoxLayout, QHBoxLayout, 
                              QFormLayout, QMessageBox, QFrame)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, Signal
import sys
from src.DB.db_manager import DBManager
from PySide6.QtWidgets import QApplication
import hashlib
import logging
import os
from datetime import datetime
from src.GUI.main_window import MainWindow

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
    """Modern card-based authentication UI"""
    
    login_success = Signal(int)  # Emits id on successful login
    
    def __init__(self, auth_system):
        super().__init__()
        self.auth = auth_system
        self.setWindowTitle("Study Planner - Authentication")
        self.setFixedSize(500, 400)
        self.setup_ui()
        self._apply_styles()
    
    def setup_ui(self):
        # Main layout with background
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        
        # Stacked widget for screens
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)
        
        # Create all screens
        self._create_login_screen()
        self._create_register_screen()
        self._create_account_screen()
        
        # Set initial screen
        self.stacked_widget.setCurrentIndex(0)
    
    def _apply_styles(self):
        self.setStyleSheet("""
            AuthUI {
                background-color: #121212;
            }

            .AuthCard {
                background-color: #1e1e1e;
                border-radius: 12px;
                padding: 30px;
                border: 1px solid #2c2c2c;
            }

            QLabel#title {
                font-size: 24px;
                font-weight: bold;
                color: #FFD700; /* Gold */
                margin-bottom: 5px;
            }

            QLabel#subtitle {
                font-size: 14px;
                color: #bbbbbb;
                margin-bottom: 20px;
            }

            QLabel {
                color: #eeeeee;
            }

            QLineEdit {
                padding: 12px;
                border: 2px solid #333;
                border-radius: 8px;
                font-size: 14px;
                background-color: #2a2a2a;
                color: #fefefe;
                margin-bottom: 5px;
            }

            QLineEdit:focus {
                border: 2px solid #FFD700; /* Gold border on focus */
            }

            QPushButton {
                padding: 12px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                border: none;
            }

            QPushButton#primary {
                background-color: #FFD700;
                color: #121212;
            }

            QPushButton#primary:hover {
                background-color: #e6c200;
            }

            QPushButton#secondary {
                background-color: #444;
                color: #FFD700;
            }

            QPushButton#secondary:hover {
                background-color: #555;
            }

            QPushButton#danger {
                background-color: #ff4c4c;
                color: white;
            }

            QPushButton#danger:hover {
                background-color: #c0392b;
            }

            .FormRow {
                margin-bottom: 15px;
            }
        """)
    
    def _create_auth_card(self, title):
        """Create a base card widget for auth screens"""
        card = QFrame()
        card.setObjectName("AuthCard")
        card.setFrameShape(QFrame.StyledPanel)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel(title)
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        return card, layout
    
    def _create_form_row(self, label_text, widget):
        """Create a consistent form row"""
        row = QHBoxLayout()
        row.setObjectName("FormRow")
        
        label = QLabel(label_text)
        label.setMinimumWidth(120)
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        row.addWidget(label)
        row.addWidget(widget, 1)
        
        return row
    
    def _create_login_screen(self):
        card, layout = self._create_auth_card("Welcome Back")
        
        # Username field
        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("Your username")
        layout.addLayout(self._create_form_row("Username:", self.login_username))
        
        # Password field
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Your password")
        self.login_password.setEchoMode(QLineEdit.Password)
        layout.addLayout(self._create_form_row("Password:", self.login_password))
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        login_btn = QPushButton("Sign In")
        login_btn.setObjectName("primary")
        login_btn.clicked.connect(self._handle_login)
        
        register_btn = QPushButton("Create Account")
        register_btn.setObjectName("secondary")
        register_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        
        btn_layout.addWidget(login_btn)
        btn_layout.addWidget(register_btn)
        
        layout.addLayout(btn_layout)
        card.setLayout(layout)
        self.stacked_widget.addWidget(card)
    
    def _create_register_screen(self):
        card, layout = self._create_auth_card("Create Account")
        
        # Username field
        self.register_username = QLineEdit()
        self.register_username.setPlaceholderText("Choose a username")
        layout.addLayout(self._create_form_row("Username:", self.register_username))
        
        # Password field
        self.register_password = QLineEdit()
        self.register_password.setPlaceholderText("Create password")
        self.register_password.setEchoMode(QLineEdit.Password)
        layout.addLayout(self._create_form_row("Password:", self.register_password))
        
        # Confirm password
        self.register_confirm = QLineEdit()
        self.register_confirm.setPlaceholderText("Confirm password")
        self.register_confirm.setEchoMode(QLineEdit.Password)
        layout.addLayout(self._create_form_row("Confirm:", self.register_confirm))
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        register_btn = QPushButton("Register")
        register_btn.setObjectName("primary")
        register_btn.clicked.connect(self._handle_register)
        
        back_btn = QPushButton("Back")
        back_btn.setObjectName("secondary")
        back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        
        btn_layout.addWidget(register_btn)
        btn_layout.addWidget(back_btn)
        
        layout.addLayout(btn_layout)
        card.setLayout(layout)
        self.stacked_widget.addWidget(card)
    
    def _create_account_screen(self):
        card, layout = self._create_auth_card("Your Account")
        
        # Account info
        self.account_info = QLabel()
        self.account_info.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.account_info)
        
        # Current password
        self.current_password = QLineEdit()
        self.current_password.setPlaceholderText("Current password")
        self.current_password.setEchoMode(QLineEdit.Password)
        layout.addLayout(self._create_form_row("Current:", self.current_password))
        
        # New password
        self.new_password = QLineEdit()
        self.new_password.setPlaceholderText("New password")
        self.new_password.setEchoMode(QLineEdit.Password)
        layout.addLayout(self._create_form_row("New:", self.new_password))
        
        # Confirm new password
        self.confirm_password = QLineEdit()
        self.confirm_password.setPlaceholderText("Confirm new")
        self.confirm_password.setEchoMode(QLineEdit.Password)
        layout.addLayout(self._create_form_row("Confirm:", self.confirm_password))
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        change_btn = QPushButton("Change Password")
        change_btn.setObjectName("primary")
        change_btn.clicked.connect(self._handle_password_change)
        
        delete_btn = QPushButton("Delete Account")
        delete_btn.setObjectName("danger")
        delete_btn.clicked.connect(self._handle_account_deletion)
        
        logout_btn = QPushButton("Logout")
        logout_btn.setObjectName("secondary")
        logout_btn.clicked.connect(self._handle_logout)
        
        btn_layout.addWidget(change_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(logout_btn)
        
        layout.addLayout(btn_layout)
        card.setLayout(layout)
        self.stacked_widget.addWidget(card)
    
    # [Keep all your existing handler methods unchanged]
    def _handle_login(self):
        username = self.login_username.text()
        password = self.login_password.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please fill in all fields")
            return
            
        success, message = self.auth.login_user(username, password)
        if success:
            self.login_success.emit(self.auth.current_user)
            self._show_account_screen()
            
            self.main = MainWindow.StudyPlanner(user_id=self.auth.current_user)
            self.main.show()
            self.close()
        else:
            QMessageBox.warning(self, "Login Failed", message)
    
    def _handle_register(self):
        if self.register_password.text() != self.register_confirm.text():
            QMessageBox.warning(self, "Error", "Passwords don't match")
            return
            
        if not self.register_username.text() or not self.register_password.text():
            QMessageBox.warning(self, "Error", "Please fill in all fields")
            return
            
        success, message = self.auth.register_user(
            self.register_username.text(),
            self.register_password.text()
        )
        
        if success:
            QMessageBox.information(self, "Success", message)
            self.stacked_widget.setCurrentIndex(0)
            self.register_username.clear()
            self.register_password.clear()
            self.register_confirm.clear()
        else:
            QMessageBox.warning(self, "Registration Failed", message)
    
    def _handle_password_change(self):
        if self.new_password.text() != self.confirm_password.text():
            QMessageBox.warning(self, "Error", "New passwords don't match")
            return
            
        if not self.current_password.text() or not self.new_password.text():
            QMessageBox.warning(self, "Error", "Please fill in all fields")
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
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
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
            f"Logged in as: {user_data['username']}"
        )
        self.stacked_widget.setCurrentIndex(2)
