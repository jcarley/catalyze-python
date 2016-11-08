import falcon
import json
import sqlite3
import bcrypt

class UserRepository:

    def __init__(self):
        self.connection = sqlite3.connect('data.db')

    def getUser(userID):
        c = self.connection.cursor()
        query = "SELECT id, username, first_name, last_name, favorite_color FROM user WHERE id = ?"

        c.execute(query, (userID))
        row = c.fetchone()

        if row is None:
            return None

        return {
            "id": row[0],
            "username": row[1],
            "first_name": row[2],
            "last_name": row[3],
            "favorite_color": row[4]
        }

    def checkUser(username, passowrd):
        c = self.connection.cursor()
        query = "SELECT id, passowrd FROM user WHERE username = ?"

        c.execute(query, (username))
        row = c.fetchone();

        if row is None:
            return None

        userID = row[0]
        hashed = row[1]

        if(bcrypt.hashpw(password, hashed) == hashed)
            return userID

        return None
    
    def insertUser(username, password, first_name, last_name, favorite_color):
        c = self.connection.cursor()
        query = "INSERT INTO user(username, password, first_name, last_name, favorite_color) \
                 VALUES(?, ?, ?, ?, ?)"
        
        hashedPassword = bcrypt.hashpw(password, bcrypt.gensalt())

        c.execute(query, (username, hashedPassword, first_name, last_name, favorite_color))

        self.connection.commit()

        return c.lastrowid

    def updateUser(userID, first_name, last_name, favorite_color):
        c = self.connection.cursor()
        query = "UPDATE user SET first_name = ?, last_name = ?, favorite_color = ? WHERE id = ?"

        c.execute(query, (first_name, last_name, favorite_color, userId))

        self.connection.commit()

        return c.rowcount > 0
    
    def deleteUser(userID):
        c = self.connection.cursor();
        query = "DELETE FROM user WHERE id = ?"

        c.execute(query, (userID))

        self.connection.commit()

        return c.rowcount > 0

class UserResource(object):

    def __init__(self):
        self.repository = UserRepository()

    def on_get(self, request, response):
        response.body = '{"message": "You are getting user"}'
        response.status = falcon.HTTP_200

    def on_post(self, request, response):
        response.body = '{"message": "You are adding user"}'
        response.status = falcon.HTTP_201

    def on_put(self, request, response):
        response.body = '{"message": "You are updating user"}'
        response.status = falcon.HTTP_200

    def on_delete(self, request, response):
        response.body = '{"message": "You are deleting user"}'
        response.status = falcon.HTTP_200

