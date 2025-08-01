import sys
import random
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QLabel, 
                              QPushButton, QHBoxLayout, QWidget)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import (QFont, QPalette, QColor, QLinearGradient, 
                          QBrush, QKeySequence, QShortcut)

class DarkStudyTimer(QMainWindow):
    def __init__(self):
        super().__init__()
        # Timer settings
        self.study_time = 25 * 60
        self.time_left = self.study_time
        self.is_running = False
        
        # Dark gradient themes
        self.themes = [
            {"gradient": ["#1a1a2e", "#16213e"], "accent": "#e94560"},  # Navy/Crimson
            {"gradient": ["#0f0c29", "#302b63"], "accent": "#f857a6"},  # Purple/Pink
            {"gradient": ["#000000", "#434343"], "accent": "#00dbde"},  # Black/Cyan
            {"gradient": ["#0f2027", "#203a43"], "accent": "#000000"},  # Teal/Amber
            {"gradient": ["#1e0010", "#3a1c1c"], "accent": "#c31432"}   # Blood Red
        ]
        self.current_theme = 0
        
        # Quotes
        self.quotes = [
            "The darkness is where focus thrives",
            "No distractions. Only progress.",
            "Burn bright in the shadows",
            "Night owls finish first",
            "Code like the world is asleep"
        ]
        
        # UI Setup
        self.setWindowTitle("Midnight Focus Timer")
        self.showFullScreen()
        self.setCursor(Qt.BlankCursor)
        self.setup_ui()
        self.apply_theme()
        
        # ESC to exit
        QShortcut(QKeySequence("Esc"), self).activated.connect(self.toggle_fullscreen)
        
        # Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Timer Display
        self.time_label = QLabel("25:00")
        self.time_label.setFont(QFont("consolas", 120, QFont.Bold))
        self.time_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.time_label)
        
        # Quote
        self.quote_label = QLabel(random.choice(self.quotes))
        self.quote_label.setFont(QFont("consolas", 20))
        self.quote_label.setAlignment(Qt.AlignCenter)
        self.quote_label.setWordWrap(True)
        layout.addWidget(self.quote_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.theme_btn = QPushButton("🌘 Theme")
        self.theme_btn.clicked.connect(self.cycle_theme)
        
        self.add5_btn = QPushButton("+5 Min")
        self.add5_btn.clicked.connect(lambda: self.add_time(300))
        
        self.start_btn = QPushButton("▶ Start")
        self.start_btn.clicked.connect(self.toggle_timer)
        
        btn_layout.addWidget(self.theme_btn)
        btn_layout.addWidget(self.add5_btn)
        btn_layout.addWidget(self.start_btn)
        layout.addLayout(btn_layout)
    
    def apply_theme(self):
        palette = QPalette()
        theme = self.themes[self.current_theme]
        
        # Gradient background
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(theme["gradient"][0]))
        gradient.setColorAt(1, QColor(theme["gradient"][1]))
        palette.setBrush(QPalette.Window, QBrush(gradient))
        
        # Accent colors
        accent = QColor(theme["accent"])
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.ButtonText, accent)
        
        self.setPalette(palette)
        
        # Transparent button style
        button_style = f"""
            QPushButton {{
                background: transparent;
                border: 2px solid {accent.name()};
                border-radius: 8px;
                padding: 10px;
                font-family: "consolas";
                font-size: 16px;
                color: {accent.name()};
                min-width: 100px;
            }}
            QPushButton:hover {{
                background: rgba({accent.red()}, {accent.green()}, {accent.blue()}, 0.1);
            }}
            QPushButton:pressed {{
                background: rgba({accent.red()}, {accent.green()}, {accent.blue()}, 0.2);
            }}
        """
        for btn in [self.theme_btn, self.add5_btn, self.start_btn]:
            btn.setStyleSheet(button_style)
    
    def cycle_theme(self):
        self.current_theme = (self.current_theme + 1) % len(self.themes)
        self.apply_theme()
    
    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
            self.setCursor(Qt.ArrowCursor)
        else:
            self.showFullScreen()
            self.setCursor(Qt.BlankCursor)
    
    def toggle_timer(self):
        if self.is_running:
            self.timer.stop()
            self.start_btn.setText("▶ Start")
        else:
            self.timer.start(1000)
            self.start_btn.setText("⏸ Pause")
        self.is_running = not self.is_running
    
    def update_timer(self):
        self.time_left -= 1
        if self.time_left <= 0:
            self.timer.stop()
            self.time_label.setText("Done!")
            self.quote_label.setText("Step into the light")
        else:
            mins, secs = divmod(self.time_left, 60)
            self.time_label.setText(f"{mins:02}:{secs:02}")
            if self.time_left % 30 == 0:
                self.quote_label.setText(random.choice(self.quotes))
    
    def add_time(self, seconds):
        self.time_left += seconds
        mins, secs = divmod(self.time_left, 60)
        self.time_label.setText(f"{mins:02}:{secs:02}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = DarkStudyTimer()
    sys.exit(app.exec()) 