document.addEventListener("DOMContentLoaded", () => {
  const searchInput = document.getElementById("search-input");
  const searchButton = document.querySelector("button");

  searchButton.addEventListener("click", () => {
    searchAlbums();
  });

  searchInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault(); // Prevent form submission if inside a form
      searchAlbums();
    }
  });

  searchInput.focus();
});

async function searchAlbums() {
  const searchInput = document.getElementById("search-input");
  const searchButton = document.querySelector("button");
  const searchTypeSelect = document.getElementById("search-type");

  const releaseDateInput = document.getElementById("release-date");
  const minDurationInput = document.getElementById("min-duration");
  const maxDurationInput = document.getElementById("max-duration");

  const searchType = searchTypeSelect?.value;
  const searchTerm = searchInput?.value.trim();

  const releaseDate = releaseDateInput?.value;
  const minDuration = minDurationInput?.value * 60000; // Convert to milliseconds
  const maxDuration = maxDurationInput?.value * 60000; // Convert to milliseconds

  if (!searchTerm || searchType === "none") {
    alert(`Pease enter a valid parameter to search for ${searchType}.`);
    return;
  }

  let queryParams = `${encodeURIComponent(searchTerm)}`;
  if (releaseDate)
    queryParams += `&release_date=${encodeURIComponent(releaseDate)}`;
  if (minDuration)
    queryParams += `&min_duration=${encodeURIComponent(minDuration)}`;
  if (maxDuration)
    queryParams += `&max_duration=${encodeURIComponent(maxDuration)}`;

  try {
    searchButton.disabled = true;
    searchInput.disabled = true;
    searchTypeSelect.disabled = true;

    let response;
    switch (searchType) {
      case "artists":
        response = await fetch(`/artist/${encodeURIComponent(searchTerm)}`);
        break;
      case "albums":
        response = await fetch(`/albums/${queryParams}`);
        break;
      case "tracks":
        response = await fetch(`/tracks/${encodeURIComponent(searchTerm)}`);
        break;
      default:
        throw new Error("Invalid search type.");
    }

    const data = await response.json();
    if (response.ok) {
      // displayAlbums(data);
      searchInput.value = "";
      releaseDateInput.value = "";
      minDurationInput.value = "";
      maxDurationInput.value = "";

      console.log(data);
    } else alert(data.detail ?? "Oops! Something failed. Please try again.");
  } catch (error) {
    console.error("Error:", error);
    alert(`Could not retrieve ${searchType}. Please try again later.`);
  } finally {
    searchTypeSelect.disabled = false;
    searchButton.disabled = false;
    searchInput.disabled = false;

    searchTypeSelect.disabled = false;
    releaseDateInput.disabled = false;
    minDurationInput.disabled = false;
    maxDurationInput.disabled = false;
    searchInput.focus();
  }
}

function displayAlbums(data) {
  const albumsContainer = document.getElementById("albums");
  albumsContainer.innerHTML = ""; // Clear any existing content

  if (data.albums.length === 0) {
    albumsContainer.innerHTML = "<p>No albums found for this artist.</p>";
    return;
  }

  data.albums &&
    data.albums.forEach((album) => {
      const albumElement = document.createElement("div");
      albumElement.classList.add("album");

      const discs = groupTracksByDisc(album.tracks);

      const discSections = discs
        .map(
          (disc) => `
      <div class="disc-section">
          <h3>Disc ${disc.discNumber}</h3>
          <div class="track-list">
              ${disc.tracks
                .map(
                  (track) => `
                  <div class="track">
                      <div class="track-number">${track.number}</div>
                      <div class="track-name">${track.name}</div>
                      <div class="track-time">${(
                        track.time_millis / 60000
                      ).toFixed(2)}
                      </div>
                      <div class="track-preview">
                          ${
                            track.preview_url
                              ? `
                          <audio class="audio-player" controls src="${track.preview_url}" />`
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

      albumElement.innerHTML = `
            <img src="${album.image_url.replace(
              "100x100",
              "600x600"
            )}" alt="Album Cover">
            <div class="album-info">
                <h2>${album.title}</h2>
                <p>${data.name}</p>
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
