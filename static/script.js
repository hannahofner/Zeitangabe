let currentStopId = null;
let currentStopName = null;
let allDepartures = [];
let displayedDepartures = [];
let itemsToShow = 10;

document.addEventListener('DOMContentLoaded', () => {
    loadFavourites();

    // Initialize Select2
    // Note: We use jQuery syntax here because Select2 depends on it
    $('#stopSelect').select2({
        placeholder: "Select a stop or type to search",
        allowClear: true
    });

    // Handle selection event from Select2
    $('#stopSelect').on('select2:select', function (e) {
        const data = e.params.data;
        // data.id is the value (stop ID), data.text is the name
        if (data.id) {
            currentStopName = data.text;
            loadDepartures(data.id);
        }
    });
});

function setStop(id, name) {
    // Helper for favourites clicks
    // Update Select2 selection if possible
    $('#stopSelect').val(id).trigger('change');

    currentStopName = name;
    loadDepartures(id);
}

async function loadDepartures(id) {
    const stopId = id;
    if (!stopId) return;

    currentStopId = stopId;

    const resultsArea = document.getElementById('resultsArea');
    const tbody = document.querySelector('#departuresTable tbody');
    const nameHeader = document.getElementById('currentStopName');
    const showMoreBtn = document.getElementById('showMoreBtn');

    nameHeader.innerText = `Departures for ${currentStopName}`;
    tbody.innerHTML = '<tr><td colspan="3">Loading...</td></tr>';
    resultsArea.classList.remove('hidden');
    showMoreBtn.classList.add('hidden');

    try {
        const response = await fetch(`/api/departures?stop_id=${stopId}`);
        const data = await response.json();

        allDepartures = data;
        itemsToShow = 10; // Reset pagination

        updateDirectionFilter(allDepartures);
        renderDepartures();

    } catch (err) {
        console.error(err);
        tbody.innerHTML = '<tr><td colspan="3">Error loading data</td></tr>';
    }
}

function updateDirectionFilter(data) {
    const filter = document.getElementById('directionFilter');
    const directions = new Set(data.map(d => d.direction));

    // Keep "All Directions"
    filter.innerHTML = '<option value="all">All Directions</option>';

    directions.forEach(dir => {
        const option = document.createElement('option');
        option.value = dir;
        option.innerText = dir;
        filter.appendChild(option);
    });
}

function filterDepartures() {
    itemsToShow = 10; // Reset pagination on filter change
    renderDepartures();
}

function showMore() {
    itemsToShow += 10;
    renderDepartures();
}

function renderDepartures() {
    const tbody = document.querySelector('#departuresTable tbody');
    const filterVal = document.getElementById('directionFilter').value;
    const showMoreBtn = document.getElementById('showMoreBtn');

    let filtered = allDepartures;
    if (filterVal !== 'all') {
        filtered = allDepartures.filter(d => d.direction === filterVal);
    }

    const toDisplay = filtered.slice(0, itemsToShow);

    tbody.innerHTML = '';
    if (toDisplay.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3">No departures found</td></tr>';
        showMoreBtn.classList.add('hidden');
        return;
    }

    toDisplay.forEach(dep => {
        const row = `
            <tr>
                <td>${dep.line}</td>
                <td>${dep.direction}</td>
                <td>${dep.countdown} min</td>
            </tr>
        `;
        tbody.innerHTML += row;
    });

    if (filtered.length > itemsToShow) {
        showMoreBtn.classList.remove('hidden');
    } else {
        showMoreBtn.classList.add('hidden');
    }
}

async function addToFavourites() {
    if (!currentStopId) return;

    try {
        const response = await fetch('/api/favourites', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ stop_id: currentStopId, stop_name: currentStopName })
        });

        if (response.ok) {
            loadFavourites();
            alert('Added to favourites!');
        } else {
            const msg = await response.json();
            if (msg.status === 'exists') alert('Already in favourites!');
            else alert('Failed to add.');
        }
    } catch (err) {
        console.error(err);
    }
}

async function loadFavourites() {
    const list = document.getElementById('favouritesList');
    list.innerHTML = '<li>Loading...</li>';

    try {
        const response = await fetch('/api/favourites');
        const favs = await response.json();

        list.innerHTML = '';
        if (favs.length === 0) {
            list.innerHTML = '<li>No favourites yet.</li>';
            return;
        }

        favs.forEach(fav => {
            const li = document.createElement('li');
            // Create a container for the stop info and the delete button
            const headerDiv = document.createElement('div');
            headerDiv.className = 'fav-header';

            headerDiv.innerHTML = `
                <span class="fav-link" onclick="setStop('${fav.stop_id}', '${fav.stop_name}')">
                    ${fav.stop_name}
                </span>
                <button class="delete-btn" onclick="removeFavourite(${fav.id})">X</button>
            `;

            // Create a container for the departures
            const departuresDiv = document.createElement('div');
            departuresDiv.className = 'fav-departures-container';
            departuresDiv.id = `fav-dep-${fav.stop_id}`;
            departuresDiv.innerText = 'Loading departures...';

            li.appendChild(headerDiv);
            li.appendChild(departuresDiv);
            list.appendChild(li);

            // Fetch departures for this favourite
            fetchAndRenderFavDepartures(fav.stop_id, departuresDiv);
        });
    } catch (err) {
        console.error(err);
        list.innerHTML = '<li>Error loading favourites.</li>';
    }
}

async function fetchAndRenderFavDepartures(stopId, container) {
    try {
        const response = await fetch(`/api/departures?stop_id=${stopId}`);
        const data = await response.json();

        if (!data || data.length === 0) {
            container.innerHTML = '<span style="font-style:italic;">No upcoming departures.</span>';
            return;
        }

        // Group by direction
        const byDirection = {};
        data.forEach(dep => {
            if (!byDirection[dep.direction]) {
                byDirection[dep.direction] = [];
            }
            byDirection[dep.direction].push(dep.countdown);
        });

        container.innerHTML = '';

        for (const [direction, times] of Object.entries(byDirection)) {
            // Take next 2 times
            const nextTimes = times.slice(0, 2).map(t => `${t} min`).join(', ');

            const row = document.createElement('div');
            row.className = 'fav-direction-row';

            row.innerHTML = `
                <span class="dir-name">${direction}</span>
                <span class="dir-times">${nextTimes}</span>
            `;

            container.appendChild(row);
        }

    } catch (err) {
        console.error(err);
        container.innerText = 'Error loading times.';
    }
}

async function removeFavourite(id) {
    if (!confirm('Remove this favourite?')) return;

    try {
        const response = await fetch(`/api/favourites/${id}`, { method: 'DELETE' });
        if (response.ok) {
            loadFavourites();
        }
    } catch (err) {
        console.error(err);
    }
}
