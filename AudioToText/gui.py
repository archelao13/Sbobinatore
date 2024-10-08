import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
from audio_processing import convert_audio_to_text, stop_execution
import os

def create_gui(root):
    root.configure(bg='#191414')

    # Variabile per la lingua
    language_var = tk.StringVar(value='it-IT')

    # Bottone per selezionare il file audio
    load_button = tk.Button(root, text="Carica Audio", command=lambda: load_file(root, language_var), bg="#1DB954", fg="white")
    load_button.pack(pady=10)

    # Bottone per fermare l'esecuzione
    stop_button = tk.Button(root, text="Ferma", command=stop_transcription, bg="#FF3B30", fg="white")
    stop_button.pack(pady=10)

    # Label per lo stato
    status_label = tk.Label(root, text="", bg='#191414', fg='white')
    status_label.pack(pady=5)

    # Label per mostrare il nome del file caricato
    loaded_file_label = tk.Label(root, text="", bg='#191414', fg='white')
    loaded_file_label.pack(pady=5)

    # Menu a discesa per selezionare la lingua
    language_menu = ttk.Combobox(root, textvariable=language_var, values=["it-IT", "en-US"])
    language_menu.pack(pady=5)

    # Barre di avanzamento
    progress_bar = ttk.Progressbar(root, length=300, mode='determinate')
    progress_bar.pack(pady=10)

    # Area di testo per la trascrizione
    transcription_text = tk.Text(root, height=10, width=50, bg="#121212", fg="white")
    transcription_text.pack(pady=5)

    # Area di testo per il riassunto
    transcription_summary_text = tk.Text(root, height=10, width=50, bg="#121212", fg="white")
    transcription_summary_text.pack(pady=5)

    root.transcription_text = transcription_text
    root.transcription_summary_text = transcription_summary_text
    root.status_label = status_label
    root.progress_bar = progress_bar
    root.language_var = language_var
    root.loaded_file_label = loaded_file_label

def load_file(root, language_var):
    file_path = filedialog.askopenfilename(
        filetypes=[("Audio Files", "*.wav *.mp3 *.flac *.m4a")]
    )
    if file_path:
        root.status_label.config(text="File selezionato: " + file_path)
        root.update_idletasks()
        root.loaded_file_label.config(text=os.path.basename(file_path))

        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension == '.wav':
            threading.Thread(target=select_language_and_transcribe, args=(root, file_path)).start()
        else:
            ask_to_convert(root, file_path)

def ask_to_convert(root, file_path):
    convert_now = messagebox.askyesno("Conversione richiesta", "Il file non è in formato WAV. Vuoi convertirlo?")
    if convert_now:
        threading.Thread(target=convert_file, args=(root, file_path)).start()
    else:
        root.status_label.config(text="Conversione annullata.")

def convert_file(root, file_path):
    from pydub import AudioSegment

    file_extension = os.path.splitext(file_path)[1].lower()
    audio = None

    if file_extension in ['.m4a', '.mp3', '.flac']:
        if file_extension == '.m4a':
            audio = AudioSegment.from_file(file_path, format="m4a")
        elif file_extension == '.mp3':
            audio = AudioSegment.from_mp3(file_path)
        elif file_extension == '.flac':
            audio = AudioSegment.from_file(file_path, format="flac")

        if audio:
            wav_path = file_path.replace(file_extension, '.wav')
            audio.export(wav_path, format="wav")
            root.status_label.config(text="File convertito: " + wav_path)
            download_and_continue(root, wav_path)

def download_and_continue(root, wav_path):
    messagebox.showinfo("Conversione completata", f"Il file è stato convertito in WAV: {wav_path}\nPuoi scaricarlo ora.")
    continue_transcription = messagebox.askyesno("Continuare con la trascrizione?", "Vuoi procedere con la trascrizione?")
    if continue_transcription:
        threading.Thread(target=select_language_and_transcribe, args=(root, wav_path)).start()

def select_language_and_transcribe(root, file_path):
    language = root.language_var.get()
    if language:
        threading.Thread(target=convert_audio_to_text, args=(file_path, language, root)).start()
    else:
        messagebox.showwarning("Selezione lingua", "Per favore seleziona una lingua prima di continuare.")

def stop_transcription():
    stop_execution()  # Chiama la funzione per fermare l'esecuzione

