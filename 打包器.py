import sys
import subprocess
import os
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QFileDialog,
    QVBoxLayout, QHBoxLayout, QLineEdit, QMessageBox
)
from PySide6.QtCore import Qt

class PyInstallerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python 打包器 GUI")
        self.setFixedSize(500, 200)

        self.py_file_path = ""
        self.output_dir = ""

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 選擇檔案按鈕與路徑
        file_layout = QHBoxLayout()
        btn_select_file = QPushButton("選擇 Python 檔案")
        btn_select_file.clicked.connect(self.select_py_file)
        self.file_label = QLineEdit()
        self.file_label.setReadOnly(True)
        file_layout.addWidget(btn_select_file)
        file_layout.addWidget(self.file_label)
        layout.addLayout(file_layout)

        # 選擇輸出位置
        out_layout = QHBoxLayout()
        btn_select_output = QPushButton("選擇輸出資料夾")
        btn_select_output.clicked.connect(self.select_output_folder)
        self.output_label = QLineEdit()
        self.output_label.setReadOnly(True)
        out_layout.addWidget(btn_select_output)
        out_layout.addWidget(self.output_label)
        layout.addLayout(out_layout)

        # 打包按鈕
        btn_build = QPushButton("開始打包")
        btn_build.clicked.connect(self.build_exe)
        layout.addWidget(btn_build)

        self.setLayout(layout)

    def select_py_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "選擇 Python 檔案", "", "Python (*.py)")
        if file_path:
            self.py_file_path = file_path
            self.file_label.setText(file_path)

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "選擇輸出資料夾")
        if folder:
            self.output_dir = folder
            self.output_label.setText(folder)

    def build_exe(self):
        if not self.py_file_path:
            QMessageBox.warning(self, "錯誤", "請選擇要打包的 Python 檔案！")
            return

        output_arg = f"--distpath={self.output_dir}" if self.output_dir else ""

        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile", "--noconfirm", "--windowed",
            output_arg,
            self.py_file_path
        ]

        # 移除空字串（output_arg 可能為空）
        cmd = [arg for arg in cmd if arg]

        try:
            subprocess.run(cmd, check=True)
            QMessageBox.information(self, "完成", "打包完成！")
        except subprocess.CalledProcessError:
            QMessageBox.critical(self, "錯誤", "打包失敗，請確認程式碼與環境無誤。")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PyInstallerGUI()
    window.show()
    sys.exit(app.exec())