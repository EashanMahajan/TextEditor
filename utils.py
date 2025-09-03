import tkinter as tk
from tkinter import ttk

text_box = None
window = None
font_dropdown = None
color_dropdown = None   
lbl_font = None
lbl_color = None

def utils_references(tb, wd, font, color, font_config, color_config):
    global text_box, window, font_dropdown, color_dropdown, lbl_color, lbl_font
    text_box = tb
    window = wd
    font_dropdown = font
    color_dropdown = color
    lbl_font = font_config
    lbl_color = color_config

def change_font(event=None):
    selected_font = font_dropdown.get()
    text_box.config(font=selected_font)
    lbl_font.config(text=f"Font:\n{selected_font}")

def change_color(event=None):
    selected_color = color_dropdown.get()
    text_box.config(fg=selected_color)
    lbl_color.config(text=f"Font:\n{selected_color}")