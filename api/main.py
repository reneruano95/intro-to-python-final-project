import logging
import re
from fastapi import FastAPI, HTTPException, Request, responses, templating
from model.artist import Artist
from service.AlbumService import AlbumService
from service.filecache import FileCacheAlbumService
from service.itunes import iTunesAlbumService

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(levelname)s: %(name)s - %(message)s')

# Configure HTML template engine
templates = templating.Jinja2Templates(directory="templates")

# Configure album services
AlbumService.init([FileCacheAlbumService(), iTunesAlbumService()])

app = FastAPI()


# Home page
@app.get("/", response_class=responses.HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# API - use api routes module
@app.get("/artist/{name}")
async def get_artist(name: str):
    if match := re.search(r"([A-Za-z]{2,20})[^A-Za-z]*([A-Za-z]{0,20})", name.strip().lower()):
        first, last = match.groups()
        artist = Artist(f"{first.capitalize()} {last.capitalize()}")
        await artist.get_albums(3)
        return artist
    else:
        raise HTTPException(
            status_code=400, detail=f"Invalid artist name: {name}")
