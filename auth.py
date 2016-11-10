import falcon
import json
import sqlite3
import uuid
import datetime
from users import UserRepository

class AuthRepository:
    def __init__(self, dbPath):
        self.dbPath = dbPath

    def createToken(self, userID, lifespan):
        conn = sqlite3.connect(self.dbPath);
        c = conn.cursor()
        query = "INSERT INTO auth_token(token, user_id, created, expires) \
                 VALUES(?, ?, ?, ?)"

        token = uuid.uuid4().hex
        currentTime = datetime.datetime.now()
        expires = currentTime + datetime.timedelta(seconds=lifespan)

        c.execute(query, (uuid.uuid4().hex, userID,
                          currentTime.strftime("%Y-%m-%d %H:%M:%S"),
                          expires.strftime("%Y-%m-%d %H:%M:%S")))

        conn.commit()
        conn.close()

        return token
    
    def checkToken(self, token):
        conn = sqlite3.connect(self.dbPath)
        c = conn.cursor()
        query = "SELECT userID, expires FROM auth_token WHERE token = ?"

        c.execute(query, (token,))
        row = c.fetchone();

        conn.close()

        if row is None:
            return None

        userID = row[0]
        expires = datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")
        currentTime = datetime.datetime.now()

        if(currentTime <= expires):
            return userID

        self.deleteToken(token)
        return None
    
    def deleteToken(self, token):
        conn = sqlite3.connect(self.dbPath)
        c = conn.cursor()
        query = "DELETE FROM auth_token WHERE token = ?"

        c.execute(query, (token,))

        conn.commit()
        conn.close()

        return c.rowcount > 0
    
class AuthResource(object):
    def __init__(self, dbPath):
        self.users = UserRepository(dbPath)
        self.repository = AuthRepository(dbPath)
        self.lifespan = 24 * 60 * 60
        
    def on_post(self, request, response):
        if request.content_length:
            try:
                raw_data = request.stream.read().decode("utf-8")
            except Exception as ex:
                raise falcon.HTTPError(falcon.HTTP_400, 'Bad request',
                                       'Error reading request body')

            try:
                authdata = json.loads(raw_data)
            except ValueError:
                raise falcon.HTTPError(falcon.HTTP_400, 'Malformed JSON',
                    'Could not decode request body. JSON was improperly formed.')
        else:
            raise falcon.HTTPError(falcon.HTTP_400, 'Empty Request',
                                   'The request body was empty.')
        
        authUser = self.users.checkUser(authdata['username'], authdata['password'])

        if authUser is None:
            raise falcon.HTTPError(falcon.HTTP_401, "Incorrect Credentials",
                                   'The username and password were incorrect')
        
        token = self.repository.createToken(authUser, self.lifespan)

        response.body = '{"token": "' + token + '"}'
        response.status = falcon.HTTP_200

        