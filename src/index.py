import tkinter as tk
from tkinter import messagebox
import time
import threading
import requests
import os
import sys
import zipfile
import shutil
import subprocess
import pyttsx3

GITHUB_USER = "Aroiuqes2"
REPO_NAME = "review-timer"
CURRENT_VERSION = "1.0.5"
GITHUB_VERSION_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/main/version.txt"
GITHUB_ZIP_URL = f"https://github.com/{GITHUB_USER}/{REPO_NAME}/archive/refs/heads/main.zip"

root = tk.Tk()
root.title("Revtime App")
root.geometry("1000x450")
root.config(bg="#2C2F33")
root.iconbitmap("logo.ico")

tts_engine = pyttsx3.init()
tts_engine.setProperty("rate", 150)


def check_update():
    try:
        response = requests.get(GITHUB_VERSION_URL, timeout=5)
        latest_version = response.text.strip()
        if latest_version != CURRENT_VERSION:
            update_prompt(latest_version)
        else:
            messagebox.showinfo("Update Checker", "Aplikasi sudah versi terbaru!")
    except Exception as e:
        messagebox.showerror("Error", f"Tidak dapat mengecek update: {e}")


def update_prompt(latest_version):
    response = messagebox.askyesno("Update Tersedia", f"Versi terbaru {latest_version} tersedia!\nIngin mengupdate sekarang?")
    if response:
        update_application()


def update_application():
    try:
        messagebox.showinfo("Update", "Mengunduh update terbaru...")
        response = requests.get(GITHUB_ZIP_URL, stream=True)
        zip_path = "update.zip"
        with open(zip_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
        
        messagebox.showinfo("Update", "Update berhasil diunduh! Memperbarui aplikasi...")
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall("update_temp")
        extracted_folder = "update_temp/review-timer-main"
        
        if not os.access(os.getcwd(), os.W_OK):
            messagebox.showinfo("Izin Diperlukan", "Aplikasi perlu dijalankan dengan izin admin untuk memperbarui.")
            subprocess.run(["powershell", "Start-Process", "python", "-ArgumentList", "'" + sys.argv[0] + "'", "-Verb", "RunAs"])
            sys.exit()
        
        for item in os.listdir(extracted_folder):
            src = os.path.join(extracted_folder, item)
            dst = os.path.join(os.getcwd(), item)
            if os.path.exists(dst):
                if os.path.isdir(dst):
                    shutil.rmtree(dst)
                else:
                    os.remove(dst)
            shutil.move(src, dst)
        
        os.remove(zip_path)
        shutil.rmtree("update_temp")
        messagebox.showinfo("Update", "Update berhasil! Restart aplikasi.")
        restart_application()
    except Exception as e:
        messagebox.showerror("Update Gagal", f"Gagal mengupdate: {e}")


def restart_application():
    python = sys.executable
    os.execl(python, python, *sys.argv)


update_button = tk.Button(root, text="Cek Update", command=check_update, font=("Arial", 12), bg="blue", fg="white")
update_button.pack(pady=20)

root.mainloop()
