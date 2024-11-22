import logging
import re
from fastapi import FastAPI, HTTPException, Request, responses, templating
from model.artist import Artist
from service.itunes import search_artist, search_albums

"""
This is the main entry point for the application.

Here we configure app level services and routes, 
like logging and the template engine used to render the HTML pages.

We also initialize our AlbumService port, which is configured with
two adapters:
- FileCacheAlbumService, which uses the file system to cache albums that have been downloaded
- iTunesAlbumService, which uses the iTunes API to download new albums
"""

# Configure logging to show info level and above to the console, using our custom format
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(name)s - %(message)s")

# Configure the Jinja2 template engine
templates = templating.Jinja2Templates(directory="templates")

# Configure the FastAPI app to serve the API and the home page
app = FastAPI()


# Serves the home page at / using the Jinja2 template engine
@app.get("/", response_class=responses.HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# API route to get a list of albums for an artist
@app.get("/artist/{name}")
def get_artist(name: str):
    if match := re.search(
        r"([A-Za-z]{2,20})[^A-Za-z]*([A-Za-z]{0,20})", name.strip().lower()
    ):
        artist_name = " ".join(match.groups())
        # should we pass in the limit in the querystring?
        artist = search_artist(artist_name, 3)
        # print(artist)
        return artist
    else:
        raise HTTPException(status_code=400, detail=f"Invalid artist name: {name}")


# Here we can add more API routes for other functionality, like:
# - API route to get a list of albums for a genre
# - API route to get a list of albums for a year
# - API route to get a list of albums for a decade


# - API route to get a list of albums
@app.get("/albums/{album_name}")
def get_albums(album_name: str):
    # Here we would call the AlbumService to get a list of albums
    if match := re.search(
        r"([A-Za-z]{2,20})[^A-Za-z]*([A-Za-z]{0,20})", album_name.strip().lower()
    ):
        album_name = " ".join(match.groups())
        # should we pass in the limit in the querystring?
        albums = search_albums(album_name, 3)
        print(albums)
        return albums
    else:
        raise HTTPException(status_code=400, detail=f"Invalid album name: {album_name}")
