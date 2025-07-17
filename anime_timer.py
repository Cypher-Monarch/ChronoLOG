# === ANIME STUDY TIMER (PySide6 version with Character Selector, Fullscreen Character, G-Key Theme Toggle, Coins UI, and Shop) ===

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QLineEdit, QMessageBox, QStackedWidget, QComboBox, QListWidget, QListWidgetItem
)

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QFont, QPainter, QColor, QPalette, QLinearGradient, QBrush, QKeySequence, QShortcut

import json, os, time, sys

# === CONFIG ===
DATA_FILE = "userdata.json"
CHARACTERS = {
    "Zenitsu": {"img": "zenitsu.png", "locked": False},
    "Jinwoo": {"img": "jinwoo.png", "locked": True, "price": 1000},
    "Gojo": {"img": "gojo.png", "locked": True, "price": 1500}
}
QUOTES = {
    "Zenitsu": "It's time to delve into the sleep of focus.",
    "Jinwoo": "Arise, giving up is not an option.",
    "Gojo": "You're weak. As expected."
}

THEMES = [
    {"gradient": ["#1a1a2e", "#16213e"], "accent": "#e94560"},
    {"gradient": ["#0f0c29", "#302b63"], "accent": "#f857a6"},
    {"gradient": ["#20002c", "#cbb4d4"], "accent": "#f8ff00"},
    {"gradient": ["#1f4037", "#99f2c8"], "accent": "#ff6f61"},
    {"gradient": ["#614385", "#516395"], "accent": "#f5e625"},
    {"gradient": ["#4776e6", "#8e54e9"], "accent": "#ffd700"},
    {"gradient": ["#5c258d", "#4389a2"], "accent": "#f4c4f3"},
    {"gradient": ["#3a7bd5", "#00d2ff"], "accent": "#ff5e62"},
    {"gradient": ["#1e3c72", "#2a5298"], "accent": "#ff7e5f"},
    {"gradient": ["#141e30", "#243b55"], "accent": "#f79d00"}
]

# === LOAD / SAVE ===
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"coins": 0, "unlocked": ["Zenitsu"]}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(user_data, f, indent=4)

user_data = load_data()
selected_character = user_data["unlocked"][0]

# === Shop Screen ===
class ShopScreen(QWidget):
    def __init__(self, return_home):
        super().__init__()
        self.return_home = return_home
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        self.setStyleSheet("background-color: #0a0a0a;")

        title = QLabel("🛒 Character Shop", alignment=Qt.AlignCenter)
        title.setStyleSheet("color: white; font-size: 26px; font-weight: bold;")
        layout.addWidget(title)

        self.coins_label = QLabel(f"Coins: {user_data['coins']}", alignment=Qt.AlignCenter)
        self.coins_label.setStyleSheet("color: gold; font-size: 18px;")
        layout.addWidget(self.coins_label)

        from PySide6.QtWidgets import QGridLayout

        self.char_grid = QGridLayout()
        self.char_grid.setSpacing(20)

        row = 0
        col = 0
        for name, data in CHARACTERS.items():
            if name not in user_data["unlocked"]:
                card = QWidget()
                card_layout = QVBoxLayout(card)
                card.setStyleSheet("background-color: #1a1a1a; border: 2px solid #444; border-radius: 10px; transition: 0.3s;")
                card.setCursor(Qt.PointingHandCursor)

                image_label = QLabel()
                pixmap = QPixmap(data["img"]).scaled(180, 240, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                if data.get("locked", False):
                    temp = QPixmap(pixmap.size())
                    temp.fill(Qt.transparent)
                    painter = QPainter(temp)
                    painter.setOpacity(0.4)
                    painter.drawPixmap(0, 0, pixmap)
                    painter.end()
                    pixmap = temp
                image_label.setPixmap(pixmap)
                image_label.setAlignment(Qt.AlignCenter)

                price_label = QLabel(f"{name}\n{data['price']} coins")

                price_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
                price_label.setAlignment(Qt.AlignCenter)

                buy_button = QPushButton(f"Unlock {name}")
                buy_button.setStyleSheet("background-color: #e94560; color: white; padding: 6px; border-radius: 5px;")
                buy_button.clicked.connect(lambda _, n=name: self.unlock_character(n))

                card_layout.addWidget(image_label)
                card_layout.addWidget(price_label)
                card_layout.addWidget(buy_button)
                self.char_grid.addWidget(card, row, col)

                col += 1
                if col >= 2:
                    col = 0
                    row += 1

        layout.addLayout(self.char_grid)

        back_btn = QPushButton("⬅ Back to Home")
        back_btn.clicked.connect(self.return_home)
        layout.addWidget(back_btn)

    def unlock_character(self, name):

      char = CHARACTERS.get(name)
      if user_data["coins"] >= char["price"]:
            user_data["coins"] -= char["price"]
            user_data["unlocked"].append(name)
            save_data()
            QMessageBox.information(self, "Unlocked!", f"{name} is now available!")
            self.return_home()
      else:
            QMessageBox.warning(self, "Not enough coins", "You need more coins to unlock this character.")
     
    


# === TimerScreen, HomeScreen, MainWindow with Shop Navigation ===

class TimerScreen(QWidget):
    def __init__(self, focus_seconds, break_seconds, return_home):
        super().__init__()
        self.focus_seconds = focus_seconds
        self.break_seconds = break_seconds
        self.return_home = return_home
        self.is_focus = True
        self.time_left = focus_seconds
        self.use_gradient = False
        self.current_theme = 0

        self.setLayout(QVBoxLayout())
        self.setStyleSheet("background-color: #0a0a0a;")

        self.timer_label = QLabel("00:00")
        self.timer_label.setFont(QFont("Courier", 64))
        self.timer_label.setStyleSheet("color: white;")
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.layout().addWidget(self.timer_label)

        self.note_label = QLabel("Apps are locked during focus time.")
        self.note_label.setStyleSheet("color: red;")
        self.note_label.setAlignment(Qt.AlignCenter)
        self.layout().addWidget(self.note_label)

        self.stop_btn = QPushButton("STOP")
        self.stop_btn.setStyleSheet("background-color: #111; color: white; padding: 10px;")
        self.stop_btn.clicked.connect(self.stop_timer)
        self.layout().addWidget(self.stop_btn)

        self.qtimer = QTimer()
        self.qtimer.timeout.connect(self.update_timer)
        self.qtimer.start(1000)

        QShortcut(QKeySequence("G"), self).activated.connect(self.toggle_background_mode)

    def toggle_background_mode(self):
        self.use_gradient = not self.use_gradient
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.use_gradient:
            theme = THEMES[self.current_theme % len(THEMES)]
            grad = QLinearGradient(0, 0, 0, self.height())
            grad.setColorAt(0, QColor(theme["gradient"][0]))
            grad.setColorAt(1, QColor(theme["gradient"][1]))
            painter.fillRect(self.rect(), grad)
        else:
            painter.drawPixmap(self.rect(), QPixmap(CHARACTERS[selected_character]["img"]))

    def update_timer(self):
        mins, secs = divmod(self.time_left, 60)
        self.timer_label.setText(f"{mins:02}:{secs:02}")
        if self.time_left > 0:
            self.time_left -= 1
        else:
            self.qtimer.stop()
            if self.is_focus:
                earned = self.focus_seconds // 60 * 10
                user_data["coins"] += earned
                save_data()
                QMessageBox.information(self, "Session Complete", f"+{earned} coins earned")
                self.is_focus = False
                self.time_left = self.break_seconds
                self.qtimer.start(1000)
            else:
                QMessageBox.information(self, "Break Over", "Back to training...")
                self.return_home()

    def stop_timer(self):
        quote = QUOTES.get(selected_character, "Stay strong.")
        reply = QMessageBox.question(
    self, "Leave Focus Mode?",
    f"{selected_character} says:\n\n\"{quote}\"\n\nDo you really want to stop?",
    QMessageBox.Yes | QMessageBox.No
)


        if reply == QMessageBox.Yes:
            self.qtimer.stop()
            self.return_home()

class HomeScreen(QWidget):
    def __init__(self, start_callback, go_to_shop):
        super().__init__()
        self.start_callback = start_callback
        self.go_to_shop = go_to_shop
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background-color: #0a0a0a;")

        self.bg_label = QLabel(self)
        self.bg_label.setPixmap(QPixmap("background.jpg").scaled(600, 650, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        self.bg_label.setGeometry(0, 0, 600, 650)
        self.bg_label.lower()

        self.title = QLabel("✨ Anime Focus Timer ✨", alignment=Qt.AlignCenter)
        self.title.setStyleSheet("color: white; font-size: 28px; font-weight: bold;")
        layout.addWidget(self.title)

        self.coins_label = QLabel(f"🪙 Coins: {user_data['coins']}", alignment=Qt.AlignCenter)
        self.coins_label.setStyleSheet("color: gold; font-size: 20px;")
        layout.addWidget(self.coins_label)

        layout.addWidget(QLabel("Set Focus Time (min)", styleSheet="color: white; font-size: 16px;"))
        self.focus_input = QLineEdit("25")
        self.focus_input.setStyleSheet("font-size: 16px; padding: 5px;")
        layout.addWidget(self.focus_input)

        layout.addWidget(QLabel("Set Break Time (min)", styleSheet="color: white; font-size: 16px;"))
        self.break_input = QLineEdit("5")
        self.break_input.setStyleSheet("font-size: 16px; padding: 5px;")
        layout.addWidget(self.break_input)

        layout.addWidget(QLabel("Select Character", styleSheet="color: white; font-size: 16px;"))
        self.character_selector = QComboBox()
        self.character_selector.setStyleSheet("font-size: 16px; padding: 4px;")
        for char in user_data["unlocked"]:
            self.character_selector.addItem(char)
        self.character_selector.currentTextChanged.connect(self.update_character_preview)
        layout.addWidget(self.character_selector)

        self.char_preview = QLabel()
        self.char_preview.setAlignment(Qt.AlignCenter)
        self.char_preview.setPixmap(QPixmap(CHARACTERS[selected_character]["img"]).scaled(200, 240, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        layout.addWidget(self.char_preview)

        start_btn = QPushButton("▶ Start Focus")
        start_btn.setStyleSheet("background-color: #28a745; color: white; font-size: 18px; padding: 10px; border-radius: 6px;")
        start_btn.clicked.connect(self.start_focus)
        layout.addWidget(start_btn)

        shop_btn = QPushButton("🛒 Open Shop")
        shop_btn.setStyleSheet("background-color: #ffc107; color: black; font-size: 18px; padding: 10px; border-radius: 6px;")
        shop_btn.clicked.connect(self.go_to_shop)
        layout.addWidget(shop_btn)

    def update_character_preview(self, name):
        if name in CHARACTERS:
            self.char_preview.setPixmap(QPixmap(CHARACTERS[name]["img"]).scaled(200, 240, Qt.KeepAspectRatio, Qt.SmoothTransformation))

      
        if name in CHARACTERS:
            self.char_preview.setPixmap(QPixmap(CHARACTERS[name]["img"]).scaled(200, 240, Qt.KeepAspectRatio, Qt.SmoothTransformation))
    def start_focus(self):
        global selected_character
        selected_character = self.character_selector.currentText()
        try:
            f = int(self.focus_input.text()) * 60
            b = int(self.break_input.text()) * 60
            self.start_callback(f, b)
        except ValueError:
            QMessageBox.warning(self, "Invalid input", "Please enter valid numbers.")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Anime Focus Timer")
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.home = HomeScreen(self.start_timer, self.show_shop)
        self.stack.addWidget(self.home)

    def start_timer(self, focus, brk):
        self.timer_screen = TimerScreen(focus, brk, self.show_home)
        self.stack.addWidget(self.timer_screen)
        self.stack.setCurrentWidget(self.timer_screen)

    def show_home(self):
        self.stack.setCurrentWidget(self.home)
        self.stack.removeWidget(self.timer_screen)
        self.home.coins_label.setText(f"Coins: {user_data['coins']}")
        self.home.character_selector.clear()
        for char in user_data["unlocked"]:
            self.home.character_selector.addItem(char)

    def show_shop(self):
        self.shop_screen = ShopScreen(self.show_home)
        self.stack.addWidget(self.shop_screen)
        self.stack.setCurrentWidget(self.shop_screen)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(600, 650)
    window.show()
    sys.exit(app.exec())
