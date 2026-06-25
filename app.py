from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import sqlite3
from datetime import datetime, timedelta
import os
from models import get_db, comparePass, isAdmin, hash_password, register_user

app = Flask(__name__)
app.secret_key = "my-secret-key"

@app.route("/")
def index():
    return render_template("index.html")  # loads home page

@app.route("/admin-dashboard")
def admin_dashboard():
    if session.get('isAdmin') != 1:
        return redirect(url_for('standard_dashboard')) #loads standard dashboard if not an admin
    
    return render_template("AdminDashboard.html") #loads admin dashboard if user is admin

@app.route("/standard-dashboard")
def standard_dashboard():
    return render_template("StandardDashboard.html") #loads standard dashboard



@app.route("/login", methods=['POST', 'GET'])
def login():
    username = request.form.get('username', '').strip() #removes any spaces before or after username 
    userPassword = request.form.get('password', '').strip() #removes any spaces before or after password

    if comparePass(username, userPassword): #checks if the enteered password is correct 

        db = get_db()
        user = db.execute(
            "SELECT userID, isAdmin FROM users WHERE username = ?",
            (username,)).fetchone()

        session['userID'] = user['userID'] #stores userID in session
        session['username'] = username #stores username in session
        session['isAdmin'] = user['isAdmin'] #stores if the user is an admin in session

        if isAdmin(username):
            return redirect(url_for('admin_dashboard')) #if user is an admin, they are redirected to the admin dashboard
        else:
            return redirect(url_for('standard_dashboard')) #if user is not an admin, they are redirected to the standard dashboard
        
    return render_template('index.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.clear() #clears the user information from session, logging them out
    return jsonify({"message": "Logged out"})

@app.route('/currentuser')
def current_user():
    return jsonify({
        "username": session.get("username") #gets the username of the currently logged in user to be displayed in the dashboard
    })

@app.route("/register", methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}),400 #if register is blank, an error is thrown

    firstName = data.get('firstName', '').strip() #stores the first name from the input
    lastName = data.get('lastName', '').strip() #stores the last name from the input
    username = data.get('username', '').strip() #stores the username from the input
    password = data.get('password', '') #stores the password from the input

    if ' ' in username or ' ' in password: #checks if there are spaces in the username or password
        return jsonify({"error": "Username and password must not contain spaces."}), 400

    if not all([firstName, lastName, username, password]): #checks if the user has filled in all fields
        return jsonify({"error": "All fields are required."}), 400

    try:
        register_user(firstName, lastName, username, hash_password(password)) #adds the credentials and user details to the 'users' table
    except sqlite3.IntegrityError: #error for if a username that already exists is being registered
        return jsonify({"error": "Username already exists."}), 400 
    except Exception: #all other errors
        return jsonify({"error": "Registration failed due to server error."}), 500

    return jsonify({"message": "Registration successful!"}), 200 

@app.route("/floors") #returns all data about each floor and its availability on a date
def get_floors():
    date = request.args.get('date')

    if not date:
        date = datetime.today().strftime('%Y-%m-%d')

    db = get_db()

    floors = db.execute("""
        SELECT 
            f.floorID,
            f.floorName,
            fa.availableSpaces
        FROM carparkFloors f
        JOIN floorAvailability fa 
            ON f.floorID = fa.floorID
        WHERE fa.date = ?
    """, (date,)).fetchall()

    return jsonify([{
        "id": f["floorID"],
        "name": f["floorName"],
        "available": f["availableSpaces"]
    } for f in floors])

@app.route("/book", methods=['POST']) #allows a user to book a space
def book():
    data = request.get_json()

    floor_id = data['floorID']
    date = data['date']
    user_id = session.get('userID')

    db = get_db()

    # reduce availability
    db.execute("""
        UPDATE floorAvailability
        SET availableSpaces = availableSpaces - 1
        WHERE floorID = ? AND date = ? AND availableSpaces > 0
    """, (floor_id, date))

    #assigns the booking to the user
    db.execute("""
        INSERT INTO bookings (userID, parkingFloor, bookingDate)
        VALUES (?, ?, ?)
    """, (user_id, floor_id, date))

    db.commit()

    return jsonify({"message": "Booked successfully"})

@app.route('/cancelbooking', methods=['POST']) #allows the user to cancel a booking
def cancel_booking():

    data = request.get_json()

    bookingID = data['bookingID']

    db = get_db()

    booking = db.execute("""
        SELECT parkingFloor, bookingDate
        FROM bookings
        WHERE bookingID = ?                         
    """, (bookingID,)).fetchone()

    #updates floor availability 
    db.execute("""
        UPDATE floorAvailability
        SET availableSpaces = availableSpaces + 1
        WHERE floorID = ?
        AND date = ?           
    """, (booking['parkingFloor'], booking['bookingDate']))

    #booking removed from users active bookings
    db.execute("""
        DELETE FROM bookings
        WHERE bookingID = ?      
    """, (bookingID,))

    db.commit()

    return jsonify({"message": "Booking cancelled"})

    

@app.route('/mybookings') #returns all information about all bookings for a particular user
def my_bookings():

    user_id = session.get('userID')

    db = get_db()

    bookings = db.execute("""
        SELECT
            b.bookingID,
            f.floorName,
            b.bookingDate
        FROM bookings b
        JOIN carparkFloors f
            ON b.parkingFloor = f.floorID
        WHERE b.userID = ?
        ORDER BY b.bookingDate
    """, (user_id,)).fetchall()

    return jsonify([
        {
            "bookingID": booking["bookingID"],
            "floor": booking["floorName"],
            "date": booking["bookingDate"]
        }
        for booking in bookings
    ])

@app.route("/allbookings") #returns all information about all bookings from all users to be displayed in the admin dashboard
def all_bookings():

    db = get_db()

    rows = db.execute("""
        SELECT 
            b.bookingID,
            b.bookingDate,
            f.floorName,
            u.username
        FROM bookings b
        JOIN carparkFloors f ON b.parkingFloor = f.floorID
        JOIN users u ON b.userID = u.userID
        ORDER BY b.bookingDate
    """).fetchall()

    return jsonify([{
        "bookingID": r["bookingID"],
        "date": r["bookingDate"],
        "floor": r["floorName"],
        "user": r["username"]
    } for r in rows])

if __name__ == "__main__":
    app.run(debug=True)