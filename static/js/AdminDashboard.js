window.onload = function () {
    loadAllBookings();
    loadCurrentUser();
};

function loadAllBookings() {

    fetch('/allbookings')
        .then(response => response.json())
        .then(bookingsList => {

            const bookingsTable = document.getElementById('all-bookings-table');
            bookingsTable.innerHTML = '';

            bookingsList
                .sort((firstBooking, secondBooking) =>
                    firstBooking.date.localeCompare(secondBooking.date)
                )
                .forEach(booking => {

                    const row = document.createElement('tr');

                    row.innerHTML = `
                        <td>${booking.date}</td>
                        <td>${booking.floor}</td>
                        <td>${booking.user}</td>
                        <td>${booking.bookingID}</td>
                        <td>
                            <button onclick="cancelBooking(${booking.bookingID})">
                                Cancel
                            </button>
                        </td>
                    `;

                    bookingsTable.appendChild(row);
                });
        })
        .catch(error => console.error("Failed to load bookings:", error));
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
        loadAllBookings();
    })
    .catch(error => {
        console.error(error);
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