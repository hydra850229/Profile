import sys
import os
import subprocess
import platform
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QFileDialog,
    QVBoxLayout, QHBoxLayout, QListWidget, QMessageBox, QMenu, QProgressBar
)
from PySide6.QtCore import Qt, QPoint

def convert_mov_to_mp4(input_path, output_path):
    cmd = [
        "ffmpeg",
        "-i", input_path,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-movflags", "+faststart",
        "-y",
        output_path
    ]

    startupinfo = None
    if platform.system() == "Windows":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, startupinfo=startupinfo)
        return os.path.exists(output_path) and os.path.getsize(output_path) > 1024
    except subprocess.CalledProcessError:
        return False


def convert_heic_to_jpeg(input_path, output_path):
    try:
        from pillow_heif import register_heif_opener
        from PIL import Image

        register_heif_opener()
        image = Image.open(input_path)
        image.save(output_path, format="JPEG")
        return True
    except Exception:
        return False


class ConverterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("轉碼器")
        self.setFixedSize(500, 440)

        self.file_list = []
        self.output_folder = ""

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 檔案選擇
        btn_select_files = QPushButton("選擇檔案")
        btn_select_files.clicked.connect(self.select_files)
        layout.addWidget(btn_select_files)

        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.ExtendedSelection)
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.list_widget)

        # 資料夾選擇
        hlayout = QHBoxLayout()
        btn_select_folder = QPushButton("選擇輸出資料夾")
        btn_select_folder.clicked.connect(self.select_output_folder)
        self.label_output = QLabel("未選擇")

        hlayout.addWidget(btn_select_folder)
        hlayout.addWidget(self.label_output)
        layout.addLayout(hlayout)

        # 進度條
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)

        # 開始轉檔
        btn_convert = QPushButton("開始轉檔")
        btn_convert.clicked.connect(self.start_conversion)
        layout.addWidget(btn_convert)

        self.setLayout(layout)

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "選擇檔案", "", "影片/圖片 (*.mov *.heic)")
        if files:
            self.file_list.extend(files)
            self.refresh_file_list()

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "選擇資料夾")
        if folder:
            self.output_folder = folder
            self.label_output.setText(folder)

    def start_conversion(self):
        if not self.file_list or not self.output_folder:
            QMessageBox.warning(self, "提醒", "請選擇檔案與輸出資料夾！")
            return

        success = 0
        total = len(self.file_list)
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(0)

        for index, file_path in enumerate(self.file_list, start=1):
            ext = os.path.splitext(file_path)[1].lower()
            filename = os.path.splitext(os.path.basename(file_path))[0]

            if ext == ".mov":
                output_path = os.path.join(self.output_folder, filename + ".mp4")
                if convert_mov_to_mp4(file_path, output_path):
                    success += 1
            elif ext == ".heic":
                output_path = os.path.join(self.output_folder, filename + ".jpeg")
                if convert_heic_to_jpeg(file_path, output_path):
                    success += 1

            self.progress_bar.setValue(index)

        QMessageBox.information(self, "完成", f"已成功轉檔 {success} 個檔案！")

    def refresh_file_list(self):
        self.list_widget.clear()
        self.list_widget.addItems(self.file_list)

    def show_context_menu(self, pos: QPoint):
        menu = QMenu()
        remove_action = menu.addAction("移除選取項目")
        action = menu.exec(self.list_widget.mapToGlobal(pos))
        if action == remove_action:
            selected_items = self.list_widget.selectedItems()
            for item in selected_items:
                file_path = item.text()
                if file_path in self.file_list:
                    self.file_list.remove(file_path)
            self.refresh_file_list()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConverterApp()
    window.show()
    sys.exit(app.exec())
