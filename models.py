import sqlite3
import bcrypt

def get_db(): #establishes a connection with the SQLite database
    db = sqlite3.connect("carpark.db")
    db.row_factory = sqlite3.Row
    return db

def get_availability(): #returns the availability for a carpark floor
    db = get_db()
    floors = db.execute("SELECT * FROM carparkFloors").fetchall()
    db.close

    result = []
    for floor in floors:
        result.append({
            "id": floor["floorID"],
            "name": floor["floorName"],
            "capacity": floor['capacity'],
            "available": floor["availableSpaces"]
        })

    return result

def comparePass(username, userPassword): #checks the password in the login section to see if it is correct
    db = get_db()
    result = db.execute('SELECT userPassword FROM users WHERE username = ?', (username,)).fetchone()
    if not result:
        return False

    storedHash = result['userPassword'].encode('utf-8')
    user_bytes = userPassword.encode('utf-8')

    return bcrypt.checkpw(user_bytes, storedHash)

def hash_password(passwordInput): #hashes a password to ensure security
    user_bytes = passwordInput.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(user_bytes, salt)
    return hashed.decode('utf-8') #returns the hashed password to where the function is called

def isAdmin(username): #returns whether the user is an administrator user or not
    db = get_db()
    user = db.execute('SELECT isAdmin FROM users WHERE username = ?', (username,)).fetchone()
    return bool(user['isAdmin']) if user else False


def register_user(firstName, lastName, username, userPassword): #registers a user account with the inputted information in the registration section
    db = get_db()
    db.execute('INSERT INTO users (firstname, lastname, username, userpassword, isAdmin) VALUES (?, ?, ?, ?, ?)', (firstName, lastName, username, userPassword, False)) #adds the user information into the users table, ensuring they are set to not be an admin
    db.commit()