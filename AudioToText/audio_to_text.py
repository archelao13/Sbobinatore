import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import speech_recognition as sr
from pydub import AudioSegment
import os
import threading
import openai

# Usa una variabile d'ambiente per la chiave API
openai_api_key = os.getenv("OPENAI_API_KEY")

# Funzione per mostrare la finestra di caricamento
def show_loading_window():
    loading_window = tk.Toplevel(root)
    loading_window.title("Caricamento...")
    loading_window.geometry("300x100")
    loading_label = tk.Label(loading_window, text="Elaborazione in corso, attendere...")
    loading_label.pack(pady=20)

    # Impedisce la chiusura della finestra di caricamento
    loading_window.grab_set()

    return loading_window

# Funzione per caricare il file audio
def load_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("Audio Files", "*.wav *.mp3 *.flac *.m4a")]
    )
    if file_path:
        status_label.config(text="File selezionato: " + file_path)
        root.update_idletasks()

        # Mostra il nome del file caricato in basso a destra
        loaded_file_label.config(text=os.path.basename(file_path))

        # Controllo se il file è già in formato WAV
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension == '.wav':
            # Se è WAV, parte subito la trascrizione
            threading.Thread(target=select_language_and_transcribe, args=(file_path,)).start()
        else:
            # Se non è WAV, chiedi se convertire il file
            ask_to_convert(file_path)

# Funzione per chiedere all'utente se desidera convertire il file
def ask_to_convert(file_path):
    convert_now = messagebox.askyesno("Conversione richiesta", "Il file non è in formato WAV. Vuoi convertirlo?")
    if convert_now:
        # Converti il file
        threading.Thread(target=convert_file, args=(file_path,)).start()
    else:
        status_label.config(text="Conversione annullata.")

# Funzione per convertire un file non WAV in WAV
def convert_file(file_path):
    loading_window = show_loading_window()  # Mostra la finestra di caricamento

    file_extension = os.path.splitext(file_path)[1].lower()
    audio = None

    # Converti il file audio in formato WAV
    if file_extension in ['.m4a', '.mp3', '.flac']:
        if file_extension == '.m4a':
            audio = AudioSegment.from_file(file_path, format="m4a")
        elif file_extension == '.mp3':
            audio = AudioSegment.from_mp3(file_path)
        elif file_extension == '.flac':
            audio = AudioSegment.from_file(file_path, format="flac")

        if audio:
            # Salva il file convertito come WAV
            wav_path = file_path.replace(file_extension, '.wav')
            audio.export(wav_path, format="wav")
            status_label.config(text="File convertito: " + wav_path)
            download_and_continue(wav_path)

    loading_window.destroy()  # Chiudi la finestra di caricamento

# Funzione per chiedere se continuare con la trascrizione dopo la conversione
def download_and_continue(wav_path):
    messagebox.showinfo("Conversione completata",
                        f"Il file è stato convertito in WAV: {wav_path}\nPuoi scaricarlo ora.")

    # Offri la possibilità di continuare con la trascrizione
    continue_transcription = messagebox.askyesno("Continuare con la trascrizione?",
                                                 "Vuoi procedere con la trascrizione?")
    if continue_transcription:
        threading.Thread(target=select_language_and_transcribe, args=(wav_path,)).start()

# Funzione per selezionare la lingua e avviare la trascrizione
def select_language_and_transcribe(file_path):
    language = language_var.get()
    if language:
        threading.Thread(target=convert_audio_to_text, args=(file_path, language)).start()
    else:
        messagebox.showwarning("Selezione lingua", "Per favore seleziona una lingua prima di continuare.")

# Funzione per trascrivere l'audio in blocchi di 10 secondi
def convert_audio_to_text(file_path, language):
    loading_window = show_loading_window()  # Mostra la finestra di caricamento
    recognizer = sr.Recognizer()
    transcription_summary = []  # Lista per riassunto puntato
    unclear_word_count = 0  # Contatore per parole non comprese

    try:
        with sr.AudioFile(file_path) as source:
            total_duration = source.DURATION  # Durata totale del file audio
            chunk_duration = 10  # Lunghezza del blocco in secondi
            current_offset = 0  # Inizio da 0 secondi

            # Imposta la barra di avanzamento
            progress_bar['maximum'] = total_duration

            # Processa in blocchi di 10 secondi
            while current_offset < total_duration:
                audio_data = recognizer.record(source, offset=current_offset, duration=chunk_duration)

                try:
                    # Trascrizione del blocco
                    text = recognizer.recognize_google(audio_data, language=language)  # Specifica la lingua selezionata
                    transcription_summary.append(text)  # Aggiunge il testo per il riassunto
                    # Aggiunge la trascrizione al widget Text
                    transcription_text.insert(tk.END, text + " ")
                    transcription_text.yview(tk.END)

                except sr.UnknownValueError:
                    unclear_word_count += 1  # Incrementa il contatore per le parole non comprese
                except sr.RequestError as e:
                    transcription_text.insert(tk.END, f"Errore con il servizio di trascrizione: {e}")
                    break

                # Aggiorna l'offset e la barra di avanzamento
                current_offset += chunk_duration
                progress_bar['value'] = current_offset

                # Aggiorna l'interfaccia grafica
                root.update_idletasks()

            # Riassunto della trascrizione
            summary_text = generate_summary(transcription_summary)
            transcription_summary_text.insert(tk.END, summary_text)  # Aggiorna la finestra del riassunto

            # Chiedi se salvare la trascrizione e il riassunto
            save_transcription(file_path, unclear_word_count)

            # Trascrizione completata
            status_label.config(text="Trascrizione completata")

    except ValueError as ve:
        status_label.config(text=f"Errore con il file audio: {ve}")

    loading_window.destroy()  # Chiudi la finestra di caricamento

# Funzione per generare un riassunto
def generate_summary(transcription):
    joined_text = " ".join(transcription)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"Fai un riassunto del seguente testo: {joined_text}"}
        ]
    )
    return response['choices'][0]['message']['content']

# Funzione per chiedere se salvare la trascrizione e il riassunto
def save_transcription(original_file_path, unclear_word_count):
    save_now = messagebox.askyesno("Salvare trascrizione?", "Vuoi salvare la trascrizione e il riassunto?")
    if save_now:
        transcription_file_name = os.path.splitext(original_file_path)[0] + "_trascrizione.txt"
        summary_file_name = os.path.splitext(original_file_path)[0] + "_riassunto.txt"

        with open(transcription_file_name, 'w', encoding='utf-8') as f:
            f.write(transcription_text.get(1.0, tk.END))  # Salva il contenuto del Text widget

        with open(summary_file_name, 'w', encoding='utf-8') as f:
            f.write(transcription_summary_text.get(1.0, tk.END))  # Salva il contenuto del riassunto

        messagebox.showinfo("Salvataggio completato",
                            f"Trascrizione salvata come {transcription_file_name}\nRiassunto salvato come {summary_file_name}\nParole non comprese: {unclear_word_count}")

# Creazione dell'interfaccia grafica
root = tk.Tk()
root.title("Audio to Text Converter")

# Stile simile a Spotify
root.configure(bg='#191414')  # Colore di sfondo simile a Spotify

# Variabile per la lingua
language_var = tk.StringVar(value='it-IT')  # Imposta l'italiano come lingua di default

# Bottone per selezionare il file audio
load_button = tk.Button(root, text="Carica Audio", command=load_file, bg="#1DB954", fg="white")
load_button.pack(pady=10)

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

# Esegui l'applicazione
root.mainloop()
