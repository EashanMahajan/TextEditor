import re
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.filedialog import asksaveasfilename, askopenfilename
from groq import Groq
import os
from dotenv import load_dotenv, find_dotenv
import json
import requests
import threading

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

GROQ_API_KEY = os.getenv("API_KEY")
client = Groq(api_key=GROQ_API_KEY)
GROQ_API_URL = os.getenv("API_URL")

current_file_path = None
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

def count(event):
    words = text_box.get("1.0", "end-1c")
    w_count = len(re.findall(r'\w+', words))
    lbl_word_count["text"] = "Word count:\n " + str(w_count)
    lbl_char_count["text"] = "Characters:\n " + str(len(words))

def change_font(event=None):
    selected_font = font_dropdown.get()
    text_box.config(font=selected_font)
    lbl_font.config(text=f"Font:\n{selected_font}")

def change_color(event=None):
    selected_color = color_dropdown.get()
    text_box.config(fg=selected_color)
    lbl_color.config(text=f"Font:\n{selected_color}")

def call_groq_api(text):
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not found. Please set the environment variable.")

    headers = {
        "Authorization":f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    return headers

def summary_results(text, parent_window):
    try:
        headers = call_groq_api(text)
        data = {
            "model": "llama-3.1-8b-instant",
            "messages" : [
                {"role": "system", "content": "You are a helpful assistant that summarizes text."},
                {"role": "user", "content": f"Summarize this text:\n{text}"}
            ],
            "temperature": 0.3,
            "max_tokens": 300
        }
        response = requests.post(GROQ_API_URL, headers=headers, data = json.dumps(data))
        response.raise_for_status()

        result = response.json()
        summary = result["choices"][0]["message"]["content"]

        parent_window.after(0, lambda: display_summary_window(parent_window, summary))

    except ValueError as e:
        messagebox.showerror("Error", str(e))
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Network Error", f"Failed to connect to the API: {e}")
    except KeyError:
        messagebox.showerror("API Error", "The API response was not in the expected format.")
    except Exception as e:
        messagebox.showerror("An unexpected error occurred", f"Failed to summarize: {e}")

def display_summary_window(parent_window, summary):
    summary_window = tk.Toplevel(parent_window)
    summary_window.title("Summary")

    summary_text = tk.Text(summary_window, wrap="word", font="Arial 12", bg="#f7f7f7", fg="Black")
    summary_text.insert(tk.END, summary)
    summary_text.config(state="disabled") 
    
    scrollbar = ttk.Scrollbar(summary_window, command=summary_text.yview)
    summary_text.config(yscrollcommand=scrollbar.set)
    
    summary_text.pack(side="left", expand=True, fill="both")
    scrollbar.pack(side="right", fill="y")

def summarize_text(text_box, parent_window):
    text = text_box.get("1.0", tk.END).strip()
    if not text:
        messagebox.showwarning("There is no text to summarize.")
        return 0

    thread = threading.Thread(target=summary_results, args=(text, parent_window))
    thread.daemon = True
    thread.start()

def sentiment_analysis_results(text, parent_window):
    headers = call_groq_api(text)
    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that performs detailed sentiment analysis."},
            {"role": "user", "content": f"Analyze the sentiment of this text. Indicate whether it is positive, negative, or neutral, and explain why:\n{text}"}
        ],
        "temperature": 0.3,
        "max_tokens": 300
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, data=json.dumps(data))
        response.raise_for_status()

        result = response.json()
        sentiment = result["choices"][0]["message"]["content"]
        parent_window.after(0, lambda: display_sentiment_window(parent_window, sentiment))
    except ValueError as e:
        messagebox.showerror("Error", str(e))
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Network Error", f"Failed to connect to the API: {e}")
    except KeyError:
        messagebox.showerror("API Error", "The API response was not in the expected format.")
    except Exception as e:
        messagebox.showerror("An unexpected error occurred", f"Failed to analyze: {e}")


def display_sentiment_window(parent_window, analysis):
    analysis_window = tk.Toplevel(parent_window)
    analysis_window.title("Sentiment Analysis")

    analysis_text = tk.Text(analysis_window, wrap="word", font="Arial 12", bg="#f7f7f7", fg="Black")
    analysis_text.insert(tk.END, analysis)
    analysis_text.config(state="disabled") 
    
    scrollbar = ttk.Scrollbar(analysis_window, command=analysis_text.yview)
    analysis_text.config(yscrollcommand=scrollbar.set)
    
    analysis_text.pack(side="left", expand=True, fill="both")
    scrollbar.pack(side="right", fill="y")

def analyze_sentiment(text_box, parent_window):
    text = text_box.get("1.0", tk.END).strip()
    if not text:
        messagebox.showwarning("There is no text to analyze for sentiment.")
        return 0

    thread = threading.Thread(target=sentiment_analysis_results, args=(text, parent_window))
    thread.daemon = True
    thread.start()

def generate_ai_rewrite(text, tone, max_tokens = 512):
    headers = call_groq_api(text)
    preset = Tone_Options.get(tone, Tone_Options["Simple"])
    system_msg = (
        "You are an assistant that rewrites text. "
        "When asked to rewrite, output ONLY the rewritten text with no extra commentary or labels. "
        "Preserve the original meaning and do not invent facts."
    )
    user_prompt = (
        f"Rewrite the following text in a {tone} tone.\n\n"
        f"Instructions: {preset['instruction']}\n\n"
        f"Text to rewrite:\n\n{text}"
    )
    
    data = {
        "model": "llama-3.1-8b-instant",
        "messages" : [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": preset["temperature"],
        "max_tokens": max_tokens
    }
    
    response = requests.post(GROQ_API_URL, headers=headers, data=json.dumps(data), timeout=60)
    response.raise_for_status()
    j = response.json()

    return j["choices"][0]["message"]["content"].strip()

def main_thread_callback(parent_window, result=None, error=None, selection_indices=None, working_window=None):
    if working_window:
        try:
            working_window.destroy()
        except tk.TclError:
            pass
    
    btn_paraphrase.config(state=tk.NORMAL)

    if error:
        messagebox.showerror("Paraphrase error", f"Failed to paraphrase: {error}")
    elif result:
        display_paraphrase_result(parent_window, result, selection_indices)

def display_paraphrase_result(parent_window, rewritten_text, selection_indices):
    paraphrase_window = tk.Toplevel(parent_window)
    paraphrase_window.title("Paraphrase Result")

    txt = tk.Text(paraphrase_window, wrap="word", font=("Arial", 12))
    txt.insert("1.0", rewritten_text)
    txt.pack(expand=True, fill="both", padx=8, pady=8)

    def replace_selection():
        if selection_indices:
            start_idx, end_idx = selection_indices
            text_box.delete(start_idx, end_idx)
            text_box.insert(start_idx, rewritten_text)
        else:
            text_box.delete("1.0", tk.END)
            text_box.insert("1.0", rewritten_text)
        paraphrase_window.destroy()

    def insert_at_cursor():
        text_box.insert(tk.INSERT, rewritten_text)
        paraphrase_window.destroy()

    def copy_to_clipboard():
        window.clipboard_clear()
        window.clipboard_append(rewritten_text)

    btn_frame = tk.Frame(paraphrase_window)
    btn_frame.pack(fill="x", pady=6)

    tk.Button(btn_frame, text="Replace Selection / Document", command=replace_selection).pack(side="left", padx=6)
    tk.Button(btn_frame, text="Insert at Cursor", command=insert_at_cursor).pack(side="left", padx=6)
    tk.Button(btn_frame, text="Copy", command=copy_to_clipboard).pack(side="left", padx=6)
    tk.Button(btn_frame, text="Close", command=paraphrase_window.destroy).pack(side="right", padx=6)

def paraphrase_button_clicked(parent_window):
    try:
        sel_ranges = text_box.tag_ranges("sel")
    except tk.TclError:
        sel_ranges = ()

    if sel_ranges:
        start_idx, end_idx = sel_ranges
        source_text = text_box.get(start_idx, end_idx).strip()
        selection_indices = (start_idx, end_idx)
    else:
        source_text = text_box.get("1.0", tk.END).strip()
        selection_indices = None

    if not source_text:
        messagebox.showinfo("Paraphrase", "No text selected and document is empty.")
        return

    tone = tone_dropdown.get()

    btn_paraphrase.config(state=tk.DISABLED)
    working_window = tk.Toplevel(window)
    working_window.transient(window)
    working_window.title("Working...")
    tk.Label(working_window, text="Paraphrasing...").pack(padx=20, pady=20)
    working_window.update()

    def worker():
        rewritten = generate_ai_rewrite(source_text, tone, max_tokens=1024)
        window.after(0, lambda: main_thread_callback(parent_window=parent_window, result=rewritten, selection_indices=selection_indices, working_window=working_window))
    
    threading.Thread(target=worker, daemon=True).start()


#Code for the window
window = tk.Tk()
window.title("Text Editor")
window.configure(bg='#404d44')

fr_buttons = tk.Frame(master=window, bg='#404d44')
fr_buttons.pack(side="top", fill="x")

text_box = tk.Text(master=window, font="Arial 12", bg="#e6f0e9", fg="black")
text_box.pack(expand=True, fill="both")

text_box.bind("<KeyPress>", count)
text_box.bind("<KeyRelease>", count)
text_box.focus_set()
text_box.config(insertbackground="black")

btn_open = tk.Button(master=fr_buttons, text="Open", width=10, bg='#91a18d', command=open_file)
btn_open.pack(side="left", padx=5, pady=5)

btn_save_as = tk.Button(master=fr_buttons, text="Save As", width=10, bg="#91a18d", command=save_file_as)
btn_save_as.pack(side="left", padx=5, pady=5)

btn_save = tk.Button(master=fr_buttons, text="Save", width=10, bg="#91a18d", command=save_file)
btn_save.pack(side="left", padx=5, pady=5)

btn_summarize = tk.Button(master=fr_buttons, text="Summarize Page", width=10, bg='#91a18d', command= lambda: summarize_text(text_box, window))
btn_summarize.pack(side="left", padx=5, pady=5)

btn_sentiment_analysis = tk.Button(master=fr_buttons, text="Sentiment Analysis Page", width=15, bg='#91a18d', command= lambda: analyze_sentiment(text_box, window))
btn_sentiment_analysis.pack(side="left", padx=5, pady=5)

btn_paraphrase = tk.Button(fr_buttons, text="Paraphrase", command= lambda: paraphrase_button_clicked(parent_window=window), bg="#91a18d")
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
font_dropdown.bind("<<ComboboxSelected>>", change_font)
font_dropdown.pack(side="left", padx=5, pady=5)

color_list = ["Black", "Red", "Blue", "Green", "Purple", "Yellow", "Pink", "Orange", "White", "Gray"]
max_color_length = 0
for color in color_list:
    if len(color) > max_color_length:
        max_color_length = len(color)
color_dropdown = ttk.Combobox(fr_buttons, values=color_list, state="readonly", width=max_color_length)
color_dropdown.set("Black")
color_dropdown.bind("<<ComboboxSelected>>", change_color)
color_dropdown.pack(side="left", padx=5, pady=5)

max_tone_length = 0
tone_list = Tone_Options.keys()
for tone in tone_list:
    if len(tone) > max_tone_length:
        max_tone_length = len(tone)
tone_dropdown = ttk.Combobox(fr_buttons, values=list(Tone_Options.keys()), state="readonly", width=max_tone_length)
tone_dropdown.set("Simple")
tone_dropdown.pack(side="left", padx=5, pady=5)

window.mainloop()