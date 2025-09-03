import sys
import random
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QLabel, 
                              QPushButton, QHBoxLayout, QWidget)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import (QFont, QPalette, QColor, QLinearGradient, 
                          QBrush, QKeySequence, QShortcut)

class UltimateStudyTimer(QMainWindow):
    def __init__(self):
        super().__init__()
        # Timer settings
        self.study_time = 25 * 60
        self.time_left = self.study_time
        self.is_running = False
        self.gradient_enabled = True
        self.current_theme = 0
        
        # Theme system
        self.themes = [
    {"gradient": ["#4776e6", "#8e54e9"], "solid": "#4776e6", "accent": "#ffd700"},
    {"gradient": ["#0d0d0d", "#1a1a1a"], "solid": "#0d0d0d", "accent": "#ffcc00"},
    {"gradient": ["#1a1a2e", "#16213e"], "solid": "#1a1a2e", "accent": "#e94560"},
    {"gradient": ["#0f0c29", "#302b63"], "solid": "#0f0c29", "accent": "#f857a6"},
    {"gradient": ["#000000", "#434343"], "solid": "#121212", "accent": "#00dbde"},
    {"gradient": ["#0f2027", "#203a43"], "solid": "#0f2027", "accent": "#ffd89b"},
    {"gradient": ["#1e0010", "#3a1c1c"], "solid": "#1e0010", "accent": "#c31432"},
    {"gradient": ["#23074d", "#cc5333"], "solid": "#23074d", "accent": "#e8c547"},
    {"gradient": ["#1f4037", "#99f2c8"], "solid": "#1f4037", "accent": "#f857a6"},
    {"gradient": ["#4b79cf", "#283e51"], "solid": "#283e51", "accent": "#f5af19"},
    {"gradient": ["#20002c", "#cbb4d4"], "solid": "#20002c", "accent": "#f8ff00"},
    {"gradient": ["#136a8a", "#267871"], "solid": "#136a8a", "accent": "#f39c12"},
    {"gradient": ["#5c258d", "#4389a2"], "solid": "#5c258d", "accent": "#f4c4f3"},
    {"gradient": ["#1d4350", "#a43931"], "solid": "#1d4350", "accent": "#fdc830"},
    {"gradient": ["#3a7bd5", "#00d2ff"], "solid": "#3a7bd5", "accent": "#ff5e62"},
    {"gradient": ["#42275a", "#734b6d"], "solid": "#42275a", "accent": "#f8c537"},
    {"gradient": ["#141e30", "#243b55"], "solid": "#141e30", "accent": "#f79d00"},
    {"gradient": ["#1a2980", "#26d0ce"], "solid": "#1a2980", "accent": "#ff758c"},
    {"gradient": ["#ff4e50", "#f9d423"], "solid": "#ff4e50", "accent": "#3a1c71"},
    {"gradient": ["#614385", "#516395"], "solid": "#614385", "accent": "#f5e625"},
    {"gradient": ["#1e3c72", "#2a5298"], "solid": "#1e3c72", "accent": "#ff7e5f"}
       ]
        
        # Quotes
        self.quotes = [
            "The darkness is where focus thrives",
            "No distractions. Only progress.",
            "Burn bright in the shadows",
            "Night owls finish first",
            "Code like the world is asleep"
        ]
        
        # UI Setup
        self.setWindowTitle("Nocturnal Focus Timer")
        self.resize(800, 600)
        self.setup_ui()
        self.apply_theme()
        
        # Shortcuts
        QShortcut(QKeySequence("Esc"), self).activated.connect(self.toggle_fullscreen)
        QShortcut(QKeySequence("G"), self).activated.connect(self.toggle_gradient)
        
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
        self.time_label.setFont(QFont("Courier New", 120, QFont.Bold))
        self.time_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.time_label)
        
        # Quote
        self.quote_label = QLabel(random.choice(self.quotes))
        self.quote_label.setFont(QFont("Arial", 20))
        self.quote_label.setAlignment(Qt.AlignCenter)
        self.quote_label.setWordWrap(True)
        layout.addWidget(self.quote_label)
        
        # Control Buttons
        btn_layout = QHBoxLayout()
        
        self.theme_btn = QPushButton("🌓 Theme")
        self.theme_btn.clicked.connect(self.cycle_theme)
        
        self.gradient_btn = QPushButton("🌈 Gradient")
        self.gradient_btn.clicked.connect(self.toggle_gradient)
        
        self.add5_btn = QPushButton("+5 Min")
        self.add5_btn.clicked.connect(lambda: self.add_time(300))
        
        self.start_btn = QPushButton("▶ Start")
        self.start_btn.clicked.connect(self.toggle_timer)
        
        btn_layout.addWidget(self.theme_btn)
        btn_layout.addWidget(self.gradient_btn)
        btn_layout.addWidget(self.add5_btn)
        btn_layout.addWidget(self.start_btn)
        layout.addLayout(btn_layout)
    
    def apply_theme(self):
        palette = QPalette()
        theme = self.themes[self.current_theme]
        
        if self.gradient_enabled:
            gradient = QLinearGradient(0, 0, 0, self.height())
            gradient.setColorAt(0, QColor(theme["gradient"][0]))
            gradient.setColorAt(1, QColor(theme["gradient"][1]))
            palette.setBrush(QPalette.Window, QBrush(gradient))
        else:
            palette.setColor(QPalette.Window, QColor(theme["solid"]))
        
        accent = QColor(theme["accent"])
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.ButtonText, accent)
        
        self.setPalette(palette)
        
        # Button styling
        button_style = f"""
            QPushButton {{
                background: transparent;
                border: 2px solid {accent.name()};
                border-radius: 8px;
                padding: 10px;
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
        for btn in [self.theme_btn, self.gradient_btn, self.add5_btn, self.start_btn]:
            btn.setStyleSheet(button_style)
        
        self.gradient_btn.setText("🌈 Gradient ON" if self.gradient_enabled else "🌈 Gradient OFF")
    
    def toggle_gradient(self):
        self.gradient_enabled = not self.gradient_enabled
        self.apply_theme()
    
    def cycle_theme(self):
        self.current_theme = (self.current_theme + 1) % len(self.themes)
        self.apply_theme()
    
    def toggle_fullscreen(self):
        self.showFullScreen() if not self.isFullScreen() else self.showNormal()
    
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
    window = UltimateStudyTimer()
    window.show()
    sys.exit(app.exec())
