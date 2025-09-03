import tkinter as tk
from tkinter.filedialog import asksaveasfilename, askopenfilename

current_file_path = None
window = None
text_box = None

def references(tb, wd):
    global text_box, window
    text_box = tb
    window = wd

def open_file():
    global current_file_path
    file_path = askopenfilename(
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if not file_path:
        return
    current_file_path = file_path
    text_box.delete("1.0", tk.END)
    with open(file_path, "r") as input_file:
        text = input_file.read()
        text_box.insert(tk.END, text)
    window.title(f"Text Editor - {file_path}")

def save_file():
    global current_file_path
    if current_file_path:
        with open(current_file_path, "w") as output_file:
            text = text_box.get("1.0", tk.END)
            output_file.write(text)
    else:
        save_file_as()

def save_file_as():
    global current_file_path
    file_path = asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if not file_path:
        return
    current_file_path = file_path
    with open(file_path, "w") as output_file:
        text = text_box.get("1.0", tk.END)
        output_file.write(text)
    window.title(f"Text Editor - {file_path}")