import tkinter as tk
from tkinter import ttk
import sounddevice as sd
import wavio as wv
from scipy.io.wavfile import write
import requests
import webbrowser

# Base URL för FastAPI-servern
API_URL = "http://127.0.0.1:8000/analyze-voice/"

# Spotify-URL
SPOTIFY_URL = "https://open.spotify.com/"

# Funktion för att öppna Spotify
def open_spotify(playlist=None):
    if playlist:
        webbrowser.open(playlist)  # Öppna den angivna Spotify-länken
    else:
        webbrowser.open(SPOTIFY_URL)  # Öppna standard Spotify-sidan

# Funktion för att skicka inspelad ljudfil till FastAPI och öppna Spotify automatiskt
def analyze_voice():
    file_path = "recording1.wav"
    
    try:
        # Skicka POST-anrop till FastAPI med ljudfilen som multipart-form-data
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(API_URL, files=files)
        
        # Hantera framgångsrik förfrågan
        if response.status_code == 200:
            result = response.json()
            mood = result.get("mood")
            playlist = result.get("playlist")
            
            # Uppdatera gränssnittet med humör och länk
            output_window.insert(tk.END, f"Detected Mood: {mood}\nPlaylist: {playlist}\n")
            
            # Ändra bakgrundsfärgen baserat på humöret (matcha FastAPI:s mappning)
            if mood == "happy":
                window.configure(bg='yellow')
            elif mood == "neutral":
                window.configure(bg='gray')
            elif mood == "surprised":
                window.configure(bg='orange')
            else:
                window.configure(bg='#5696b8')
            
            # Öppna Spotify automatiskt baserat på spellistan
            if playlist:
                open_spotify(playlist)
        else:
            output_window.insert(tk.END, f"Error analyzing voice. Status Code: {response.status_code}\n")
    
    except requests.exceptions.RequestException as e:
        output_window.insert(tk.END, f"Failed to send request: {str(e)}\n")

# Funktion för att spela in ljud
def record():
    freq = 44100
    duration = 5
    try:
        # Starta inspelningen
        recording = sd.rec(int(duration * freq), samplerate=freq, channels=2)
        sd.wait()
        
        # Spara inspelningen som recording1.wav
        write("recording0.wav", freq, recording)
        wv.write("recording1.wav", recording, freq, sampwidth=2)
        
        # Skicka inspelad fil till FastAPI-servern för analys
        analyze_voice()
    
    except Exception as e:
        output_window.insert(tk.END, f"Error recording audio: {str(e)}\n")

# Funktion för att cykla genom färger baserat på humör (manuellt)
def colorchange():
    global mood
    if mood > 3:
        mood = 0

    mood += 1
    if mood == 1:
        window.configure(bg='green')
    elif mood == 2:
        window.configure(bg='red')
    elif mood == 3:
        window.configure(bg='blue')
    else:
        window.configure(bg='#5696b8')

# Tkinter inställningar för fönstret
window = tk.Tk()
window.title('Emotion Detection')
window.geometry('360x800')
window.configure(bg='#5696b8')

# Skapa en meny och binda den till fönstret
menu = tk.Menu(window)
window.config(menu=menu)

# Lägga till menyalternativ
spotify_menu = tk.Menu(menu, tearoff=0)
spotify_menu.add_command(label="Open Spotify", command=open_spotify)
menu.add_cascade(label="Spotify", menu=spotify_menu)

# Lägga till en "About Us"-meny
about_menu = tk.Menu(menu, tearoff=0)
about_menu.add_command(label="About Us", command=lambda: print('This project was created by David Norman, Ming Fondberg, Muhannad Naser, and Parsan Amani'))
menu.add_cascade(label="About", menu=about_menu)

# Titel
title_label = ttk.Label(master=window,
                        text='Emotion Detection',
                        font='Calibri 24',
                        background='#5696b8',
                        foreground='black')
title_label.pack()

# Outputfält
output_frame = ttk.Frame(master=window)
output_window = tk.Text(master=output_frame, background='#1d4b63')
output_window.pack()
output_frame.pack()

# Inputfält och knappar
input_frame = ttk.Frame(master=window)
mood_btn = ttk.Button(master=input_frame, text='Cycle', command=colorchange)
record_btn = ttk.Button(master=input_frame, text='Record and Analyze', command=record)
spotify_btn = ttk.Button(master=input_frame, text='Open Spotify', command=open_spotify)

# Lägg till knapparna i gränssnittet
mood_btn.pack(side='left')
record_btn.pack(side='left')
spotify_btn.pack(side='left')  # Spotify-knappen för att öppna Spotify

input_frame.pack(pady=10, anchor='center', expand=True)

# Kör Tkinter-mainloop
window.mainloop()

