import os
import subprocess
import sys

# 自動安裝 tkinter（大多數 Windows 已內建）
try:
    import tkinter as tk
    from tkinter import filedialog, messagebox
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "tk"])
    import tkinter as tk
    from tkinter import filedialog, messagebox

from datetime import timedelta

def seconds_to_timestamp(seconds):
    t = timedelta(seconds=seconds)
    total_seconds = int(t.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    millis = int((t.total_seconds() - total_seconds) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

def generate_srt_from_text(text):
    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
    srt_output = []
    current_time = 0.0

    for i, line in enumerate(lines, start=1):
        start = seconds_to_timestamp(current_time)
        end = seconds_to_timestamp(current_time + 3.0)
        srt_output.append(f"{i}\n{start} --> {end}\n{line}\n")
        current_time += 4.0  # 3秒顯示 + 1秒間隔

    return "\n".join(srt_output)

def convert_to_srt():
    text = input_text.get("1.0", tk.END)
    if not text.strip():
        messagebox.showwarning("⚠️", "請先輸入文案")
        return

    srt_content = generate_srt_from_text(text)
    filepath = filedialog.asksaveasfilename(defaultextension=".srt",
                                            filetypes=[("SubRip Subtitle", "*.srt")],
                                            title="儲存字幕檔案")
    if filepath:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(srt_content)
        messagebox.showinfo("✅ 成功", f"字幕檔已儲存至：\n{filepath}")

# 建立 GUI
root = tk.Tk()
root.title("SRT轉換器")

input_text = tk.Text(root, height=50, width=50)
input_text.pack(padx=10, pady=10)

convert_button = tk.Button(root, text="轉換為SRT", command=convert_to_srt)
convert_button.pack(pady=(0, 10))

root.mainloop()
