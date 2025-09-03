import re
import tkinter as tk
from tkinter import ttk
from groq import Groq
import os
from dotenv import load_dotenv, find_dotenv
import file_operations
import ai_features
import utils

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

GROQ_API_KEY = os.getenv("API_KEY")
client = Groq(api_key=GROQ_API_KEY)
GROQ_API_URL = os.getenv("API_URL")

Tone_Options = {
    "Simple": {
        "instruction": "Simplify the vocabulary and sentence structure while preserving the original meaning. Make it easier to read.",
        "temperature": 0.2
    },
    "Formal": {
        "instruction": "Rewrite in a clear, professional, and formal tone while preserving the original meaning.",
        "temperature": 0.2
    },
    "Creative": {
        "instruction": "Make the writing more vivid and creative; feel free to enhance imagery and use expressive language while preserving meaning.",
        "temperature": 0.7
    }
}

window = tk.Tk()
text_box = tk.Text(master=window, font="Arial 12", bg="#e6f0e9", fg="black")
btn_paraphrase = None
tone_dropdown = None
lbl_word_count = None
lbl_char_count = None
lbl_font = None
font_dropdown = None
lbl_color = None
color_dropdown = None

def count(event):
    words = text_box.get("1.0", "end-1c")
    w_count = len(re.findall(r'\w+', words))
    lbl_word_count["text"] = "Word count:\n " + str(w_count)
    lbl_char_count["text"] = "Characters:\n " + str(len(words))

def ui_configuration():
    global btn_paraphrase, tone_dropdown, lbl_word_count, lbl_char_count, lbl_font, font_dropdown, lbl_color, color_dropdown

    window.title("Text Editor")
    window.configure(bg='#404d44')

    fr_buttons = tk.Frame(master=window, bg='#404d44')
    fr_buttons.pack(side="top", fill="x")

    text_box.pack(expand=True, fill="both")
    text_box.bind("<KeyPress>", count)
    text_box.bind("<KeyRelease>", count)
    text_box.focus_set()
    text_box.config(insertbackground="black")

    btn_open = tk.Button(master=fr_buttons, text="Open", width=10, bg='#91a18d', command=file_operations.open_file)
    btn_open.pack(side="left", padx=5, pady=5)

    btn_save_as = tk.Button(master=fr_buttons, text="Save As", width=10, bg="#91a18d", command=file_operations.save_file_as)
    btn_save_as.pack(side="left", padx=5, pady=5)

    btn_save = tk.Button(master=fr_buttons, text="Save", width=10, bg="#91a18d", command=file_operations.save_file)
    btn_save.pack(side="left", padx=5, pady=5)

    btn_summarize = tk.Button(master=fr_buttons, text="Summarize Page", width=10, bg='#91a18d', command= lambda: ai_features.summarize_text(text_box, window))
    btn_summarize.pack(side="left", padx=5, pady=5)

    btn_sentiment_analysis = tk.Button(master=fr_buttons, text="Sentiment Analysis Page", width=15, bg='#91a18d', command= lambda: ai_features.analyze_sentiment(text_box, window))
    btn_sentiment_analysis.pack(side="left", padx=5, pady=5)

    btn_paraphrase = tk.Button(fr_buttons, text="Paraphrase", command= lambda: ai_features.paraphrase_button_clicked(parent_window=window), bg="#91a18d")
    btn_paraphrase.pack(side="left", padx=5, pady=5)

    status_frame = tk.Frame(master=window)
    status_frame.pack(side="bottom", anchor="e", padx=10,pady=5)
    lbl_word_count = tk.Label(master=status_frame, text="Words: 0")
    lbl_word_count.pack(side="left", anchor="e", padx=5)

    lbl_char_count = tk.Label(master=status_frame, text="Characters: 0")
    lbl_char_count.pack(side="right", anchor="e", padx=5)

    lbl_font = tk.Label(master=fr_buttons, text="Font:")
    lbl_font.pack(side="left", padx=(15, 0), pady=5)

    lbl_color = tk.Label(master=fr_buttons, text="Color:")
    lbl_color.pack(side="left", padx=(15, 0), pady=5)

    font_list = ["Arial 12", "Arial 20", "Comfortaa 12", "Comfortaa 20"]
    max_font_length = 0
    for font in font_list:
        if len(font) > max_font_length:
            max_font_length = len(font)
    font_dropdown = ttk.Combobox(fr_buttons, values=font_list, state="readonly", width=max_font_length)
    font_dropdown.set("Arial 12")
    font_dropdown.bind("<<ComboboxSelected>>", utils.change_font)
    font_dropdown.pack(side="left", padx=5, pady=5)

    color_list = ["Black", "Red", "Blue", "Green", "Purple", "Yellow", "Pink", "Orange", "White", "Gray"]
    max_color_length = 0
    for color in color_list:
        if len(color) > max_color_length:
            max_color_length = len(color)
    color_dropdown = ttk.Combobox(fr_buttons, values=color_list, state="readonly", width=max_color_length)
    color_dropdown.set("Black")
    color_dropdown.bind("<<ComboboxSelected>>", utils.change_color)
    color_dropdown.pack(side="left", padx=5, pady=5)

    max_tone_length = 0
    tone_list = Tone_Options.keys()
    for tone in tone_list:
        if len(tone) > max_tone_length:
            max_tone_length = len(tone)
    tone_dropdown = ttk.Combobox(fr_buttons, values=list(Tone_Options.keys()), state="readonly", width=max_tone_length)
    tone_dropdown.set("Simple")
    tone_dropdown.pack(side="left", padx=5, pady=5)

def main():
    ui_configuration()
    utils.utils_references(text_box, window, font_dropdown, color_dropdown, lbl_font, lbl_color)
    file_operations.references(text_box, window)
    ai_features.ai_references(GROQ_API_KEY, GROQ_API_URL, Tone_Options, window, text_box, btn_paraphrase, tone_dropdown)
    window.mainloop()

if __name__ == "__main__":
    main()