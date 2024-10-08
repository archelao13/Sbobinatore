import openai
from config import API_KEY

openai.api_key = API_KEY

def generate_summary(transcription):
    joined_text = " ".join(transcription)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"Fai un riassunto del seguente testo: {joined_text}"}
        ]
    )
    return response['choices'][0]['message']['content']

def save_transcription(original_file_path, unclear_word_count, transcription_text, transcription_summary_text):
    from tkinter import messagebox
    import os

    save_now = messagebox.askyesno("Salvare trascrizione?", "Vuoi salvare la trascrizione e il riassunto?")
    if save_now:
        transcription_file_name = os.path.splitext(original_file_path)[0] + "_trascrizione.txt"
        summary_file_name = os.path.splitext(original_file_path)[0] + "_riassunto.txt"

        with open(transcription_file_name, 'w', encoding='utf-8') as f:
            f.write(transcription_text.get(1.0, tk.END))

        with open(summary_file_name, 'w', encoding='utf-8') as f:
            f.write(transcription_summary_text.get(1.0, tk.END))

        messagebox.showinfo("Salvataggio completato",
                            f"Trascrizione salvata come {transcription_file_name}\nRiassunto salvato come {summary_file_name}\nParole non comprese: {unclear_word_count}")
