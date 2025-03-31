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

# UI Elements
input_frame = tk.Frame(root, padx=20, pady=20, bg="#23272A", relief="ridge", bd=2)
input_frame.pack(side="left", fill="y", padx=10, pady=10)

right_frame = tk.Frame(root, padx=20, pady=20, bg="#2C2F33")
right_frame.pack(side="right", fill="both", expand=True)

filter_frame = tk.Frame(right_frame, bg="#2C2F33")
filter_frame.pack(fill="x", pady=(0, 10))

data_frame = tk.Frame(right_frame, bg="#2C2F33")
data_frame.pack(fill="both", expand=True)

youtube_var = tk.StringVar()
osu_var = tk.StringVar()
selected_time = tk.StringVar(value="30 Menit")
search_var = tk.StringVar()
entries = []

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

def submit():
    youtube_user = youtube_var.get()
    osu_user = osu_var.get()
    waktu_str = selected_time.get()
    
    if not youtube_user or not osu_user:
        return
    
    waktu_dict = {"10 Menit": 600, "20 Menit": 1200, "30 Menit": 1800}
    waktu = waktu_dict[waktu_str]
    
    entry_frame = tk.Frame(data_frame, padx=10, pady=5, bg="#7289DA", relief="ridge", bd=2)
    entry_frame.pack(pady=5, fill="x")
    
    user_label = tk.Label(entry_frame, text=f"YouTube: {youtube_user} | Osu: {osu_user} ({waktu_str})", font=("Arial", 10, "bold"), fg="white", bg="#7289DA")
    user_label.pack(side="left", padx=10)
    
    timer_label = tk.Label(entry_frame, text=f"{waktu // 60:02}:00", font=("Arial", 12, "bold"), fg="white", bg="#7289DA")
    timer_label.pack(side="right", padx=10)
    
    entries.append((youtube_user.lower(), osu_user.lower(), entry_frame))
    threading.Thread(target=update_timer, args=(timer_label, waktu), daemon=True).start()
    
    youtube_var.set("")
    osu_var.set("")

def update_timer(timer_label, waktu):
    while waktu > 0:
        mins, secs = divmod(waktu, 60)
        if waktu < 600:
            timer_label.config(fg="yellow")
        if waktu < 300:
            timer_label.config(fg="red")
        timer_label.config(text=f"{mins:02}:{secs:02}")
        time.sleep(1)
        waktu -= 1
    timer_label.config(text="Timeout!", fg="green")

tk.Button(root, text="Cek Update", command=check_update, font=("Arial", 12), bg="blue", fg="white").pack(pady=20)

tk.Button(input_frame, text="Submit", command=submit, font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", width=15).pack(pady=10)

root.mainloop()
