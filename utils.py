import tkinter as tk
from tkinter import ttk
import re

text_box = None
window = None
font_dropdown = None
color_dropdown = None   
lbl_font = None
lbl_color = None
format_dropdown = None
lbl_format = None

def utils_references(tb, wd, font, color, font_config, color_config, format, format_config):
    global text_box, window, font_dropdown, color_dropdown, lbl_color, lbl_font, format_dropdown, lbl_format
    text_box = tb
    window = wd
    font_dropdown = font
    color_dropdown = color
    lbl_font = font_config
    lbl_color = color_config
    format_dropdown = format
    lbl_format = format_config

def change_font(event):
    selected_font = font_dropdown.get()
    text_box.config(font=selected_font)
    lbl_font.config(text=f"Font:\n{selected_font}")

def change_color(event):
    selected_color = color_dropdown.get()
    text_box.config(fg=selected_color)
    lbl_color.config(text=f"Font:\n{selected_color}")

def format_action(event):
    action = format_dropdown.get()
    if action == "Bulleted List":
        add_list_item(list_type="bullet")
    elif action == "Numbered List":
        add_list_item(list_type="number")

def add_list_item(list_type):
    if list_type == "bullet":
        text_box.insert(tk.INSERT, "*")
    elif list_type == "number":
        current_line = int(text_box.index(tk.INSERT).split('.')[0])
        prev_line_text = text_box.get(f"{current_line-1}.0", f"{current_line-1}.end")
        match = re.match(r'(\d+)\.', prev_line_text.strip())
        if match:
            current_number = int(match.group(1)) + 1
            text_box.insert(tk.INSERT, f"{current_number}. ")
        else:
            text_box.insert(tk.INSERT, "1. ")

    text_box.focus_set()