# lyrics.ovh: Only the lyrics

Source of the website https://lyrics.ovh which allows you to find the lyrics for a song quickly and without ads.

A Chrome Extension is also available, thanks to Varal7: https://github.com/Varal7/lyrics-chrome-extension.

## API documentation

An API is available to get the lyrics of a song.
The documentation is available on Apiary.io: http://docs.lyricsovh.apiary.io/.

## How to start
```
npm install
node .
```

Then, you must uncomment the line 6 of `frontend/search.js`.

Finally you can open your browser and access http://localhost:8081 to reach the frontend (while the API is available at http://localhost:8080).
