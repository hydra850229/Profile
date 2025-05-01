import os
import shutil
from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QLineEdit, QFileDialog,
    QVBoxLayout, QHBoxLayout, QDateTimeEdit, QMessageBox, QFrame, QComboBox
)
from PySide6.QtCore import QDateTime

VIDEO_EXTS = {'.mp4', '.mov', '.avi', '.mkv'}
AUDIO_EXTS = {'.mp3', '.wav', '.aac', '.flac'}

class Archiver(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("歸檔器")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("File"))

        # From 路徑
        from_layout = QHBoxLayout()
        from_layout.addWidget(QLabel("From"))
        self.src_input = QLineEdit()
        from_layout.addWidget(self.src_input)
        src_btn = QPushButton("瀏覽")
        src_btn.clicked.connect(self.browse_source)
        from_layout.addWidget(src_btn)
        layout.addLayout(from_layout)

        # To 路徑
        to_layout = QHBoxLayout()
        to_layout.addWidget(QLabel("To"))
        self.dst_input = QLineEdit()
        to_layout.addWidget(self.dst_input)
        dst_btn = QPushButton("瀏覽")
        dst_btn.clicked.connect(self.browse_target)
        to_layout.addWidget(dst_btn)
        layout.addLayout(to_layout)

        layout.addWidget(QLabel("Range"))

        # 時間範圍
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("From"))
        self.start_dt = QDateTimeEdit()
        self.start_dt.setDateTime(QDateTime.currentDateTime())
        time_layout.addWidget(self.start_dt)
        time_layout.addWidget(QLabel("to"))
        self.end_dt = QDateTimeEdit()
        self.end_dt.setDateTime(QDateTime.currentDateTime())
        time_layout.addWidget(self.end_dt)
        layout.addLayout(time_layout)

        # 分隔線（含上下空行）
        layout.addSpacing(10)
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)
        layout.addSpacing(10)

        # 專案選擇或輸入
        self.project_input = QComboBox()
        self.project_input.setEditable(True)
        self.project_input.setPlaceholderText("輸入新專案名稱或從下拉中選擇")
        layout.addWidget(self.project_input)

        # 開始按鈕
        start_btn = QPushButton("Start")
        start_btn.clicked.connect(self.start_archiving)
        layout.addWidget(start_btn)

        self.setLayout(layout)

    def browse_source(self):
        folder = QFileDialog.getExistingDirectory(self, "選擇來源資料夾")
        if folder:
            self.src_input.setText(folder)

    def browse_target(self):
        folder = QFileDialog.getExistingDirectory(self, "選擇目標資料夾")
        if folder:
            self.dst_input.setText(folder)
            self.update_project_dropdown(folder)

    def update_project_dropdown(self, base_path):
        self.project_input.clear()
        try:
            for name in os.listdir(base_path):
                folder = os.path.join(base_path, name)
                if not os.path.isdir(folder):
                    continue
                subfolders = ["01-Project", "02-Video", "03-Render", "04-Audio", "05-Export"]
                if all(os.path.isdir(os.path.join(folder, sf)) for sf in subfolders):
                    self.project_input.addItem(name)
        except Exception as e:
            QMessageBox.warning(self, "錯誤", f"讀取專案清單失敗：{e}")

    def start_archiving(self):
        src = self.src_input.text().strip()
        dst_root = self.dst_input.text().strip()
        proj_name = self.project_input.currentText().strip()

        if not os.path.isdir(src) or not os.path.isdir(dst_root) or not proj_name:
            QMessageBox.warning(self, "錯誤", "請確認來源、目標與專案名稱皆已填寫")
            return

        start_dt = self.start_dt.dateTime().toPython()
        end_dt = self.end_dt.dateTime().toPython()

        base_path = os.path.join(dst_root, proj_name)
        is_new = not os.path.exists(base_path)

        os.makedirs(base_path, exist_ok=True)
        for folder in ["01-Project", "02-Video", "03-Render", "04-Audio", "05-Export", "06-Other"]:
            os.makedirs(os.path.join(base_path, folder), exist_ok=True)

        count = 0
        for file in os.listdir(src):
            full_path = os.path.join(src, file)
            if not os.path.isfile(full_path):
                continue
            file_time = datetime.fromtimestamp(os.path.getmtime(full_path))
            if not (start_dt <= file_time <= end_dt):
                continue

            ext = Path(file).suffix.lower()
            if ext in VIDEO_EXTS:
                dest = os.path.join(base_path, "02-Video", file)
            elif ext in AUDIO_EXTS:
                dest = os.path.join(base_path, "04-Audio", file)
            else:
                dest = os.path.join(base_path, "06-Other", file)

            shutil.move(full_path, dest)
            count += 1

        QMessageBox.information(self, "完成", f"已成功歸檔 {count} 個檔案！")

if __name__ == '__main__':
    app = QApplication([])
    window = Archiver()
    window.resize(600, 340)
    window.show()
    app.exec()