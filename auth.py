import falcon
import json
import sqlite3
import uuid
import datetime
import users

def authHook(request, response, resource, params):
    if not resource.authcheck.isAuthenticated(request):
        if(resource.authcheck.token is None):
            title = "No Token"
            message = "You did not provide an authentication token with your request."
        else:
            title = "Invalid Token"
            message = "The token you provided is invalid or expired."

        raise falcon.HTTPError(falcon.HTTP_401, title, message)

class Authorizer:
    def __init__(self, dbPath):
        self.authRepo = AuthRepository(dbPath)
        self.userID = None
        self.token = None

    def isAuthenticated(self, request):
        if request.auth is None :
            self.token = None
            self.userID = None

        #if token doesn't match cach or this is a fresh instance,
        #query the database. otherwise use cached values
        elif self.token is None or self.token is not request.auth:
            self.token = request.auth
            self.userID = self.authRepo.checkToken(self.token)

        return self.userID is not None


class AuthRepository:
    def __init__(self, dbPath):
        self.dbPath = dbPath

    def createToken(self, userID, lifespan):
        conn = self._makeConnection()
        c = conn.cursor()
        query = "INSERT INTO auth_token(token, user_id, created, expires) \
                 VALUES(?, ?, ?, ?)"

        token = uuid.uuid4().hex
        currentTime = datetime.datetime.now()
        expires = currentTime + datetime.timedelta(seconds=lifespan)

        c.execute(query, (token, userID,
                          currentTime.strftime("%Y-%m-%d %H:%M:%S"),
                          expires.strftime("%Y-%m-%d %H:%M:%S")))

        conn.commit()
        conn.close()

        return token
    
    def checkToken(self, token):
        conn = self._makeConnection()
        c = conn.cursor()
        query = "SELECT user_id, expires FROM auth_token WHERE token = ?"

        c.execute(query, (token,))
        row = c.fetchone();

        conn.close()

        print(row)

        if row is None:
            return None

        userID = row[0]
        expires = datetime.datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")
        currentTime = datetime.datetime.now()

        if(currentTime <= expires):
            return userID

        self.deleteToken(token)
        return None
    
    def deleteToken(self, token):
        conn = self._makeConnection()
        c = conn.cursor()
        query = "DELETE FROM auth_token WHERE token = ?"

        c.execute(query, (token,))

        conn.commit()
        conn.close()

        return c.rowcount > 0
    
    def _makeConnection(self):
        conn = sqlite3.connect(self.dbPath)
        conn.execute("PRAGMA foreign_keys = 1")

        return conn
    
class AuthResource(object):
    def __init__(self, dbPath, authcheck):
        self.users = users.UserRepository(dbPath)
        self.repository = AuthRepository(dbPath)
        self.authcheck = authcheck
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

    @falcon.before(authHook)
    def on_delete(self, request, response):
        if(not self.repository.deleteToken(self.authcheck.token)):
            raise falcon.HTTPError(falcon.HTTP_400, 'Delete Error',
                                   'Problem invalidating token. It might already be invalid.')

        response.body = '{"message": "Token has been successfully invalidated"}'
        response.status = falcon.HTTP_200
