document.addEventListener("DOMContentLoaded", () => {
  const artistInput = document.getElementById("artist-name");
  const searchButton = document.querySelector("button");

  searchButton.addEventListener("click", () => {
    searchAlbums();
  });

  artistInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault(); // Prevent form submission if inside a form
      searchAlbums();
    }
  });

  artistInput.focus();
});

async function searchAlbums() {
  const artistInput = document.getElementById("artist-name");
  const searchButton = document.querySelector("button");

  const artistName = artistInput?.value.trim();
  if (!artistName) {
    alert("Please enter an artist name.");
    return;
  }

  try {
    searchButton.disabled = true;
    artistInput.disabled = true;
    const response = await fetch(`/artist/${encodeURIComponent(artistName)}`);
    // const response = await fetch(
    //   `/albums/${encodeURIComponent(artistName)}`
    // );

    // const response = await fetch(`/tracks/${encodeURIComponent(artistName)}`);

    const data = await response.json();
    if (response.ok) {
      displayAlbums(data);
      artistInput.value = "";
    } else alert(data.detail ?? "Oops! Something failed. Please try again.");
  } catch (error) {
    console.error("Error:", error);
    alert("Could not retrieve albums. Please try again later.");
  } finally {
    searchButton.disabled = false;
    artistInput.disabled = false;
    artistInput.focus();
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
