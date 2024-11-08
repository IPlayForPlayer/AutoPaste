import sys
import time
from itertools import repeat

import pyautogui
import keyboard
import pyperclip
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QScrollArea, QLineEdit, QLabel
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("自动粘贴工具")
        self.setFixedSize(QSize(600, 400))
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        left_layout = QVBoxLayout()
        main_layout.addLayout(left_layout)

        self.add_layer_button = QPushButton("增加拷贝层")
        self.remove_layer_button = QPushButton("删除拷贝层")
        left_layout.addWidget(self.add_layer_button)
        left_layout.addWidget(self.remove_layer_button)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        left_layout.addWidget(self.scroll_area)

        self.scroll_content = QWidget()
        self.scroll_area.setWidget(self.scroll_content)
        self.scroll_layout = QVBoxLayout(self.scroll_content)

        self.add_layer_button.clicked.connect(self.add_copy_layer)
        self.remove_layer_button.clicked.connect(self.remove_copy_layer)

        self.input_fields = []

        right_layout = QVBoxLayout()
        main_layout.addLayout(right_layout)

        self.select_position_button = QPushButton("选择点击坐标")
        right_layout.addWidget(self.select_position_button)

        self.interval_label = QLabel("点击间隔 (ms):")
        right_layout.addWidget(self.interval_label)

        self.interval_input = QLineEdit()
        self.interval_input.setPlaceholderText("例如：500")
        right_layout.addWidget(self.interval_input)

        self.execute_button = QPushButton("执行批量粘贴")
        right_layout.addWidget(self.execute_button)

        right_layout.addStretch()

        self.tip_label = QLabel(

            "在点击“选择点击坐标”按钮后，\n请将光标移动到要点击的位置，"

            "比如“发送”按键，然后按下键盘上的\nX键来锁定点击坐标。\n"

            "如果想在锁定坐标的情况下选取其他坐标，您可以\n再次点击该按钮来进行相同的操作覆盖坐标。\n"

            "在执行点击期间，请不要移动光标，在开始点击之前\n您可以先点击一下预粘贴的输入框。\n"

            "点击间隔是指两次点击之间的\n间隔时间，单位是毫秒。\n"

            "如果您不确定间隔时间应该设定成多少，可以尝试\n设置一个较小的值，然后观察粘贴效果。\n"

            "如果粘贴效果不理想，可以\n适当调整间隔时间。\n"

        )
        right_layout.addWidget(self.tip_label)

        self.select_position_button.clicked.connect(self.select_click_position)
        self.execute_button.clicked.connect(self.execute_batch_paste)

        self.click_position = None

    def add_copy_layer(self):
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)

        label = QLabel(str(len(self.input_fields) + 1))
        row_layout.addWidget(label)

        input_field = QLineEdit()
        row_layout.addWidget(input_field)

        self.scroll_layout.addWidget(row_widget)
        self.input_fields.append((label, input_field))

    def remove_copy_layer(self):
        if self.input_fields:
            label, input_field = self.input_fields.pop()
            self.scroll_layout.removeWidget(label.parentWidget())
            label.parentWidget().deleteLater()

        for index, (label, _) in enumerate(self.input_fields, start=1):
            label.setText(str(index))

    def select_click_position(self):
        self.setCursor(QCursor(Qt.CrossCursor))

        keyboard.on_press_key("x", lambda _: self.on_key_press())

    def on_key_press(self):
        self.click_position = pyautogui.position()

        self.setCursor(Qt.ArrowCursor)

        keyboard.unhook_all()

        print(f"选择的点击坐标: {self.click_position}")

        self.select_position_button.setText(f"坐标已选: {self.click_position}")

    def execute_batch_paste(self):
        if not self.click_position:
            self.select_position_button.setText("请先选择点击坐标")
            return

        try:
            interval = int(self.interval_input.text())
            if interval < 0:
                raise ValueError
        except ValueError:
            self.interval_input.setText("请输入有效的间隔时间")
            return

        paste_texts = [input_field.text() for _, input_field in self.input_fields]

        for text in paste_texts:
         pyperclip.copy(text)

         pyautogui.click(self.click_position)

         pyautogui.hotkey("ctrl", "v")

        pyautogui.press("enter")

        repeat(pyautogui.press("enter"), len(paste_texts) - 1)

        time.sleep(interval / 1000.0)

        self.execute_button.setText("批量粘贴")
        print("批量粘贴完成")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())