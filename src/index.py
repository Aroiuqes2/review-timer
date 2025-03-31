import tkinter as tk
from tkinter import messagebox, ttk
import time
import threading
import requests
import os
import sys
import zipfile
import shutil
import psutil
import pyttsx3

GITHUB_USER = "Aroiuqes2"
REPO_NAME = "review-timer"
CURRENT_VERSION = "1.0.8"

GITHUB_VERSION_URL = f"https://raw.githubusercontent.com/Aroiuqes2/review-timer/refs/heads/main/version.txt"
GITHUB_ZIP_URL = f"https://github.com/Aroiuqes2/review-timer/archive/refs/heads/main.zip"

# MAIN
root = tk.Tk()
root.title("Revtim App")
root.geometry("840x300")
root.config(bg="#2C2F33")
root.iconbitmap("logo.ico")
root.resizable(False, True)

# updateRoot = tk.Tk()
# updateRoot.title("Check for Update")
# updateRoot.geometry('300x200')

tts_engine = pyttsx3.init()
tts_engine.setProperty("rate", 150)

# FRAMING
input_frame = tk.Frame(root, padx=20, pady=20, bg="#23272A", relief="ridge", bd=2)
input_frame.pack(side="left", fill="y", padx=10, pady=10)

right_frame = tk.Frame(root, padx=20, pady=20, bg="#2C2F33")
right_frame.pack(side="right", fill="both", expand=True)

filter_frame = tk.Frame(right_frame, bg="#2C2F33")
filter_frame.pack(fill="x", pady=(0, 10))

# SCROLLABLE DATA FRAME
canvas = tk.Canvas(right_frame, bg="#2C2F33")
scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=canvas.yview)
data_frame = tk.Frame(canvas, bg="#2C2F33")

canvas.create_window((0, 0), window=data_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

data_frame.bind("<Configure>", on_frame_configure)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

tk.Label(input_frame, text="Masukkan Data", font=("Arial", 14, "bold"), fg="white", bg="#23272A").pack(pady=10)

# INPUT_VAR
# youtube_var = tk.StringVar()
osu_var = tk.StringVar()
selected_time = tk.StringVar(value="30 Menit")
search_var = tk.StringVar()

# tk.Label(input_frame, text="YouTube User:", font=("Arial", 10), fg="white", bg="#23272A").pack(anchor="w")
# youtube_entry = tk.Entry(input_frame, textvariable=youtube_var, font=("Arial", 12), width=25)
# youtube_entry.pack(pady=5)

tk.Label(input_frame, text="Osu User:", font=("Arial", 10), fg="white", bg="#23272A").pack(anchor="w")
osu_entry = tk.Entry(input_frame, textvariable=osu_var, font=("Arial", 12), width=25)
osu_entry.pack(pady=5)

tk.Label(input_frame, text="Pilih Waktu:", font=("Arial", 10), fg="white", bg="#23272A").pack(anchor="w")
time_options = ["10 Menit", "20 Menit", "30 Menit"]
time_dropdown = tk.OptionMenu(input_frame, selected_time, *time_options)
time_dropdown.pack(pady=5)

entries = []

def add_time(timer_label, waktu_var, add_time_var):
    waktu_dict = {"10 Menit": 600, "20 Menit": 1200, "30 Menit": 1800}
    waktu_var[0] += waktu_dict[add_time_var.get()]
    mins, secs = divmod(waktu_var[0], 60)
    timer_label.config(text=f"{mins:02}:{secs:02}")

def adjust_window_size():
    if len(entries) == 0:
        root.geometry("300x450")
    else:
        max_width = 300
        root.update_idletasks()

        for entry_frame in data_frame.winfo_children():
            width = entry_frame.winfo_reqwidth() + 40
            if width > max_width:
                max_width = width

        root.geometry(f"{max_width + 320}x450")

# SUBMITTING FUNCTION
def submit():
    # youtube_user = youtube_var.get()
    osu_user = osu_var.get()
    waktu_str = selected_time.get()

    if not osu_user:
        return

    waktu_dict = {"10 Menit": 600, "20 Menit": 1200, "30 Menit": 1800}
    waktu = [waktu_dict[waktu_str]]

    entry_frame = tk.Frame(data_frame, padx=10, pady=5, bg="#7289DA", relief="ridge", bd=2)
    entry_frame.pack(pady=5, fill="x")

    user_label = tk.Label(entry_frame, text=f"{osu_user}",
                      font=("Arial", 10, "bold"), fg="white", bg="#7289DA")
    user_label.pack(side="left", padx=10, expand=True)

    timer_label = tk.Label(entry_frame, text=f"{waktu[0] // 60:02}:00", font=("Arial", 12, "bold"), fg="white", bg="#7289DA")
    timer_label.pack(side="left", padx=10)

    button_frame = tk.Frame(entry_frame, bg="#7289DA")
    button_frame.pack(side="right", padx=10)

    add_time_var = tk.StringVar(value="10 Menit")
    add_time_dropdown = tk.OptionMenu(button_frame, add_time_var, *time_options)
    add_time_dropdown.pack(side="left")
    
    add_time_btn = tk.Button(button_frame, text="Add", command=lambda: add_time(timer_label, waktu, add_time_var),
                         font=("Arial", 10, "bold"), bg="#4CAF50", fg="white")
    add_time_btn.pack(side="left", padx=5)

    delete_btn = tk.Button(button_frame, text="Delete", command=lambda: delete_entry(entry_frame),
                       font=("Arial", 10, "bold"), bg="red", fg="white")
    delete_btn.pack(side="left", padx=5)

    entries.append((osu_user.lower(), entry_frame))

    threading.Thread(target=update_timer, args=(timer_label, waktu, entry_frame), daemon=True).start()

    adjust_window_size()

    # youtube_var.set("")
    osu_var.set("")

# TIMER UPDATER FUNCTION
def update_timer(timer_label, waktu_var, entry_frame):
    while waktu_var[0] > 0:
        if not timer_label.winfo_exists():
            return
        mins, secs = divmod(waktu_var[0], 60)
        if waktu_var[0] < 600:
            timer_label.config(fg="yellow")
        if waktu_var[0] < 300:
            timer_label.config(fg="red") 
        timer_label.config(text=f"{mins:02}:{secs:02}")
        time.sleep(1)
        waktu_var[0] -= 1
    if entry_frame.winfo_exists():
        entry_frame.destroy()

# DATA SEARCH/FILTER FUNCTION
def filter_data(*args):
    query = search_var.get().lower()
    
    for osu_user, entry_frame in entries:
        if query in osu_user:
            entry_frame.pack(pady=5, fill="x")
        else:
            entry_frame.pack_forget()

# DELETE BUTTON FUNCTION
def delete_entry(entry_frame):
    entry_frame.destroy()
    global entries
    entries = [entry for entry in entries if entry[1] != entry_frame]

# tk.Label(updateRoot, text=f"Versi Saat Ini: {CURRENT_VERSION}", font=("Arial", 12)).pack(pady=10)
# update_button = tk.Button(updateRoot, text="Cek Update", command=lambda: None, font=("Arial", 12), bg="blue", fg="white")
# update_button.pack(pady=20)

tk.Label(filter_frame, text="Search:", font=("Arial", 10), fg="white", bg="#2C2F33").pack(anchor="w")
search_entry = tk.Entry(filter_frame, textvariable=search_var, font=("Arial", 12), width=30)
search_entry.pack(pady=5, fill="x")
search_var.trace_add("write", filter_data)


submit_btn = tk.Button(input_frame, text="Submit", command=submit, font=("Arial", 12, "bold"),
                       bg="#4CAF50", fg="white", activebackground="#388E3C", width=15)
submit_btn.pack(pady=10)

root.mainloop()