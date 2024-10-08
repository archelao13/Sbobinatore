# Sbobinatore
Report dettagliato sull'applicazione
Nome dell'applicazione: Sbobinatore

Descrizione: L'applicazione "Audio to Text Converter" è progettata per convertire file audio in testo. Utilizza la libreria di riconoscimento vocale speech_recognition per trascrivere l'audio e l'API di OpenAI per generare riassunti del testo trascritto. L'interfaccia utente è sviluppata utilizzando Tkinter, fornendo un'interfaccia grafica intuitiva per l'utente.

Caratteristiche principali:

Caricamento Audio: L'utente può caricare file audio nei formati .wav, .mp3, o .m4a tramite un pulsante dedicato.
Selezione della Lingua: L'utente può selezionare la lingua di riconoscimento vocale tramite un menu a discesa (attualmente supporta italiano e inglese).
Trascrizione in Tempo Reale: L'audio viene trascritto in blocchi di 10 secondi, con l'aggiornamento in tempo reale della barra di avanzamento e dell'area di testo che mostra la trascrizione.
Riassunto del Testo: Una volta completata la trascrizione, l'applicazione genera un riassunto del testo utilizzando l'API di OpenAI.
Salvataggio della Trascrizione e del Riassunto: L'utente ha la possibilità di salvare sia la trascrizione che il riassunto in file di testo separati.
Interruzione del Processo: Un pulsante "Ferma" consente all'utente di interrompere l'operazione di trascrizione in qualsiasi momento.
Tecnologie utilizzate:

Librerie Python:
Tkinter per l'interfaccia grafica.
speech_recognition per il riconoscimento vocale.
openai per la generazione del riassunto.
Struttura dei file:
main.py: Punto di ingresso dell'applicazione.
gui.py: Contiene il codice per l'interfaccia utente.
audio_processing.py: Gestisce la logica di trascrizione e interazione con l'API di OpenAI.
Requisiti di installazione:

Python 3.x
Librerie necessarie specificate in requirements.txt.
