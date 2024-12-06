import requests
import logging
from fastapi import FastAPI, HTTPException, responses, Request
from fastapi.templating import Jinja2Templates
import urllib.parse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Configure FastAPI and Jinja2Templates
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# API route to fetch and display lyrics for a song
@app.get("/lyrics/{artist}/{song}", response_class=responses.HTMLResponse)
async def get_lyrics(request: Request, artist: str, song: str):
    try:
        # Encode artist and song names to handle special characters
        artist_encoded = urllib.parse.quote(artist)
        song_encoded = urllib.parse.quote(song)

        # Fetch lyrics using lyrics.ovh API
        response = requests.get(f"https://api.lyrics.ovh/v1/{artist_encoded}/{song_encoded}")
        response.raise_for_status()  # Raise an error if the request failed
        data = response.json()
        lyrics = data.get("lyrics", "Lyrics not found for this song.")

        # Render lyrics in a simple HTML template
        return templates.TemplateResponse("lyrics.html", {
            "request": request,
            "artist": artist,
            "song": song,
            "lyrics": lyrics.replace("\n", "<br>")  # Replace newlines with HTML line breaks
        })

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching lyrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch lyrics.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
