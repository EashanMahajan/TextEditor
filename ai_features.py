import tkinter as tk
from tkinter import ttk, messagebox
import json
import requests
import threading

GROQ_API_KEY = None
GROQ_API_URL = None
Tone_Options = None
window = None
text_box = None
btn_paraphrase = None
tone_dropdown = None

def ai_references(api_key, api_url, tone_choices, wd, tb, paraphrase, tone_menu):
    global GROQ_API_KEY, GROQ_API_URL, Tone_Options, window, text_box, btn_paraphrase, tone_dropdown
    GROQ_API_KEY = api_key
    GROQ_API_URL = api_url
    Tone_Options = tone_choices
    window = wd
    text_box = tb
    btn_paraphrase = paraphrase
    tone_dropdown = tone_menu

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