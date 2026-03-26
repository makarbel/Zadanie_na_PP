import random
from PyQt6.QtWidgets import QWidget, QGridLayout, QPushButton
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize

class ChallengeCaptchaWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid = QGridLayout(self)
        self.image_paths = ["1.png", "2.png", "3.png", "4.png"]
        self.current_order = list(range(4))
        self.buttons = []
        self.first_selected_idx = None 
        self._init_ui()

    def _init_ui(self):
        for i in range(4):
            btn = QPushButton()
            btn.setFixedSize(110, 110)
            btn.setIconSize(QSize(100, 100))
            btn.clicked.connect(lambda ch, idx=i: self._on_click(idx))
            self.grid.addWidget(btn, i // 2, i % 2)
            self.buttons.append(btn)
        self.reset_captcha()

    def reset_captcha(self):
        self.first_selected_idx = None
        for b in self.buttons: 
            b.setStyleSheet("")
        random.shuffle(self.current_order)
        if self.is_correct(): 
            return self.reset_captcha()
        self._update_icons()

    def _on_click(self, idx):
        if self.first_selected_idx is None:
            self.first_selected_idx = idx
            self.buttons[idx].setStyleSheet("border: 3px solid #3498db;")
        else:
            i1, i2 = self.first_selected_idx, idx
            self.current_order[i1], self.current_order[i2] = self.current_order[i2], self.current_order[i1]
            self.buttons[i1].setStyleSheet("")
            self.first_selected_idx = None
            self._update_icons()

    def _update_icons(self):
        for i, img_idx in enumerate(self.current_order):
            self.buttons[i].setIcon(QIcon(self.image_paths[img_idx]))

    def is_correct(self):
        return self.current_order == [0, 1, 2, 3]