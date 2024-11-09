import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox, Menu
import os
from PIL import Image, ImageTk
import time
import psutil
import datetime
import subprocess
import random
import zipfile
import webbrowser
from io import BytesIO
from pygame import mixer

# Initialize root as None to prevent loading the main window immediately
root = None

# Function for loading screen
def show_loading_screen():
    loading_root = tk.Tk()
    loading_root.title("Loading ArkaOs")
    loading_root.geometry("300x200")
    loading_root.configure(bg="#1e1e1e")

    # Center label with loading text
    loading_label = tk.Label(loading_root, text="Loading ArkaOs...", fg="white", bg="#1e1e1e", font=("Segoe UI", 14))
    loading_label.pack(expand=True)

    # Progress indicator (animated dot text)
    progress_label = tk.Label(loading_root, text="Please wait...", fg="gray", bg="#1e1e1e", font=("Segoe UI", 10))
    progress_label.pack()

    # Update progress label to simulate loading
    for i in range(3):
        progress_label.config(text=f"Loading{'.' * (i + 1)}")
        loading_root.update()
        time.sleep(0.5)  # Simulate loading time

    # Destroy loading screen after "loading"
    loading_root.destroy()

# Call loading screen function before main application
show_loading_screen()

# Initialize main application window
root = tk.Tk()
root.title("ArkaOs")
root.geometry("900x600")
root.configure(bg="#1e1e1e")

# Desktop area
desktop_frame = tk.Frame(root, bg="#1e1e1e")
desktop_frame.pack(fill="both", expand=True)

# Scrollbar
scrollbar = tk.Scrollbar(desktop_frame)
scrollbar.pack(side="right", fill="y")

# Canvas for displaying desktop icons
canvas = tk.Canvas(desktop_frame, bg="#1e1e1e", yscrollcommand=scrollbar.set)
canvas.pack(side="left", fill="both", expand=True)
scrollbar.config(command=canvas.yview)

# Frame for desktop icons
icon_frame = tk.Frame(canvas, bg="#1e1e1e")
canvas.create_window((0, 0), window=icon_frame, anchor="nw")

# List for storing desktop applications
desktop_apps = []


# Function to add files to desktop
def add_file_to_desktop():
    file_path = filedialog.askopenfilename(
        title="Choose a file",
        filetypes=[("All files", "*.*"),
                  ("Executable files", "*.exe"),
                  ("Text files", "*.txt"),
                  ("Image files", "*.jpg;*.png"),
                  ("PDF files", "*.pdf")]
    )
    if file_path:
        file_name = os.path.basename(file_path)
        desktop_apps.append((file_name, file_path))
        create_desktop_icon(file_name, file_path)


# Function to create desktop icon
def create_desktop_icon(name, path, is_folder=False):
    icon_button = tk.Button(icon_frame, text=name, fg="white", bg="#333333", font=("Segoe UI", 9), width=15, height=2)

    # Right-click menu for icon
    def on_right_click(event, path=path, is_folder=is_folder):
        right_click_menu = Menu(root, tearoff=0)
        if is_folder:
            right_click_menu.add_command(label="Open Folder")
        else:
            right_click_menu.add_command(label="Open", command=lambda: open_file(path))
        right_click_menu.add_command(label="Properties")
        right_click_menu.add_separator()
        right_click_menu.add_command(label="Remove from Desktop", command=lambda: remove_icon(icon_button))
        right_click_menu.tk_popup(event.x_root, event.y_root)

    icon_button.bind("<Button-3>", on_right_click)
    icon_button.pack(pady=5)

    # Update canvas size
    icon_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))


# Function to open a file
def open_file(file_path):
    try:
        os.startfile(file_path)  # Opens file in the default program
    except Exception as e:
        print(f"Error opening file {file_path}: {e}")


# Function to remove icon from desktop
def remove_icon(button):
    button.destroy()
    icon_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))


# Function to change background color
def change_background_color():
    color = filedialog.askcolor(title="Choose background color")[1]
    if color:
        desktop_frame.configure(bg=color)
        canvas.configure(bg=color)
        icon_frame.configure(bg=color)


# Function to change background to an image from files
def change_background_image():
    file_path = filedialog.askopenfilename(
        title="Select Image for Background",
        filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp")]
    )
    if file_path:
        try:
            image = Image.open(file_path)
            image = image.resize((root.winfo_width(), root.winfo_height()), Image.Resampling.LANCZOS)  # Updated line
            bg_image = ImageTk.PhotoImage(image)

            # Create background label and place it behind other widgets
            background_label = tk.Label(desktop_frame, image=bg_image)
            background_label.place(relwidth=1, relheight=1)
            background_label.image = bg_image  # Keep reference to the image

            # Ensure the icon_frame is on top of the background
            icon_frame.lift()
        except Exception as e:
            messagebox.showerror("Error", f"Unable to load image: {e}")


# Taskbar
taskbar = tk.Frame(root, bg="#333333", height=40)
taskbar.pack(side="bottom", fill="x")

# Add button for File Explorer
explorer_button = tk.Button(taskbar, text="File Explorer", fg="white", bg="#333333", font=("Segoe UI", 10, "bold"), command=add_file_to_desktop)
explorer_button.pack(side="left", padx=10, pady=5)

# Add button for Calculator
def open_calculator():
    calculator_window = tk.Toplevel(root)
    calculator_window.title("Calculator")
    calculator_window.geometry("300x400")

    # Entry to display results
    result_var = tk.StringVar()
    result_display = tk.Entry(calculator_window, textvariable=result_var, font=("Segoe UI", 20), bd=10, relief="sunken", justify="right")
    result_display.grid(row=0, column=0, columnspan=4)

    # Button click handler
    def button_click(value):
        current = result_var.get()
        result_var.set(current + str(value))

    # Clear display
    def clear_display():
        result_var.set("")

    # Calculate result
    def calculate():
        try:
            result_var.set(eval(result_var.get()))
        except Exception:
            result_var.set("Error")

    # Button definitions
    buttons = [
        "7", "8", "9", "/",
        "4", "5", "6", "*",
        "1", "2", "3", "-",
        "0", ".", "=", "+"
    ]

    row = 1
    col = 0
    for button in buttons:
        action = calculate if button == "=" else button_click
        button = tk.Button(calculator_window, text=button, font=("Segoe UI", 15), width=5, height=2,
                           command=lambda value=button: action(value))
        button.grid(row=row, column=col)
        col += 1
        if col > 3:
            col = 0
            row += 1

    # Clear button
    clear_button = tk.Button(calculator_window, text="C", font=("Segoe UI", 15), width=5, height=2, command=clear_display)
    clear_button.grid(row=row, column=0, columnspan=4)

calculator_button = tk.Button(taskbar, text="Calculator", fg="white", bg="#333333", font=("Segoe UI", 10, "bold"), command=open_calculator)
calculator_button.pack(side="left", padx=10, pady=5)

root.mainloop()
