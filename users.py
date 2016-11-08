import falcon
import json
import sqlite3
import bcrypt

class UserRepository:

    def __init__(self, dbPath):
        self.connection = sqlite3.connect(dbPath)
        c = self.connection.cursor()

    def getUser(self, userID):
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

    def checkUser(self, username, passowrd):
        c = self.connection.cursor()
        query = "SELECT id, passowrd FROM user WHERE username = ?"

        c.execute(query, (username))
        row = c.fetchone();

        if row is None:
            return None

        userID = row[0]
        hashed = row[1].encode()

        if(bcrypt.hashpw(password.encode(), hashed) == hashed):
            return userID

        return None
    
    def insertUser(self, username, password, first_name, last_name, favorite_color):
        c = self.connection.cursor()
        query = "INSERT INTO user(username, password, first_name, last_name, favorite_color) \
                 VALUES(?, ?, ?, ?, ?)"
        
        hashedPassword = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        c.execute(query, (username, hashedPassword.decode("utf-8"), first_name, last_name, favorite_color))

        self.connection.commit()

        return c.lastrowid

    def updateUser(self, userID, first_name, last_name, favorite_color):
        c = self.connection.cursor()
        query = "UPDATE user SET first_name = ?, last_name = ?, favorite_color = ? WHERE id = ?"

        c.execute(query, (first_name, last_name, favorite_color, userId))

        self.connection.commit()

        return c.rowcount > 0
    
    def deleteUser(self, userID):
        c = self.connection.cursor();
        query = "DELETE FROM user WHERE id = ?"

        c.execute(query, (userID))

        self.connection.commit()

        return c.rowcount > 0

    def __del__(self):
        self.connection.close()

class UserResource(object):

    def __init__(self, dbPath):
        self.repository = UserRepository(dbPath)

    def on_get(self, request, response, userID):

        user = self.repository.getUser(userID)
        if(user is not None):
            response.body = json.dumps(user)
            response.status = falcon.HTTP_200

        else:
            response.body = '{"error": "User not found"}'
            response.status = falcon.HTTP_404

    def on_put(self, request, response, userID):
        response.body = '{"message": "You are updating user"}'
        response.status = falcon.HTTP_200

    def on_delete(self, request, response, userID):
        response.body = '{"message": "You are deleting user"}'
        response.status = falcon.HTTP_200

class UserCollectionResource(object):
    def __init__(self, dbPath):
        self.repository = UserRepository(dbPath)

    def on_get(self, request, response):
        response.body = '{"message": "You are getting all users"}'
        response.status = falcon.HTTP_200

    def on_post(self, request, response):

        if request.content_length:
            try:
                raw_data = request.stream.read().decode("utf-8") 
            except Exception as ex:
                response.body = '{"error": "Error reading request body"}'
                response.status = falcon.HTTP_400
                return

            try:
                userdata = json.loads(raw_data)
            except ValueError:
                response.body = '{"error": "Malformed JSON"}'
                response.status = falcon.HTTP_400
                return
        else:
            response.body = '{"error": "Empty request"}'
            response.status = falcon.HTTP_400
            return

        newID = self.repository.insertUser(userdata['username'], userdata['password'],
                                           userdata['first_name'], userdata['last_name'],
                                           userdata['favorite_color'])
            
        if newID is not None:
            response.body = '{"message": "You are adding user"}'
            response.status = falcon.HTTP_201
        else:
            response.body = '{"error": "Could not add user"}'
            response.status = falcon.HTTP_400