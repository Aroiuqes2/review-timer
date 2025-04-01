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
import subprocess
from tkinter import font as tkfont

GITHUB_USER = "Aroiuqes2"
REPO_NAME = "review-timer"
CURRENT_VERSION = "1.0.8"

GITHUB_VERSION_URL = f"https://raw.githubusercontent.com/Aroiuqes2/review-timer/refs/heads/main/version.txt"
GITHUB_ZIP_URL = f"https://github.com/Aroiuqes2/review-timer/archive/refs/heads/main.zip"

# MAIN WINDOW SETUP
root = tk.Tk()
root.title("Revtim App")
root.geometry("840x500")
root.config(bg="#1E1E1E") 
root.iconbitmap("logo.ico")
root.resizable(False, True)

# Custom fonts
title_font = tkfont.Font(family="Segoe UI", size=14, weight="bold")
label_font = tkfont.Font(family="Segoe UI", size=10)
entry_font = tkfont.Font(family="Segoe UI", size=11)
button_font = tkfont.Font(family="Segoe UI", size=10, weight="bold")
timer_font = tkfont.Font(family="Segoe UI", size=12, weight="bold")

# STYLE CONFIGURATION
style = ttk.Style()
style.theme_use('clam')

# Configure colors
style.configure('TFrame', background='#1E1E1E')
style.configure('TLabel', background='#1E1E1E', foreground='white', font=label_font)
style.configure('TButton', font=button_font, padding=6)
style.configure('TEntry', font=entry_font, padding=5)
style.configure('TCombobox', font=entry_font, padding=5)
style.configure('TEntry', 
                fieldbackground='white',  # Background putih
                foreground='black',      # Teks hitam
                font=entry_font, 
                padding=5)

# FRAMING
input_frame = tk.Frame(root, padx=20, pady=20, bg="#252526", relief="flat", bd=0)
input_frame.pack(side="left", fill="y", padx=10, pady=10, ipadx=5, ipady=5)

right_frame = tk.Frame(root, padx=20, pady=20, bg="#1E1E1E")
right_frame.pack(side="right", fill="both", expand=True)

filter_frame = tk.Frame(right_frame, bg="#1E1E1E")
filter_frame.pack(fill="x", pady=(0, 10))

# SCROLLABLE DATA FRAME
canvas = tk.Canvas(right_frame, bg="#1E1E1E", highlightthickness=0)
scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=canvas.yview)
data_frame = tk.Frame(canvas, bg="#1E1E1E")

canvas.create_window((0, 0), window=data_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

data_frame.bind("<Configure>", on_frame_configure)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# TITLE
tk.Label(input_frame, text="Revtim Timer", font=title_font, fg="#569CD6", bg="#252526").pack(pady=(0, 15))

# INPUT VARIABLES
osu_var = tk.StringVar()
selected_time = tk.StringVar(value="30 Menit")
search_var = tk.StringVar()

# PLACEHOLDER
def create_placeholder_entry(parent, textvariable, placeholder):
    entry = ttk.Entry(parent, textvariable=textvariable, font=entry_font, width=25)
    entry.insert(0, placeholder)
    entry.config(foreground='#A0A0A0')
    
    def on_focus_in(event):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
        entry.config(foreground='black') 
    
    def on_focus_out(event):
        if not entry.get():
            entry.insert(0, placeholder)
            entry.config(foreground='#A0A0A0')  
        else:
            entry.config(foreground='black')  
    
    entry.bind('<FocusIn>', on_focus_in)
    entry.bind('<FocusOut>', on_focus_out)
    
    return entry

# OSU USER INPUT
tk.Label(input_frame, text="Osu User:", font=label_font, fg="white", bg="#252526").pack(anchor="w")
osu_entry = create_placeholder_entry(input_frame, osu_var, "Enter osu! username")
osu_entry.pack(pady=5)

# TIME SELECTION
tk.Label(input_frame, text="Select Time:", font=label_font, fg="white", bg="#252526").pack(anchor="w")
time_options = ["10 Menit", "20 Menit", "30 Menit"]
time_dropdown = ttk.Combobox(input_frame, textvariable=selected_time, values=time_options, state="readonly")
time_dropdown.pack(pady=5)

entries = []

# MODERN BUTTON STYLING
def create_modern_button(parent, text, command, bg_color, fg_color="white", hover_color=None):
    if hover_color is None:
        hover_color = bg_color
    
    btn = tk.Button(parent, text=text, command=command, 
                    font=button_font, bg=bg_color, fg=fg_color,
                    activebackground=hover_color,
                    relief="flat", bd=0, padx=12, pady=6)
    
    def on_enter(e):
        btn['background'] = hover_color
    
    def on_leave(e):
        btn['background'] = bg_color
    
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    
    return btn

def add_time(timer_label, waktu_var, add_time_var):
    waktu_dict = {"10 Menit": 600, "20 Menit": 1200, "30 Menit": 1800}
    waktu_var[0] += waktu_dict[add_time_var.get()]
    mins, secs = divmod(waktu_var[0], 60)
    timer_label.config(text=f"{mins:02}:{secs:02}")

def adjust_window_size():
    if len(entries) == 0:
        root.geometry("300x500")
    else:
        max_width = 300
        root.update_idletasks()

        for entry_frame in data_frame.winfo_children():
            width = entry_frame.winfo_reqwidth() + 40
            if width > max_width:
                max_width = width

        root.geometry(f"{max_width + 320}x500")

# SUBMITTING FUNCTION
def submit():
    osu_user = osu_var.get()
    waktu_str = selected_time.get()

    if not osu_user or osu_user == "Enter osu! username":
        return

    waktu_dict = {"10 Menit": 600, "20 Menit": 1200, "30 Menit": 1800}
    waktu = [waktu_dict[waktu_str]]

    entry_frame = tk.Frame(data_frame, padx=15, pady=10, bg="#252526", relief="flat", bd=0)
    entry_frame.pack(pady=5, fill="x", ipadx=5, ipady=5)

    user_label = tk.Label(entry_frame, text=f"{osu_user}",
                      font=("Segoe UI", 10, "bold"), fg="white", bg="#252526")
    user_label.pack(side="left", padx=10, expand=True)

    timer_label = tk.Label(entry_frame, text=f"{waktu[0] // 60:02}:00", 
                          font=timer_font, fg="#4EC9B0", bg="#252526")
    timer_label.pack(side="left", padx=10)

    button_frame = tk.Frame(entry_frame, bg="#252526")
    button_frame.pack(side="right", padx=10)

    add_time_var = tk.StringVar(value="10 Menit")
    add_time_dropdown = ttk.Combobox(button_frame, textvariable=add_time_var, 
                                    values=time_options, state="readonly", width=8)
    add_time_dropdown.pack(side="left", padx=2)
    
    add_time_btn = create_modern_button(button_frame, "+", 
                                     lambda: add_time(timer_label, waktu, add_time_var),
                                     "#4CAF50", hover_color="#388E3C")
    add_time_btn.pack(side="left", padx=2)

    delete_btn = create_modern_button(button_frame, "×", 
                                   lambda: delete_entry(entry_frame),
                                   "#F44336", hover_color="#D32F2F")
    delete_btn.pack(side="left", padx=2)

    entries.append((osu_user.lower(), entry_frame))

    threading.Thread(target=update_timer, args=(timer_label, waktu, entry_frame), daemon=True).start()

    adjust_window_size()
    osu_var.set("")

# TIMER UPDATER FUNCTION
def update_timer(timer_label, waktu_var, entry_frame):
    while waktu_var[0] > 0:
        if not timer_label.winfo_exists():
            return
        
        mins, secs = divmod(waktu_var[0], 60)
        
        if waktu_var[0] < 600:
            ratio = min(1.0, (600 - waktu_var[0]) / 300)
            r = int(255 * ratio)
            g = int(255 * ratio)
            b = int(109 + (182 - 109) * (1 - ratio))
            color = f"#{r:02x}{g:02x}{b:02x}"
            timer_label.config(fg=color)
        
        timer_label.config(text=f"{mins:02}:{secs:02}")
        time.sleep(1)
        waktu_var[0] -= 1
    
    if entry_frame.winfo_exists():
        for alpha in range(100, 0, -10):
            if not entry_frame.winfo_exists():
                break
            alpha_hex = hex(int(alpha * 255 / 100))[2:].zfill(2)
            entry_frame.config(bg=f"#252526{alpha_hex}")
            entry_frame.update()
            time.sleep(0.03)
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
    if entry_frame.winfo_exists():
        entry_frame.destroy()
    global entries
    entries = [entry for entry in entries if entry[1] != entry_frame]

# ... (keep all your existing imports and constants)

# Add this function to check for updates
def check_for_updates():
    try:
        response = requests.get(GITHUB_VERSION_URL)
        if response.status_code == 200:
            latest_version = response.text.strip()
            if latest_version == CURRENT_VERSION:
                return False, latest_version  # No update available
            else:
                return True, latest_version  # Update available
    except Exception as e:
        print(f"Error checking for updates: {e}")
    return False, CURRENT_VERSION  # Default to no update if there's an error

# PERFORM UPDATE
def perform_update():
    try:
        # Show confirmation dialog
        confirm = messagebox.askyesno(
            "Confirm Update",
            "A new version is available. Update now?\nThe application will restart after updating."
        )
        if not confirm:
            return False

        # Create temp directory
        temp_dir = "temp_update"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Download the update
        zip_path = os.path.join(temp_dir, "update.zip")
        response = requests.get(GITHUB_ZIP_URL, stream=True)
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Extract the update
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Find the extracted folder (GitHub adds -main to folder name)
        extracted_folder = None
        for item in os.listdir(temp_dir):
            if item.startswith(f"{REPO_NAME}-"):
                extracted_folder = os.path.join(temp_dir, item)
                break
        
        if not extracted_folder:
            raise Exception("Update folder not found")

        # Create a batch file to perform the update after we exit
        batch_script = f"""@echo off
timeout /t 2 /nobreak >nul

xcopy /s /y "{extracted_folder}\\*" "{os.getcwd()}"

rmdir /s /q "{temp_dir}"

start "" "{sys.executable}" "{os.path.join(os.getcwd(), os.path.basename(__file__))}"
"""
        batch_path = os.path.join(temp_dir, "update.bat")
        with open(batch_path, 'w') as f:
            f.write(batch_script)

        # Launch the batch file and exit
        subprocess.Popen(['cmd.exe', '/c', batch_path], shell=True)
        root.destroy()
        return True
        
    except Exception as e:
        messagebox.showerror("Update Failed", f"Error during update: {str(e)}")
        return False

# UPDATE UI
def create_update_ui(parent):
    update_frame = tk.Frame(parent, bg="#252526", pady=10)
    update_frame.pack(side="bottom", fill="x", padx=20, pady=(0, 10))
    
    version_label = tk.Label(
        update_frame,
        text=f"Version: {CURRENT_VERSION}",
        font=label_font,
        fg="white",
        bg="#252526"
    )
    version_label.pack(side="left")
    
    # Check for updates in a separate thread to avoid UI freeze
    def check_updates_thread():
        update_available, latest_version = check_for_updates()
        
        # Update UI in main thread
        root.after(0, lambda: update_ui(update_available, latest_version))
    
    def update_ui(update_available, latest_version):
        if update_available:
            version_label.config(text=f"Version: {CURRENT_VERSION} → {latest_version}")
            
            update_btn = create_modern_button(
                update_frame,
                "Install Update",
                perform_update,
                "#4CAF50",
                hover_color="#388E3C"
            )
            update_btn.pack(side="right", padx=5)
        else:
            tk.Label(
                update_frame,
                text="Up to date",
                font=label_font,
                fg="#A0A0A0",
                bg="#252526"
            ).pack(side="right")
    
    # Start the update check thread
    threading.Thread(target=check_updates_thread, daemon=True).start()
    
    return update_frame

# SEARCH BAR
tk.Label(filter_frame, text="Search:", font=label_font, fg="white", bg="#1E1E1E").pack(anchor="w")
search_entry = ttk.Entry(filter_frame, textvariable=search_var, font=entry_font, width=30)
search_entry.pack(pady=5, fill="x")
search_var.trace_add("write", filter_data)

# SUBMIT BUTTON
submit_btn = create_modern_button(input_frame, "Start Timer", submit, 
                                "#569CD6", hover_color="#4A8FC7")
submit_btn.pack(pady=15)

def on_enter_window(e):
    root.config(bg="#1E1E1E")

def on_leave_window(e):
    root.config(bg="#1E1E1E")

root.bind("<Enter>", on_enter_window)
root.bind("<Leave>", on_leave_window)

# SHADOW EFFECT
for frame in [input_frame]:
    frame.config(highlightbackground="#3E3E42", highlightthickness=1)

create_update_ui(input_frame)

root.mainloop()