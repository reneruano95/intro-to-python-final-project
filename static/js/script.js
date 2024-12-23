// Define variables in a scope that won't show on the page
const state = {
  currentPage: 1,
  pageSize: 5,
  currentArtist: "",
  totalPages: 0,
  currentView: "",
  currentData: null,
};

let sortOrder = "asc";

document.addEventListener("DOMContentLoaded", () => {
  const searchInput = document.getElementById("search-input");
  const searchButton = document.querySelector("button");
  const searchTypeSelect = document.getElementById("search-type");
  const advancedSearchContainer = document.getElementById("advanced-search");

  console.log("Document loaded");

  searchButton.addEventListener("click", () => {
    search();
  });

  document.getElementById("sort-button").addEventListener("click", () => {
    sortOrder = sortOrder === "asc" ? "desc" : "asc";
    const sortButton = document.getElementById("sort-button");
    sortButton.textContent = `Sort by Name (${
      sortOrder === "asc" ? "Asc" : "Desc"
    })`;
    console.log("Sorting results by name:", sortOrder);
    sortResultsByName(sortOrder);
  });

  searchInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault(); // Prevent form submission if inside a form
      state.currentPage = 1; // Reset page on new search
      search();
    }
  });

  searchTypeSelect.addEventListener("change", () => {
    if (searchTypeSelect.value === "albums") {
      advancedSearchContainer.style.display = "block";
    } else {
      advancedSearchContainer.style.display = "none";
    }
  });

  // Use event delegation to handle clicks on dynamically added .track elements
  document.getElementById("albums").addEventListener("click", (event) => {
    const trackElement = event.target.closest(".track");
    if (trackElement) {
      const artist = trackElement.dataset.artist;
      const song = trackElement.dataset.song;
      console.log(`Track clicked: artist=${artist}, song=${song}`);
      fetchLyrics(artist, song);
    }
  });

  searchInput.focus();
});

async function search() {
  const searchInput = document.getElementById("search-input");
  const searchButton = document.querySelector("button");
  const searchTypeSelect = document.getElementById("search-type");

  const releaseYearInput = document.getElementById("release-year");
  const genreInput = document.getElementById("genre");
  const limitInput = document.getElementById("limit");

  const searchType = searchTypeSelect?.value;
  const searchTerm = searchInput?.value.trim();

  const releaseYear = releaseYearInput?.value;
  const genre = genreInput?.value.trim();
  const limit = limitInput?.value;

  if (!searchTerm || searchType === "none") {
    alert(`Pease enter a valid parameter to search for ${searchType}.`);
    return;
  }

  let queryParams = buildQueryParams(searchTerm, releaseYear, genre, limit);

  state.currentArtist = searchTerm;
  state.searchType = searchType;
  state.searchTerm = searchTerm;

  console.log("Searching for", searchType, searchTerm, queryParams);

  try {
    disableSearchControls(true);

    searchButton.disabled = true;
    searchInput.disabled = true;
    searchTypeSelect.disabled = true;

    let response;
    switch (searchType) {
      case "artists":
        response = await fetch(
          `/artist/${encodeURIComponent(searchTerm)}${queryParams}`
        );
        break;
      case "albums":
        response = await fetch(`/albums/${queryParams}`);
        break;
      case "tracks":
        response = await fetch(
          `/tracks/${encodeURIComponent(searchTerm)}${queryParams}`
        );
        break;
      default:
        throw new Error("Invalid search type.");
    }

    const data = await response.json();
    if (response.ok) {
      handleSearchResults(searchType, data);
    } else
      alert(
        data.detail ??
          `Failed to retrieve ${searchType} for "${searchTerm}". Please try again.`
      );
  } catch (error) {
    console.error("Error:", error);

    alert(`Could not retrieve ${searchType}. Please try again later.`);
  } finally {
    disableSearchControls(false);

    searchInput.focus();
  }
}

function buildQueryParams(searchTerm, releaseYear, genre, limit) {
  let queryParams = `?album_name=${encodeURIComponent(searchTerm)}`;
  if (releaseYear) {
    queryParams += `&release_year=${encodeURIComponent(releaseYear)}`;
  }
  if (genre) {
    queryParams += `&genre=${encodeURIComponent(genre)}`;
  }
  if (limit) {
    queryParams += `&limit=${encodeURIComponent(limit)}`;
  }
  queryParams += `&page=${state.currentPage}&page_size=${state.pageSize}`;
  return queryParams;
}

function disableSearchControls(disable) {
  const searchButton = document.querySelector("button");
  const searchInput = document.getElementById("search-input");
  const searchTypeSelect = document.getElementById("search-type");

  searchButton.disabled = disable;
  searchInput.disabled = disable;
  searchTypeSelect.disabled = disable;
}

function handleSearchResults(searchType, data) {
  state.currentData = data; // Store the current data in state
  state.currentView = searchType; // Store the current view in state

  switch (searchType) {
    case "artists":
      displayArtists(data.artist);
      updatePagination(data.pagination);
      break;
    case "albums":
      displayAlbums(data.albums);
      updatePagination(data.pagination);
      break;
    case "tracks":
      displayTracks(data.tracks);
      updatePagination(data.pagination);
      break;
  }
}

function updatePagination(pagination) {
  const paginationContainer = document.getElementById("pagination");
  state.totalPages = pagination.total_pages;

  paginationContainer.innerHTML = `
    <button 
      onclick="changePage(${state.currentPage - 1})" 
      ${state.currentPage <= 1 ? "disabled" : ""}
    >Previous</button>
    <span class="pagination-info">Page ${state.currentPage} of ${
    state.totalPages
  }</span>
    <button 
      onclick="changePage(${state.currentPage + 1})" 
      ${state.currentPage >= state.totalPages ? "disabled" : ""}
    >Next</button>
  `;
}

async function changePage(newPage) {
  if (newPage >= 1 && newPage <= state.totalPages) {
    state.currentPage = newPage;
    await search();
    window.scrollTo(0, 0);
  }
}

function displayAlbums(data) {
  const albumsContainer = document.getElementById("albums");
  albumsContainer.innerHTML = ""; // Clear any existing content

  if (!data || data.length === 0) {
    albumsContainer.innerHTML = "<p>No albums found.</p>";
    return;
  }

  data.forEach((album, index) => {
    const albumElement = document.createElement("div");
    albumElement.classList.add("album");

    const discs = groupTracksByDisc(album.tracks);

    const discSections = discs
      .map(
        (disc) => `
      <div class="disc-section">
          <h3>Genre: ${album.genre}</h3>
          <div class="track-list">
              ${disc.tracks
                .map(
                  (track) => `
                  <div class="track">
                      <div class="track-number">${track.number}</div>
                      <div class="track-name">${track.name}</div>
                      <div class="track-time"><p class="card-text"><strong>Duration:</strong> ${formatTimeMillis(
                        track.time_millis
                      )}</p>
                      </div>
                      <div class="track-preview">
                          ${
                            track.preview_url
                              ? `<audio class="audio-player" controls src="${track.preview_url}" />`
                              : ""
                          }
                      </div>
                  </div>
              `
                )
                .join("")}
          </div>
      </div>
  `
      )
      .join("");

    const albumId = `album-${index}`;

    albumElement.innerHTML = `
              <button class="btn btn-link" type="button" data-bs-toggle="collapse" data-bs-target="#${albumId}" aria-expanded="false" aria-controls="${albumId}">
                  <img src="${album.image_url.replace(
                    "100x100",
                    "600x600"
                  )}" alt="Album Cover">
                  <div class="album-info">
                      <h2>${album.title}</h2>
                      <p>${album.artist_name}</p>
                  </div>
              </button>
              <div id="${albumId}" class="collapse">
                  ${discSections}
              </div>
          `;

    albumsContainer.appendChild(albumElement);
  });
}

function groupTracksByDisc(tracks) {
  const discs = {};

  tracks &&
    tracks.forEach((track) => {
      if (!discs[track.disc]) {
        discs[track.disc] = {
          discNumber: track.disc,
          tracks: [],
        };
      }
      discs[track.disc].tracks.push(track);
    });

  return Object.values(discs);
}

function displayTracks(data) {
  const albumsContainer = document.getElementById("albums");
  albumsContainer.innerHTML = ""; // Clear any existing content

  if (data.length === 0) {
    albumsContainer.innerHTML = "<p>No tracks found.</p>";
    return;
  }

  data.forEach((track) => {
    const trackElement = document.createElement("div");
    trackElement.className = "track";
    trackElement.dataset.artist = track.artist_name;
    trackElement.dataset.song = track.name;

    // console.log(trackElement.dataset.song);
    trackElement.innerHTML = `
      <div class="card-body">
        <h3 class="card-title">${track.name}</h3>
        <p class="card-text"><strong>Artist:</strong> ${track.artist_name}</p>
        <p class="card-text"><strong>Album:</strong> ${track.album_name}</p>
        <p class="card-text"><strong>Genre:</strong> ${track.genre}</p>
        
        <p class="card-text"><strong>Duration:</strong> ${formatTimeMillis(
          track.time_millis
        )}</p>
        <audio controls class="w-100">
          <source src="${track.preview_url}" type="audio/mpeg">
          Your browser does not support the audio element.
        </audio>
      </div>
    `;
    albumsContainer.appendChild(trackElement);
  });
}

function displayArtists(data) {
  const albumsContainer = document.getElementById("albums");
  albumsContainer.innerHTML = ""; // Clear any existing content

  if (!data || data.length === 0) {
    albumsContainer.innerHTML = "<p>No artists found.</p>";
    return;
  }

  data.forEach((artist, index) => {
    const artistElement = document.createElement("div");
    artistElement.classList.add("artist", "card", "mb-3");

    const artistId = `artist-${index}`;

    artistElement.innerHTML = `
      <div class="card-body">
        <h2 class="card-title d-flex justify-content-between">
          <a class="link-dark link-underline-opacity-0" data-bs-toggle="collapse" href="#${artistId}" role="button" aria-expanded="false" aria-controls="${artistId}">
            ${artist.name}
          </a>
          <div>(${artist.albums.length} albums)</div>
        </h2>
        <div class="collapse" id="${artistId}">
          <div class="card card-body">
            ${
              artist.albums.length === 0
                ? "<p>No albums found for this artist.</p>"
                : ""
            }
          </div>
        </div>
      </div>
    `;

    const collapseContainer = artistElement.querySelector(
      ".card-body .card-body"
    );

    if (artist.albums.length > 0) {
      artist.albums.forEach((album) => {
        const albumElement = document.createElement("div");
        albumElement.classList.add("album", "card", "mb-3");

        albumElement.innerHTML = `
          <button class="btn btn-link" type="button" data-bs-toggle="collapse" data-bs-target="#album-${
            album.id
          }" aria-expanded="false" aria-controls="album-${album.id}">
            <img src="${album.image_url.replace(
              "100x100",
              "600x600"
            )}" alt="Album Cover" class="img-fluid">
            <div class="album-info">
              <h3>${album.title}</h3>
              <p>Release Date: ${new Date(
                album.release_date
              ).toLocaleDateString()}</p>
            </div>
          </button>
          <div id="album-${
            album.id
          }" class="collapse tracks-container" style="display: none;"></div>
        `;

        albumElement.addEventListener("click", async () => {
          const tracksContainer =
            albumElement.querySelector(".tracks-container");
          if (tracksContainer.style.display === "none") {
            tracksContainer.style.display = "block";
            const tracks = await fetchAlbumTracks(album.id);
            displayTracksInAlbum(tracks, tracksContainer);
          } else {
            tracksContainer.style.display = "none";
          }
        });

        collapseContainer.appendChild(albumElement);
      });
    }

    albumsContainer.appendChild(artistElement);
  });
}

async function fetchAlbumTracks(albumId) {
  try {
    const response = await fetch(`/albums/${albumId}/tracks`);
    if (!response.ok) {
      throw new Error("Failed to fetch tracks");
    }
    return await response.json();
  } catch (error) {
    console.error("Error fetching tracks:", error);
    return [];
  }
}

function displayTracksInAlbum(tracks, container) {
  container.innerHTML = ""; // Clear any existing content

  if (!tracks || tracks.length === 0) {
    container.innerHTML = "<p>No tracks found for this album.</p>";
    return;
  }

  tracks.forEach((track) => {
    const trackElement = document.createElement("div");
    trackElement.classList.add("track");

    trackElement.innerHTML = `
      <div class="track-info">
        <p>${track.number}. ${track.name} (${(
      track.time_millis / 60000
    ).toFixed(2)} minutes)</p>
        ${
          track.preview_url
            ? `<audio class="audio-player" controls src="${track.preview_url}"></audio>`
            : ""
        }
      </div>
    `;

    container.appendChild(trackElement);
  });
}

function formatTimeMillis(timeMillis) {
  const minutes = Math.floor(timeMillis / 60000);
  const seconds = ((timeMillis % 60000) / 1000).toFixed(0);
  return `${minutes}:${seconds < 10 ? "0" : ""}${seconds}`;
}

async function fetchLyrics(artist, song) {
  try {
    const response = await fetch(
      `/lyrics/${encodeURIComponent(artist)}/${encodeURIComponent(song)}`
    );
    if (!response.ok) {
      throw new Error("Failed to fetch lyrics");
    }
    const lyricsHtml = await response.text();
    // console.log(lyricsHtml);

    // displayLyrics(lyricsHtml);
    displayLyricsInModal(lyricsHtml, artist, song);
  } catch (error) {
    console.error("Error fetching lyrics:", error);
    alert("Failed to fetch lyrics. Please try again later.");
  }
}

function displayLyrics(lyricsHtml) {
  const lyricsContainer = document.getElementById("lyrics-container");
  lyricsContainer.innerHTML = lyricsHtml;
  lyricsContainer.style.display = "block";
}

function cleanLyrics(lyricsHtml) {
  // Remove unnecessary spaces and add line breaks
  return lyricsHtml
    .replace(/<br\s*\/?>/g, "\n") // Replace <br> tags with newlines
    .replace(/\n\s*\n/g, "\n\n") // Remove multiple newlines
    .replace(/\n/g, "<br>"); // Replace newlines with <br> tags
}

function displayLyricsInModal(lyricsHtml, artist, song) {
  const lyricsModalLabel = document.getElementById("lyricsModalLabel");
  const lyricsModalBody = document.getElementById("lyrics-modal-body");

  lyricsModalLabel.textContent = `${artist} - ${song}`;
  lyricsModalBody.innerHTML = cleanLyrics(lyricsHtml);

  const lyricsModal = new bootstrap.Modal(
    document.getElementById("lyricsModal")
  );
  lyricsModal.show();
}

function sortResultsByName(order) {
  switch (state.currentView) {
    case "artists":
      sortArtistsByName(order);
      break;
    case "albums":
      sortAlbumsByName(order);
      break;
    case "tracks":
      sortTracksByName(order);
      break;
  }
}

function sortArtistsByName(order) {
  const artistsContainer = document.getElementById("albums");
  const artists = Array.from(artistsContainer.getElementsByClassName("artist"));

  artists.sort((a, b) => {
    const nameA = a.querySelector(".card-title a").textContent.toUpperCase();
    const nameB = b.querySelector(".card-title a").textContent.toUpperCase();

    if (order === "asc") {
      return nameA < nameB ? -1 : nameA > nameB ? 1 : 0;
    } else {
      return nameA > nameB ? -1 : nameA < nameB ? 1 : 0;
    }
  });

  artistsContainer.innerHTML = "";
  artists.forEach((artist) => artistsContainer.appendChild(artist));
}

function sortAlbumsByName(order) {
  const albumsContainer = document.getElementById("albums");
  const albums = Array.from(albumsContainer.getElementsByClassName("album"));

  albums.sort((a, b) => {
    const nameA = a.querySelector(".album-info h2").textContent.toUpperCase();
    const nameB = b.querySelector(".album-info h2").textContent.toUpperCase();

    if (order === "asc") {
      return nameA < nameB ? -1 : nameA > nameB ? 1 : 0;
    } else {
      return nameA > nameB ? -1 : nameA < nameB ? 1 : 0;
    }
  });

  albumsContainer.innerHTML = "";
  albums.forEach((album) => albumsContainer.appendChild(album));
}

function sortTracksByName(order) {
  const tracksContainer = document.getElementById("albums");
  const tracks = Array.from(tracksContainer.getElementsByClassName("track"));

  tracks.sort((a, b) => {
    const nameA = a.querySelector(".card-title").textContent.toUpperCase();
    const nameB = b.querySelector(".card-title").textContent.toUpperCase();

    if (order === "asc") {
      return nameA < nameB ? -1 : nameA > nameB ? 1 : 0;
    } else {
      return nameA > nameB ? -1 : nameA < nameB ? 1 : 0;
    }
  });

  tracksContainer.innerHTML = "";
  tracks.forEach((track) => tracksContainer.appendChild(track));
}
