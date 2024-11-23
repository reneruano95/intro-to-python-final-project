import logging
import re
from fastapi import FastAPI, HTTPException, Request, responses, templating, Query
from typing import Optional
from model.artist import Artist
from service.itunes import search_artist

logging.basicConfig(level=logging.INFO,
                   format='%(levelname)s: %(name)s - %(message)s')

templates = templating.Jinja2Templates(directory="templates")
app = FastAPI()

@app.get("/", response_class=responses.HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
@app.get("/artist/{name}")
def get_artist(
    name: str, 
    page: Optional[int] = Query(1, ge=1),
    page_size: Optional[int] = Query(3, ge=1, le=20)
):
    if match := re.search(r"([A-Za-z]{2,20})[^A-Za-z]*([A-Za-z]{0,20})", name.strip().lower()):
        artist_name = " ".join(match.groups())
        # Fetch more results than page_size to support pagination
        artist = search_artist(artist_name, page_size * 2)
        
        # Calculate pagination
        total_albums = len(artist.albums)  # Get total number of albums
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        # Create paginated response
        paginated_artist = Artist(
            name=artist.name,
            albums=artist.albums[start_idx:end_idx]
        )
        
        return {
            "artist": paginated_artist,
            "pagination": {
                "total": total_albums,  # Use total_albums instead of total_count
                "page": page,
                "page_size": page_size,
                "total_pages": -(-total_albums // page_size)  # Ceiling division
            }
        }
    else:
        raise HTTPException(
            status_code=400, detail=f"Invalid artist name: {name}")