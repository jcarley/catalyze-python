import falcon
import json
import sqlite3
import bcrypt

class UserRepository:

    def __init__(self, dbPath):
        self.dbPath = dbPath

    def getAllUsers(self):
        conn = sqlite3.connect(self.dbPath)
        c = self.conn.cursor()
        query = "SELECT id, username, first_name, last_name, favorite_color FROM user"

        c.execute(query)

        users = []
        for row in c:
            users.append({
                "id": row[0],
                "username": row[1],
                "first_name": row[2],
                "last_name": row[3],
                "favorite_color": row[4]
            })

        conn.close()
    
        return users

    def getUser(self, userID):
        conn = sqlite3.connect(self.dbPath)
        c = conn.cursor()
        query = "SELECT id, username, first_name, last_name, favorite_color FROM user WHERE id = ?"

        c.execute(query, (userID,))
        row = c.fetchone()
        
        conn.close()

        if row is None:
            return None

        return {
            "id": row[0],
            "username": row[1],
            "first_name": row[2],
            "last_name": row[3],
            "favorite_color": row[4]
        }

    def checkUser(self, username, password):
        conn = sqlite3.connect(self.dbPath)
        c = conn.cursor()
        query = "SELECT id, password FROM user WHERE username = ?"

        c.execute(query, (username,))
        row = c.fetchone();

        conn.close()

        if row is None:
            return None

        userID = row[0]
        hashed = row[1].encode()

        if(bcrypt.hashpw(password.encode(), hashed) == hashed):
            return userID

        return None
    
    def insertUser(self, username, password, first_name, last_name, favorite_color):
        conn = sqlite3.connect(self.dbPath);
        c = conn.cursor()
        query = "INSERT INTO user(username, password, first_name, last_name, favorite_color) \
                 VALUES(?, ?, ?, ?, ?)"
        
        hashedPassword = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        c.execute(query, (username, hashedPassword.decode("utf-8"), first_name, last_name, favorite_color))

        conn.commit()
        conn.close()

        return c.lastrowid

    def updateUser(self, userID, first_name, last_name, favorite_color):
        conn = sqlite3.connect(self.dbPath)
        c = conn.cursor()
        query = "UPDATE user SET first_name = ?, last_name = ?, favorite_color = ? WHERE id = ?"

        c.execute(query, (first_name, last_name, favorite_color, userID))

        conn.commit()
        conn.close()

        return c.rowcount > 0
    
    def deleteUser(self, userID):
        conn = sqlite3.connect(self.dbPath)
        c = conn.cursor()
        query = "DELETE FROM user WHERE id = ?"

        c.execute(query, (userID,))

        conn.commit()
        conn.close()

        return c.rowcount > 0

class UserResource(object):

    def __init__(self, dbPath):
        self.repository = UserRepository(dbPath)

    def on_get(self, request, response, userID):

        user = self.repository.getUser(userID)
        if(user is not None):
            response.body = json.dumps(user)
            response.status = falcon.HTTP_200

        else:
            raise falcon.HTTPError(falcon.HTTP_404, 'User not found',
                                   'No user with ID of ' + userID + ' exists.')

    def on_put(self, request, response, userID):
        if request.content_length:
            try:
                raw_data = request.stream.read().decode("utf-8")
            except Exception as ex:
                raise falcon.HTTPError(falcon.HTTP_400, 'Bad request',
                                       'Error reading request body')

            try:
                userdata = json.loads(raw_data)
            except ValueError:
                raise falcon.HTTPError(falcon.HTTP_400, 'Malformed JSON',
                    'Could not decode request body. JSON was improperly formed.')
        else:
            raise falcon.HTTPError(falcon.HTTP_400, 'Empty Request',
                                   'The request body was empty.')

        success = self.repository.updateUser(userID, userdata['first_name'],
                                            userdata['last_name'],
                                            userdata['favorite_color'])

        if(success):
            response.body = '{"message": "You updated the user"}'
            response.status = falcon.HTTP_200
        else:
            raise falcon.HTTPError(falcon.HTTP_400, 'Update Error',
                                   'Could not update user #' + userID)

    def on_delete(self, request, response, userID):

        if self.repository.deleteUser(userID):
            response.body = '{"message": "You deleted the user"}'
            response.status = falcon.HTTP_200
        else:
            raise falcon.HTTPError(falcon.HTTP_400, 'Update Error',
                                   'Could not delete user #' + userID)

class UserCollectionResource(object):
    def __init__(self, dbPath):
        self.repository = UserRepository(dbPath)

    def on_get(self, request, response):
        users = self.repository.getAllUsers()
        response.body = json.dumps({"users": users})
        response.status = falcon.HTTP_200

    def on_post(self, request, response):

        if request.content_length:
            try:
                raw_data = request.stream.read().decode("utf-8")
            except Exception as ex:
                raise falcon.HTTPError(falcon.HTTP_400, 'Bad request',
                                       'Error reading request body')

            try:
                userdata = json.loads(raw_data)
            except ValueError:
                raise falcon.HTTPError(falcon.HTTP_400, 'Malformed JSON',
                    'Could not decode request body. JSON was improperly formed.')
        else:
            raise falcon.HTTPError(falcon.HTTP_400, 'Empty Request',
                                   'The request body was empty.')

        newID = self.repository.insertUser(userdata['username'], userdata['password'],
                                           userdata['first_name'], userdata['last_name'],
                                           userdata['favorite_color'])
            
        if newID is not None:
            response.body = json.dumps(self.repository.getUser(newID))
            response.status = falcon.HTTP_201
        else:
            raise falcon.HTTPError(falcon.HTTP_400, 'Create Error',
                                   'Could not create new user')