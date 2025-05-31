import subprocess
import sys
import os
import urllib.request
import zipfile
import shutil

###### 安裝 Python（建議 3.10+）再執行此檔案  ######

REQUIRED_PACKAGES = [
    "PySide6",
    "pillow-heif"
]

FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
FFMPEG_DIR = os.path.join(os.getcwd(), "tools")
FFMPEG_EXE = os.path.join(FFMPEG_DIR, "ffmpeg.exe")

def install_pip_package(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except subprocess.CalledProcessError:
        print(f"[X] 安裝 {package} 失敗！請手動處理。")

def ensure_python_packages():
    for package in REQUIRED_PACKAGES:
        try:
            __import__(package.lower().replace('-', '_'))
        except ImportError:
            print(f"[-] 尚未安裝 {package}，正在安裝...")
            install_pip_package(package)

def download_ffmpeg():
    print("[-] 開始下載 ffmpeg...")
    zip_path = "ffmpeg.zip"
    urllib.request.urlretrieve(FFMPEG_URL, zip_path)

    print("[-] 解壓縮 ffmpeg...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall("temp_ffmpeg")

    bin_folder = None
    for root, dirs, files in os.walk("temp_ffmpeg"):
        if "ffmpeg.exe" in files:
            bin_folder = root
            break

    if bin_folder:
        os.makedirs(FFMPEG_DIR, exist_ok=True)
        shutil.copy(os.path.join(bin_folder, "ffmpeg.exe"), FFMPEG_EXE)
        print("[✔] ffmpeg 安裝完成")
    else:
        print("[X] ffmpeg.exe 找不到，請手動安裝")

    shutil.rmtree("temp_ffmpeg")
    os.remove(zip_path)

def ensure_ffmpeg():
    if not os.path.exists(FFMPEG_EXE):
        download_ffmpeg()
    else:
        print("[✔] 已找到 ffmpeg")

def main():
    print("==== 初始安裝程序開始 ====")
    ensure_python_packages()
    ensure_ffmpeg()

    print("\n[✔] 環境已準備完成，可以開始使用轉檔器工具！")

if __name__ == "__main__":
    main()