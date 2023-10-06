import threading
import speech_recognition as sr
from googletrans import Translator
import tkinter as tk
from tkinter import ttk, filedialog, Text, Scrollbar
import logging

listening = False


def start_listen():
    global listening
    if not listening:
        listening = True
        threading.Thread(target=speech_recognition_loop, daemon=True).start()


def stop_listen():
    global listening
    listening = False


def save_translations():
    with filedialog.asksaveasfile(mode='w', defaultextension=".txt") as f:
        f.write(text_widget.get(1.0, tk.END))


def parse_google_recognition(text):
    parsed_text = text.get("alternative")
    if parsed_text:
        return parsed_text[0].get("transcript")
    return None


def speech_recognition_loop():
    """Main loop for speech recognition and translation."""
    global listening

    r = sr.Recognizer()
    translator = Translator()
    src_language = source_language_combobox.get()
    dest_language = dest_language_combobox.get()

    try:
        with sr.Microphone(chunk_size=8192) as source:
            r.adjust_for_ambient_noise(source)
            append_to_window("Listening... Press 'Stop Listening' to stop.")
            while listening:
                audio = r.listen(source)
                try:
                    text = r.recognize_google(audio, show_all=True)
                    if text:
                        transcript = parse_google_recognition(text)
                        if transcript:
                            translated = translator.translate(
                                transcript, src=src_language, dest=dest_language)
                            output = f"Original: {transcript}\n\nTranslated: {translated.text}"
                            append_to_window(output, is_translation=True)
                except sr.UnknownValueError:
                    append_to_window('Could not understand audio.')
                except sr.RequestError as e:
                    append_to_window(f"API Error: {e}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        append_to_window(f"An error occurred: Check logs for more info.")


def append_to_window(text, is_translation=False):
    text_widget.insert(tk.END, text + '\n')
    if is_translation:
        text_widget.tag_add("translation", "end-2c linestart", "end-1c")
        text_widget.see(tk.END)


def create_combobox(frame, label_text, row, default_value):
    ttk.Label(frame, text=label_text).grid(row=row, column=0)
    combobox = ttk.Combobox(
        frame, values=["en", "fr", "es", "de"], state="readonly")
    combobox.set(default_value)
    combobox.grid(row=row, column=1, padx=10, pady=10)
    return combobox


def main():
    global text_widget, source_language_combobox, dest_language_combobox

    root = tk.Tk()
    root.title('Speech Recognition and Translation')
    frame = ttk.Frame(root)
    frame.grid(row=0, column=0, padx=10, pady=10)

    # GUI elements using utility function
    source_language_combobox = create_combobox(
        frame, "Source Language:", 0, "en")
    dest_language_combobox = create_combobox(
        frame, "Destination Language:", 1, "fr")

    start_button = tk.Button(
        frame, text="Start Listening", command=start_listen)
    start_button.grid(row=2, column=0, padx=10, pady=10)

    stop_button = tk.Button(frame, text="Stop Listening", command=stop_listen)
    stop_button.grid(row=2, column=1, padx=10, pady=10)

    ttk.Button(frame, text="Save Translations", command=save_translations).grid(
        row=3, column=0, columnspan=2, padx=10, pady=10)

    scrollbar = ttk.Scrollbar(root)
    scrollbar.grid(row=1, column=1, sticky='ns')

    text_widget = Text(root, wrap=tk.WORD, yscrollcommand=scrollbar.set)
    text_widget.grid(row=1, column=0, sticky='nsew')
    text_widget.tag_configure("bold", font=("Helvetica", 12, "bold"))
    text_widget.tag_configure("translation", foreground="dark blue")
    scrollbar.config(command=text_widget.yview)

    root.mainloop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)  # Logging setup
    main()
