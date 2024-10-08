import tkinter as tk  # Importazione di Tkinter
import speech_recognition as sr
import openai
from tkinter import messagebox
import os  # Importazione di os per la gestione dei file

# Variabile globale per controllare l'esecuzione
is_running = True

# Funzione per fermare l'esecuzione
def stop_execution():
    global is_running
    is_running = False

# Funzione per mostrare la finestra di caricamento
def show_loading_window(root):
    loading_window = tk.Toplevel(root)
    loading_window.title("Caricamento...")
    loading_window.geometry("300x100")
    loading_label = tk.Label(loading_window, text="Elaborazione in corso, attendere...")
    loading_label.pack(pady=20)

    # Impedisce la chiusura della finestra di caricamento
    loading_window.grab_set()

    return loading_window

# Funzione per trascrivere l'audio in blocchi di 10 secondi
def convert_audio_to_text(file_path, language, root):
    global is_running
    loading_window = show_loading_window(root)  # Mostra la finestra di caricamento
    recognizer = sr.Recognizer()
    transcription_summary = []  # Lista per il riassunto puntato
    unclear_word_count = 0  # Contatore per parole non comprese

    try:
        with sr.AudioFile(file_path) as source:
            total_duration = source.DURATION  # Durata totale del file audio
            chunk_duration = 10  # Lunghezza del blocco in secondi
            current_offset = 0  # Inizio da 0 secondi

            # Imposta la barra di avanzamento
            root.progress_bar['maximum'] = total_duration

            # Processa in blocchi di 10 secondi
            while current_offset < total_duration and is_running:
                audio_data = recognizer.record(source, offset=current_offset, duration=chunk_duration)

                try:
                    # Trascrizione del blocco
                    text = recognizer.recognize_google(audio_data, language=language)  # Specifica la lingua selezionata
                    transcription_summary.append(text)  # Aggiunge il testo per il riassunto
                    # Aggiunge la trascrizione al widget Text
                    root.transcription_text.insert(tk.END, text + " ")
                    root.transcription_text.yview(tk.END)

                except sr.UnknownValueError:
                    unclear_word_count += 1  # Incrementa il contatore per le parole non comprese
                except sr.RequestError as e:
                    root.transcription_text.insert(tk.END, f"Errore con il servizio di trascrizione: {e}")
                    break

                # Aggiorna l'offset e la barra di avanzamento
                current_offset += chunk_duration
                root.progress_bar['value'] = current_offset

                # Aggiorna l'interfaccia grafica
                root.update_idletasks()

            # Riassunto della trascrizione
            if is_running:
                summary_text = generate_summary(transcription_summary)
                root.transcription_summary_text.insert(tk.END, summary_text)  # Aggiorna la finestra del riassunto

            # Chiedi se salvare la trascrizione e il riassunto
            save_transcription(file_path, unclear_word_count, root)

            # Trascrizione completata
            root.status_label.config(text="Trascrizione completata")

    except ValueError as ve:
        root.status_label.config(text=f"Errore con il file audio: {ve}")

    loading_window.destroy()  # Chiudi la finestra di caricamento
    is_running = True  # Reset della variabile globale

# Funzione per generare un riassunto
def generate_summary(transcription):
    joined_text = " ".join(transcription)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Fai un riassunto del seguente testo: {joined_text}"}]
    )
    return response['choices'][0]['message']['content']

# Funzione per chiedere se salvare la trascrizione e il riassunto
def save_transcription(original_file_path, unclear_word_count, root):
    save_now = messagebox.askyesno("Salvare trascrizione?", "Vuoi salvare la trascrizione e il riassunto?")
    if save_now:
        transcription_file_name = os.path.splitext(original_file_path)[0] + "_trascrizione.txt"
        summary_file_name = os.path.splitext(original_file_path)[0] + "_riassunto.txt"

        with open(transcription_file_name, 'w', encoding='utf-8') as f:
            f.write(root.transcription_text.get(1.0, tk.END))  # Salva il contenuto del Text widget

        with open(summary_file_name, 'w', encoding='utf-8') as f:
            f.write(root.transcription_summary_text.get(1.0, tk.END))  # Salva il contenuto del riassunto

        messagebox.showinfo("Salvataggio completato",
                            f"Trascrizione salvata come {transcription_file_name}\nRiassunto salvato come {summary_file_name}\nParole non comprese: {unclear_word_count}")

