import tkinter as tk
from tkinter import messagebox
import time
import threading
import requests
import os
import sys
import zipfile
import shutil
import pyttsx3

GITHUB_USER = "Aroiuqes2"
REPO_NAME = "review-timer"
CURRENT_VERSION = "1.0.5"

GITHUB_VERSION_URL = f"https://raw.githubusercontent.com/Aroiuqes2/review-timer/refs/heads/main/version.txt"
GITHUB_ZIP_URL = f"https://github.com/Aroiuqes2/review-timer/archive/refs/heads/main.zip"

# MAIN
root = tk.Tk()
root.title("Revtime App")
root.geometry("1000x450")
root.config(bg="#2C2F33")
root.iconbitmap("logo.ico")

updateRoot = tk.Tk()
updateRoot.title("Check for Update")
updateRoot.geometry('300x200')

tts_engine = pyttsx3.init()
tts_engine.setProperty("rate", 150)


# FRAMING
input_frame = tk.Frame(root, padx=20, pady=20, bg="#23272A", relief="ridge", bd=2)
input_frame.pack(side="left", fill="y", padx=10, pady=10)

right_frame = tk.Frame(root, padx=20, pady=20, bg="#2C2F33")
right_frame.pack(side="right", fill="both", expand=True)

filter_frame = tk.Frame(right_frame, bg="#2C2F33")
filter_frame.pack(fill="x", pady=(0, 10))

data_frame = tk.Frame(right_frame, bg="#2C2F33")
data_frame.pack(fill="both", expand=True)

tk.Label(input_frame, text="Masukkan Data", font=("Arial", 14, "bold"), fg="white", bg="#23272A").pack(pady=10)

# INPUT_VAR
youtube_var = tk.StringVar()
osu_var = tk.StringVar()
selected_time = tk.StringVar(value="30 Menit")
search_var = tk.StringVar()

tk.Label(input_frame, text="YouTube User:", font=("Arial", 10), fg="white", bg="#23272A").pack(anchor="w")
youtube_entry = tk.Entry(input_frame, textvariable=youtube_var, font=("Arial", 12), width=25)
youtube_entry.pack(pady=5)

tk.Label(input_frame, text="Osu User:", font=("Arial", 10), fg="white", bg="#23272A").pack(anchor="w")
osu_entry = tk.Entry(input_frame, textvariable=osu_var, font=("Arial", 12), width=25)
osu_entry.pack(pady=5)

tk.Label(input_frame, text="Pilih Waktu:", font=("Arial", 10), fg="white", bg="#23272A").pack(anchor="w")
time_options = ["10 Menit", "20 Menit", "30 Menit"]
time_dropdown = tk.OptionMenu(input_frame, selected_time, *time_options)
time_dropdown.pack(pady=5)

entries = []

# UPDATE CHECK
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

# NOTIF UPDATE
def update_prompt(latest_version):
    response = messagebox.askyesno("Update Tersedia",
                                   f"Versi terbaru {latest_version} tersedia!\n"
                                   "Apakah ingin mengupdate sekarang?")
    if response:
        update_application()

# UPDATE PROSES
def update_application():
    try:
        root.destroy()
        updateRoot.destroy()
        messagebox.showinfo("Update", "Mengunduh update terbaru...")

        # DOWNLOAD FILE FROM GITHUB
        response = requests.get(GITHUB_ZIP_URL, stream=True)
        zip_path = "update.zip"

        with open(zip_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)

        messagebox.showinfo("Update", "Update berhasil diunduh! Memperbarui aplikasi...")

        # EXTRACT
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall("update_temp")

        extracted_folder = f"update_temp/review-timer-main"

        # REMOVE OLD FILE, REPLACE NEW FILE
        for item in os.listdir(extracted_folder):
            src = os.path.join(extracted_folder, item)
            dst = os.path.join(os.getcwd(), item)

            if os.path.exists(dst):
                if os.path.isdir(dst):
                    shutil.rmtree(dst)
                else:
                    os.remove(dst)

            shutil.move(src, dst)

        # CLEARING CACHE
        os.remove(zip_path)
        shutil.rmtree("update_temp")

        messagebox.showinfo("Update", "Update berhasil! Restart aplikasi.")
        restart_application()
    except Exception as e:
        messagebox.showerror("Update Gagal", f"Gagal mengupdate: {e}")

# RESTART APP AFTER UPD
def restart_application():
    python = sys.executable
    os.execl(python, python, *sys.argv)

# SUBMIT
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

    user_label = tk.Label(entry_frame, text=f"YouTube: {youtube_user}  |  Osu: {osu_user} ({waktu_str})",
                          font=("Arial", 10, "bold"), fg="white", bg="#7289DA")
    user_label.pack(side="left", padx=10)

    timer_label = tk.Label(entry_frame, text=f"{waktu // 60:02}:00", font=("Arial", 12, "bold"), fg="white", bg="#7289DA")
    timer_label.pack(side="right", padx=10)

    entries.append((youtube_user.lower(), osu_user.lower(), entry_frame))

    threading.Thread(target=update_timer, args=(timer_label, waktu), daemon=True).start()

    youtube_var.set("")
    osu_var.set("")

# NOTIF
def play_alarm(youtube_user, osu_user):
    message = f"Time for {youtube_user} is expired!"
    print(message)  # Debugging (opsional)
    tts_engine.say(message)
    tts_engine.runAndWait()

# TIMER UPDATE
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
    play_alarm(youtube_user)

# DATA SEARCH/FILTER
def filter_data(*args):
    query = search_var.get().lower()
    
    for youtube_user, osu_user, entry_frame in entries:
        if query in youtube_user or query in osu_user:
            entry_frame.pack(pady=5, fill="x")
        else:
            entry_frame.pack_forget()

tk.Label(updateRoot, text=f"Versi Saat Ini: {CURRENT_VERSION}", font=("Arial", 12)).pack(pady=10)
update_button = tk.Button(updateRoot, text="Cek Update", command=check_update, font=("Arial", 12), bg="blue", fg="white")
update_button.pack(pady=20)

tk.Label(filter_frame, text="Search:", font=("Arial", 10), fg="white", bg="#2C2F33").pack(anchor="w")
search_entry = tk.Entry(filter_frame, textvariable=search_var, font=("Arial", 12), width=30)
search_entry.pack(pady=5, fill="x")
search_var.trace_add("write", filter_data)

submit_btn = tk.Button(input_frame, text="Submit", command=submit, font=("Arial", 12, "bold"),
                       bg="#4CAF50", fg="white", activebackground="#388E3C", width=15)
submit_btn.pack(pady=10)

root.mainloop()
