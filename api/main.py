import logging
import re
import requests
from typing import Optional
from fastapi import FastAPI, HTTPException, Request, responses, templating, Query
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from model.artist import Artist
from model.album import Album
from service.itunes import (
    search_artists,
    search_albums,
    search_tracks,
    search_tracks_by_album,
)

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

# Define a regex pattern for name normalization
NAME_PATTERN = r"([A-Za-z]{2,20})[^A-Za-z]*([A-Za-z]{0,20})"

templates = templating.Jinja2Templates(directory="templates")
app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent.parent.absolute() / "static"),
    name="static",
)


@app.get("/", response_class=responses.HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
        },
    )


# API route to get a list of albums for an artist
@app.get("/artist/{name}")
def get_artist(
    name: str, page: int = Query(1, ge=1), page_size: int = Query(3, ge=1, le=20)
):
    if match := re.search(NAME_PATTERN, name.strip().lower()):
        artist_name = " ".join(match.groups())
        # Fetch more results than page_size to support pagination
        artist = search_artists(
            artist_name, page_size * 2
        )  # TODO: fetch more results with the advanced search
        # Calculate pagination
        total_albums = len(artist.albums)  # Get total number of albums
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size

        # Create paginated response
        paginated_artist = Artist(
            name=artist.name, albums=artist.albums[start_idx:end_idx]
        )

        return {
            "artist": paginated_artist,
            "pagination": {
                "total": total_albums,  # Use total_albums instead of total_count
                "page": page,
                "page_size": page_size,
                "total_pages": -(-total_albums // page_size),  # Ceiling division
            },
        }
    else:
        raise HTTPException(status_code=400, detail=f"Invalid artist name: {name}")


# Here we can add more API routes for other functionality, like:
# - API route to get a list of albums for a genre
# - API route to get a list of albums for a year
# - API route to get a list of albums for a decade


# - API route to get a list of albums by name
@app.get("/albums/")
def get_albums(
    album_name: str,
    release_year: Optional[int] = Query(
        None, description="Release year in YYYY format", ge=1900, le=2024
    ),
    genre: Optional[str] = Query(None, description="Genre of the album"),
    limit: int = Query(3, description="Maximum number of results", ge=1, le=100),
):
    """
    Search for albums with optional filtering and pagination.

    Args:
        album_name: Name of the album to search
        release_year: Filter by exact release year
        min_duration: Minimum track duration (in seconds)
        max_duration: Maximum track duration (in seconds)
        genre: Exact genre match
        limit: Maximum number of results to return

    Returns:
        List of matching albums
    """
    # Normalize album name using regex
    name_match = re.search(NAME_PATTERN, album_name.strip().lower())

    if not name_match:
        raise HTTPException(
            status_code=400, detail=f"Invalid album name format: {album_name}"
        )

    # Join matched name groups
    normalized_name = " ".join(name_match.groups())
    # print(f"Normalized Name: {normalized_name}")

    # Search albums from iTunes API
    try:
        albums = search_albums(normalized_name, limit)
        # print(f"Albums Retrieved: {albums}")
    except requests.RequestException as e:
        raise HTTPException(
            status_code=500, detail=f"Error searching iTunes API: {str(e)}"
        )

    # Filter albums based on additional criteria
    filtered_albums: list[Album] = []
    for album in albums:
        # print(f"Processing Album: {album}")
        # Release year filter (using release date)
        if release_year:
            release_date = album.release_date
            print(f"Release Date: {release_date}")
            album_year = int(release_date.split("-")[0]) if release_date else None
            print(f"Album Year: {album_year}")
            if not album_year or album_year != release_year:
                continue

        # Genre filter
        if genre:
            album_genre = album.genre.lower()
            # print(f"Album Genre: {album_genre}")
            if genre.lower() not in album_genre:
                continue

        filtered_albums.append(album)

    return filtered_albums


# - API route to get a list of tracks by name
@app.get("/tracks/{track_name}")
def get_tracks(track_name: str):

    # Here we would call the AlbumService to get a list of tracks

    if match := re.search(NAME_PATTERN, track_name.strip().lower()):
        tracks = search_tracks(track_name, 10)
        # print(tracks)
        return tracks
    else:
        raise HTTPException(status_code=400, detail=f"Invalid track name: {track_name}")


#  - API route to get a list of tracks by album
@app.get("/albums/{albumId}/tracks")
def get_tracks_by_album(albumId: str):
    # Here we would call the AlbumService to get a list of tracks
    tracks = search_tracks_by_album(albumId)
    return tracks
