import io
from fastapi import FastAPI, UploadFile, File
import librosa
import numpy as np
import tensorflow as tf

# Skapa FastAPI-applikationen
app = FastAPI()

# Ladda den tränade modellen (justera sökvägen till där din modell är sparad)
model = tf.keras.models.load_model(r'C:\Users\Admin\Desktop\final_emotion_model')

# Funktion för att extrahera MFCC från en ljudfil och platta dem (samma som träningskoden)
def extract_features(audio_data, sr=22050, n_mfcc=13, max_len=100):
    try:
        # Extrahera MFCC från ljuddata
        mfccs = librosa.feature.mfcc(y=audio_data, sr=sr, n_mfcc=n_mfcc)
        
        # Trimma eller padda MFCC till en fast längd (100 tidssteg här)
        if mfccs.shape[1] > max_len:
            mfccs = mfccs[:, :max_len]
        else:
            pad_width = max_len - mfccs.shape[1]
            mfccs = np.pad(mfccs, pad_width=((0, 0), (0, pad_width)), mode='constant')
        
        # Transponera MFCC så att formen är (100, 13) och platta ut för att skapa en vektor
        mfccs = mfccs.T.flatten()

        # Returnera den plattade MFCC-vektorn
        return mfccs
    
    except Exception as e:
        print(f"Error processing audio: {e}")
        return None

# Funktion för att förutsäga humöret baserat på ljuddata
def predict_mood(audio_data):
    # Extrahera MFCC-funktioner från ljuddata
    features = extract_features(audio_data)
    if features is None:
        return "unknown"

    # Normalisera MFCC-funktionerna (samma som i träningskoden)
    features = np.array(features)
    features = (features - np.mean(features)) / np.std(features)

    # Lägg till en batch-dimension för att få formen (1, feature_length)
    features = np.expand_dims(features, axis=0)
    
    # Gör en prediktion med modellen
    prediction = model.predict(features)

    # Logga prediktionerna för att se vad modellen förutsäger
    print(f"Model predictions (raw probabilities): {prediction}")

    # Hitta indexet för den högsta sannolikheten
    mood_index = np.argmax(prediction)
    
    # Mappning av prediktionen till ett humör (anpassa efter din modell och etiketter)
    mood_map = {0: "happy", 1: "neutral", 2: "surprised"}  # Anpassa efter dina etiketter

    return mood_map.get(mood_index, "unknown")

# Endpoint för att analysera röstfilen
@app.post("/analyze-voice/")
async def analyze_voice(file: UploadFile = File(...)):
    try:
        # Läs filens innehåll och omvandla till bytes
        contents = await file.read()
        
        # Använd librosa för att ladda ljudfilen från bytes
        audio_data, sr = librosa.load(io.BytesIO(contents), sr=22050)

        # Förutsäg humöret med hjälp av modellen
        mood = predict_mood(audio_data)

        # Hämta tillhörande Spotify-spellista baserat på det förutsagda humöret (anpassa denna funktion efter dina behov)
        playlist = get_playlist_for_mood(mood)

        return {
            "mood": mood,
            "playlist": playlist,
            "message": "Voice analyzed successfully!"
        }
    except Exception as e:
        return {"error": str(e)}

# Dummyfunktion för att mappa humör till Spotify-spellista (anpassa efter dina behov)
def get_playlist_for_mood(mood: str):
    playlists = {
        "happy": "spotify:playlist:Yhttps://open.spotify.com/playlist/6q3PaxFBRZQl3HfwvNN77B?si=b422b33227f74c39",  # Ersätt med din faktiska URI
        "neutral": "spotify:playlist:https://open.spotify.com/playlist/6cERoqY06r7n2oabXdqwCx?si=8751834d77ed4fc6",  # Ersätt med din faktiska URI
        "surprised": "spotify:playlist:https://open.spotify.com/playlist/6fU3w80Jnn6gpk6dyZGMce?si=65c5c04591804aaf"  # Ersätt med din faktiska URI
    }
    return playlists.get(mood, "spotify:playlist:YOUR_DEFAULT_PLAYLIST_URI")

