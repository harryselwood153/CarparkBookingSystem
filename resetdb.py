import sqlite3
from datetime import datetime, timedelta
from models import hash_password

def init_db():
    db = sqlite3.connect("carpark.db")
    cursor = db.cursor()

    print("Starting reset...")

    cursor.executescript("""
    DROP TABLE IF EXISTS bookings;
    DROP TABLE IF EXISTS floorAvailability;
    DROP TABLE IF EXISTS carparkFloors;
    DROP TABLE IF EXISTS users;

    CREATE TABLE users (
        userID INTEGER PRIMARY KEY AUTOINCREMENT,
        firstName TEXT NOT NULL,
        lastName TEXT NOT NULL,
        username TEXT NOT NULL UNIQUE,
        userPassword TEXT NOT NULL,
        isAdmin BOOLEAN NOT NULL
    );

    CREATE TABLE carparkFloors (
        floorID INTEGER PRIMARY KEY AUTOINCREMENT,
        floorName TEXT NOT NULL,
        capacity INTEGER NOT NULL
    );

    CREATE TABLE floorAvailability (
        availabilityID INTEGER PRIMARY KEY AUTOINCREMENT,
        floorID INTEGER NOT NULL,
        date TEXT NOT NULL,
        availableSpaces INTEGER NOT NULL,
        UNIQUE(floorID, date)
    );

    CREATE TABLE bookings (
        bookingID INTEGER PRIMARY KEY AUTOINCREMENT,
        userID INTEGER NOT NULL,
        parkingFloor INTEGER NOT NULL,
        bookingDate TEXT NOT NULL
    );
    """)

    print("Schema created")

    # insert floors
    cursor.executemany("""
        INSERT INTO carparkFloors (floorName, capacity)
        VALUES (?, ?)
    """, [
        ("Floor 1", 15),
        ("Floor 2", 15),
        ("Floor 3", 15),
        ("Floor 4", 15),
        ("Floor 5", 15)
    ])

    print("Floors inserted")

    floors = cursor.execute("SELECT floorID, capacity FROM carparkFloors").fetchall()

    start = datetime.today()

    for i in range(31):
        day = (start + timedelta(days=i)).strftime("%Y-%m-%d")

        for f in floors:
            cursor.execute("""
                INSERT INTO floorAvailability (floorID, date, availableSpaces)
                VALUES (?, ?, ?)
            """, (f[0], day, f[1]))

    cursor.execute("""
    INSERT INTO users (firstName, lastName, username, userPassword, isAdmin)
    VALUES (?, ?, ?, ?, ?)
    """, ("Admin", "User", "AdminUser", hash_password("AdminPassword"), 1))

    db.commit()
    db.close()

    print("DATABASE READY")

init_db()
