import tkinter as tk
from gui import create_gui, stop_execution  # Importa la funzione per fermare l'esecuzione

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Audio to Text Converter")
    root.geometry("400x600")  # Imposta la dimensione della finestra
    root.configure(bg='#191414')  # Colore di sfondo

    create_gui(root)

    # Aggiungi un pulsante "Ferma" nella GUI
    stop_button = tk.Button(root, text="Ferma", command=stop_execution, bg="#FF3B30", fg="white")
    stop_button.pack(pady=10)

    root.mainloop()
