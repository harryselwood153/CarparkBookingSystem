window.onload = function () {
    loadFloors();
    getBookings();
    loadNextBooking();
    setTodayAsDefaultDate();
    loadCurrentUser();
};

function refresh() {
    loadFloors();
    getBookings();
    loadNextBooking();
}

function setTodayAsDefaultDate() {
    const input = document.getElementById("bookingDate");

    const today = new Date().toISOString().split('T')[0];

    input.value = today;
}

function getBookings() {

    fetch('/mybookings')
        .then(response => response.json())
        .then(bookings => {

            const table = document.getElementById('booking-table');

            table.innerHTML = '';

            bookings.forEach(booking => {

                const row = document.createElement('tr');

                row.innerHTML = `
                    <td>${booking.bookingID}</td>
                    <td>${booking.floor}</td>
                    <td>${booking.date}</td>
                    <td>
                        <button onclick="cancelBooking(${booking.bookingID})">
                            Cancel
                        </button>
                    </td>
                `;

                table.appendChild(row);
            });
        });
}

function cancelBooking(bookingID) {
    fetch('/cancelbooking', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            bookingID: bookingID
        })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);

        refresh();
    })
    .catch(error => {
        console.error(error);
    });
}

function loadFloors() {
    const date = document.getElementById("bookingDate").value 
                || new Date().toISOString().split('T')[0];

    fetch(`/floors?date=${date}`)
        .then(res => res.json())
        .then(data => {

            const table = document.getElementById("floor-table");
            table.innerHTML = "";

            data.forEach(floor => {
                const row = document.createElement("tr");

                row.innerHTML = `
                    <td>${floor.id}</td>
                    <td>${floor.name}</td>
                    <td>${floor.available}</td>
                    <td>
                        <button onclick="bookFloor(${floor.id})">
                            Book
                        </button>
                    </td>
                `;

                table.appendChild(row);
            });
        });
}

window.bookFloor = function (floorID) {
    const date = document.getElementById("bookingDate").value;

    fetch('/book', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            floorID: floorID,
            date: date
        })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
        refresh();
    });
};

function loadNextBooking() {

    fetch('/mybookings')
        .then(res => res.json())
        .then(bookings => {

            const container = document.getElementById('next-booking');
            container.innerHTML = '';

            const today = new Date().toISOString().split('T')[0];

            const upcoming = bookings
                .filter(b => b.date >= today)
                .sort((a, b) => a.date.localeCompare(b.date));

            if (upcoming.length === 0) {
                container.textContent = "No upcoming bookings";
                return;
            }

            const next = upcoming[0];

            container.innerHTML = `
                <strong>${next.date}</strong><br>
                ${next.floor}
            `;
        });
}

function loadCurrentUser() {
    fetch('/currentuser')
        .then(res => res.json())
        .then(data => {
            document.getElementById('current-user').innerText =
                data.username || "Not logged in";
        });
}

function logOut() {
    fetch('/logout', {
        method: 'POST'
    })
    .then(() => {
        window.location.href = '/';
    })
    .catch(error => {
        console.error('Logout failed:', error);
    });
}