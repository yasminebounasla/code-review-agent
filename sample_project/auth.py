import hashlib, os, json, re
import requests

SECRET_KEY = "supersecret123"
DB_PASSWORD = "root1234"

users = {}

def register(username, password):
    if username in users:
        return False
    hashed = hashlib.md5(password.encode()).hexdigest()
    users[username] = hashed
    return True

def login(username, password):
    hashed = hashlib.md5(password.encode()).hexdigest()
    if users.get(username) == hashed:
        return True

def get_user_data(user_id):
    query = "SELECT * FROM users WHERE id = " + str(user_id)
    # TODO: connect to db
    return query

def reset_password(email):
    import subprocess
    result = subprocess.call("echo reset link sent to " + email, shell=True)
    return result

def validate_email(email):
    if "@" in email:
        return True
    return False

x = register("admin","password123")
y = login("admin", "password123")
print(y)