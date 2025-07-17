import sys
import os
import re
import random
import pyttsx3
import random
import pyttsx3
import logging
from PySide6.QtGui import QColor, QFont, QIcon, QKeySequence, QTextCharFormat,QAction,  QPixmap,QPainter,QPen
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,QSizePolicy,QLabel, QLineEdit, QPushButton, QComboBox, QTreeWidget,QListWidgetItem, QTreeWidgetItem,QDialogButtonBox,QSpinBox, QDoubleSpinBox, QTextEdit, QListWidget, QDialog, QMessageBox,QFileDialog,QDateEdit, QTimeEdit, QRadioButton, QGroupBox, QMenu, QStatusBar, QGridLayout, QButtonGroup, QFrame, QToolButton, QToolBar, QSplitter, QInputDialog, QProgressBar, QSlider,QFormLayout,QStackedWidget, 
)
from PySide6.QtCore import Qt, QTimer, QDate, QTime, QSize, QPoint, QDateTime, QPropertyAnimation, QEasingCurve
from src.CORE.core import ChronoCore
from src.DB.db_manager import DBManager
from src.GUI.anime_study_timer import UltimateStudyTimer
# from src.CORE.notification import Notification
import random
import pyttsx3
from pydub import AudioSegment
import logging
from datetime import datetime, timedelta

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

class MainWindow():
    class CollapsibleSidebar(QWidget):
        """Modern collapsible sidebar with smooth animations"""
        
        def __init__(self, parent=None):
            super().__init__(parent)
            self.parent = parent
            self.expanded_width = 220
            self.collapsed_width = 60
            self.is_expanded = True
            self.animation_duration = 250
            
            self.setup_ui()
            self.setup_animations()
            
        def setup_ui(self):
            self.setFixedWidth(self.expanded_width)
            self.setObjectName("sidebar")
            
            # Main layout
            self.main_layout = QVBoxLayout(self)
            self.main_layout.setContentsMargins(0, 0, 0, 0)
            self.main_layout.setSpacing(0)
            
            # Header section with toggle button
            self.header = QWidget()
            self.header.setObjectName("sidebarHeader")
            self.header.setFixedHeight(60)
            header_layout = QHBoxLayout(self.header)
            header_layout.setContentsMargins(15, 10, 15, 10)
            
            # Toggle button
            self.toggle_btn = QPushButton()
            self.toggle_btn.setObjectName("toggleBtn")
            self.toggle_btn.setFixedSize(35, 35)
            self.toggle_btn.setIcon(self.create_hamburger_icon())
            self.toggle_btn.clicked.connect(self.toggle_sidebar)
            header_layout.addWidget(self.toggle_btn)
            
            # App title (hidden when collapsed)
            self.app_title = QLabel("Study Hub")
            self.app_title.setObjectName("appTitle")
            self.app_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
            header_layout.addWidget(self.app_title)
            header_layout.addStretch()
            
            self.main_layout.addWidget(self.header)
            
            # Navigation section
            self.nav_widget = QWidget()
            self.nav_layout = QVBoxLayout(self.nav_widget)
            self.nav_layout.setContentsMargins(10, 20, 10, 10)
            self.nav_layout.setSpacing(8)
            
            # Navigation buttons
            self.nav_buttons = []
            nav_items = [
                ("Home", "🏠", 0),
                ("Subjects", "📚", 1),
                ("Tasks", "✅", 2),
                ("Schedule", "📅", 3),
                ("Progress", "📊", 4),
                ("Notes", "📝", 5),
            ]
            
            for text, icon, index in nav_items:
                btn = self.create_nav_button(text, icon, index)
                self.nav_buttons.append(btn)
                self.nav_layout.addWidget(btn)
            
            # Set home as active by default
            self.nav_buttons[0].setChecked(True)
            
            self.nav_layout.addStretch()
            self.main_layout.addWidget(self.nav_widget)
            
            # Footer section
            self.footer = QWidget()
            self.footer.setObjectName("sidebarFooter")
            footer_layout = QVBoxLayout(self.footer)
            footer_layout.setContentsMargins(10, 10, 10, 20)
            footer_layout.setSpacing(8)
            
            # Settings button
            self.settings_btn = self.create_nav_button("Settings", "⚙️", -1)
            self.settings_btn.clicked.connect(self.open_settings)
            footer_layout.addWidget(self.settings_btn)
            
            # Theme toggle button
            self.theme_btn = self.create_nav_button("Dark Mode", "🌙", -2)
            self.theme_btn.setCheckable(True)
            self.theme_btn.setChecked(True)  # Default to dark mode
            self.theme_btn.clicked.connect(self.toggle_theme)
            footer_layout.addWidget(self.theme_btn)
            
            self.main_layout.addWidget(self.footer)
            
        def setup_animations(self):
            """Setup smooth resize animation"""
            self.resize_animation = QPropertyAnimation(self, b"minimumWidth")
            self.resize_animation.setDuration(self.animation_duration)
            self.resize_animation.setEasingCurve(QEasingCurve.OutCubic)
            
            self.resize_animation2 = QPropertyAnimation(self, b"maximumWidth")
            self.resize_animation2.setDuration(self.animation_duration)
            self.resize_animation2.setEasingCurve(QEasingCurve.OutCubic)
            
        def create_nav_button(self, text, icon, index):
            """Create a navigation button with icon and text"""
            btn = QPushButton()
            btn.setObjectName("navBtn")
            btn.setCheckable(True)
            btn.setFixedHeight(45)
            btn.setCursor(Qt.PointingHandCursor)
            
            # Create layout for button content
            btn_layout = QHBoxLayout(btn)
            btn_layout.setContentsMargins(15, 0, 15, 0)
            btn_layout.setSpacing(12)
            
            # Icon label
            icon_label = QLabel(icon)
            icon_label.setObjectName("navIcon")
            icon_label.setFont(QFont("Segoe UI Emoji", 16))
            icon_label.setFixedSize(20, 20)
            icon_label.setAlignment(Qt.AlignCenter)
            btn_layout.addWidget(icon_label)
            
            # Text label
            text_label = QLabel(text)
            text_label.setObjectName("navText")
            text_label.setFont(QFont("Segoe UI", 10, QFont.Medium))
            btn_layout.addWidget(text_label)
            btn_layout.addStretch()
            
            # Store references for later use
            btn.icon_label = icon_label
            btn.text_label = text_label
            
            # Connect click handler
            if index >= 0:
                btn.clicked.connect(lambda: self.navigate_to_tab(index))
            
            return btn
            
        def create_hamburger_icon(self):
            """Create hamburger menu icon"""
            pixmap = QPixmap(24, 24)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            painter.setPen(QPen(QColor("#ffffff"), 2, Qt.SolidLine, Qt.RoundCap))
            
            # Draw three horizontal lines
            painter.drawLine(4, 6, 20, 6)
            painter.drawLine(4, 12, 20, 12)
            painter.drawLine(4, 18, 20, 18)
            
            painter.end()
            return QIcon(pixmap)
            
        def toggle_sidebar(self):
            """Toggle sidebar between expanded and collapsed states"""
            if self.is_expanded:
                # Collapse
                target_width = self.collapsed_width
                self.app_title.hide()
                for btn in self.nav_buttons + [self.settings_btn, self.theme_btn]:
                    btn.text_label.hide()
            else:
                # Expand
                target_width = self.expanded_width
                self.app_title.show()
                for btn in self.nav_buttons + [self.settings_btn, self.theme_btn]:
                    btn.text_label.show()
            
            # Animate the resize
            self.resize_animation.setStartValue(self.width())
            self.resize_animation.setEndValue(target_width)
            self.resize_animation2.setStartValue(self.width())
            self.resize_animation2.setEndValue(target_width)
            
            self.resize_animation.start()
            self.resize_animation2.start()
            
            self.is_expanded = not self.is_expanded
            
        def navigate_to_tab(self, index):
            """Handle navigation to different tabs"""
            # Clear all checked states
            for btn in self.nav_buttons:
                btn.setChecked(False)
            
            # Set the clicked button as checked
            self.nav_buttons[index].setChecked(True)
            
            # Notify parent to change content
            if self.parent:
                self.parent.switch_to_tab(index)
                
        def open_settings(self):
            """Open settings dialog (placeholder)"""
            QMessageBox.information(self, "Settings", "Settings dialog will be implemented later.")
            
        def toggle_theme(self):
            """Toggle between dark and light theme"""
            if self.parent:
                self.parent.toggle_theme()
                # Update button text
                is_dark = self.parent.dark_mode
                self.theme_btn.text_label.setText("Light Mode" if is_dark else "Dark Mode")
                self.theme_btn.icon_label.setText("☀️" if is_dark else "🌙")

    class StudyPlanner(QMainWindow):
        def __init__(self, user_id):
            super().__init__()
            self.current_user_id = user_id
            self.setWindowTitle("ChronoLOG")
            self.setWindowIcon(QIcon("assets/AppIcon.png"))
            self.resize(1400, 900)
            
            # Define mono font
            self.mono_font = QFont("Monospace", 10)
        
            # Core components
            self.core = ChronoCore()
            self.db = DBManager()
            self.tts_engine = pyttsx3.init()
            
            # Theme control
            self.dark_mode = True
            
            self.setup_ui()
            self.apply_theme()
            
            # Initialize data
            self.update_subjects_list()
            self.update_tasks_list()
            self.update_schedule_list()
            self.update_progress_stats()

            # AFK Detection System
            self.afk_timer = QTimer()
            self.afk_timer.timeout.connect(self.check_afk_status)
            self.afk_check_interval = 20 * 60 * 1000  # 20 minutes
            self.current_session_active = False
            self.afk_timeout = 2 * 60 * 1000  # 2 minutes to respond
            self.afk_response_timer = QTimer()
            self.afk_response_timer.setSingleShot(True)
            self.afk_response_timer.timeout.connect(self.handle_afk_timeout)
            self.current_schedule_id = None

        def apply_theme(self):
            """Apply theme with both old and new styling"""
            if self.dark_mode:
                base_stylesheet = """
                    /* Existing dark mode styles */
                    QMainWindow {
                        background-color: #0f0f0f;
                    }
                    
                    QTreeWidget {
                        background-color: #1e1e1e;
                        color: #ffffff;
                        border: 1px solid #444;
                    }
                    
                    QTextEdit, QLineEdit, QComboBox, QSpinBox, QTextBrowser {
                        background-color: #1e1e1e;
                        color: #ffffff;
                        border: 1px solid #444;
                    }
                    
                    /* New sidebar styles */
                    QWidget#sidebar {
                        background-color: #1a1a1a;
                        border-right: 1px solid #333;
                    }
                    
                    QWidget#sidebarHeader {
                        background-color: #1a1a1a;
                        border-bottom: 1px solid #333;
                    }
                    
                    QLabel#appTitle {
                        color: #ffffff;
                    }
                    
                    QPushButton#navBtn:hover {
                        background-color: #2d2d2d;
                    }
                    
                    /* Home screen styles */
                    QWidget#statCard {
                        background-color: #1e1e1e;
                        border: 1px solid #333;
                    }
                    
                    QListWidget#activityList {
                        background-color: transparent;
                        color: #cccccc;
                    }
                """
            else:
                base_stylesheet = """
                    /* Existing light mode styles */
                    QMainWindow {
                        background-color: #f5f5f5;
                    }
                    
                    QTreeWidget {
                        background-color: #ffffff;
                        color: #000000;
                        border: 1px solid #ddd;
                    }
                    
                    QTextEdit, QLineEdit, QComboBox, QSpinBox, QTextBrowser {
                        background-color: #ffffff;
                        color: #000000;
                        border: 1px solid #ddd;
                    }
                    
                    /* New sidebar styles */
                    QWidget#sidebar {
                        background-color: #ffffff;
                        border-right: 1px solid #e0e0e0;
                    }
                    
                    QWidget#sidebarHeader {
                        background-color: #ffffff;
                        border-bottom: 1px solid #e0e0e0;
                    }
                    
                    QLabel#appTitle {
                        color: #333333;
                    }
                    
                    QPushButton#navBtn:hover {
                        background-color: #f0f0f0;
                    }
                    
                    /* Home screen styles */
                    QWidget#statCard {
                        background-color: #ffffff;
                        border: 1px solid #e0e0e0;
                    }
                    
                    QListWidget#activityList {
                        background-color: transparent;
                        color: #333333;
                    }
                """
            
            self.setStyleSheet(base_stylesheet)

        def toggle_theme(self):
            self.dark_mode = not self.dark_mode
            self.apply_theme()
            
            # Update all UI components
            self.update_tasks_list()
            self.update_schedule_list()
            self.update_progress_stats()
            
            # Update notes tab by applying main stylesheet
            notes_tab = self.content_stack.widget(4)
            if notes_tab:
                notes_tab.setStyleSheet(self.styleSheet())
      
        def activate_study_mode(self):
            """Create and show the fullscreen study mode window"""
            self.study_mode = UltimateStudyTimer()# Your existing StudyModeWindow
            self.hide()  # Hide main window
            self.study_mode.showFullScreen()
            
            # Connect the closed signal
            self.study_mode.destroyed.connect(self.on_study_mode_closed)

        def setup_ui(self):
            # Main widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # Main horizontal layout
            main_layout = QHBoxLayout(central_widget)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
            
            # Create modern sidebar
            self.sidebar = MainWindow.CollapsibleSidebar(self)
            main_layout.addWidget(self.sidebar)
            
            # Create content area
            self.content_stack = QStackedWidget()
            self.content_stack.setObjectName("contentArea")
            main_layout.addWidget(self.content_stack)
            
            # Create all content pages
            self.create_home_screen()
            self.create_subjects_tab()
            self.create_tasks_tab()
            self.create_schedule_tab()
            self.create_progress_tab()
            self.create_notes_tab()
            
            # Status bar
            self.status_bar = QStatusBar()
            self.status_bar.setFont(QFont("Monospace", 10))
            self.setStatusBar(self.status_bar)
            
            # Set home as default
            self.content_stack.setCurrentIndex(0)

        def on_study_mode_closed(self):
            """Handle study mode window being closed"""
            self.show()  # Show the main window again

        def create_ui(self):
            # Main container
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # Main vertical layout
            main_layout = QVBoxLayout(central_widget)
            main_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for full-width layout
            main_layout.setSpacing(0)

            # Header with theme toggle (keep your existing header code)
            header_layout = QHBoxLayout()
            header = QLabel("STUDY PLANNER")
            header.setFont(QFont("Monospace", 14, QFont.Bold))
            header.setAlignment(Qt.AlignCenter)
            header_layout.addWidget(header)

            self.study_now_btn = QPushButton("Study Now")
            self.study_now_btn.setFont(self.mono_font)
            self.study_now_btn.clicked.connect(self.activate_study_mode)
            header_layout.addWidget(self.study_now_btn)

            self.theme_btn = QToolButton()
            self.theme_btn.setIcon(QIcon.fromTheme("color-management"))
            self.theme_btn.setToolTip("Toggle Dark Mode")
            self.theme_btn.clicked.connect(self.toggle_theme)
            header_layout.addWidget(self.theme_btn)
            main_layout.addLayout(header_layout)

            # Stats bar (keep your existing stats bar code)
            self.stats_bar = QFrame()
            self.stats_bar.setFrameShape(QFrame.StyledPanel)
            stats_layout = QHBoxLayout(self.stats_bar)
            stats_layout.setContentsMargins(10, 5, 10, 5)
            
            self.current_date_label = QLabel()
            self.current_date_label.setFont(self.mono_font)
            stats_layout.addWidget(self.current_date_label)
            
            stats_layout.addWidget(self.create_divider())
            
            self.pending_tasks_label = QLabel()
            self.pending_tasks_label.setFont(self.mono_font)
            stats_layout.addWidget(self.pending_tasks_label)
            
            stats_layout.addWidget(self.create_divider())
            
            self.today_sessions_label = QLabel()
            self.today_sessions_label.setFont(self.mono_font)
            stats_layout.addWidget(self.today_sessions_label)
            
            main_layout.addWidget(self.stats_bar)
            self.update_current_date()
            self.update_header_stats()

            # Replace horizontal tabs with vertical tabs
            content_layout = QHBoxLayout()
            content_layout.setContentsMargins(0, 0, 0, 0)
            content_layout.setSpacing(0)

            # Create vertical tab bar (left side)
            self.tab_bar = QWidget()
            self.tab_bar.setFixedWidth(200)  # Fixed width for the sidebar
            self.tab_bar.setObjectName("tabBar")
            tab_layout = QVBoxLayout(self.tab_bar)
            tab_layout.setContentsMargins(5, 10, 5, 10)
            tab_layout.setSpacing(5)

            # Create tab buttons
            self.tab_buttons = []
            tab_names = ["Subjects", "Tasks", "Schedule", "Progress", "Notes"]
            
            for name in tab_names:
                btn = QPushButton(name)
                btn.setCheckable(True)
                btn.setFixedHeight(40)
                btn.setFont(self.mono_font)
                btn.setObjectName("tabButton")
                self.tab_buttons.append(btn)
                tab_layout.addWidget(btn)

            # Add stretch to push buttons to top
            tab_layout.addStretch()
            
            # Create content area (right side)
            self.content_stack = QStackedWidget()
            
            # Add to content layout
            content_layout.addWidget(self.tab_bar)
            content_layout.addWidget(self.content_stack)
            
            # Add to main layout
            main_layout.addLayout(content_layout)

            # Create all tabs (modify these to add to content_stack instead of tabs)
            self.create_subjects_tab()  # These methods need to add widgets to content_stack
            self.create_tasks_tab()
            self.create_schedule_tab()
            self.create_progress_tab()
            self.create_notes_tab()

            # Connect tab buttons
            for i, btn in enumerate(self.tab_buttons):
                btn.clicked.connect(lambda _, x=i: self.content_stack.setCurrentIndex(x))
            
            # Set first tab as active
            self.tab_buttons[0].setChecked(True)
            self.content_stack.setCurrentIndex(0)

            # Status bar (keep your existing status bar code)
            self.status_bar = QStatusBar()
            self.status_bar.setFont(self.mono_font)
            self.setStatusBar(self.status_bar)

            # Apply theme (make sure to update this for vertical tabs)
            self.apply_theme()

        def switch_to_tab(self, index):
            if 0 <= index < self.content_stack.count():
                self.content_stack.setCurrentIndex(index)
            else:
                print(f"[TabSwitch] Invalid index: {index}")


        def create_divider(self):
            divider = QFrame()
            divider.setFrameShape(QFrame.VLine)
            divider.setFrameShadow(QFrame.Sunken)
            return divider

        def create_subjects_tab(self):
            tab = QWidget()
            self.content_stack.addWidget(tab)
            layout = QVBoxLayout(tab)
            layout.setContentsMargins(5, 5, 5, 5)
            layout.setSpacing(10)

            # Add subject frame
            add_frame = QGroupBox("Add Subject")
            add_frame.setFont(self.mono_font)
            add_layout = QVBoxLayout(add_frame)
            add_layout.setSpacing(5)

            # Subject name
            name_layout = QHBoxLayout()
            name_layout.addWidget(QLabel("Name:"))
            self.subject_name_edit = QLineEdit()
            self.subject_name_edit.setFont(self.mono_font)
            name_layout.addWidget(self.subject_name_edit)
            add_layout.addLayout(name_layout)

            # Priority
            priority_layout = QHBoxLayout()
            priority_layout.addWidget(QLabel("Priority:"))
            self.subject_priority_combo = QComboBox()
            self.subject_priority_combo.setFont(self.mono_font)
            self.subject_priority_combo.addItems(["High", "Medium", "Low"])
            priority_layout.addWidget(self.subject_priority_combo)
            add_layout.addLayout(priority_layout)

            # Add button
            self.add_subject_btn = QPushButton("Add")
            self.add_subject_btn.setFont(self.mono_font)
            self.add_subject_btn.clicked.connect(self.add_subject)
            add_layout.addWidget(self.add_subject_btn)

            layout.addWidget(add_frame)

            # Subjects list
            list_frame = QGroupBox("Subjects")
            list_frame.setFont(self.mono_font)
            list_layout = QVBoxLayout(list_frame)
            list_layout.setSpacing(5)

            self.subjects_tree = QTreeWidget()
            self.subjects_tree.setFont(self.mono_font)
            self.subjects_tree.setHeaderLabels(["Name", "Priority"])
            self.subjects_tree.setSelectionMode(QTreeWidget.SingleSelection)
            list_layout.addWidget(self.subjects_tree)

            # Buttons frame
            btn_frame = QWidget()
            btn_layout = QHBoxLayout(btn_frame)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setSpacing(5)

            self.edit_subject_btn = QPushButton("Edit")
            self.edit_subject_btn.setFont(self.mono_font)
            self.edit_subject_btn.clicked.connect(self.edit_subject)
            btn_layout.addWidget(self.edit_subject_btn)

            self.delete_subject_btn = QPushButton("Delete")
            self.delete_subject_btn.setFont(self.mono_font)
            self.delete_subject_btn.clicked.connect(self.delete_subject)
            btn_layout.addWidget(self.delete_subject_btn)

            list_layout.addWidget(btn_frame)
            layout.addWidget(list_frame)

            # Context menu
            self.subjects_tree.setContextMenuPolicy(Qt.CustomContextMenu)
            self.subjects_tree.customContextMenuRequested.connect(self.show_subjects_context_menu)

        def can_delete_subject(self, group_id):
            """Check if a subject has no associated tasks before deletion."""
            tasks = self.core.get_all_tasks(group_id)
            return len(tasks) == 0  # True if no tasks exist
            
        def create_home_screen(self):
            """Create the modern home screen"""
            self.home_screen = MainWindow.HomeScreen(self)
            self.content_stack.addWidget(self.home_screen)
            
            # Make widgets accessible
            self.home_screen.tasks_card.statValue = self.home_screen.tasks_card.findChild(QLabel, "statValue")
            self.home_screen.sessions_card.statValue = self.home_screen.sessions_card.findChild(QLabel, "statValue") 
            self.home_screen.streak_card.statValue = self.home_screen.streak_card.findChild(QLabel, "statValue")
            self.home_screen.progress_card.statValue = self.home_screen.progress_card.findChild(QLabel, "statValue")
            self.home_screen.activity_list = self.home_screen.findChild(QListWidget, "activityList")
            
            # Connect buttons
            self.home_screen.start_study_btn.clicked.connect(self.activate_study_mode)
            
            # Initial update
            self.update_home_stats()

        def create_tasks_tab(self):
            tab = QWidget()
            self.content_stack.addWidget(tab)
            layout = QVBoxLayout(tab)
            layout.setContentsMargins(5, 5, 5, 5)
            layout.setSpacing(10)

            # Add task frame
            add_frame = QGroupBox("Add Task")
            add_frame.setFont(self.mono_font)
            add_layout = QVBoxLayout(add_frame)
            add_layout.setSpacing(5)

            # Subject selection
            subject_layout = QHBoxLayout()
            subject_layout.addWidget(QLabel("Subject:"))
            self.task_subject_combo = QComboBox()
            self.task_subject_combo.setFont(self.mono_font)
            self.update_subject_combobox()
            subject_layout.addWidget(self.task_subject_combo)
            add_layout.addLayout(subject_layout)

            # Task description
            desc_layout = QHBoxLayout()
            desc_layout.addWidget(QLabel("Description:"))
            self.task_desc_edit = QLineEdit()
            self.task_desc_edit.setFont(self.mono_font)
            desc_layout.addWidget(self.task_desc_edit)
            add_layout.addLayout(desc_layout)

            # Due date
            date_layout = QHBoxLayout()
            date_layout.addWidget(QLabel("Due Date:"))
            self.task_due_date_edit = QDateEdit()
            self.task_due_date_edit.setFont(self.mono_font)
            self.task_due_date_edit.setCalendarPopup(True)
            date_layout.addWidget(self.task_due_date_edit)
            add_layout.addLayout(date_layout)

            # Duration
            duration_layout = QHBoxLayout()
            duration_layout.addWidget(QLabel("Duration (hrs):"))
            self.task_duration_spin = QDoubleSpinBox()
            self.task_duration_spin.setFont(self.mono_font)
            self.task_duration_spin.setRange(0.5, 10)
            self.task_duration_spin.setSingleStep(0.5)
            self.task_duration_spin.setValue(1.0)
            duration_layout.addWidget(self.task_duration_spin)
            add_layout.addLayout(duration_layout)

            # Priority
            priority_layout = QHBoxLayout()
            priority_layout.addWidget(QLabel("Priority:"))
            self.task_priority_combo = QComboBox()
            self.task_priority_combo.setFont(self.mono_font)
            self.task_priority_combo.addItems(["High", "Medium", "Low"])
            priority_layout.addWidget(self.task_priority_combo)
            add_layout.addLayout(priority_layout)

            # Add button
            self.add_task_btn = QPushButton("Add Task")
            self.add_task_btn.setFont(self.mono_font)
            self.add_task_btn.clicked.connect(self.add_task)
            add_layout.addWidget(self.add_task_btn)

            layout.addWidget(add_frame)

            # Tasks list
            list_frame = QGroupBox("Tasks")
            list_frame.setFont(self.mono_font)
            list_layout = QVBoxLayout(list_frame)
            list_layout.setSpacing(5)

            self.tasks_tree = QTreeWidget()
            self.tasks_tree.setFont(self.mono_font)
            self.tasks_tree.setHeaderLabels(["Subject", "Task", "Due", "Hrs", "Priority", "✓"])
            self.tasks_tree.setSelectionMode(QTreeWidget.ExtendedSelection)
            self.tasks_tree.setAlternatingRowColors(True)
            list_layout.addWidget(self.tasks_tree)

            # Buttons frame
            btn_frame = QWidget()
            btn_layout = QHBoxLayout(btn_frame)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setSpacing(5)

            self.complete_task_btn = QPushButton("Complete")
            self.complete_task_btn.setFont(self.mono_font)
            self.complete_task_btn.clicked.connect(self.mark_task_completed)
            btn_layout.addWidget(self.complete_task_btn)

            self.edit_task_btn = QPushButton("Edit")
            self.edit_task_btn.setFont(self.mono_font)
            self.edit_task_btn.clicked.connect(self.edit_task)
            btn_layout.addWidget(self.edit_task_btn)

            self.delete_task_btn = QPushButton("Delete")
            self.delete_task_btn.setFont(self.mono_font)
            self.delete_task_btn.clicked.connect(self.delete_task)
            btn_layout.addWidget(self.delete_task_btn)

            self.schedule_task_btn = QPushButton("Schedule")
            self.schedule_task_btn.setFont(self.mono_font)
            self.schedule_task_btn.clicked.connect(self.schedule_task_dialog)
            btn_layout.addWidget(self.schedule_task_btn)

            list_layout.addWidget(btn_frame)
            layout.addWidget(list_frame)

            # Context menu
            self.tasks_tree.setContextMenuPolicy(Qt.CustomContextMenu)
            self.tasks_tree.customContextMenuRequested.connect(self.show_tasks_context_menu)

        def create_schedule_tab(self):
            tab = QWidget()
            self.content_stack.addWidget(tab)
            layout = QVBoxLayout(tab)

            # Filter frame
            filter_frame = QGroupBox("Filter")
            filter_layout = QHBoxLayout(filter_frame)

            self.schedule_filter_group = QButtonGroup()
            
            self.all_radio = QRadioButton("All")
            self.all_radio.setChecked(True)
            self.schedule_filter_group.addButton(self.all_radio)
            filter_layout.addWidget(self.all_radio)

            self.today_radio = QRadioButton("Today")
            self.schedule_filter_group.addButton(self.today_radio)
            filter_layout.addWidget(self.today_radio)

            self.upcoming_radio = QRadioButton("Upcoming")
            self.schedule_filter_group.addButton(self.upcoming_radio)
            filter_layout.addWidget(self.upcoming_radio)

            self.completed_radio = QRadioButton("Completed")
            self.schedule_filter_group.addButton(self.completed_radio)
            filter_layout.addWidget(self.completed_radio)

            self.schedule_filter_group.buttonClicked.connect(self.update_schedule_list)
            layout.addWidget(filter_frame)

            # Schedule list
            list_frame = QGroupBox("Your Study Schedule")
            list_layout = QVBoxLayout(list_frame)

            self.schedule_tree = QTreeWidget()
            self.schedule_tree.setHeaderLabels(["Date", "Start", "End", "Subject", "Description", "Duration", "Status"])
            self.schedule_tree.setSelectionMode(QTreeWidget.ExtendedSelection)
            list_layout.addWidget(self.schedule_tree)

            # Buttons frame
            btn_frame = QWidget()
            btn_layout = QHBoxLayout(btn_frame)

            self.complete_schedule_btn = QPushButton("Mark Completed")
            self.complete_schedule_btn.clicked.connect(self.mark_scheduled_completed)
            btn_layout.addWidget(self.complete_schedule_btn)

            self.delete_schedule_btn = QPushButton("Delete Schedule")
            self.delete_schedule_btn.clicked.connect(self.delete_schedule)
            btn_layout.addWidget(self.delete_schedule_btn)

            list_layout.addWidget(btn_frame)
            layout.addWidget(list_frame)

            # Context menu
            self.schedule_tree.setContextMenuPolicy(Qt.CustomContextMenu)
            self.schedule_tree.customContextMenuRequested.connect(self.show_schedule_context_menu)

        def create_progress_tab(self):
            tab = QWidget()
            self.content_stack.addWidget(tab)
            layout = QVBoxLayout(tab)

            # Create a splitter for better layout management
            splitter = QSplitter(Qt.Vertical)

            # 1. Stats Frame (Top Section)
            stats_frame = QGroupBox("Study Statistics")
            stats_layout = QVBoxLayout(stats_frame)

            # Create a grid for stats
            stats_grid = QWidget()
            grid_layout = QGridLayout(stats_grid)
            grid_layout.setSpacing(15)

            # Row 1 - Basic Stats
            grid_layout.addWidget(QLabel("Total Subjects:"), 0, 0)
            self.total_subjects_label = QLabel("0")
            self.total_subjects_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            grid_layout.addWidget(self.total_subjects_label, 0, 1)

            grid_layout.addWidget(QLabel("Total Tasks:"), 0, 2)
            self.total_tasks_label = QLabel("0")
            self.total_tasks_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            grid_layout.addWidget(self.total_tasks_label, 0, 3)

            # Row 2 - Completion Stats
            grid_layout.addWidget(QLabel("Completed Tasks:"), 1, 0)
            self.completed_tasks_label = QLabel("0")
            self.completed_tasks_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            grid_layout.addWidget(self.completed_tasks_label, 1, 1)

            grid_layout.addWidget(QLabel("Completion %:"), 1, 2)
            self.completion_percent_label = QLabel("0%")
            self.completion_percent_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            grid_layout.addWidget(self.completion_percent_label, 1, 3)

            # Row 3 - Time Stats
            grid_layout.addWidget(QLabel("Total Study Hours:"), 2, 0)
            self.total_hours_label = QLabel("0h")
            self.total_hours_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            grid_layout.addWidget(self.total_hours_label, 2, 1)

            grid_layout.addWidget(QLabel("Hours Completed:"), 2, 2)
            self.completed_hours_label = QLabel("0h")
            self.completed_hours_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            grid_layout.addWidget(self.completed_hours_label, 2, 3)

            # Row 4 - Streak
            grid_layout.addWidget(QLabel("Current Streak:"), 3, 0)
            self.streak_label = QLabel("0 🔥")
            self.streak_label.setStyleSheet("font-weight: bold; font-size: 14px; color: orange;")
            grid_layout.addWidget(self.streak_label, 3, 1)

            stats_layout.addWidget(stats_grid)

            # Add a progress bar for overall completion
            self.overall_progress = QProgressBar()
            self.overall_progress.setRange(0, 100)
            self.overall_progress.setTextVisible(True)
            stats_layout.addWidget(self.overall_progress)

            
            # Add the stats frame to the splitter
            splitter.addWidget(stats_frame)
            
            # 2. Subject-wise Progress (Middle Section)
            subject_frame = QGroupBox("Subject-wise Progress")
            subject_layout = QVBoxLayout(subject_frame)
            
            self.progress_tree = QTreeWidget()
            self.progress_tree.setHeaderLabels(["Subject", "Tasks", "Completed", "Progress", "Hours", "Done"])
            self.progress_tree.setColumnCount(6)
            self.progress_tree.setSortingEnabled(True)
            self.progress_tree.setAlternatingRowColors(True)
            self.progress_tree.setSelectionMode(QTreeWidget.SingleSelection)
            
            # Set column widths
            self.progress_tree.setColumnWidth(0, 150)  # Subject
            self.progress_tree.setColumnWidth(1, 60)   # Tasks
            self.progress_tree.setColumnWidth(2, 80)   # Completed
            self.progress_tree.setColumnWidth(3, 150)  # Progress
            self.progress_tree.setColumnWidth(4, 60)   # Hours
            self.progress_tree.setColumnWidth(5, 60)   # Done
            
            subject_layout.addWidget(self.progress_tree)
            splitter.addWidget(subject_frame)
            
            # 3. Visualization (Bottom Section)
            viz_frame = QGroupBox("Progress Visualization")
            viz_layout = QHBoxLayout(viz_frame)
            
            # Add tabs for different visualizations
            viz_tabs = QTabWidget()
            
            # Tab 1: Completion Chart
            completion_tab = QWidget()
            self.completion_chart_view = QLabel("Completion chart will appear here")
            self.completion_chart_view.setAlignment(Qt.AlignCenter)
            completion_tab_layout = QVBoxLayout(completion_tab)
            completion_tab_layout.addWidget(self.completion_chart_view)
            viz_tabs.addTab(completion_tab, "Completion")
            
            # Tab 2: Time Spent Chart
            time_tab = QWidget()
            self.time_chart_view = QLabel("Time spent chart will appear here")
            self.time_chart_view.setAlignment(Qt.AlignCenter)
            time_tab_layout = QVBoxLayout(time_tab)
            time_tab_layout.addWidget(self.time_chart_view)
            viz_tabs.addTab(time_tab, "Time Spent")
            
            viz_layout.addWidget(viz_tabs)
            splitter.addWidget(viz_frame)
            
            # Set splitter stretch factors
            splitter.setStretchFactor(0, 1)
            splitter.setStretchFactor(1, 2)
            splitter.setStretchFactor(2, 2)
            
            layout.addWidget(splitter)
            
            # Add refresh button
            refresh_btn = QPushButton("Refresh Stats")
            refresh_btn.setFont(self.mono_font)
            refresh_btn.clicked.connect(self.update_progress_stats)
            layout.addWidget(refresh_btn)
            
            # Initial update
            self.update_progress_stats() 

        def update_progress_stats(self):
            try:
                # Get all data from database
                subjects = self.core.get_all_subjects()
                tasks = []
                schedules = []
                
                for subj in subjects:
                    tasks.extend(self.core.get_all_tasks(subj['group_id']))
                schedules = self.core.get_user_schedule(self.current_user_id)
                
                # Calculate overall stats
                total_subjects = len(subjects)
                total_tasks = len(tasks)
                completed_tasks = sum(1 for task in tasks if task.get('is_completed', False))
                completion_percent = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
                
                # Calculate time stats
                total_hours = sum(task.get('duration', 0) for task in tasks) / 60  # Convert minutes to hours
                completed_hours = sum(
                    sched.get('duration', 0) / 60 
                    for sched in schedules 
                    if sched.get('end_time') and datetime.now() > sched['end_time']
                )
                
                # --- STREAK SYSTEM ---
                streak = 0
                try:
                    streak = self.core.get_user_streak(self.current_user_id)
                except Exception as e:
                    print(f"[Streak] Could not fetch streak: {e}")
                self.streak_label.setText(f"{streak} 🔥")

                # Update UI
                self.total_subjects_label.setText(str(total_subjects))
                self.total_tasks_label.setText(str(total_tasks))
                self.completed_tasks_label.setText(str(completed_tasks))
                self.completion_percent_label.setText(f"{completion_percent:.1f}%")
                self.total_hours_label.setText(f"{total_hours:.1f}h")
                self.completed_hours_label.setText(f"{completed_hours:.1f}h")
                self.overall_progress.setValue(int(completion_percent))
                
                # Update subject-wise progress
                self.progress_tree.clear()
                
                for subj in subjects:
                    subj_tasks = [t for t in tasks if t['group_id'] == subj['group_id']]
                    subj_total = len(subj_tasks)
                    subj_completed = sum(1 for t in subj_tasks if t.get('is_completed', False))
                    subj_percent = (subj_completed / subj_total * 100) if subj_total > 0 else 0
                    
                    # Calculate time spent on subject
                    subj_hours = sum(
                        sched.get('duration', 0) / 60 
                        for sched in schedules 
                        if sched.get('category') == subj['name'] and 
                        sched.get('end_time') and 
                        datetime.now() > sched['end_time']
                    )
                    
                    item = QTreeWidgetItem([
                        subj['name'],
                        str(subj_total),
                        str(subj_completed),
                        f"{subj_percent:.1f}%",
                        f"{sum(task.get('duration', 0)/60 for task in subj_tasks):.1f}h",
                        f"{subj_hours:.1f}h"
                    ])
                    
                    # Add progress bar to the item
                    progress_bar = QProgressBar()
                    progress_bar.setRange(0, 100)
                    progress_bar.setValue(int(subj_percent))
                    progress_bar.setTextVisible(True)
                    self.progress_tree.setItemWidget(item, 3, progress_bar)
                    
                    # Color coding based on completion
                    if subj_percent == 100:
                        for i in range(6):
                            item.setForeground(i, QColor(0, 128, 0))  # Green
                    elif subj_percent >= 75:
                        for i in range(6):
                            item.setForeground(i, QColor(0, 0, 255))  # Blue
                    elif subj_percent >= 50:
                        for i in range(6):
                            item.setForeground(i, QColor(255, 165, 0))  # Orange
                    
                    self.progress_tree.addTopLevelItem(item)
                
                # Update visualizations (placeholder - would use matplotlib or similar in real implementation)
                self.completion_chart_view.setText(f"Completion Chart\n{completed_tasks}/{total_tasks} tasks completed")
                self.time_chart_view.setText(f"Time Spent Chart\n{completed_hours:.1f}/{total_hours:.1f} hours completed")
                
            except Exception as e:
                self.show_error("Failed to update progress stats", e)

            def add_subtask_to_task(self, task, subtask_edit, subtasks_list):
                    """Add a subtask to the given task."""
                    description = subtask_edit.text().strip()
                    if description:
                        if 'subtasks' not in task:
                            task['subtasks'] = []
                        task['subtasks'].append({
                            "description": description,
                            "completed": False
                        })
                        subtasks_list.addItem(f"✗ {description}")
                        subtask_edit.clear()
                        self.core.save_data()
                    description = subtask_edit.text().strip()
                    if description:
                        if 'subtasks' not in task:
                            task['subtasks'] = []
                        task['subtasks'].append({
                            "description": description,
                            "completed": False
                        })
                        subtasks_list.addItem(f"✗ {description}")
                        subtask_edit.clear()
                        self.core.save_data()
        
        def update_home_stats(self):
            """Update the statistics cards on the home screen"""
            try:
                # Get all needed data
                subjects = self.core.get_all_subjects()
                tasks = []
                for subj in subjects:
                    tasks.extend(self.core.get_all_tasks(subj['group_id']))
                
                schedules = self.core.get_user_schedule(self.current_user_id)
                
                # Calculate stats
                pending_tasks = sum(1 for task in tasks if not task.get('is_completed', False))
                
                today = datetime.now().date()
                today_sessions = sum(
                    1 for sched in schedules 
                    if sched['start_time'] and sched['start_time'].date() == today
                )
                
                # Get streak from core (assuming you have this method)
                streak = self.core.get_user_streak(self.current_user_id)
                
                # Calculate progress percentage (example implementation)
                total_tasks = len(tasks)
                completed_tasks = sum(1 for task in tasks if task.get('is_completed', False))
                progress_percent = int((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0
                
                # Update the home screen cards
                if hasattr(self, 'home_screen'):
                    self.home_screen.tasks_card.statValue.setText(str(pending_tasks))
                    self.home_screen.sessions_card.statValue.setText(str(today_sessions))
                    self.home_screen.streak_card.statValue.setText(f"{streak} days")
                    self.home_screen.progress_card.statValue.setText(f"{progress_percent}%")
                    
                    # Update recent activity list
                    self.update_recent_activity()
                    
            except Exception as e:
                print(f"Error updating home stats: {e}")
                logging.error(f"Error updating home stats: {e}")

        def update_recent_activity(self):
            """Update the recent activity list on home screen"""
            if not hasattr(self, 'home_screen'):
                return
            
            try:
                # Get recent completed tasks (last 5)
                completed_tasks = []
                subjects = self.core.get_all_subjects()
                for subj in subjects:
                    tasks = self.core.get_all_tasks(subj['group_id'])
                    completed_tasks.extend(
                        task for task in tasks 
                        if task.get('is_completed', False)
                    )
                
                # Sort by completion date (newest first)
                completed_tasks.sort(key=lambda x: x.get('completion_date', datetime.min), reverse=True)
                
                # Get recent sessions (last 5)
                recent_sessions = sorted(
                    self.core.get_user_schedule(self.current_user_id),
                    key=lambda x: x.get('end_time', datetime.min),
                    reverse=True
                )
                
                # Clear existing items
                self.home_screen.activity_list.clear()
                
                # Add completed tasks (up to 3)
                for task in completed_tasks[:3]:
                    subject = next(
                        (subj['name'] for subj in subjects 
                        if subj['group_id'] == task['group_id']),
                        "Unknown"
                    )
                    item = QListWidgetItem(f"✅ Completed: {subject} - {task['title']}")
                    self.home_screen.activity_list.addItem(item)
                
                # Add recent sessions (up to 2)
                for session in recent_sessions[:2]:
                    if session.get('end_time'):
                        time_str = session['end_time'].strftime("%I:%M %p")
                        item = QListWidgetItem(f"⏰ Session: {session.get('category', '')} at {time_str}")
                        self.home_screen.activity_list.addItem(item)
                        
            except Exception as e:
                print(f"Error updating activity list: {e}")

        # UI update methods
        def update_current_date(self):
            today = datetime.now().strftime("%A, %B %d, %Y")
            self.current_date_label.setText(f"Today: {today}")

        def update_status(self, message):
            self.statusBar().showMessage(message)

        def update_subjects_list(self):
            self.subjects_tree.clear()
            subjects = self.core.get_all_subjects()
            for subj in subjects:
                item = QTreeWidgetItem([subj['name'], subj['type']])
                item.setData(0, Qt.UserRole, subj['group_id'])
                self.subjects_tree.addTopLevelItem(item)

        def refresh_tasks_tab(self):
            """Fully refresh the task tab: subjects + tasks"""
            self.update_subject_combobox()  # Refresh dropdown
            self.update_tasks_list()        # Refresh tree
            self.update_status("Tasks refreshed successfully")

        def update_tasks_list(self):
            self.tasks_tree.clear()
            subjects = self.core.get_all_subjects()
            for subj in subjects:
                tasks = self.core.get_all_tasks(subj['group_id'])
                for task in tasks:
                    item = QTreeWidgetItem([
                        subj['name'],
                        task['title'],
                        task['due_date'].strftime('%Y-%m-%d') if task['due_date'] else '',
                        "-",  # Duration (not tracked for tasks rn)
                        subj['type'],
                        "Done" if task['is_completed'] else "Pending"
                    ])
                    item.setData(0, Qt.UserRole, task['task_id'])
                    self.tasks_tree.addTopLevelItem(item)

        def update_schedule_list(self):
            self.schedule_tree.clear()
            today = datetime.now().strftime("%Y-%m-%d")
            now = datetime.now()

            # Determine filter
            filter_type = "All"
            if self.today_radio.isChecked():
                filter_type = "Today"
            elif self.upcoming_radio.isChecked():
                filter_type = "Upcoming"
            elif self.completed_radio.isChecked():
                filter_type = "Completed"

            # Get all schedules from database
            schedules = self.core.get_user_schedule(self.current_user_id)

            for sched in sorted(schedules, key=lambda x: (x.get('start_time', ''))):
                sched_date = sched['start_time'].strftime("%Y-%m-%d") if sched['start_time'] else ''
                sched_time = sched['start_time'].strftime("%H:%M") if sched['start_time'] else ''
                end_time = sched['end_time'].strftime("%H:%M") if sched['end_time'] else ''
                duration = sched.get('duration', 0)
                notes = sched.get('notes', '')

                # Apply filter
                include = False
                if filter_type == "All":
                    include = True
                elif filter_type == "Today" and sched_date == today:
                    include = True
                elif filter_type == "Upcoming" and (
                    sched_date > today or 
                    (sched_date == today and 
                    sched['start_time'].time() > now.time())
                ):
                    include = True
                elif filter_type == "Completed" and duration and sched['end_time'] and now > sched['end_time']:
                    include = True

                if not include:
                    continue

                item = QTreeWidgetItem()
                item.setText(0, sched_date)
                item.setText(1, sched_time)
                item.setText(2, end_time)
                item.setText(3, sched.get('category', ''))
                item.setText(4, notes)
                item.setText(5, f"{duration} mins" if duration else "-")

                status = "Pending"
                if duration and sched['end_time'] and now > sched['end_time']:
                    status = "Completed"

                # Check if schedule is in progress or overdue
                if sched['start_time'] and sched['end_time']:
                    if sched['start_time'] <= now <= sched['end_time']:
                        status = "IN PROGRESS"
                    elif now > sched['end_time'] and status != "Completed":
                        status = "OVERDUE"

                item.setText(6, status)

                # Color coding
                if status == "Completed":
                    for i in range(7):
                        item.setForeground(i, Qt.gray)
                elif status == "IN PROGRESS":
                    for i in range(7):
                        item.setForeground(i, Qt.blue)
                elif status == "OVERDUE":
                    for i in range(7):
                        item.setForeground(i, Qt.red)

                item.setData(0, Qt.UserRole, sched['id'])
                self.schedule_tree.addTopLevelItem(item)

        def update_header_stats(self):
            tasks = []
            schedules = []

            try:
                subjects = self.core.get_all_subjects()
                for subj in subjects:
                    tasks.extend(self.core.get_all_tasks(subj['group_id']))
                
                schedules = self.core.get_user_schedule(self.current_user_id)
                if schedules is None:
                    schedules = []

            except Exception as e:
                print(f"[Error] Failed to fetch tasks/schedules: {e}")
                schedules = []

            pending_tasks = sum(1 for task in tasks if not task.get('is_completed', False))
            today_sessions = sum(
                1 for sched in schedules
                if sched['start_time'] and sched['start_time'].date() == datetime.today().date()
            )

            self.pending_tasks_label.setText(f"Pending Tasks: {pending_tasks}")
            self.today_sessions_label.setText(f"Today's Sessions: {today_sessions}")

            
        def update_subject_combobox(self):
            self.task_subject_combo.clear()
            subjects = self.core.get_all_subjects()
            for subj in subjects:
                self.task_subject_combo.addItem(subj['name'], userData=subj['group_id'])

        # Subject management
        def add_subject(self):
            name = self.subject_name_edit.text().strip()
            priority = self.subject_priority_combo.currentText()
            
            if not name:
                QMessageBox.critical(self, "Error", "Subject name cannot be empty")
                return
                
            # Check if subject already exists
            existing_subjects=self.core.get_all_subjects()
            if any(subj['name'].lower() == name.lower() for subj in existing_subjects):
                QMessageBox.critical(self, "Error", f"Subject '{name}' already exists")
                return
            
            self.core.create_subject(name,priority)                

            self.subject_name_edit.clear()
            self.update_subjects_list()
            self.update_subject_combobox()
            self.update_status(f"Subject '{name}' added successfully")

        def edit_subject(self):
            selected = self.subjects_tree.selectedItems()
            if not selected:
                QMessageBox.warning(self, "Warning", "Please select a subject to edit")
                return

            item = selected[0]
            group_id = item.data(0, Qt.UserRole)
            old_name = item.text(0)

            dialog = QDialog(self)
            dialog.setWindowTitle("Edit Subject")
            dialog.resize(400, 200)
            layout = QVBoxLayout(dialog)

            name_layout = QHBoxLayout()
            name_layout.addWidget(QLabel("Subject Name:"))
            name_edit = QLineEdit(old_name)
            name_layout.addWidget(name_edit)
            layout.addLayout(name_layout)

            priority_layout = QHBoxLayout()
            priority_layout.addWidget(QLabel("Priority:"))
            priority_combo = QComboBox()
            priority_combo.addItems(["High", "Medium", "Low"])
            priority_layout.addWidget(priority_combo)
            layout.addLayout(priority_layout)

            save_btn = QPushButton("Save")
            save_btn.clicked.connect(lambda: self.save_subject_changes(dialog, group_id, old_name, name_edit.text(), priority_combo.currentText()))
            layout.addWidget(save_btn)

            cancel_btn = QPushButton("Cancel")
            cancel_btn.clicked.connect(dialog.reject)
            layout.addWidget(cancel_btn)

            dialog.exec()

        def save_subject_changes(self, dialog, group_id, old_name, new_name, new_priority):
            new_name = new_name.strip()
            if not new_name:
                QMessageBox.critical(dialog, "Error", "Subject name cannot be empty")
                return

            subjects = self.core.get_all_subjects()
            if new_name.lower() != old_name.lower() and any(subj['name'].lower() == new_name.lower() for subj in subjects):
                QMessageBox.critical(dialog, "Error", f"Subject '{new_name}' already exists")
                return

            try:
                self.core.edit_subject(group_id, new_name, new_priority)
                self.update_subjects_list()
                self.update_tasks_list()
                self.update_subject_combobox()
                self.update_status(f"Subject '{old_name}' updated to '{new_name}'")
                dialog.accept()
            except Exception as e:
                self.show_error("Failed to update subject", e)#

        def delete_subject(self):
            selected = self.subjects_tree.selectedItems()
            if not selected:
                return

            item = selected[0]
            group_id = item.data(0, Qt.UserRole)
            subject_name = item.text(0)

            # --- Safety Check Added Here ---
            if not self.can_delete_subject(group_id):
                QMessageBox.warning(
                    self, 
                    "Cannot Delete", 
                    f"Subject '{subject_name}' has tasks assigned.\n"
                    "Delete or reassign its tasks first."
                )
                return  # Abort deletion

            # Proceed if no tasks exist
            confirm = QMessageBox.question(
                self, "Confirm Delete",
                f"Delete subject '{subject_name}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm == QMessageBox.Yes:
                self.core.delete_subject(group_id)
                self.update_subjects_list()
                self.update_tasks_list()  # Refresh UI
                self.update_status(f"Deleted subject '{subject_name}'")

        def delete_subject_force(self, group_id):
            """Admin-only: Delete subject AND all its tasks."""
            tasks = self.core.get_all_tasks(group_id)
            for task in tasks:
                self.core.delete_task(task['task_id'])
            self.core.delete_subject(group_id)
       
        # Task management
        def add_task(self):
            title = self.task_desc_edit.text().strip()
            group_id = self.task_subject_combo.currentData()
            due_date = self.task_due_date_edit.date().toString("yyyy-MM-dd")

            if not title or group_id is None:
                QMessageBox.warning(self, "Error", "Please fill all task fields.")
                return

            self.core.create_task(group_id, title, due_date)
            self.update_tasks_list()
            self.update_status(f"Task '{title}' added successfully!")

        def edit_task(self):
            selected = self.tasks_tree.selectedItems()
            if not selected:
                QMessageBox.warning(self, "Error", "Please select a task to edit.")
                return

            item = selected[0]
            task_id = item.data(0, Qt.UserRole)
            task = self.core.get_task(task_id)

            dialog = QDialog(self)
            layout = QVBoxLayout(dialog)

            title_edit = QLineEdit(task['title'])
            due_date_edit = QDateEdit()
            due_date_edit.setDate(task['due_date'])
            group_combo = QComboBox()
            subjects = self.core.get_all_subjects()
            for subj in subjects:
                group_combo.addItem(subj['name'], userData=subj['group_id'])
            group_combo.setCurrentIndex(group_combo.findData(task['group_id']))

            save_btn = QPushButton("Save")
            save_btn.clicked.connect(lambda: self.save_task_changes(dialog, task_id, title_edit.text(), due_date_edit.date().toString("yyyy-MM-dd"), group_combo.currentData()))

            layout.addWidget(title_edit)
            layout.addWidget(due_date_edit)
            layout.addWidget(group_combo)
            layout.addWidget(save_btn)

            dialog.exec()


        def save_task_changes(self, dialog, task_id, new_title, new_due_date, new_group_id):
            self.core.edit_task(task_id, new_title, new_due_date, new_group_id)
            self.update_tasks_list()
            self.update_subject_combobox()
            dialog.accept()
            self.update_status(f"Task '{new_title}' updated successfully.")

        def mark_task_completed(self):
            selected = self.tasks_tree.selectedItems()
            if not selected:
                return

            item = selected[0]
            task_id = item.data(0, Qt.UserRole)
            tasks = []
            subjects = self.core.get_all_subjects()
            for subj in subjects:
                tasks.extend(self.core.get_all_tasks(subj['group_id']))
            task = next((t for t in tasks if t['task_id'] == task_id), None)

            if task:
                new_status = not task['is_completed']
                self.core.update_task_status(task_id, new_status)
                self.update_tasks_list()

        def delete_task(self):
            selected = self.tasks_tree.selectedItems()
            if not selected:
                return

            item = selected[0]
            task_id = item.data(0, Qt.UserRole)
            self.core.delete_task(task_id)
            self.update_tasks_list()
            self.update_status("Task deleted.")

        def schedule_task_dialog(self, tasks):
            selected = self.tasks_tree.selectedItems()
            if not selected:
                QMessageBox.warning(self, "Warning", "Please select task(s) to schedule")
                return
                
            # Get all selected tasks
            tasks_to_schedule = []
            total_duration = 0.0
            for item in selected:
                task_id = item.data(0, Qt.UserRole)
                task = self.core.get_task(task_id)  # 🔥 Fetch directly from SQL
                if task and not task['is_completed']:  # 🔥 Use SQL field properly
                    tasks_to_schedule.append(task)
                    total_duration += task.get('duration', 0) if 'duration' in task else 0
            
            if not tasks_to_schedule:
                QMessageBox.warning(self, "Warning", "Selected tasks are already completed")
                return
                
            # Create dialog window
            dialog = QDialog(self)
            dialog.setWindowTitle("Schedule Task(s)")
            dialog.resize(300, 100)
            layout = QVBoxLayout(dialog)
            
            if len(tasks_to_schedule) == 1:
                layout.addWidget(QLabel(f"Scheduling: {tasks_to_schedule[0].get('title', '')}"))
            else:
                layout.addWidget(QLabel(f"Scheduling {len(tasks_to_schedule)} tasks (Total: {total_duration:.1f} hours)"))
            
            # Date selection
            date_layout = QHBoxLayout()
            date_layout.addWidget(QLabel("Date:"))
            date_edit = QDateEdit()
            date_edit.setCalendarPopup(True)
            date_edit.setDate(QDate.currentDate())
            date_layout.addWidget(date_edit)
            layout.addLayout(date_layout)
            
            # Time selection
            time_layout = QHBoxLayout()
            time_layout.addWidget(QLabel("Start Time:"))
            time_edit = QTimeEdit()
            time_edit.setTime(QTime(19, 0))  # Default to 7 PM
            time_layout.addWidget(time_edit)
            layout.addLayout(time_layout)
            
            # Buttons
            btn_layout = QHBoxLayout()
            schedule_btn = QPushButton("Schedule")
            schedule_btn.clicked.connect(lambda: self.schedule_tasks(
                tasks_to_schedule,
                date_edit.date().toString("yyyy-MM-dd"),
                time_edit.time().toString("HH:mm"),
                dialog
            ))
            btn_layout.addWidget(schedule_btn)
            
            cancel_btn = QPushButton("Cancel")
            cancel_btn.clicked.connect(dialog.reject)
            btn_layout.addWidget(cancel_btn)
            
            layout.addLayout(btn_layout)
            dialog.exec()

        def schedule_tasks(self, tasks, date, time, dialog):
            try:
                datetime.strptime(date, "%Y-%m-%d")
                datetime.strptime(time, "%H:%M")
            except ValueError:
                QMessageBox.critical(self, "Error", "Invalid date or time format. Use YYYY-MM-DD and HH:MM")
                return
            
            # Calculate the end time based on the total duration of all tasks
            total_duration = sum(task.get('duration', 0) for task in tasks)
            start_time_str = f"{date} {time}"
            start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M")
            end_time = (start_time + timedelta(hours=total_duration))

            # Then format both for SQL
            start_time_sql = start_time.strftime("%Y-%m-%d %H:%M:%S")
            end_time_sql = end_time.strftime("%Y-%m-%d %H:%M:%S")

            
            # Insert each task into the schedule using ChronoCore methods
            for task in tasks:
                task_id = task.get('id', '')
                subject = task.get('subject', '')
                description = task.get('description', '')
                duration = task.get('duration', 0)
                
                self.core.add_task_to_schedule(
                    user_id=self.current_user_id, 
                    start_time=start_time_sql,
                    end_time=end_time_sql,
                    duration=duration,
                    category=subject,
                    notes=description
                )

                
                # Update start time for the next task if there are multiple tasks
                if len(tasks) > 1:
                    start_time = datetime.strptime(end_time, "%H:%M")
                    end_time = (start_time + timedelta(hours=duration)).strftime("%H:%M")
            
            # Call save_data to persist changes
            self.core.save_data()

            # Update the schedule list in the UI
            self.update_schedule_list()
            dialog.accept()

            if len(tasks) == 1:
                self.update_status(f"Task '{tasks[0].get('description', '')}' scheduled for {date} at {time}")
            else:
                self.update_status(f"{len(tasks)} tasks scheduled for {date} starting at {time}")

            
        # Schedule management
        def save_schedule_changes(self, dialog, schedule_id, new_category, new_notes, new_start_time, new_end_time, new_duration):
            try:
                query = "UPDATE schedule SET category = %s, notes = %s, start_time = %s, end_time = %s, duration = %s WHERE id = %s"
                self.core.db.execute_query(query, (
                    new_category,
                    new_notes,
                    new_start_time,
                    new_end_time,
                    new_duration,
                    schedule_id
                ))
                self.update_schedule_list()
                self.update_status("Schedule updated successfully")
                dialog.accept()
            except Exception as e:
                self.show_error("Failed to save schedule changes", e)

        def mark_scheduled_completed(self):
            selected = self.schedule_tree.selectedItems()
            if not selected:
                return

            item = selected[0]
            schedule_id = item.data(0, Qt.UserRole)

            # Start the session with AFK checks
            self.start_study_session(schedule_id)
            
            try:
                end_time = datetime.now()
                start_time_query = "SELECT start_time FROM schedule WHERE id = %s"
                start_time_row = self.core.db.fetch_one(start_time_query, (schedule_id,))
                if start_time_row:
                    start_time = start_time_row['start_time']
                    duration = int((end_time - start_time).total_seconds() // 60)
                    self.core.end_schedule(schedule_id, end_time, duration)
                    self.update_schedule_list()
                    self.update_status("Marked as completed")
            except Exception as e:
                self.show_error("Failed to mark schedule completed", e)

        def delete_schedule(self):
            selected = self.schedule_tree.selectedItems()
            if not selected:
                return

            item = selected[0]
            schedule_id = item.data(0, Qt.UserRole)

            try:
                self.core.delete_schedule(schedule_id)
                self.update_schedule_list()
                self.update_status("Scheduled session deleted")
            except Exception as e:
                self.show_error("Failed to delete schedule", e)

        # Advanced features
        def manage_subtasks(self):
            selected = self.tasks_tree.selectedItems()
            if not selected or len(selected) > 1:
                QMessageBox.warning(self, "Warning", "Please select exactly one task to manage subtasks")
                return
                
            item = selected[0]
            task_id = item.data(0, Qt.UserRole)
            
            # Find the task
            task = next((t for t in self.tasks if t.get('id', '') == task_id), None)
            if not task:
                return
            
            # Create dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Manage Subtasks")
            dialog.resize(500, 400)
            layout = QVBoxLayout(dialog)
            
            layout.addWidget(QLabel(f"Manage subtasks for: {task.get('description', '')}"))
            
            # Subtasks list
            subtasks_list = QListWidget()
            for subtask in task.get('subtasks', []):
                status = "✓" if subtask.get('completed', False) else "✗"
                subtasks_list.addItem(f"{status} {subtask.get('description', '')}")
            layout.addWidget(subtasks_list)
            
            # Add subtask
            add_layout = QHBoxLayout()
            subtask_edit = QLineEdit()
            add_layout.addWidget(subtask_edit)
            
            add_btn = QPushButton("Add")
            add_btn.clicked.connect(lambda: self.add_subtask_to_task(task, subtask_edit, subtasks_list))
            add_layout.addWidget(add_btn)
            layout.addLayout(add_layout)
            
            # Toggle completion
            toggle_btn = QPushButton("Toggle Completion")
            toggle_btn.clicked.connect(lambda: self.toggle_subtask_completion(task, subtasks_list))
            layout.addWidget(toggle_btn)
            
            # Remove
            remove_btn = QPushButton("Remove Selected")
            remove_btn.clicked.connect(lambda: self.remove_subtask(task, subtasks_list))
            layout.addWidget(remove_btn)
            
            # Close button
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.accept)
            layout.addWidget(close_btn)
            
            dialog.exec()
        

        def start_study_session(self, schedule_id):
            """Call this when a study session begins"""
            self.current_session_active = True
            self.current_schedule_id = schedule_id
            self.afk_timer.start(self.afk_check_interval)
            self.update_status("Study session started - AFK checks active")

        def end_study_session(self):
            """Call this when study session ends"""
            self.current_session_active = False
            self.afk_timer.stop()
            self.afk_response_timer.stop()
            self.current_schedule_id = None
            self.update_status("Study session ended")

        def check_afk_status(self):
            """Show AFK check dialog"""
            if not self.current_session_active:
                return
            
            # Create the AFK check dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("AFK Check")
            dialog.setModal(True)
            layout = QVBoxLayout(dialog)
            
            label = QLabel("Are you still studying?")
            layout.addWidget(label)
            
            btn_box = QDialogButtonBox()
            yes_btn = btn_box.addButton("Yes", QDialogButtonBox.AcceptRole)
            no_btn = btn_box.addButton("No", QDialogButtonBox.RejectRole)
            layout.addWidget(btn_box)
            
            # Start response timeout timer
            self.afk_response_timer.start(self.afk_timeout)
            
            def handle_response():
                self.afk_response_timer.stop()
                if dialog.result() == QDialog.Accepted:
                    self.update_status("Study session confirmed")
                    # Reset the AFK timer
                    self.afk_timer.start(self.afk_check_interval)
                else:
                    self.handle_afk_timeout()
            
            btn_box.accepted.connect(handle_response)
            btn_box.rejected.connect(handle_response)
            
            dialog.finished.connect(handle_response)
            dialog.show()

        def handle_afk_timeout(self):
            """Called when user doesn't respond to AFK check"""
            if not self.current_session_active:
                return
            
            # Log the AFK event and pause tracking
            self.core.log_afk_event(self.current_schedule_id)
            self.end_study_session()
            
            # Show warning
            QMessageBox.warning(
                self,
                "Session Paused",
                "Study session paused due to inactivity.\n"
                "Please start a new session when ready to continue."
            )
            self.update_status("Study session paused due to AFK")

        def toggle_subtask_completion(self, task, subtasks_list):
            selected = subtasks_list.currentRow()
            if selected >= 0 and 'subtasks' in task and selected < len(task['subtasks']):
                task['subtasks'][selected]['completed'] = not task['subtasks'][selected]['completed']
                status = "✓" if task['subtasks'][selected]['completed'] else "✗"
                subtasks_list.currentItem().setText(
                    f"{status} {task['subtasks'][selected]['description']}"
                )
                self.core.save_data()

        def remove_subtask(self, task, subtasks_list):
            selected = subtasks_list.currentRow()
            if selected >= 0 and 'subtasks' in task and selected < len(task['subtasks']):
                task['subtasks'].pop(selected)
                subtasks_list.takeItem(selected)
                self.core.save_data()

        def manage_dependencies(self):
            selected = self.tasks_tree.selectedItems()
            if not selected or len(selected) > 1:
                QMessageBox.warning(self, "Warning", "Please select exactly one task to manage dependencies")
                return
                
            item = selected[0]
            task_id = item.data(0, Qt.UserRole)
            
            # Find the task
            task = next((t for t in self.tasks if t.get('id', '') == task_id), None)
            if not task:
                return
            
            # Create dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Manage Dependencies")
            dialog.resize(500, 400)
            layout = QVBoxLayout(dialog)
            
            layout.addWidget(QLabel(f"Manage dependencies for: {task.get('description', '')}"))
            
            # Available tasks (excluding current task and its existing dependencies)
            available_tasks = [
                t for t in self.tasks 
                if t.get('id', '') != task_id and 
                t.get('id', '') not in task.get('depends_on', [])
            ]
            
            # Current dependencies
            current_deps = QListWidget()
            for dep_id in task.get('depends_on', []):
                dep_task = next((t for t in self.tasks if t.get('id', '') == dep_id), None)
                if dep_task:
                    current_deps.addItem(
                        f"{dep_task.get('subject', '')}: {dep_task.get('description', '')}"
                    )
            layout.addWidget(QLabel("Current Dependencies:"))
            layout.addWidget(current_deps)
            
            # Available tasks list
            available_list = QListWidget()
            for t in available_tasks:
                available_list.addItem(
                    f"{t.get('subject', '')}: {t.get('description', '')}"
                )
            available_list.setSelectionMode(QListWidget.MultiSelection)
            layout.addWidget(QLabel("Available Tasks:"))
            layout.addWidget(available_list)
            
            # Buttons
            btn_layout = QHBoxLayout()
            
            add_btn = QPushButton("Add Selected as Dependencies")
            add_btn.clicked.connect(lambda: self.add_dependencies(
                task, available_tasks, available_list, current_deps
            ))
            btn_layout.addWidget(add_btn)
            
            remove_btn = QPushButton("Remove Selected Dependencies")
            remove_btn.clicked.connect(lambda: self.remove_dependencies(
                task, current_deps
            ))
            btn_layout.addWidget(remove_btn)
            
            layout.addLayout(btn_layout)
            
            # Close button
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.accept)
            layout.addWidget(close_btn)
            
            dialog.exec()

        def add_dependencies(self, task, available_tasks, available_list, current_deps):
            selected = available_list.selectedItems()
            if not selected:
                return
                
            for item in selected:
                index = available_list.row(item)
                if index < len(available_tasks):
                    dep_id = available_tasks[index].get('id', '')
                    if 'depends_on' not in task:
                        task['depends_on'] = []
                    if dep_id not in task['depends_on']:
                        task['depends_on'].append(dep_id)
                        current_deps.addItem(item.text())
            self.core.save_data()

        def remove_dependencies(self, task, current_deps):
            selected = current_deps.selectedItems()
            if not selected:
                return
                
            for item in selected:
                index = current_deps.row(item)
                if 'depends_on' in task and index < len(task['depends_on']):
                    task['depends_on'].pop(index)
                    current_deps.takeItem(index)
            self.core.save_data()

        def add_recurring_task(self):
            # First add the task normally
            self.add_task()
            
            # Then open recurrence dialog for the last added task
            if not self.tasks:
                return
                
            task = self.tasks[-1]
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Set Recurrence")
            dialog.resize(400, 300)
            layout = QVBoxLayout(dialog)
            
            layout.addWidget(QLabel(f"Set recurrence for: {task.get('description', '')}"))
            
            # Recurrence type
            layout.addWidget(QLabel("Recurrence Pattern:"))
            
            recurrence_type = QButtonGroup()
            daily_radio = QRadioButton("Daily")
            daily_radio.setChecked(True)
            recurrence_type.addButton(daily_radio)
            layout.addWidget(daily_radio)
            
            weekly_radio = QRadioButton("Weekly")
            recurrence_type.addButton(weekly_radio)
            layout.addWidget(weekly_radio)
            
            monthly_radio = QRadioButton("Monthly")
            recurrence_type.addButton(monthly_radio)
            layout.addWidget(monthly_radio)
            
            # Interval
            layout.addWidget(QLabel("Interval:"))
            interval_spin = QSpinBox()
            interval_spin.setRange(1, 30)
            interval_spin.setValue(1)
            layout.addWidget(interval_spin)
            
            # End date
            layout.addWidget(QLabel("End Date (optional):"))
            end_date_edit = QDateEdit()
            end_date_edit.setCalendarPopup(True)
            end_date_edit.setDate(QDate.currentDate().addMonths(1))
            layout.addWidget(end_date_edit)
            
            # Buttons
            btn_layout = QHBoxLayout()
            
            save_btn = QPushButton("Save")
            save_btn.clicked.connect(lambda: self.save_recurrence(
                dialog, task, 
                "daily" if daily_radio.isChecked() else "weekly" if weekly_radio.isChecked() else "monthly",
                interval_spin.value(),
                end_date_edit.date().toString("yyyy-MM-dd") if end_date_edit.date() > QDate.currentDate() else ""
            ))
            btn_layout.addWidget(save_btn)
            
            cancel_btn = QPushButton("Cancel")
            cancel_btn.clicked.connect(dialog.reject)
            btn_layout.addWidget(cancel_btn)
            
            layout.addLayout(btn_layout)
            dialog.exec()

        def save_recurrence(self, dialog, task, recurrence_type, interval, end_date):
            recurrence = {
                "type": recurrence_type,
                "interval": interval,
                "end_date": end_date if end_date else None
            }
            task['recurrence'] = recurrence
            self.core.save_data()
            dialog.accept()
            self.update_status(f"Recurrence set for task '{task.get('description', '')}'")

        # Context menus
        def show_subjects_context_menu(self, pos):
            item = self.subjects_tree.itemAt(pos)
            if item:
                menu = QMenu(self)
                
                edit_action = QAction("Edit Subject", self)
                edit_action.triggered.connect(self.edit_subject)
                menu.addAction(edit_action)
                
                delete_action = QAction("Delete Subject", self)
                delete_action.triggered.connect(self.delete_subject)
                menu.addAction(delete_action)
                
                menu.exec_(self.subjects_tree.viewport().mapToGlobal(pos))

        def show_tasks_context_menu(self, pos):
            item = self.tasks_tree.itemAt(pos)
            if item:
                menu = QMenu(self)
                
                complete_action = QAction("Mark Completed", self)
                complete_action.triggered.connect(self.mark_task_completed)
                menu.addAction(complete_action)
                
                edit_action = QAction("Edit Task", self)
                edit_action.triggered.connect(self.edit_task)
                menu.addAction(edit_action)
                
                delete_action = QAction("Delete Task", self)
                delete_action.triggered.connect(self.delete_task)
                menu.addAction(delete_action)
                
                schedule_action = QAction("Schedule Task", self)
                schedule_action.triggered.connect(self.schedule_task_dialog)
                menu.addAction(schedule_action)
                
                menu.exec_(self.tasks_tree.viewport().mapToGlobal(pos))

        def show_schedule_context_menu(self, pos):
            item = self.schedule_tree.itemAt(pos)
            if item:
                menu = QMenu(self)
                
                complete_action = QAction("Mark Completed", self)
                complete_action.triggered.connect(self.mark_scheduled_completed)
                menu.addAction(complete_action)

                
                delete_action = QAction("Delete Schedule", self)
                delete_action.triggered.connect(self.delete_schedule)
                menu.addAction(delete_action)
                
                menu.exec_(self.schedule_tree.viewport().mapToGlobal(pos))

        def closeEvent(self, event):
            self.core.close_connection()
            super().closeEvent(event)

        def create_notes_tab(self):
            """Create and add the notes tab"""
            tab = NotesTab(self, user_id=self.current_user_id)  # Pass self as parent for theme access
            self.content_stack.addWidget(tab)

    class HomeScreen(QWidget):
        """Modern home screen with stats cards and activity feed"""
        
        def __init__(self, parent=None):
            super().__init__(parent)
            self.parent = parent
            self.setup_ui()  # Initialize the UI when created
        
        def setup_ui(self):
            """Construct all UI elements for the home screen"""
            layout = QVBoxLayout(self)
            layout.setContentsMargins(30, 30, 30, 30)
            layout.setSpacing(25)
            
            # 1. Welcome header (date + title)
            welcome_layout = QHBoxLayout()
            welcome_label = QLabel("Welcome back!")
            date_label = QLabel(QDate.currentDate().toString("dddd, MMMM d, yyyy"))
            welcome_layout.addWidget(welcome_label)
            welcome_layout.addStretch()
            welcome_layout.addWidget(date_label)
            layout.addLayout(welcome_layout)
            
            # 2. Stats cards (tasks, sessions, streak, progress)
            stats_layout = QHBoxLayout()
            self.tasks_card = self.create_stat_card("📋", "Pending Tasks", "0", "#4CAF50")
            self.sessions_card = self.create_stat_card("⏱️", "Today's Sessions", "0", "#2196F3")
            self.streak_card = self.create_stat_card("🔥", "Study Streak", "0 days", "#FF9800")
            self.progress_card = self.create_stat_card("📈", "Weekly Goal", "0%", "#9C27B0")
            stats_layout.addWidget(self.tasks_card)
            stats_layout.addWidget(self.sessions_card)
            stats_layout.addWidget(self.streak_card)
            stats_layout.addWidget(self.progress_card)
            layout.addLayout(stats_layout)
            
            # 3. Recent activity section
            activity_section = QWidget()
            activity_layout = QVBoxLayout(activity_section)
            activity_title = QLabel("Recent Activity")
            activity_layout.addWidget(activity_title)
            
            # 🔥 Activity list (the critical part you asked about)
            self.activity_list = QListWidget()  # Store as instance variable
            self.activity_list.setObjectName("activityList")  # Required for dynamic updates
            self.activity_list.setFont(QFont("Segoe UI", 11))
            
            # Placeholder items (replaced later by real data)
            placeholder_items = ["Loading recent activity..."]
            for item in placeholder_items:
                self.activity_list.addItem(item)
            
            activity_layout.addWidget(self.activity_list)
            layout.addWidget(activity_section)
            
            # 4. Quick action buttons
            actions_layout = QHBoxLayout()
            self.start_study_btn = QPushButton("🚀 Start Study Session")
            actions_layout.addWidget(self.start_study_btn)
            layout.addLayout(actions_layout)
                
        def create_stat_card(self, icon, title, value, color):
            """Create a statistics card widget with identifiable labels"""
            card = QWidget()
            card.setObjectName("statCard")
            card.setFixedHeight(120)
            
            layout = QVBoxLayout(card)
            layout.setContentsMargins(20, 15, 20, 15)
            layout.setSpacing(8)
            
            # Icon and value row
            top_layout = QHBoxLayout()
            
            icon_label = QLabel(icon)
            icon_label.setFont(QFont("Segoe UI Emoji", 24))
            icon_label.setFixedSize(40, 40)
            icon_label.setAlignment(Qt.AlignCenter)
            top_layout.addWidget(icon_label)
            
            top_layout.addStretch()
            
            # Value label (the number we want to update)
            value_label = QLabel(value)
            value_label.setObjectName("statValue")  # 🔥 Critical: Set object name
            value_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
            value_label.setStyleSheet(f"color: {color};")
            top_layout.addWidget(value_label)
            
            layout.addLayout(top_layout)
            
            # Title label
            title_label = QLabel(title)
            title_label.setObjectName("statTitle")  # Optional: For styling
            title_label.setFont(QFont("Segoe UI", 11))
            layout.addWidget(title_label)
            
            return card

    class StatCard(QFrame):
        def __init__(self, title, value):
            super().__init__()
            self.setFrameShape(QFrame.StyledPanel)
            self.setup_ui(title, value)
            
        def setup_ui(self, title, value):
            layout = QVBoxLayout(self)
            layout.setSpacing(5)
            
            self.titleLabel = QLabel(title)
            self.titleLabel.setFont(QFont('Monospace', 10))
            layout.addWidget(self.titleLabel)
            
            self.statValue = QLabel(value)
            self.statValue.setFont(QFont('Monospace', 20, QFont.Bold))
            layout.addWidget(self.statValue)

    class StudyModeWindow(QMainWindow):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.parent = parent
            self.setWindowTitle(" Study Mode")
            
            self.themes = {
    "warm_sunset": {
        "name": "Warm Sunset",
        "bg_color": "#1A1A2E",  # Dark navy
        "text_color": "#E6E6E6",
        "accent": "#FF7E5F",  # Coral
        "secondary_accent": "#FEB47B",  # Peach
        "end_flash": "#FF7E5F",
        "button_hover": "rgba(254, 180, 123, 0.2)"
    },
    "ocean_breeze": {
        "name": "Ocean Breeze",
        "bg_color": "#0F3460",  # Deep blue
        "text_color": "#FFFFFF",
        "accent": "#00E0FF",  # Cyan
        "secondary_accent": "#6EDCD9",  # Teal
        "end_flash": "#00E0FF",
        "button_hover": "rgba(0, 224, 255, 0.2)"
    },
    "forest_night": {
        "name": "Forest Night",
        "bg_color": "#0D1B1E",  # Almost black
        "text_color": "#E0E0E0",
        "accent": "#5CDB95",  # Mint green
        "secondary_accent": "#379683",  # Forest green
        "end_flash": "#5CDB95",
        "button_hover": "rgba(92, 219, 149, 0.2)"
    },
    "royal_elegance": {
        "name": "Royal Elegance",
        "bg_color": "#1A1A2E",  # Dark navy
        "text_color": "#FFFFFF",
        "accent": "#9370DB",  # Medium purple
        "secondary_accent": "#BA55D3",  # Orchid
        "end_flash": "#9370DB",
        "button_hover": "rgba(147, 112, 219, 0.2)"
    },
    "fiery_passion": {
        "name": "Fiery Passion",
        "bg_color": "#1E0000",  # Very dark red
        "text_color": "#FFFFFF",
        "accent": "#FF4E50",  # Red-orange
        "secondary_accent": "#F9D423",  # Yellow
        "end_flash": "#FF4E50",
        "button_hover": "rgba(255, 78, 80, 0.2)"
    },
    "moonlight_serenity": {
        "name": "Moonlight Serenity",
        "bg_color": "#0F0F1A",  # Dark blue-gray
        "text_color": "#E6E6E6",
        "accent": "#A5B4FC",  # Lavender blue
        "secondary_accent": "#818CF8",  # Light purple
        "end_flash": "#A5B4FC",
        "button_hover": "rgba(165, 180, 252, 0.2)"
            }
        }
            # Default theme
            self.current_theme = "warm_sunset"
            self.current_task = self.get_current_task_from_parent()
            self.session_start = datetime.now()
            self.session_duration = timedelta(minutes=25)
            self.remaining_time = self.session_duration
            self.is_paused = False
            self.flash_active = False
            
            # Set window properties
            self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
            self.setWindowState(Qt.WindowFullScreen)
            
            # UI Setup with minimal layout
            self.setup_ui()
            
            # Initialize timer
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_timer)
            self.timer.start(1000)
            
            # Initialize quotes rotation timer
            self.quote_timer = QTimer(self)
            self.quote_timer.timeout.connect(self.rotate_quote)
            self.quote_timer.start(30000)

        def setup_ui(self):
            # Main widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # Main horizontal layout
            main_layout = QHBoxLayout(central_widget)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
            
            # Create modern sidebar
            self.sidebar = MainWindow.CollapsibleSidebar(self)
            main_layout.addWidget(self.sidebar)
            
            # Create content area
            self.content_stack = QStackedWidget()
            self.content_stack.setObjectName("contentArea")
            main_layout.addWidget(self.content_stack)
            
            # Create all content pages
            self.create_home_screen()
            self.create_subjects_tab()
            self.create_tasks_tab()
            self.create_schedule_tab()
            self.create_progress_tab()
            self.create_notes_tab()
            
            # Status bar
            self.status_bar = QStatusBar()
            self.status_bar.setFont(QFont("Monospace", 10))
            self.setStatusBar(self.status_bar)
            
            # Set home as default
            self.content_stack.setCurrentIndex(0)
        
        def create_home_screen(self):
            """Create the modern home screen"""
            self.home_screen = MainWindow.HomeScreen(self)
            self.content_stack.addWidget(self.home_screen)
            
            # Connect home screen buttons
            self.home_screen.start_study_btn.clicked.connect(self.activate_study_mode)
            
            # Update stats
            self.update_home_stats()


        def update_home_stats(self):
            """Update the statistics on the home screen"""
            try:
                # Get all data from database
                subjects = self.core.get_all_subjects()
                tasks = []
                schedules = []
                
                for subj in subjects:
                    tasks.extend(self.core.get_all_tasks(subj['group_id']))
                schedules = self.core.get_user_schedule(self.current_user_id)
                
                # Calculate stats
                pending_tasks = sum(1 for task in tasks if not task.get('is_completed', False))
                today_sessions = sum(
                    1 for sched in schedules
                    if sched['start_time'] and sched['start_time'].date() == datetime.today().date()
                )
                
                # Update cards
                self.home_screen.tasks_card.statValue.setText(str(pending_tasks))
                self.home_screen.sessions_card.statValue.setText(str(today_sessions))
                
                # Update streak
                streak = self.core.get_user_streak(self.current_user_id)
                self.home_screen.streak_card.statValue.setText(f"{streak} days")
                
                # Update progress (placeholder - implement your own logic)
                progress = random.randint(50, 90)
                self.home_screen.progress_card.statValue.setText(f"{progress}%")
                
            except Exception as e:
                print(f"Error updating home stats: {e}")
        
        def switch_to_tab(self, index):
            """Switch to the specified tab"""
            self.content_stack.setCurrentIndex(index)
            
            # Update the stats when switching to home tab
            if index == 0:
                self.update_home_stats()

        def apply_theme(self):
            """Apply theme with more sophisticated styling"""
            theme = self.themes[self.current_theme]
            
            # Main background with subtle gradient effect
            self.central_widget.setStyleSheet(f"""
                background-color: {theme['bg_color']};
                color: {theme['text_color']};
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                border: 1px solid rgba(255, 255, 255, 0.05);
            """)
            
            # Timer display with more dramatic styling
            self.timer_label.setStyleSheet(f"""
                color: {theme['accent']};
                font-size: 160px;
                font-weight: 700;
                letter-spacing: -2px;
                margin-bottom: 0;
            """)
            
            # Task label with secondary accent
            self.task_label.setText(f"{self.current_task}")
            self.task_label.setStyleSheet(f"""
                color: {theme['secondary_accent']};
                font-size: 20px;
                font-weight: 500;
                opacity: 0.9;
                margin: 10px 0 30px 0;
            """)
            
            # Progress bar with gradient effect
            self.progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    border: none;
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 2px;
                    margin: 0 0 30px 0;
                    height: 4px;
                }}
                QProgressBar::chunk {{
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:0,
                        stop:0 {theme['accent']}, 
                        stop:1 {theme['secondary_accent']}
                    );
                    border-radius: 2px;
                }}
            """)
            
            # Buttons with hover effects using both accents
            button_style = f"""
                QPushButton {{
                    background-color: transparent;
                    color: {theme['text_color']};
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    border-radius: 20px;
                    padding: 8px 16px;
                    font-size: 14px;
                    font-weight: 500;
                    min-width: 100px;
                }}
                QPushButton:hover {{
                    background-color: {theme['button_hover']};
                    border: 1px solid {theme['accent']};
                    color: {theme['accent']};
                }}
                QPushButton:pressed {{
                    background-color: rgba({self.hex_to_rgb(theme['accent'])}, 0.3);
                }}
            """
            
            # Quote label with subtle accent
            self.quote_label.setStyleSheet(f"""
                color: {theme['secondary_accent']};
                font-size: 14px;
                font-style: italic;
                opacity: 0.7;
                margin-top: 30px;
                padding: 0 40px;
            """)

        def hex_to_rgb(self, hex_color):
            """Helper to convert hex to rgb string for rgba()"""
            hex_color = hex_color.lstrip('#')
            return ', '.join(str(int(hex_color[i:i+2], 16)) for i in (0, 2, 4))
        
        def show_theme_menu(self):
            """Show simplified theme selection menu"""
            menu = QMenu(self)
            menu.setStyleSheet(f"""
                QMenu {{
                    background-color: #111111;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 4px;
                    padding: 8px 4px;
                }}
                QMenu::item {{
                    padding: 8px 20px;
                    border-radius: 2px;
                    margin: 2px 4px;
                    color: white;
                }}
                QMenu::item:selected {{
                    background-color: rgba(255, 255, 255, 0.1);
                }}
            """)
            
            for theme_id, theme_data in self.themes.items():
                action = QAction(f" {theme_data['name']}", self)
                action.triggered.connect(lambda _, t=theme_id: self.set_theme(t))
                menu.addAction(action)
            
            menu.exec_(self.theme_btn.mapToGlobal(QPoint(0, self.theme_btn.height())))

        def set_theme(self, theme_id):
            """Change to specified theme"""
            if theme_id in self.themes:
                self.current_theme = theme_id
                self.apply_theme() 

        def update_timer(self):
            """Update the timer display"""
            if not self.is_paused and not self.flash_active:
                self.remaining_time -= timedelta(seconds=1)
                self.timer_label.setText(self.format_time(self.remaining_time))
                
                elapsed = (self.session_duration - self.remaining_time).total_seconds()
                self.progress_bar.setValue(elapsed)
                
                if self.remaining_time.total_seconds() <= 0:
                    self.timer.stop()
                    self.handle_session_end()

        def handle_session_end(self):
            """Handle what happens when study session ends"""
            theme = self.themes[self.current_theme]
            self.timer_label.setText("DONE")
            self.timer_label.setStyleSheet(f"color: {theme['accent']}; font-size: 160px; font-weight: 700;")
            
            # Flash the window
            self.flash_active = True
            self.flash_timer = QTimer(self)
            self.flash_timer.timeout.connect(self.toggle_flash)
            self.flash_count = 0
            self.flash_timer.start(500)
            

        def toggle_flash(self):
            #Flash effect for session end
            theme = self.themes[self.current_theme]
            self.flash_count += 1
            if self.flash_count > 6:  # Flash 3 times
                self.flash_timer.stop()
                self.flash_active = False
                return
                
            if self.flash_count % 2 == 0:
                self.central_widget.setStyleSheet(f"background-color: {theme['bg_color']};")
            else:
                self.central_widget.setStyleSheet(f"background-color: {theme['bg_color']}; border: 20px solid {theme['end_flash']};")

        def toggle_pause(self):
            """Toggle pause state"""
            self.is_paused = not self.is_paused
            self.pause_btn.setText("Resume" if self.is_paused else "Pause")
            
            if self.is_paused:
                self.timer.stop()
                self.timer_label.setStyleSheet("color: rgba(255, 255, 255, 0.3); font-size: 160px; font-weight: 700;")
            else:
                self.timer.start(1000)
                theme = self.themes[self.current_theme]
                self.timer_label.setStyleSheet(f"color: {theme['accent']}; font-size: 160px; font-weight: 700;")

        def adjust_time(self, minutes):
            """Add or remove time from session"""
            self.remaining_time += timedelta(minutes=minutes)
            self.session_duration += timedelta(minutes=minutes)
            self.progress_bar.setRange(0, self.session_duration.total_seconds())
            self.timer_label.setText(self.format_time(self.remaining_time))

        def rotate_quote(self):
            """Show a new motivational quote"""
            self.quote_label.setText(random.choice(self.quotes))

        def format_time(self, time_delta):
            """Format timedelta as MM:SS"""
            total_seconds = int(time_delta.total_seconds())
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            return f"{minutes:02d}:{seconds:02d}"

        def get_current_task_from_parent(self):
            #Safely get current task from parent or return default
            try:
                if hasattr(self.parent, 'tasks_tree'):
                    selected = self.parent.tasks_tree.selectedItems()
                    if selected:
                        return selected[0].text(1)  # Task description column
            except Exception as e:
                print(f"Couldn't get task from parent: {e}")
            return "Focused Work Session"

        def close_study_mode(self):
            """Properly close study mode and return to main window"""
            if self.parent:
                session_data = {
                    'task': self.current_task,
                    'start': self.session_start,
                    'end': datetime.now(),
                    'duration': (datetime.now() - self.session_start).total_seconds() / 60,
                    'theme': self.themes[self.current_theme]['name']
                }
                try:
                    if hasattr(self.parent, 'save_study_session'):
                        self.parent.save_study_session(session_data)
                except Exception as e:
                    print(f"Error saving session: {e}")
                
                self.parent.show()
            self.close()

        def keyPressEvent(self, event):
            """Handle key presses"""
            if event.key() == Qt.Key_Escape:
                self.close_study_mode()
            elif event.key() == Qt.Key_Space:
                self.toggle_pause()
            elif event.key() == Qt.Key_Plus:
                self.adjust_time(5)
            elif event.key() == Qt.Key_T:
                self.show_theme_menu()
            else:
                super().keyPressEvent(event)
       
class NotesTab(QWidget):
    def __init__(self, parent=None, user_id=None):
        super().__init__(parent)
        self.user_id = user_id
        self.notes_dir = os.path.join(os.path.expanduser("~\Documents\ChronoLOG-Notes"), f"user_{self.user_id}")
        self.current_note_path = None
        self.notes = {}
        self.current_note_name = None
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create toolbar
        self.toolbar = QToolBar("Main Toolbar")
        self.main_layout.addWidget(self.toolbar)
        
        # File actions
        self.setup_file_actions()
        # Formatting actions
        self.setup_formatting_actions()
        # TTS actions
        self.setup_tts_actions()
        
        # Horizontal layout for sidebar and editor
        self.content_layout = QHBoxLayout()
        self.main_layout.addLayout(self.content_layout)
        
        # Sidebar with note list
        self.sidebar = QWidget()
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        
        # Note list
        self.note_list = QListWidget()
        self.note_list.itemClicked.connect(self.switch_note)
        self.note_list.itemDoubleClicked.connect(self.rename_note)
        self.note_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.note_list.customContextMenuRequested.connect(self.show_context_menu)
        self.sidebar_layout.addWidget(QLabel("Your Notes:"))
        self.sidebar_layout.addWidget(self.note_list)
        
        # Add note button
        self.add_note_btn = QPushButton("+ New Note")
        self.add_note_btn.clicked.connect(self.create_new_note)
        self.sidebar_layout.addWidget(self.add_note_btn)
        
        self.content_layout.addWidget(self.sidebar, stretch=1)
        
        # Text editor area
        self.editor_area = QWidget()
        self.editor_layout = QVBoxLayout(self.editor_area)
        self.editor_layout.setContentsMargins(0, 0, 0, 0)
        
        # Text editor
        self.text_edit = QTextEdit()
        self.editor_layout.addWidget(self.text_edit)
        self.content_layout.addWidget(self.editor_area, stretch=3)

        # Word and character count bar at the bottom of the editor
        count_bar = QHBoxLayout()
        count_bar.setContentsMargins(0, 0, 0, 0)
        count_bar.setSpacing(10)

        self.word_count_label = QLabel("Words: 0")
        self.char_count_label = QLabel("| Characters: 0")
        count_bar.addStretch()
        count_bar.addWidget(self.word_count_label)
        count_bar.addWidget(self.char_count_label)

        # Connect textChanged signal to update_counts method
        self.text_edit.textChanged.connect(self.update_counts)

        # Add count bar to editor layout
        self.editor_layout.addLayout(count_bar)
        
        self.content_layout.addWidget(self.editor_area, stretch=3)

        # Load existing notes
        self.load_all_notes()
        if self.note_list.count() > 0:
            self.note_list.setCurrentRow(0)
            self.switch_note(self.note_list.currentItem())

        mono_font = QFont("Monospace", 10)
        mono_font.setStyleHint(QFont.TypeWriter)
        self.text_edit.setFont(mono_font)
        self.note_list.setFont(mono_font)  


    def update_counts(self):
        #Calculate and display both word and character counts#
        text = self.text_edit.toPlainText()
        
        # Word count calculation (handles multiple spaces/newlines)
        word_count = len(text.split()) if text.strip() else 0
        
        # Character count (includes all characters)
        char_count = len(text)
        
        # Update labels
        self.word_count_label.setText(f"Words: {word_count}")
        self.char_count_label.setText(f" | Characters: {char_count}") 

    def setup_file_actions(self):
        # File menu button with dropdown
        self.file_menu = QMenu(self)
        
        # Save action
        save_action = QAction(QIcon.fromTheme("document-save"), "Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_note_to_file)

        self.file_menu.addAction(save_action)
        
        # Save As action
        save_as_action = QAction(QIcon.fromTheme("document-save-as"), "Save As...", self)
        save_as_action.triggered.connect(self.save_note_as)
        self.file_menu.addAction(save_as_action)
        
        # Load action
        load_action = QAction(QIcon.fromTheme("document-open"), "Load...", self)
        load_action.triggered.connect(self.load_note_from_file)
        self.file_menu.addAction(load_action)

        # Create toolbar button with menu
        file_button = QToolButton()
        file_button.setPopupMode(QToolButton.InstantPopup)
        file_button.setMenu(self.file_menu)
        file_button.setIcon(QIcon.fromTheme("folder"))
        file_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toolbar.addWidget(file_button)

    def setup_formatting_actions(self):
        # Bold action
        self.bold_action = QAction(QIcon.fromTheme("format-text-bold"), "Bold", self)
        self.bold_action.setCheckable(True)
        self.bold_action.setShortcut("Ctrl+B")
        self.bold_action.triggered.connect(self.toggle_bold)
        self.toolbar.addAction(self.bold_action)
        
        # Italic action
        self.italic_action = QAction(QIcon.fromTheme("format-text-italic"), "Italic", self)
        self.italic_action.setCheckable(True)
        self.italic_action.setShortcut("Ctrl+I")
        self.italic_action.triggered.connect(self.toggle_italic)
        self.toolbar.addAction(self.italic_action)
        
        # Underline action
        self.underline_action = QAction(QIcon.fromTheme("format-text-underline"), "Underline", self)
        self.underline_action.setCheckable(True)
        self.underline_action.setShortcut("Ctrl+U")
        self.underline_action.triggered.connect(self.toggle_underline)
        self.toolbar.addAction(self.underline_action)
        
        # Add separator
        self.toolbar.addSeparator()

    def setup_tts_actions(self):
        # TTS action
        self.tts_action = QAction(QIcon.fromTheme("media-playback-start"), "TTS", self)
        self.tts_action.triggered.connect(self.show_tts_popup)
        self.toolbar.addAction(self.tts_action)

    def toggle_bold(self):
        cursor = self.text_edit.textCursor()
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Bold if not self.bold_action.isChecked() else QFont.Normal)
        cursor.mergeCharFormat(fmt)
        self.text_edit.mergeCurrentCharFormat(fmt)
        self.bold_action.setChecked(not self.bold_action.isChecked())

    def toggle_italic(self):
        cursor = self.text_edit.textCursor()
        fmt = QTextCharFormat()
        fmt.setFontItalic(not self.italic_action.isChecked())
        cursor.mergeCharFormat(fmt)
        self.text_edit.mergeCurrentCharFormat(fmt)
        self.italic_action.setChecked(not self.italic_action.isChecked())

    def toggle_underline(self):
        cursor = self.text_edit.textCursor()
        fmt = QTextCharFormat()
        fmt.setFontUnderline(not self.underline_action.isChecked())
        cursor.mergeCharFormat(fmt)
        self.text_edit.mergeCurrentCharFormat(fmt)
        self.underline_action.setChecked(not self.underline_action.isChecked())

    def save_note_as(self):
        #Save current note with a new name
        if not self.current_note_name:
            return
            
        new_name, ok = QInputDialog.getText(self, "Save As", "Enter new name for the note:", 
                                          text=self.current_note_name)
        if ok and new_name:
            old_name = self.current_note_name
            self.notes[new_name] = self.notes.pop(old_name)
            self.current_note_name = new_name
            
            # Update list widget
            items = self.note_list.findItems(old_name, Qt.MatchExactly)
            if items:
                items[0].setText(new_name)
            
            self.save_note_to_file()
            self.update_window_title()

    def show_tts_popup(self):
        #Show a popup dialog with all TTS options#
        dialog = QDialog(self)
        dialog.setWindowTitle("Text-to-Speech Options")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        # Voice selection
        voice_group = QGroupBox("Voice Settings")
        voice_layout = QFormLayout(voice_group)
        
        self.voice_combo = QComboBox()
        try:
            voices = self.parent.tts_engine.getProperty('voices')
            for voice in voices:
                self.voice_combo.addItem(voice.name, voice)
        except:
            self.voice_combo.addItem("Default Voice")
        voice_layout.addRow("Voice:", self.voice_combo)
        
        # Speed control
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(50, 300)
        self.speed_slider.setValue(150)
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Slow"))
        speed_layout.addWidget(self.speed_slider)
        speed_layout.addWidget(QLabel("Fast"))
        voice_layout.addRow("Speed:", speed_layout)
        
        layout.addWidget(voice_group)
        
        # Control buttons
        btn_group = QGroupBox("Controls")
        btn_layout = QHBoxLayout(btn_group)
        
        self.play_btn = QPushButton(QIcon.fromTheme("media-playback-start"), "Play")
        self.play_btn.clicked.connect(lambda: self.play_note(dialog))
        btn_layout.addWidget(self.play_btn)
        
        self.stop_btn = QPushButton(QIcon.fromTheme("media-playback-stop"), "Stop")
        self.stop_btn.clicked.connect(self.stop_playback)
        btn_layout.addWidget(self.stop_btn)
        
        layout.addWidget(btn_group)
        
        # Export options
        export_group = QGroupBox("Export Options")
        export_layout = QVBoxLayout(export_group)
        
        self.convert_btn = QPushButton(QIcon.fromTheme("media-record"), "Convert to MP3")
        self.convert_btn.clicked.connect(lambda: self.convert_to_mp3(dialog))
        export_layout.addWidget(self.convert_btn)
        
        layout.addWidget(export_group)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec_()

    def play_note(self, dialog=None):
        if not self.current_note_name:
            QMessageBox.warning(self, "Warning", "No note selected!")
            return
            
        text = self.text_edit.toPlainText()
        if not text.strip():
            QMessageBox.warning(self, "Warning", "Note is empty!")
            return
            
        try:
            # Set voice if available
            if hasattr(self, 'voice_combo') and self.voice_combo.currentData():
                self.parent.tts_engine.setProperty('voice', self.voice_combo.currentData().id)
            
            # Set speech properties
            self.parent.tts_engine.setProperty('rate', self.speed_slider.value())
            self.parent.tts_engine.say(text)
            self.parent.tts_engine.runAndWait()
            
            if dialog:
                dialog.accept()  # Close the dialog after playback starts
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to play note: {str(e)}")

    def stop_playback(self):
        try:
            self.parent.tts_engine.stop()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to stop playback: {str(e)}")

    def convert_to_mp3(self, dialog=None):
        if not self.current_note_name:
            QMessageBox.warning(self, "Warning", "No note selected!")
            return
            
        text = self.text_edit.toPlainText()
        if not text.strip():
            QMessageBox.warning(self, "Warning", "Note is empty!")
            return
            
        try:
            # Create output directory if needed
            mp3_dir = os.path.join(os.path.expanduser("~\Documents\ChronoLOG-Notes"), "MP3_Notes")
            os.makedirs(mp3_dir, exist_ok=True)
            
            # Set output path
            mp3_path = os.path.join(mp3_dir, f"{self.current_note_name}.mp3")
            
            # Set voice if available
            if hasattr(self, 'voice_combo') and self.voice_combo.currentData():
                self.parent.tts_engine.setProperty('voice', self.voice_combo.currentData().id)
            
            # Set speed
            self.parent.tts_engine.setProperty('rate', self.speed_slider.value())
            
            # Save to temporary WAV file
            temp_wav = os.path.join(mp3_dir, "temp.wav")
            self.parent.tts_engine.save_to_file(text, temp_wav)
            self.parent.tts_engine.runAndWait()
            
            # Convert to MP3
            AudioSegment.from_wav(temp_wav).export(mp3_path, format="mp3")
            os.remove(temp_wav)  # Clean up
            
            QMessageBox.information(self, "Success", f"MP3 saved to:\n{mp3_path}")
            if dialog:
                dialog.accept()  # Close the dialog after export
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to convert: {str(e)}")

    def show_context_menu(self, pos):
        #Show right-click context menu with Rename and Delete options#
        item = self.note_list.itemAt(pos)
        if not item:
            return
        
        context_menu = QMenu(self)
        
        rename_action = QAction("Rename", self)
        rename_action.triggered.connect(lambda: self.rename_note(item))
        context_menu.addAction(rename_action)
        
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self.delete_note(item))
        context_menu.addAction(delete_action)
        
        context_menu.exec(self.note_list.mapToGlobal(pos))

    def apply_theme(self, dark_mode):
        #Apply theme colors based on dark/light mode#
        if dark_mode:
            self.setStyleSheet(""" 
                QWidget {
                    background-color: #1e1e1e;
                    color: #eeeeee;
                }
                QListWidget {
                    background-color: #1e1e1e;
                    color: #ffffff;
                    border: 1px solid #444;
                }
                QTextEdit {
                    background-color: #1e1e1e;
                    color: #ffffff;
                    border: 1px solid #444;
                }
                QToolBar {
                    background-color: #333333;
                    border: none;
                }
                QPushButton {
                    background-color: #444444;
                    color: #ffffff;
                    border: 1px solid #555;
                    padding: 5px;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #f8f8f8;
                    color: #000000;
                }
                QListWidget {
                    background-color: white;
                    color: #000000;
                    border: 1px solid #ddd;
                }
                QTextEdit {
                    background-color: white;
                    color: #000000;
                    border: 1px solid #ddd;
                }
                QToolBar {
                    background-color: #f0f0f0;
                    border: none;
                }
                QPushButton {
                    background-color: #f0f0f0;
                    color: #000000;
                    border: 1px solid #ccc;
                    padding: 5px;
                }
                QIcon {
                        color: #000000; 
                    }
                
            """)

    def create_new_note(self, name=None):
        #Create a new empty note with a default name and allow inline rename
        if not name:
            base_name = "New Note"
            counter = 1
            name = base_name
            while name in self.notes:
                name = f"{base_name}_{counter}"
                counter += 1

        self.notes[name] = ""
        self.current_note_name = name
        self.note_list.addItem(name)

        # Select the new note
        items = self.note_list.findItems(name, Qt.MatchExactly)
        if items:
            self.note_list.setCurrentItem(items[0])
        
        self.text_edit.clear()
        self.update_window_title()

    def save_note_to_file(self):
        #Save current note to a text file in the 'notes' folder
        if not self.current_note_name:
            return
        
        # Ensure the 'notes' directory exists
        notes_dir = os.path.join(os.path.expanduser("~\Documents\ChronoLOG-Notes"), f"user_{self.user_id}")
        if not os.path.exists(notes_dir):
            os.makedirs(notes_dir)
        
        # Construct the full path for saving the note
        file_path = os.path.join(notes_dir, self.current_note_name + ".txt")
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                plain_text = self.text_edit.toPlainText()
                f.write(plain_text)
            
            self.current_note_path = file_path
            QMessageBox.information(self.parent if hasattr(self, 'parent') else None,
                                    "Success", "Note saved successfully!")
            self.update_window_title()
        except Exception as e:
            QMessageBox.critical(self.parent if hasattr(self, 'parent') else None,
                                 "Error", f"Failed to save note: {str(e)}")

    def load_note_from_file(self):
        #Load note from a text file in the 'notes' folder
        notes_dir = os.path.join(os.path.expanduser("~\Documents\ChronoLOG-Notes"), f"user_{self.user_id}")

        # if not os.path.exists(notes_dir):
        #     QMessageBox.warning(self, "Warning", "No notes folder found!")
        #     return

        file_path, _ = QFileDialog.getOpenFileName(None,"Open Note",notes_dir,"Text Files (*.txt);;All Files (*)")

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract note name
                note_name = os.path.splitext(os.path.basename(file_path))[0]

                # Avoid collision
                original_name = note_name
                counter = 1
                while note_name in self.notes:
                    note_name = f"{original_name}_{counter}"
                    counter += 1

                self.notes[note_name] = content
                self.current_note_name = note_name
                self.note_list.addItem(note_name)
                self.text_edit.setText(content)

                self.update_window_title()
            except Exception as e:
                QMessageBox.critical(self.parent if hasattr(self, 'parent') else None,
                                    "Error", f"Failed to load note: {str(e)}")

    def save_current_note(self):
        # Ensure note name is set
        if not self.current_note_name:
            print("Error: No note name set. Cannot save.")
            return

        current_content = self.text_edit.toPlainText()
        self.notes[self.current_note_name] = current_content

        notes_dir = os.path.join(os.path.expanduser("~\Documents\ChronoLOG-Notes"), f"user_{self.user_id}")
        if not os.path.exists(notes_dir):
            os.makedirs(notes_dir)

        # Make sure the note name is safe for file system
        safe_note_name = re.sub(r'[\\/*?:"<>|]', '_', self.current_note_name)  # Removes invalid characters

        file_path = os.path.join(notes_dir, f"{safe_note_name}.txt")
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(current_content)
            self.current_note_path = file_path
            print(f"Note saved successfully: {self.current_note_path}")
        except Exception as e:
            print(f"Error saving note: {e}")

    def switch_note(self, item):
        #Switch to the selected note and display its content
        note_name = item.text()  # Get the name of the clicked note
        
        # If the note exists in the dictionary, display its content
        if note_name in self.notes:
            self.current_note_name = note_name
            self.text_edit.setPlainText(self.notes[note_name])
            self.update_window_title()
        else:
            QMessageBox.warning(self.parent if hasattr(self, 'parent') else None, "Error", "Note not found!")

    def load_all_notes(self):
        #Reload all notes from disk on startup.
        if not os.path.exists(self.notes_dir):
            return

        self.notes.clear()  # Clear existing notes to avoid duplicates
        for filename in os.listdir(self.notes_dir):
            if filename.endswith(".txt"):
                note_name = os.path.splitext(filename)[0]
                try:
                    with open(os.path.join(self.notes_dir, filename), 'r', encoding='utf-8') as f:
                        self.notes[note_name] = f.read()
                    self.note_list.addItem(note_name)  # Add to UI
                except Exception as e:
                    print(f"Failed to load note {filename}: {str(e)}")

    def rename_note(self, item=None):
        #Allow user to rename a note
        if item is None:
            item = self.note_list.currentItem()
        
        if item is None:
            return
        
        new_name, ok = QInputDialog.getText(self, "Rename Note", "Enter new name for the note:", 
                                            text=item.text())
        if ok and new_name:
            old_name = item.text()
            if new_name != old_name:
                self.notes[new_name] = self.notes.pop(old_name)
                item.setText(new_name)
                self.update_window_title()
        
    def delete_note(self, item=None):
        #Delete the selected note
        if item is None:
            item = self.note_list.currentItem()
        
        if item is None:
            return
        
        note_name = item.text()
        reply = QMessageBox.question(self, 'Delete Note', f"Are you sure you want to delete the note '{note_name}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.notes.pop(note_name, None)
            note_file_path = os.path.join(self.notes_dir, f"{note_name}.txt")  # Adjust the file extension if necessary
            if os.path.exists(note_file_path):
                os.remove(note_file_path)
            self.note_list.takeItem(self.note_list.row(item))
            self.text_edit.clear()
            self.current_note_name = None
            self.update_window_title()

    def closeEvent(self, event):
        #Save all notes when closing the application.
        self.save_all_notes_to_disk()
        super().closeEvent(event)

    def save_all_notes_to_disk(self):
        #Save every note in self.notes to individual files.
        os.makedirs(self.notes_dir, exist_ok=True)  # Ensure dir exists
        for note_name, content in self.notes.items():
            note_path = os.path.join(self.notes_dir, f"{note_name}.txt")
            with open(note_path, 'w', encoding='utf-8') as f:
                f.write(content)

    def update_window_title(self):
        """Update window title with current note info"""
        title = "Notes"
        if self.current_note_name:
            title += f" - {self.current_note_name}"
            if self.current_note_path:
                title += f" ({os.path.basename(self.current_note_path)})"
        self.setWindowTitle(title)

    # Text formatting functions
    def toggle_bold(self):
        self.text_edit.setFontWeight(QFont.Bold if self.bold_action.isChecked() else QFont.Normal)

    def toggle_italic(self):
        self.text_edit.setFontItalic(self.italic_action.isChecked())

    def toggle_underline(self):
        self.text_edit.setFontUnderline(self.underline_action.isChecked())

    def keyPressEvent(self, event):
        # Handle Ctrl+S for save
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_S:
            self.save_note_to_file()
        else:
            super().keyPressEvent(event)

# class notifications:
#     def __init__(self):
#         logging.info("[Notifications] Notifications initialized.")

#     def upcoming_task(self,task):
#         if core
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setWindowIcon(QIcon("Project - ChronoLOG/assets/AppIcon.png"))
    window = MainWindow.StudyPlanner()
    window.show()
    sys.exit(app.exec())
"""
def showtext(text):
    msg = QMessageBox()
    msg.setWindowTitle("Message")
    msg.setText(text)
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()"""
#remove this later
# PySide6 color and gradient style reference for your app

# --- Color Palette ---
# Dark Mode:
#   Text:         #eeeeee
#   Background:   #1e1e1e
#   Button BG:    #444444
#   Button Text:  #ffffff

# Light Mode:
#   Text:         #000000
#   Background:   #f8f8f8
#   Button BG:    #f0f0f0
#   Button Text:  #000000

# --- Example QSS for PySide6 ---

# Dark mode stylesheet
DARK_MODE_QSS = """
QWidget {
    background-color: #1e1e1e;
    color: #eeeeee;
}
QPushButton {
    background-color: #444444;
    color: #ffffff;
    border: 1px solid #555;
    padding: 6px 12px;
    border-radius: 4px;
}
QPushButton:hover {
    background-color: #555555;
}
"""

# Light mode stylesheet
LIGHT_MODE_QSS = """
QWidget {
    background-color: #f8f8f8;
    color: #000000;
}
QPushButton {
    background-color: #f0f0f0;
    color: #000000;
    border: 1px solid #ccc;
    padding: 6px 12px;
    border-radius: 4px;
}
QPushButton:hover {
    background-color: #e0e0e0;
}
"""

# --- Gradient backgrounds in PySide6 QSS ---

# Subtle overlay gradient for dark mode:
DARK_GRADIENT_QSS = """
QWidget#gradientBg {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(255,255,255,0.08),
        stop:1 rgba(0,0,0,0.12)
    );
}
"""

# Multi-color gradient background (use on a custom QWidget with objectName "rainbowBg"):
RAINBOW_GRADIENT_QSS = """
QWidget#rainbowBg {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(255,0,0,0.8),
        stop:0.5 rgba(0,255,0,0.8),
        stop:1 rgba(0,0,255,0.8)
    );
}
"""

# To apply a gradient background to a widget:
#   widget.setObjectName("gradientBg")
#   widget.setStyleSheet(DARK_GRADIENT_QSS)

# Or for rainbow:
#   widget.setObjectName("rainbowBg")
#   widget.setStyleSheet(RAINBOW_GRADIENT_QSS)

# You can also combine these styles with the main stylesheet