import tkinter as tk
from tkinter import Menu, filedialog, colorchooser, simpledialog, messagebox
from PIL import Image, ImageTk, ImageGrab
import os
import time


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
    color = colorchooser.askcolor(title="Choose background color")[1]
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
            image = image.resize((root.winfo_width(), root.winfo_height()), Image.ANTIALIAS)  # Resize to fit the window
            bg_image = ImageTk.PhotoImage(image)

            background_label = tk.Label(desktop_frame, image=bg_image)
            background_label.place(relwidth=1, relheight=1)
            background_label.image = bg_image  # Keep reference to the image

            # Move icons on top of the background
            icon_frame.lift()
        except Exception as e:
            messagebox.showerror("Error", f"Unable to load image: {e}")


# Function to create a folder
def create_folder():
    folder_name = simpledialog.askstring("Create Folder", "Enter folder name:")
    if folder_name:
        create_desktop_icon(folder_name, path=None, is_folder=True)


# Function to open terminal
def open_terminal():
    terminal_window = tk.Toplevel(root)
    terminal_window.title("Terminal")
    terminal_window.geometry("600x400")

    output_text = tk.Text(terminal_window, bg="black", fg="white", insertbackground="white")
    output_text.pack(fill="both", expand=True)

    # Function to execute command
    def execute_command(event=None):
        command = input_entry.get().strip()
        if command == "exit":
            terminal_window.destroy()
            return
        output_text.insert(tk.END, f"$ {command}\n")
        handle_command(command)
        input_entry.delete(0, tk.END)

    # Function to handle commands
    def handle_command(command):
        try:
            if command.startswith("mkdir"):
                dir_name = command.split(" ")[1]
                os.makedirs(dir_name, exist_ok=True)
                output_text.insert(tk.END, f"Created directory: {dir_name}\n")
            elif command.startswith("ls"):
                files = os.listdir(".")
                output_text.insert(tk.END, "\n".join(files) + "\n")
            elif command.startswith("pwd"):
                output_text.insert(tk.END, os.getcwd() + "\n")
            elif command.startswith("clear"):
                output_text.delete(1.0, tk.END)
            elif command.startswith("touch"):
                file_name = command.split(" ")[1]
                open(file_name, 'a').close()
                output_text.insert(tk.END, f"Created file: {file_name}\n")
            elif command.startswith("echo"):
                output_text.insert(tk.END, " ".join(command.split(" ")[1:]) + "\n")
            elif command.startswith("whoami"):
                output_text.insert(tk.END, os.getlogin() + "\n")
            elif command.startswith("rm"):
                file_name = command.split(" ")[1]
                os.remove(file_name)
                output_text.insert(tk.END, f"Removed file: {file_name}\n")
            elif command.startswith("cat"):
                file_name = command.split(" ")[1]
                with open(file_name, 'r') as f:
                    output_text.insert(tk.END, f.read() + "\n")
            else:
                output_text.insert(tk.END, "Command not recognized.\n")
        except Exception as e:
            output_text.insert(tk.END, f"Error: {e}\n")

    # Command line input
    input_entry = tk.Entry(terminal_window, bg="black", fg="white")
    input_entry.pack(fill="x")
    input_entry.bind("<Return>", execute_command)


# Taskbar
taskbar = tk.Frame(root, bg="#202124", height=40)
taskbar.pack(side="bottom", fill="x")

# Start button functionality
def on_start_button_click():
    print("Start Button Clicked")  # Add functionality here


start_button = tk.Button(taskbar, text="⊞ Start", fg="white", bg="#333333", font=("Segoe UI", 10, "bold"), command=on_start_button_click)
start_button.pack(side="left", padx=10, pady=5)

# Add file button
add_file_button = tk.Button(taskbar, text="Add File", fg="white", bg="#333333", font=("Segoe UI", 10, "bold"), command=add_file_to_desktop)
add_file_button.pack(side="left", padx=10, pady=5)

# Create folder button
create_folder_button = tk.Button(taskbar, text="Create Folder", fg="white", bg="#333333", font=("Segoe UI", 10, "bold"), command=create_folder)
create_folder_button.pack(side="left", padx=10, pady=5)

# Terminal button
terminal_button = tk.Button(taskbar, text="Terminal", fg="white", bg="#333333", font=("Segoe UI", 10, "bold"), command=open_terminal)
terminal_button.pack(side="left", padx=10, pady=5)

# Right-click menu for taskbar (Screenshot and Change Background)
def show_taskbar_menu(event):
    taskbar_menu = Menu(root, tearoff=0)
    taskbar_menu.add_command(label="Screenshot", command=capture_screenshot)
    taskbar_menu.add_command(label="Change Background Color", command=change_background_color)
    taskbar_menu.add_command(label="Change Background Image", command=change_background_image)
    taskbar_menu.tk_popup(event.x_root, event.y_root)

taskbar.bind("<Button-3>", show_taskbar_menu)

# Function to capture screenshot
def capture_screenshot():
    screenshot = ImageGrab.grab()
    screenshot_path = os.path.join(os.getcwd(), f"screenshot_{time.strftime('%Y%m%d_%H%M%S')}.png")
    screenshot.save(screenshot_path)
    print(f"Screenshot saved at {screenshot_path}")


root.mainloop()

#Welcome to ArkaOS!

