DROP TABLE IF EXISTS bookings;
DROP TABLE IF EXISTS floorAvailability;
DROP TABLE IF EXISTS carparkFloors;
DROP TABLE IF EXISTS users;

---------------------------------------------------
-- USERS
---------------------------------------------------
CREATE TABLE users (
    userID INTEGER PRIMARY KEY AUTOINCREMENT,
    firstName TEXT NOT NULL,
    lastName TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    userPassword TEXT NOT NULL,
    isAdmin BOOLEAN NOT NULL
);

---------------------------------------------------
-- FLOORS (STATIC)
---------------------------------------------------
CREATE TABLE carparkFloors (
    floorID INTEGER PRIMARY KEY AUTOINCREMENT,
    floorName TEXT NOT NULL,
    capacity INTEGER NOT NULL
);

---------------------------------------------------
-- DAILY AVAILABILITY
---------------------------------------------------
CREATE TABLE floorAvailability (
    availabilityID INTEGER PRIMARY KEY AUTOINCREMENT,
    floorID INTEGER NOT NULL,
    date TEXT NOT NULL,
    availableSpaces INTEGER NOT NULL,

    FOREIGN KEY (floorID) REFERENCES carparkFloors(floorID),
    UNIQUE(floorID, date)
);

---------------------------------------------------
-- BOOKINGS
---------------------------------------------------
CREATE TABLE bookings (
    bookingID INTEGER PRIMARY KEY AUTOINCREMENT,
    userID INTEGER NOT NULL,
    parkingFloor INTEGER NOT NULL,
    bookingDate TEXT NOT NULL,

    FOREIGN KEY (userID) REFERENCES users(userID),
    FOREIGN KEY (parkingFloor) REFERENCES carparkFloors(floorID)
);