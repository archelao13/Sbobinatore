# utils.py
import tkinter as tk

def show_loading_window(root):
    loading_window = tk.Toplevel(root)
    loading_window.title("Caricamento...")
    loading_window.geometry("300x100")
    loading_label = tk.Label(loading_window, text="Elaborazione in corso, attendere...")
    loading_label.pack(pady=20)
    loading_window.grab_set()
    return loading_window
