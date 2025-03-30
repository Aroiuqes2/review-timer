import tkinter as tk
import time
import threading
from tkinter import messagebox
import requests

CURRENT_VERSION = "1.0.0"
GITHUB_REPO = "https://raw.githubusercontent.com/Aroiuqes2/review-timer/refs/heads/main/version.txt"

# MAIN
root = tk.Tk()
root.title("Review Time")
root.geometry("1000x450")
root.config(bg="#2C2F33")
root.iconbitmap('icon.ico')

updateRoot = tk.Tk()
updateRoot.title("Check for Update")
updateRoot.geometry('300x200')

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
        response = requests.get(GITHUB_REPO, timeout=5)
        latest_version = response.text.strip()

        if latest_version != CURRENT_VERSION:
            messagebox.showinfo("Update Tersedia", f"Versi terbaru {latest_version} tersedia!\nSilakan update.")
    except Exception as e:
        messagebox.showerror("Error", f"Tidak dapat mengecek update: {e}")

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
    timer_label.config(text="Waktu Habis!", fg="red")

# DATA SEARCH/FILTER
def filter_data(*args):
    query = search_var.get().lower()
    
    for youtube_user, osu_user, entry_frame in entries:
        if query in youtube_user or query in osu_user:
            entry_frame.pack(pady=5, fill="x")
        else:
            entry_frame.pack_forget()

tk.Label(updateRoot, text=f"Versi Saat Ini: {CURRENT_VERSION}", font=("Arial", 12)).pack(pady=10)
tk.Button(updateRoot, text="Cek Update", command=check_update, font=("Arial", 12), bg="blue", fg="white").pack(pady=20)

tk.Label(filter_frame, text="Search:", font=("Arial", 10), fg="white", bg="#2C2F33").pack(anchor="w")
search_entry = tk.Entry(filter_frame, textvariable=search_var, font=("Arial", 12), width=30)
search_entry.pack(pady=5, fill="x")
search_var.trace_add("write", filter_data)

submit_btn = tk.Button(input_frame, text="Submit", command=submit, font=("Arial", 12, "bold"),
                       bg="#4CAF50", fg="white", activebackground="#388E3C", width=15)
submit_btn.pack(pady=10)

root.mainloop()
