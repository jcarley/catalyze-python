import falcon
import json
import sqlite3
import uuid
import datetime
from users import UserRepository

class AuthRepository:
    def __init__(self, dbPath):
        self.dbPath = dbPath

    def createAuthToken(self, userID, lifespan):
        conn = sqlite3.connect(self.dbPath);
        c = conn.cursor()
        query = "INSERT INTO auth_tokens(token, user_id, created, expires) \
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